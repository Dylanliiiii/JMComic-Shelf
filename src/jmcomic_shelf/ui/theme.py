from qfluentwidgets import Theme, setTheme, setThemeColor


THEME_COLOR = '#00c8d7'

THEME_LABELS = {
    'auto': '跟随系统',
    'light': '浅色',
    'dark': '深色',
}

THEME_VALUES = {label: value for value, label in THEME_LABELS.items()}


def normalize_theme_mode(theme_mode: str) -> str:
    if theme_mode in THEME_LABELS:
        return theme_mode
    return 'auto'


def theme_from_mode(theme_mode: str) -> Theme:
    normalized = normalize_theme_mode(theme_mode)
    return {
        'auto': Theme.AUTO,
        'light': Theme.LIGHT,
        'dark': Theme.DARK,
    }[normalized]


def apply_app_theme(theme_mode: str) -> None:
    setTheme(theme_from_mode(theme_mode), lazy=False)
    setThemeColor(THEME_COLOR)
