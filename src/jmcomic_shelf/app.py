def main():
    import sys

    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication

    from .paths import get_app_icon_path
    from .paths import get_settings_path
    from .settings import ShelfSettings
    from .ui.main_window import MainWindow
    from .ui.theme import apply_app_theme

    app = QApplication(sys.argv)
    apply_app_theme(ShelfSettings.load(get_settings_path()).theme_mode)
    app.setWindowIcon(QIcon(get_app_icon_path()))
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
