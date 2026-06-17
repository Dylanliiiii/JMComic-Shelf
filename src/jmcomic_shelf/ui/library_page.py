import os

from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QFontMetrics, QPixmap
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QMenu, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget
from qfluentwidgets import BodyLabel, CardWidget, CaptionLabel, CheckBox, LineEdit, MessageBox, Pivot, PrimaryPushButton, PushButton, SmoothScrollArea, SubtitleLabel, TitleLabel, isDarkTheme

from jmcomic_shelf.database import ShelfDatabase
from jmcomic_shelf.delete_service import delete_album_files
from jmcomic_shelf.file_actions import open_pdf, reveal_in_explorer
from jmcomic_shelf.index_service import group_by_author, rebuild_index_from_download_dir
from jmcomic_shelf.paths import get_cover_cache_dir, get_database_path, get_settings_path
from jmcomic_shelf.settings import ShelfSettings

from .styles import TRANSPARENT_SCROLL_STYLE, apply_page_style


class IndexSyncWorker(QObject):
    finished = Signal(str)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    @Slot()
    def run(self):
        error = ''
        try:
            rebuild_index_from_download_dir(
                self.settings.download_dir,
                get_database_path(self.settings.app_data_dir),
                get_cover_cache_dir(self.settings.app_data_dir),
            )
        except Exception as e:
            error = str(e)
        self.finished.emit(error)


class CoverCard(CardWidget):
    selection_changed = Signal(str, bool)
    cover_width = 150
    card_width = 178

    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.record = record
        self.selection_mode = False
        self.selected = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedWidth(self.card_width)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.checkbox = CheckBox(self)
        self.checkbox.setVisible(False)
        self.checkbox.clicked.connect(self.toggle_selected)
        layout.addWidget(self.checkbox, 0, Qt.AlignmentFlag.AlignLeft)

        self.cover = QLabel(self)
        self.cover.setFixedSize(self.cover_width, 210)
        self.cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover.setStyleSheet('border-radius: 6px;')
        self._load_cover()

        caption = f'JM{record.jm_id} {record.title}'
        metrics = QFontMetrics(self.font())
        self.caption = CaptionLabel(metrics.elidedText(caption, Qt.TextElideMode.ElideRight, self.cover_width), self)
        self.caption.setFixedWidth(self.cover_width)
        self.caption.setToolTip(caption)

        layout.addWidget(self.cover)
        layout.addWidget(self.caption)

    def set_selection_mode(self, enabled: bool):
        self.selection_mode = enabled
        self.checkbox.setVisible(enabled)
        if not enabled:
            self.set_selected(False, emit=False)

    def set_selected(self, selected: bool, emit: bool = True):
        self.selected = selected
        self.checkbox.setChecked(selected)
        if selected:
            self.setStyleSheet('CoverCard { border: 1px solid #00c8d7; border-radius: 8px; }')
        else:
            self.setStyleSheet('')
        if emit:
            self.selection_changed.emit(self.record.jm_id, selected)

    def toggle_selected(self, *_):
        self.set_selected(not self.selected)

    def _load_cover(self):
        if self.record.cover_path and os.path.exists(self.record.cover_path):
            pixmap = QPixmap(self.record.cover_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.cover.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.cover.setPixmap(scaled)
                return
        self.cover.setText('无封面')

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.selection_mode:
            self.toggle_selected()
            event.accept()
            return
        if event.button() == Qt.MouseButton.LeftButton and self.record.pdf_path:
            open_pdf(self.record.pdf_path)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        open_action = QAction('打开 PDF', self)
        reveal_action = QAction('在文件资源管理器中显示位置', self)
        open_action.triggered.connect(lambda: open_pdf(self.record.pdf_path))
        reveal_action.triggered.connect(lambda: reveal_in_explorer(self.record.pdf_path))
        exists = bool(self.record.pdf_path and os.path.exists(self.record.pdf_path))
        open_action.setEnabled(exists)
        reveal_action.setEnabled(exists)
        menu.addAction(open_action)
        menu.addAction(reveal_action)
        menu.exec(event.globalPos())


class LibraryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.records = []
        self.load_error = ''
        self.current_columns = 0
        self.pending_columns = 0
        self.batch_mode = False
        self.selected_ids = set()
        self.available_tags = []
        self.active_tag = ''
        self.sync_thread = None
        self.sync_worker = None
        self.setObjectName('libraryPage')
        apply_page_style(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        self.resize_render_timer = QTimer(self)
        self.resize_render_timer.setSingleShot(True)
        self.resize_render_timer.setInterval(150)
        self.resize_render_timer.timeout.connect(self.apply_pending_resize_render)

        title = TitleLabel('本地书库', self)
        self.search_input = LineEdit(self)
        self.search_input.setPlaceholderText('搜索 JM号 / 作者 / 标签')
        self.search_input.textChanged.connect(self.on_search_changed)

        note = CaptionLabel(
            '浏览当前下载目录里的本地漫画；可输入 JM 号、作者或标签筛选，点击封面打开 PDF，右键可定位文件。',
            self,
        )
        note.setWordWrap(True)

        self.filter_pivot = Pivot(self)
        self.filter_pivot.addItem('all', '全部', self.clear_filter)
        self.filter_pivot.setCurrentItem('all')
        self.category_button = PushButton('分类', self)
        self.category_button.clicked.connect(self.toggle_category_panel)
        self.batch_button = PushButton('批量管理', self)
        self.batch_button.clicked.connect(self.toggle_batch_mode)
        filter_row = QHBoxLayout()
        filter_row.setContentsMargins(0, 0, 0, 0)
        self.filter_host = QFrame(self)
        self.filter_host.setStyleSheet(self._filter_host_style())
        filter_host_layout = QHBoxLayout(self.filter_host)
        filter_host_layout.setContentsMargins(10, 4, 10, 4)
        filter_host_layout.addWidget(self.filter_pivot)
        self.filter_host.setFixedHeight(48)
        self.category_button.setFixedHeight(self.filter_host.height())
        filter_row.addWidget(self.filter_host)
        filter_row.addWidget(self.category_button)
        filter_row.addStretch(1)
        filter_row.addWidget(self.batch_button)

        self.category_host = QFrame(self)
        self.category_host.setStyleSheet(self._filter_host_style())
        self.category_layout = QGridLayout(self.category_host)
        self.category_layout.setContentsMargins(10, 8, 10, 8)
        self.category_layout.setHorizontalSpacing(8)
        self.category_layout.setVerticalSpacing(8)
        self.category_host.setVisible(False)

        self.batch_bar = QHBoxLayout()
        self.batch_bar.setContentsMargins(0, 0, 0, 0)
        self.batch_bar.setSpacing(8)
        self.selected_label = CaptionLabel('已选 0 本', self)
        self.select_all_button = PushButton('全选', self)
        self.invert_button = PushButton('反选', self)
        self.clear_selection_button = PushButton('取消全选', self)
        self.delete_button = PrimaryPushButton('删除选中', self)
        self.exit_batch_button = PushButton('退出批量管理', self)
        self.select_all_button.clicked.connect(self.select_all)
        self.invert_button.clicked.connect(self.invert_selection)
        self.clear_selection_button.clicked.connect(self.clear_selection)
        self.delete_button.clicked.connect(self.delete_selected)
        self.exit_batch_button.clicked.connect(lambda: self.set_batch_mode(False))
        self.batch_bar.addWidget(self.selected_label)
        self.batch_bar.addStretch(1)
        self.batch_bar.addWidget(self.select_all_button)
        self.batch_bar.addWidget(self.invert_button)
        self.batch_bar.addWidget(self.clear_selection_button)
        self.batch_bar.addWidget(self.delete_button)
        self.batch_bar.addWidget(self.exit_batch_button)
        self.batch_host = QWidget(self)
        self.batch_host.setLayout(self.batch_bar)
        self.batch_host.setVisible(False)

        self.scroll = SmoothScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(self.scroll.Shape.NoFrame)
        self.scroll.setStyleSheet(TRANSPARENT_SCROLL_STYLE)
        self.content = QWidget(self.scroll)
        self.content.setStyleSheet('background: transparent;')
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 14, 0)
        self.content_layout.setSpacing(16)
        self.scroll.setWidget(self.content)

        layout.addWidget(title)
        layout.addWidget(self.search_input)
        layout.addWidget(note)
        layout.addLayout(filter_row)
        layout.addWidget(self.category_host)
        layout.addWidget(self.batch_host)
        self.action_status = CaptionLabel('', self)
        self.action_status.setWordWrap(True)
        self.action_status.setVisible(False)
        layout.addWidget(self.action_status)
        layout.addWidget(self.scroll, 1)
        self.reload()

    def clear_filter(self):
        self.active_tag = ''
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)
        self.reload()

    def on_search_changed(self):
        if self.active_tag:
            self.active_tag = ''
        self.reload()

    def reload(self, sync_index: bool = True):
        query = self.search_input.text().strip()
        settings = ShelfSettings.load(get_settings_path())
        sync_error = ''
        if sync_index:
            try:
                self._sync_index_from_settings(settings)
            except Exception as e:
                sync_error = str(e)
        db = ShelfDatabase(get_database_path(settings.app_data_dir))
        try:
            db.open()
            self.available_tags = db.list_tags()
            if self.active_tag:
                self.records = db.query_albums_by_tag(self.active_tag)
            else:
                self.records = db.query_albums(query)
            self.load_error = sync_error
        except Exception as e:
            self.records = []
            self.available_tags = []
            self.load_error = str(e)
        finally:
            db.close()
        self.selected_ids &= {record.jm_id for record in self.records}
        self.render_records()

    def reload_for_activation(self):
        self.reload(sync_index=False)
        self.start_background_sync()

    def start_background_sync(self):
        settings = ShelfSettings.load(get_settings_path())
        if not settings.download_dir:
            return
        if self.sync_thread and self.sync_thread.isRunning():
            return
        self.sync_thread = QThread(self)
        self.sync_worker = IndexSyncWorker(settings)
        self.sync_worker.moveToThread(self.sync_thread)
        self.sync_thread.started.connect(self.sync_worker.run)
        self.sync_worker.finished.connect(self.on_background_sync_finished)
        self.sync_worker.finished.connect(self.sync_thread.quit)
        self.sync_worker.finished.connect(self.sync_worker.deleteLater)
        self.sync_thread.finished.connect(self.sync_thread.deleteLater)
        self.sync_thread.finished.connect(self.clear_background_sync)
        self.sync_thread.start()

    @Slot(str)
    def on_background_sync_finished(self, error: str):
        if error:
            self.load_error = error
            self.render_records()
            return
        self.reload(sync_index=False)

    @Slot()
    def clear_background_sync(self):
        self.sync_thread = None
        self.sync_worker = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, 'scroll'):
            return
        columns = self._column_count()
        if self.records and columns != self.current_columns:
            self.pending_columns = columns
            self.resize_render_timer.start()

    def apply_pending_resize_render(self):
        if self.records and self.pending_columns and self.pending_columns != self.current_columns:
            self.render_records()

    def _sync_index_from_settings(self, settings):
        if not settings.download_dir:
            return
        rebuild_index_from_download_dir(
            settings.download_dir,
            get_database_path(settings.app_data_dir),
            get_cover_cache_dir(settings.app_data_dir),
        )

    def render_records(self):
        self._clear_content()
        self.filter_pivot.setItemText('all', f'全部 · {len(self.records)} 本')
        self.filter_host.setStyleSheet(self._filter_host_style())
        self.category_host.setStyleSheet(self._filter_host_style())
        self.render_tag_buttons()
        if not self.records:
            self.content_layout.addWidget(self._empty_card())
            self.content_layout.addStretch(1)
            return

        columns = self._column_count()
        self.current_columns = columns
        for author, records in group_by_author(self.records).items():
            self.content_layout.addWidget(SubtitleLabel(f'{author} · {len(records)} 本', self.content))
            grid_host = QWidget(self.content)
            grid_host.setStyleSheet('background: transparent;')
            grid = QGridLayout(grid_host)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(24)
            grid.setVerticalSpacing(18)
            grid.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            for index, record in enumerate(records):
                card = CoverCard(record, grid_host)
                card.set_selection_mode(self.batch_mode)
                card.set_selected(record.jm_id in self.selected_ids, emit=False)
                card.selection_changed.connect(self.on_card_selection_changed)
                grid.addWidget(card, index // columns, index % columns, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            for column in range(columns):
                grid.setColumnMinimumWidth(column, CoverCard.card_width)
                grid.setColumnStretch(column, 0)
            grid.setColumnStretch(columns, 1)
            grid.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum), 0, columns)
            self.content_layout.addWidget(grid_host)

        self.content_layout.addStretch(1)
        self.update_batch_actions()

    def toggle_category_panel(self):
        self.category_host.setVisible(not self.category_host.isVisible())
        if self.category_host.isVisible():
            self.render_tag_buttons()

    def apply_tag_filter(self, tag: str):
        self.active_tag = tag
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)
        self.reload(sync_index=False)

    def render_tag_buttons(self):
        while self.category_layout.count():
            item = self.category_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not self.available_tags:
            self.category_layout.addWidget(CaptionLabel('暂无标签', self.category_host), 0, 0)
            return

        columns = max(1, min(6, self._column_count()))
        for index, tag in enumerate(self.available_tags):
            button_cls = PrimaryPushButton if tag == self.active_tag else PushButton
            button = button_cls(tag, self.category_host)
            button.clicked.connect(lambda checked=False, value=tag: self.apply_tag_filter(value))
            self.category_layout.addWidget(button, index // columns, index % columns)

    def _column_count(self):
        available_width = max(1, self.scroll.viewport().width() - 18)
        spacing = 24
        return max(1, (available_width + spacing) // (CoverCard.card_width + spacing))

    def _filter_host_style(self):
        if isDarkTheme():
            background = '#34272c'
            border = '#46363b'
        else:
            background = '#f3ecf0'
            border = '#e4d8de'
        return f'QFrame {{ background: {background}; border: 1px solid {border}; border-radius: 8px; }}'

    def _empty_card(self):
        card = QFrame(self.content)
        if isDarkTheme():
            background = '#3a2f32'
            border = '#493d41'
        else:
            background = '#ffffff'
            border = '#ddd5d8'
        card.setStyleSheet(f'QFrame {{ background: {background}; border: 1px solid {border}; border-radius: 8px; }}')
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        if self.load_error:
            title = SubtitleLabel('无法读取书库索引', card)
            desc = BodyLabel(self.load_error, card)
        else:
            title = SubtitleLabel('暂无内容', card)
            desc = BodyLabel('请先在设置中确认下载目录，或点击“重建索引”扫描现有漫画。', card)
        desc.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(desc)
        return card

    def toggle_batch_mode(self):
        self.set_batch_mode(not self.batch_mode)

    def set_batch_mode(self, enabled: bool):
        self.batch_mode = enabled
        if not enabled:
            self.selected_ids.clear()
        self.batch_button.setText('退出批量管理' if enabled else '批量管理')
        self.batch_host.setVisible(enabled)
        self.render_records()

    def on_card_selection_changed(self, jm_id: str, selected: bool):
        if selected:
            self.selected_ids.add(jm_id)
        else:
            self.selected_ids.discard(jm_id)
        self.update_batch_actions()

    def select_all(self):
        self.selected_ids = {record.jm_id for record in self.records}
        self.render_records()

    def invert_selection(self):
        visible_ids = {record.jm_id for record in self.records}
        self.selected_ids = visible_ids - self.selected_ids
        self.render_records()

    def clear_selection(self):
        self.selected_ids.clear()
        self.render_records()

    def update_batch_actions(self):
        count = len(self.selected_ids)
        self.selected_label.setText(f'已选 {count} 本')
        self.delete_button.setEnabled(count > 0)
        has_records = bool(self.records)
        self.select_all_button.setEnabled(has_records)
        self.invert_button.setEnabled(has_records)
        self.clear_selection_button.setEnabled(count > 0)

    def delete_selected(self):
        records = [record for record in self.records if record.jm_id in self.selected_ids]
        if not records:
            return
        box = MessageBox(
            '确认删除本地漫画',
            f'此操作会删除所选 {len(records)} 本漫画对应的本地文件，包括漫画目录、PDF 文件和桌面端数据库索引。\n\n删除后无法从应用内撤销，确认继续吗？',
            self,
        )
        box.yesButton.setText('确认删除')
        box.cancelButton.setText('取消')
        if not box.exec():
            return

        settings = ShelfSettings.load(get_settings_path())
        result = delete_album_files(records, settings.download_dir)
        db = ShelfDatabase(get_database_path(settings.app_data_dir))
        try:
            db.open()
            db.delete_albums([record.jm_id for record in records])
        finally:
            db.close()
        self.selected_ids.clear()
        self.reload()
        messages = [f'已删除 {len(records)} 本漫画的本地文件和书库索引。']
        if result.skipped_paths:
            messages.append(f'有 {len(result.skipped_paths)} 个路径不在下载目录内，已跳过。')
        if result.errors:
            messages.append('部分文件删除失败：' + '；'.join(result.errors[:3]))
        self.action_status.setText(' '.join(messages))
        self.action_status.setVisible(True)

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
