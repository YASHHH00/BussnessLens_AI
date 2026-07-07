"""
BusinessLens AI — Theme Engine

Completely independent of dashboard logic.
Provides theme resolution, user preference management, and listing.
"""

from __future__ import annotations

from app.themes.theme_definitions import ALL_THEMES, ThemeDefinition
from app.core.exceptions import NotFoundError


class ThemeEngine:
    """
    Manages theme lookup and user preference resolution.
    Instantiated once at startup and injected via FastAPI Depends.
    """

    def get_theme(self, theme_name: str) -> ThemeDefinition:
        """Return the ThemeDefinition for a given name."""
        theme = ALL_THEMES.get(theme_name)
        if theme is None:
            valid = ", ".join(ALL_THEMES.keys())
            raise NotFoundError(f"Theme '{theme_name}' not found. Available: {valid}")
        return theme

    def get_user_theme(self, theme_preference: str) -> ThemeDefinition:
        """
        Resolve a user's stored theme preference to a ThemeDefinition.
        Falls back to 'system' if the stored preference is unknown.
        """
        return ALL_THEMES.get(theme_preference, ALL_THEMES["system"])

    def list_available_themes(self) -> list[ThemeDefinition]:
        """Return all themes where is_available=True."""
        return [t for t in ALL_THEMES.values() if t.is_available]

    def list_all_themes(self) -> list[ThemeDefinition]:
        """Return all themes including future stubs."""
        return list(ALL_THEMES.values())

    def is_valid_theme(self, theme_name: str) -> bool:
        """Return True if the theme name is recognized."""
        return theme_name in ALL_THEMES
