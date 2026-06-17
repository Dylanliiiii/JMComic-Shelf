from PySide6.QtWidgets import QAbstractScrollArea, QTableWidget, QWidget


PAGE_STYLE = """
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


def apply_page_style(widget: QWidget) -> None:
    widget.setStyleSheet(PAGE_STYLE)


def prepare_table(table: QTableWidget) -> None:
    table.setAlternatingRowColors(False)
    table.setShowGrid(False)
    table.setStyleSheet(PAGE_STYLE)
    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
