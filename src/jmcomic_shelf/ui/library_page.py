from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LibraryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('书库'))
