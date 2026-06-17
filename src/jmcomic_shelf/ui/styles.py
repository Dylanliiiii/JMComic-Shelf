from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractScrollArea, QTableWidget, QWidget


TRANSPARENT_SCROLL_STYLE = """
QScrollArea {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QScrollBar {
    background: transparent;
}
"""

DARK_CONTROL_STYLE = """
LineEdit, TextEdit, QLineEdit, QTextEdit {
    background: #33292c;
    color: #f5f0f1;
    border: 1px solid #493d41;
    border-radius: 6px;
}
CardWidget {
    background: #3a2f32;
    border: 1px solid #493d41;
    border-radius: 8px;
}
QTableWidget {
    background: #33292c;
    color: #f5f0f1;
    border: 1px solid #493d41;
    border-radius: 8px;
    gridline-color: #5a4a4f;
}
QHeaderView::section {
    background: #3a2f32;
    color: #f5f0f1;
    border: none;
    border-right: 1px solid #5a4a4f;
    border-bottom: 1px solid #5a4a4f;
    padding: 8px 14px;
}
QTableWidget::item {
    border-right: 1px solid #4d3f44;
    padding-left: 14px;
    padding-right: 14px;
}
"""


def apply_page_style(widget: QWidget) -> None:
    widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    widget.setStyleSheet(f'#{widget.objectName()} {{ background: transparent; }}\n{DARK_CONTROL_STYLE}')


def prepare_table(table: QTableWidget) -> None:
    table.setAlternatingRowColors(False)
    table.setShowGrid(True)
    table.verticalHeader().setVisible(False)
    table.setStyleSheet(DARK_CONTROL_STYLE)
    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
