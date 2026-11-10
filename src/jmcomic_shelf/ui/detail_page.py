from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, LineEdit, PrimaryPushButton, SmoothScrollArea, TitleLabel

from jmcomic.jm_exception import MissingAlbumPhotoException
from jmcomic_shelf.database import ShelfDatabase
from jmcomic_shelf.detail_service import fetch_album_detail_result, parse_preview_ids
from jmcomic_shelf.index_service import rebuild_index_from_download_dir, record_from_album
from jmcomic_shelf.paths import get_cover_cache_dir, get_database_path, get_settings_path
from jmcomic_shelf.settings import ShelfSettings

from .preview_card import PreviewCard
from .styles import TRANSPARENT_SCROLL_STYLE, apply_page_style


class PreviewSignals(QObject):
    progress = Signal(str)
    found = Signal(object)
    finished = Signal(list)


class PreviewQuery(QRunnable):
    def __init__(self, ids):
        super().__init__()
        self.ids = ids
        self.signals = PreviewSignals()

    def run(self):
        failures = []
        db = None
        try:
            settings = ShelfSettings.load(get_settings_path())
            cache = get_cover_cache_dir(settings.app_data_dir)
            db_path = get_database_path(settings.app_data_dir)
            try:
                if settings.download_dir:
                    rebuild_index_from_download_dir(settings.download_dir, db_path, cache)
                db = ShelfDatabase(db_path)
                db.open()
            except Exception as exc:
                if db is not None:
                    db.close()
                    db = None
                failures.append(f'本地书库读取失败：{exc}')

            for index, jm_id in enumerate(self.ids, 1):
                self.signals.progress.emit(f'正在查询 JM{jm_id}（{index}/{len(self.ids)}）')
                try:
                    local = None
                    if db is not None:
                        local = next((r for r in db.query_albums(jm_id) if r.jm_id == jm_id), None)
                    result = fetch_album_detail_result(settings.option_path, jm_id, cache,
                                                       local.cover_path if local else '')
                    record = record_from_album(result.album, local.pdf_path if local else '', result.cover_path)
                    self.signals.found.emit(record)
                except MissingAlbumPhotoException:
                    failures.append(f'JM{jm_id}：作品不存在或已下架')
                except Exception as exc:
                    failures.append(f'JM{jm_id}：查询失败，{exc}')
        except Exception as exc:
            failures.append(f'无法查询 {"、".join("JM" + i for i in self.ids)}：{exc}')
        finally:
            if db:
                db.close()
            self.signals.finished.emit(failures)


class DetailPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('detailPage')
        apply_page_style(self)
        self.query = None
        self.invalid = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)
        layout.addWidget(TitleLabel('禁漫预览', self))

        header = QHBoxLayout()
        self.input = LineEdit(self)
        self.input.setPlaceholderText('输入一个或多个 JM 号，用空格或逗号分隔')
        self.input.returnPressed.connect(self.load_detail)
        self.query_button = PrimaryPushButton('查看详情', self)
        self.query_button.clicked.connect(self.load_detail)
        header.addWidget(self.input, 1)
        header.addWidget(self.query_button)
        layout.addLayout(header)

        self.scroll = SmoothScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(TRANSPARENT_SCROLL_STYLE)
        content = QWidget()
        content.setObjectName('previewResults')
        content.setStyleSheet('#previewResults { background: transparent; }')
        column = QVBoxLayout(content)
        column.setContentsMargins(0, 0, 12, 0)
        self.cards = QVBoxLayout()
        self.cards.setSpacing(12)
        column.addLayout(self.cards)
        self.info = BodyLabel(content)
        self.info.setTextFormat(Qt.TextFormat.PlainText)
        self.info.setWordWrap(True)
        self.info.hide()
        column.addWidget(self.info)
        column.addStretch(1)
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll, 1)

    @Slot()
    def load_detail(self):
        if self.query is not None:
            return
        ids, self.invalid = parse_preview_ids(self.input.text())
        while self.cards.count():
            card = self.cards.takeAt(0).widget()
            card.hide()
            card.deleteLater()
        self.scroll.verticalScrollBar().setValue(0)
        self.info.show()
        if not ids:
            self._finish([] if self.invalid else ['请输入 JM 号。'])
            return

        self.info.setText('正在搜索中…')
        self.query_button.setEnabled(False)
        self.input.setEnabled(False)
        self.query = PreviewQuery(ids)
        self.query.signals.progress.connect(self.info.setText)
        self.query.signals.found.connect(self._add_card)
        self.query.signals.finished.connect(self._finish)
        QThreadPool.globalInstance().start(self.query)

    @Slot(object)
    def _add_card(self, record):
        self.cards.addWidget(PreviewCard(record))

    @Slot(list)
    def _finish(self, errors):
        messages = ([f'号码格式有误：{"、".join(self.invalid)}'] if self.invalid else []) + errors
        self.info.setText('\n'.join(messages))
        self.info.setVisible(bool(messages))
        self.input.setEnabled(True)
        self.query_button.setEnabled(True)
        self.query = None
