"""Theme definitions for Melodious."""

THEMES = {
    "dracula": {
        "name": "Dracula",
        "bg_primary": "#1E1E2E",
        "bg_secondary": "#181825",
        "bg_titlebar": "#11111B",
        "text": "#CDD6F4",
        "text_muted": "#A6ADC8",
        "accent": "#CBA6F7",
        "accent_hover": "#B4BEFE",
        "surface": "#313244",
        "surface_hover": "#45475A",
        "close_hover": "#F38BA8",
        "selection_bg": "#313244",
        "item_hover": "#2A2A3C",
        "border": "#1E1E2E",
        "slider_handle": "#F5E0DC",
    },
    "gruvbox": {
        "name": "Gruvbox Dark",
        "bg_primary": "#282828",
        "bg_secondary": "#1D2021",
        "bg_titlebar": "#1D2021",
        "text": "#EBDBB2",
        "text_muted": "#928374",
        "accent": "#FE8019",
        "accent_hover": "#FABD2F",
        "surface": "#3C3836",
        "surface_hover": "#504945",
        "close_hover": "#FB4934",
        "selection_bg": "#3C3836",
        "item_hover": "#32302F",
        "border": "#282828",
        "slider_handle": "#EBDBB2",
    },
    "ayu_dark": {
        "name": "Ayu Dark",
        "bg_primary": "#0F1419",
        "bg_secondary": "#0D1117",
        "bg_titlebar": "#0D1117",
        "text": "#BFBDB6",
        "text_muted": "#6C7086",
        "accent": "#FFDF00",
        "accent_hover": "#FFA759",
        "surface": "#1A1E2B",
        "surface_hover": "#252B39",
        "close_hover": "#FF6B6B",
        "selection_bg": "#1A1E2B",
        "item_hover": "#161A24",
        "border": "#0F1419",
        "slider_handle": "#BFBDB6",
    },
    "tokyo_night": {
        "name": "Tokyo Night",
        "bg_primary": "#1A1B26",
        "bg_secondary": "#16161E",
        "bg_titlebar": "#16161E",
        "text": "#C0CAF5",
        "text_muted": "#565F89",
        "accent": "#7AA2F7",
        "accent_hover": "#BB9AF7",
        "surface": "#1F2335",
        "surface_hover": "#292E42",
        "close_hover": "#F7768E",
        "selection_bg": "#1F2335",
        "item_hover": "#202430",
        "border": "#1A1B26",
        "slider_handle": "#A9B1D6",
    },
    "nord": {
        "name": "Nord",
        "bg_primary": "#2E3440",
        "bg_secondary": "#2B2F3A",
        "bg_titlebar": "#272C36",
        "text": "#D8DEE9",
        "text_muted": "#81A1C1",
        "accent": "#88C0D0",
        "accent_hover": "#8FBCBB",
        "surface": "#3B4252",
        "surface_hover": "#434C5E",
        "close_hover": "#BF616A",
        "selection_bg": "#3B4252",
        "item_hover": "#363C4A",
        "border": "#2E3440",
        "slider_handle": "#ECEFF4",
    },
}


def get_theme(name: str) -> dict:
    return THEMES.get(name, THEMES["dracula"])


def get_theme_names() -> list[str]:
    return list(THEMES.keys())


def build_stylesheet(theme: dict) -> str:
    t = theme
    return f"""
    QWidget {{
        background-color: {t['bg_primary']};
        color: {t['text']};
        font-family: "Segoe UI", "SF Pro Display", "Inter", sans-serif;
        font-size: 13px;
        border: none;
    }}

    #LeftPanel, #CenterPanel, #RightPanel {{
        background-color: {t['bg_secondary']};
        border-radius: 12px;
        padding: 8px;
    }}

    #TitleBar {{
        background-color: {t['bg_titlebar']};
        border-top-left-radius: 12px;
        border-top-right-radius: 12px;
    }}

    #MenuBar {{
        background-color: {t['bg_titlebar']};
        border-radius: 8px;
        padding: 2px 6px;
    }}
    #MenuBar::item {{
        background: transparent;
        color: {t['text']};
        padding: 6px 14px;
        border-radius: 6px;
    }}
    #MenuBar::item:selected {{
        background-color: {t['surface']};
        color: {t['accent']};
    }}
    #MenuBar::item:pressed {{
        background-color: {t['surface']};
        color: {t['accent']};
    }}

    QMenu {{
        background-color: {t['bg_secondary']};
        color: {t['text']};
        border: 1px solid {t['surface_hover']};
        border-radius: 12px;
        padding: 8px;
        min-width: 240px;
        font-size: 14px;
    }}
    QMenu::item {{
        padding: 10px 32px 10px 16px;
        border-radius: 8px;
        font-size: 14px;
    }}
    QMenu::item:hover {{
        background-color: {t['surface']};
        color: {t['accent']};
    }}
    QMenu::item:selected {{
        color: {t['accent']};
    }}
    QMenu::item:disabled {{
        color: {t['text_muted']};
    }}
    QMenu::item:checked {{
        color: {t['accent']};
        font-weight: 600;
    }}
    QMenu::separator {{
        height: 1px;
        background: {t['surface']};
        margin: 8px 12px;
    }}
    QMenu::indicator {{
        width: 16px;
        height: 16px;
        margin-left: 6px;
    }}
    QMenu::indicator:checked {{
        color: {t['accent']};
    }}

    #TitleLabel {{
        font-family: "Comfortaa", "SF Pro Display", "Cantarell", "Segoe UI", sans-serif;
        font-size: 17px;
        font-weight: 700;
        letter-spacing: 1px;
        color: {t['text']};
        background-color: transparent;
        border: none;
        padding: 0px;
    }}

    #TitleLogo {{
        background-color: transparent;
        border-radius: 6px;
    }}
    #TitleLogo:hover {{
        background-color: {t['surface']};
    }}

QToolTip {{
        background-color: {t['surface_hover']};
        color: {t['text']};
        border: 1px solid {t['surface']};
        border-radius: 6px;
        padding: 4px 8px;
        font-size: 12px;
    }}

#WinControlBtn {{
        background-color: transparent;
        color: {t['text_muted']};
        border-radius: 14px;
        min-width: 28px;
        max-width: 28px;
        min-height: 28px;
        max-height: 28px;
        font-size: 15px;
        font-weight: 600;
        padding: 0px;
    }}
    #WinControlBtn:hover {{
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {t['surface_hover']}, stop:1 {t['surface']});
        color: {t['text']};
    }}
    #WinControlBtn:pressed {{
        background-color: {t['accent']};
        color: {t['bg_titlebar']};
    }}
    #CloseBtn {{
        background-color: transparent;
        color: {t['text_muted']};
        border-radius: 14px;
        min-width: 28px;
        max-width: 28px;
        min-height: 28px;
        max-height: 28px;
        font-size: 14px;
        font-weight: 600;
        padding: 0px;
    }}
    #CloseBtn:hover {{
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {t['close_hover']}, stop:1 {t['surface']});
        color: #FFFFFF;
    }}
    #CloseBtn:pressed {{
        background-color: {t['accent']};
        color: {t['bg_titlebar']};
    }}

    #MenuBtn {{
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {t['surface_hover']}, stop:1 {t['surface']});
        color: {t['accent']};
        border: none;
        border-radius: 18px;
        min-width: 36px;
        max-width: 36px;
        min-height: 36px;
        max-height: 36px;
        font-size: 18px;
        font-weight: 600;
        padding: 0px;
    }}
    #MenuBtn:hover {{
        background-color: {t['surface_hover']};
        color: {t['accent']};
    }}
    #MenuBtn:pressed {{
        background-color: {t['surface']};
        color: {t['accent']};
    }}

    QPushButton {{
        background-color: {t['surface']};
        color: {t['text']};
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {t['surface_hover']};
        border: 1px solid {t['accent']};
    }}
    QPushButton:pressed {{
        background-color: {t['accent']};
        color: {t['bg_titlebar']};
    }}
    QPushButton:checked {{
        background-color: {t['accent']};
        color: {t['bg_titlebar']};
    }}

    #TransportBtn, #ShuffleBtn, #LoopBtn {{
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {t['surface_hover']}, stop:1 {t['surface']});
        color: {t['text']};
        border-radius: 22px;
        border: 1px solid transparent;
        font-size: 20px;
    }}
    #TransportBtn:hover, #ShuffleBtn:hover, #LoopBtn:hover {{
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {t['surface']}, stop:1 {t['surface_hover']});
        color: {t['accent']};
        border: 1px solid {t['accent']};
    }}
    #TransportBtn:pressed {{
        background-color: {t['accent']};
        color: {t['bg_titlebar']};
        border: 1px solid {t['accent']};
    }}
    #ShuffleBtn:checked, #LoopBtn:checked {{
        background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 {t['accent']}, stop:1 {t['accent_hover']});
        color: {t['bg_titlebar']};
        border: 1px solid {t['accent_hover']};
    }}
    #ShuffleBtn:checked:hover, #LoopBtn:checked:hover {{
        background-color: {t['accent_hover']};
        color: {t['bg_titlebar']};
    }}
    #VolumeBtn {{
        background-color: transparent;
        color: {t['text']};
        border-radius: 17px;
        border: 1px solid transparent;
        font-size: 18px;
    }}
    #VolumeBtn:hover {{
        background-color: {t['surface']};
        color: {t['accent']};
        border: 1px solid {t['surface_hover']};
    }}
    #VolumeBtn:pressed {{
        background-color: {t['accent']};
        color: {t['bg_titlebar']};
        border: 1px solid {t['accent']};
    }}

#PlayPauseBtn {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {t['accent']}, stop:1 {t['accent_hover']});
        color: {t['bg_titlebar']};
        border-radius: 27px;
        border: 2px solid {t['accent_hover']};
        font-weight: bold;
        font-size: 22px;
    }}
    #PlayPauseBtn:hover {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {t['accent_hover']}, stop:1 {t['accent']});
        border: 2px solid {t['accent']};
    }}
    #PlayPauseBtn:pressed {{
        background-color: {t['bg_titlebar']};
        color: {t['accent']};
        border: 2px solid {t['accent']};
    }}

    QTableWidget {{
        background-color: transparent;
        gridline-color: transparent;
        selection-background-color: {t['selection_bg']};
        selection-color: {t['accent']};
        border-radius: 8px;
    }}
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid {t['border']};
    }}
    QTableWidget::item:hover {{
        background-color: {t['item_hover']};
        border-radius: 6px;
    }}
    QTableWidget::item:selected {{
        background-color: {t['selection_bg']};
        color: {t['accent']};
        border-radius: 10px;
    }}
    QHeaderView::section {{
        background-color: transparent;
        color: {t['text_muted']};
        font-weight: 600;
        padding: 4px;
        text-transform: uppercase;
        font-size: 11px;
    }}

    QSplitter {{
        background: transparent;
    }}
    QSplitter::handle {{
        background-color: {t['surface']};
        border-radius: 2px;
    }}
    QSplitter::handle:hover {{
        background-color: {t['accent']};
    }}
    QSplitter::handle:vertical:disabled {{
        background-color: transparent;
    }}

    QSlider::groove:horizontal {{
        height: 4px;
        background: {t['surface']};
        border-radius: 2px;
    }}
    QSlider::sub-page:horizontal {{
        background: {t['accent']};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {t['slider_handle']};
        width: 12px;
        height: 12px;
        margin: -4px 0;
        border-radius: 6px;
    }}
    QSlider::handle:horizontal:hover {{
        background: #FFFFFF;
    }}

    QScrollBar:vertical {{
        background: transparent;
        width: 6px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {t['surface_hover']};
        min-height: 20px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {t['accent']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    #NavBtn {{
        background-color: transparent;
        color: {t['text']};
        border-radius: 8px;
        padding: 10px 14px;
        text-align: left;
        font-size: 13px;
    }}
    #NavBtn:hover {{
        background-color: {t['surface']};
    }}
    #NavBtnActive {{
        background-color: {t['surface']};
        color: {t['accent']};
        border-left: 3px solid {t['accent']};
        border-radius: 8px;
        padding: 10px 14px;
        text-align: left;
        font-size: 13px;
    }}

    #TrackInfoTitle {{
        font-size: 18px;
        font-weight: bold;
        color: {t['text']};
    }}
    #TrackInfoArtist {{
        font-size: 13px;
        color: {t['text_muted']};
    }}
    #TrackInfoAlbum {{
        font-size: 12px;
        color: {t['text_muted']};
    }}

    #VolumeSlider {{
        max-width: 100px;
    }}

    #InfoLabel {{
        color: {t['text_muted']};
        font-size: 11px;
    }}
    """
