from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractScrollArea, QTableWidget, QWidget
from qfluentwidgets import isDarkTheme


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

def control_style() -> str:
    if isDarkTheme():
        control_bg = '#33292c'
        card_bg = '#3a2f32'
        text = '#f5f0f1'
        border = '#493d41'
        grid = '#5a4a4f'
        item_border = '#4d3f44'
    else:
        control_bg = '#fbf7f8'
        card_bg = '#ffffff'
        text = '#211a1d'
        border = '#ddd5d8'
        grid = '#e7dde1'
        item_border = '#eee4e8'
    return f"""
LineEdit, TextEdit, QLineEdit, QTextEdit {{
    background: {control_bg};
    color: {text};
    border: 1px solid {border};
    border-radius: 6px;
}}
CardWidget {{
    background: {card_bg};
    border: 1px solid {border};
    border-radius: 8px;
}}
QTableWidget {{
    background: {control_bg};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    gridline-color: {grid};
}}
QHeaderView::section {{
    background: {card_bg};
    color: {text};
    border: none;
    border-right: 1px solid {grid};
    border-bottom: 1px solid {grid};
    padding: 8px 14px;
}}
QTableWidget::item {{
    border-right: 1px solid {item_border};
    padding-left: 14px;
    padding-right: 14px;
}}
"""


def apply_page_style(widget: QWidget) -> None:
    widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    widget.setStyleSheet(f'#{widget.objectName()} {{ background: transparent; }}\n{control_style()}')


def prepare_table(table: QTableWidget) -> None:
    table.setAlternatingRowColors(False)
    table.setShowGrid(True)
    table.verticalHeader().setVisible(False)
    table.setStyleSheet(control_style())
    table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
