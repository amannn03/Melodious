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