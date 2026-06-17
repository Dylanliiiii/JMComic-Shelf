from PySide6.QtWidgets import QAbstractScrollArea, QTableWidget, QWidget
from qfluentwidgets import isDarkTheme


LIGHT_PAGE_STYLE = """
QWidget {
    background: #fbf7f7;
    color: #1f1f1f;
    font-size: 15px;
}
QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background: #fbf7f7;
    border: none;
}
QTableWidget {
    background: #ffffff;
    color: #1f1f1f;
    gridline-color: #e6e1e1;
    selection-background-color: #e8f3ff;
    selection-color: #1f1f1f;
}
QHeaderView::section {
    background: #f3eeee;
    color: #1f1f1f;
    border: none;
    border-bottom: 1px solid #e2dddd;
    padding: 8px;
}
"""

DARK_PAGE_STYLE = """
QWidget {
    background: #202020;
    color: #f3f3f3;
    font-size: 15px;
}
QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background: #202020;
    border: none;
}
QTableWidget {
    background: #2b2b2b;
    color: #f3f3f3;
    gridline-color: #3d3d3d;
    selection-background-color: #2d5f76;
    selection-color: #ffffff;
}
QHeaderView::section {
    background: #303030;
    color: #f3f3f3;
    border: none;
    border-bottom: 1px solid #444444;
    padding: 8px;
}
"""


def page_style() -> str:
    return DARK_PAGE_STYLE if isDarkTheme() else LIGHT_PAGE_STYLE


def apply_page_style(widget: QWidget) -> None:
    widget.setStyleSheet(page_style())


def prepare_table(table: QTableWidget) -> None:
    table.setAlternatingRowColors(False)
    table.setShowGrid(False)
    table.setStyleSheet(page_style())
    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
