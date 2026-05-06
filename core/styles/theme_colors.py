# core/styles/theme_colors.py

class ThemeColors:
    DARK = {
        "next_bell_bg": "#367736",
        "active": "#39FF14",
        "inactive": "#F85149",
    }

    LIGHT = {
        "next_bell_bg": "#E8F5E9",
        "active": "#1B7F3A",
        "inactive": "#C0392B",
    }

    @staticmethod
    def get(theme: str):
        theme = (theme or "dark").lower()

        if theme == "light":
            return ThemeColors.LIGHT

        return ThemeColors.DARK