"""
BusinessLens AI — Dashboard Theme System: Definitions

Theme definitions are pure data — no rendering logic.
The frontend reads theme tokens from the API and applies them.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ThemeColors:
    primary: str
    secondary: str
    accent: str
    background: str
    surface: str
    surface_elevated: str
    text_primary: str
    text_secondary: str
    text_muted: str
    success: str
    warning: str
    error: str
    info: str
    border: str
    divider: str


@dataclass(frozen=True)
class ThemeTypography:
    font_family: str
    h1_size: str
    h2_size: str
    h3_size: str
    body_size: str
    caption_size: str
    font_weight_normal: int
    font_weight_bold: int


@dataclass(frozen=True)
class ThemeSpacing:
    card_padding: str
    grid_gap: str
    section_margin: str
    widget_border_radius: str


@dataclass(frozen=True)
class ThemeDefinition:
    name: str
    display_name: str
    description: str
    is_builtin: bool
    is_available: bool          # False for future themes (Compact, Presentation)
    colors: ThemeColors
    chart_palette: tuple[str, ...]
    typography: ThemeTypography
    spacing: ThemeSpacing


# ------------------------------------------------------------------ #
# Built-in themes
# ------------------------------------------------------------------ #

DARK_THEME = ThemeDefinition(
    name="dark",
    display_name="Dark",
    description="Dark backgrounds, high-contrast text, vibrant chart colors.",
    is_builtin=True,
    is_available=True,
    colors=ThemeColors(
        primary="#7C6FF7",
        secondary="#5B8DEF",
        accent="#F97316",
        background="#0F1117",
        surface="#1A1D2E",
        surface_elevated="#252840",
        text_primary="#F1F5F9",
        text_secondary="#94A3B8",
        text_muted="#64748B",
        success="#22C55E",
        warning="#F59E0B",
        error="#EF4444",
        info="#3B82F6",
        border="#2D3047",
        divider="#1E2138",
    ),
    chart_palette=(
        "#7C6FF7", "#5B8DEF", "#F97316", "#22C55E",
        "#F59E0B", "#EC4899", "#14B8A6", "#8B5CF6",
    ),
    typography=ThemeTypography(
        font_family="'Inter', 'Segoe UI', system-ui, sans-serif",
        h1_size="2rem", h2_size="1.5rem", h3_size="1.25rem",
        body_size="0.875rem", caption_size="0.75rem",
        font_weight_normal=400, font_weight_bold=600,
    ),
    spacing=ThemeSpacing(
        card_padding="1.5rem", grid_gap="1rem",
        section_margin="2rem", widget_border_radius="0.75rem",
    ),
)

LIGHT_THEME = ThemeDefinition(
    name="light",
    display_name="Light",
    description="Clean white backgrounds, muted tones, professional chart colors.",
    is_builtin=True,
    is_available=True,
    colors=ThemeColors(
        primary="#6366F1",
        secondary="#3B82F6",
        accent="#F97316",
        background="#F8FAFC",
        surface="#FFFFFF",
        surface_elevated="#F1F5F9",
        text_primary="#0F172A",
        text_secondary="#475569",
        text_muted="#94A3B8",
        success="#16A34A",
        warning="#D97706",
        error="#DC2626",
        info="#2563EB",
        border="#E2E8F0",
        divider="#F1F5F9",
    ),
    chart_palette=(
        "#6366F1", "#3B82F6", "#F97316", "#16A34A",
        "#D97706", "#DB2777", "#0891B2", "#7C3AED",
    ),
    typography=ThemeTypography(
        font_family="'Inter', 'Segoe UI', system-ui, sans-serif",
        h1_size="2rem", h2_size="1.5rem", h3_size="1.25rem",
        body_size="0.875rem", caption_size="0.75rem",
        font_weight_normal=400, font_weight_bold=600,
    ),
    spacing=ThemeSpacing(
        card_padding="1.5rem", grid_gap="1rem",
        section_margin="2rem", widget_border_radius="0.75rem",
    ),
)

SYSTEM_THEME = ThemeDefinition(
    name="system",
    display_name="System",
    description="Follows the operating system's dark/light mode preference.",
    is_builtin=True,
    is_available=True,
    # System theme uses the same tokens as dark — resolved client-side
    colors=DARK_THEME.colors,
    chart_palette=DARK_THEME.chart_palette,
    typography=DARK_THEME.typography,
    spacing=DARK_THEME.spacing,
)

ALL_THEMES: dict[str, ThemeDefinition] = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
    "system": SYSTEM_THEME,
}
