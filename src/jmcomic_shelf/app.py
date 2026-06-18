def main():
    import sys

    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    from .paths import get_app_icon_path
    from .ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(get_app_icon_path()))
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
