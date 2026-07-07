"""
BusinessLens AI — Business Field Registry

The singleton registry that holds all FieldDefinitions for the active domain.
Populated at startup by the domain plugin. Consumed by every downstream module.

Design: dependency-injected (not a global singleton accessed via import),
initialized in app lifespan and provided via FastAPI Depends.
"""

from __future__ import annotations

from threading import Lock
from typing import Iterator

from app.registry.field_definitions import FieldDefinition
from app.registry.field_types import FieldCategory


class BusinessFieldRegistry:
    """
    Thread-safe registry of business field definitions.

    All modules that need to know what fields exist, what types they expect,
    what aggregations they use, and what conflicts they have — query this registry.
    The registry is populated once at startup by the active domain plugin,
    then read-only for the rest of the app's lifetime.

    This makes the platform domain-agnostic: engines, validators, and AI prompts
    read the registry instead of hardcoding domain knowledge.
    """

    def __init__(self) -> None:
        self._fields: dict[str, FieldDefinition] = {}
        self._lock = Lock()
        self._active_plugin_meta: dict = {}

    # ------------------------------------------------------------------ #
    # Registration (called by domain plugin at startup)
    # ------------------------------------------------------------------ #

    def register(self, field: FieldDefinition) -> None:
        """Register a field definition. Overwrites if the name already exists."""
        with self._lock:
            self._fields[field.name] = field

    def register_many(self, fields: list[FieldDefinition]) -> None:
        """Batch registration — registers all fields in the list."""
        for f in fields:
            self.register(f)

    def set_active_plugin_metadata(self, meta: dict) -> None:
        """Store plugin metadata for AI prompt context (set by PluginManager)."""
        with self._lock:
            self._active_plugin_meta = meta

    def get_active_plugin_metadata(self) -> dict:
        """Return plugin metadata dict for AI prompt context."""
        return dict(self._active_plugin_meta)

    # ------------------------------------------------------------------ #
    # Lookups
    # ------------------------------------------------------------------ #

    def get(self, name: str) -> FieldDefinition | None:
        """Return the FieldDefinition for `name`, or None if not registered."""
        return self._fields.get(name)

    def get_or_raise(self, name: str) -> FieldDefinition:
        """Return the FieldDefinition for `name`, raising ValueError if not found."""
        field = self._fields.get(name)
        if field is None:
            valid = ", ".join(sorted(self._fields.keys()))
            raise ValueError(
                f"Unknown business field: '{name}'. "
                f"Valid fields for the active domain: {valid}"
            )
        return field

    def exists(self, name: str) -> bool:
        """Return True if the field name is registered."""
        return name in self._fields

    # ------------------------------------------------------------------ #
    # Filtered views
    # ------------------------------------------------------------------ #

    def list_all(self) -> list[FieldDefinition]:
        """Return all registered field definitions."""
        return list(self._fields.values())

    def list_names(self) -> list[str]:
        """Return all registered field names (sorted)."""
        return sorted(self._fields.keys())

    def list_by_category(self, category: FieldCategory) -> list[FieldDefinition]:
        """Return all fields with the given category."""
        return [f for f in self._fields.values() if f.category == category]

    def list_forecastable(self) -> list[FieldDefinition]:
        """Return all fields eligible for forecasting."""
        return [f for f in self._fields.values() if f.is_forecastable]

    def list_metrics(self) -> list[FieldDefinition]:
        return self.list_by_category(FieldCategory.METRIC)

    def list_dimensions(self) -> list[FieldDefinition]:
        return self.list_by_category(FieldCategory.DIMENSION)

    def list_temporals(self) -> list[FieldDefinition]:
        return self.list_by_category(FieldCategory.TEMPORAL)

    def list_identifiers(self) -> list[FieldDefinition]:
        return self.list_by_category(FieldCategory.IDENTIFIER)

    def list_date_fields(self) -> list[FieldDefinition]:
        """Return all temporal/date-type fields (alias for list_temporals)."""
        return self.list_temporals()

    def get_all_fields(self) -> list[FieldDefinition]:
        """Return all registered fields (alias for list_all — used by validation engine)."""
        return self.list_all()

    # ------------------------------------------------------------------ #
    # Validation helpers (used by MappingService)
    # ------------------------------------------------------------------ #

    def get_expected_types(self, field_name: str) -> list[str]:
        """Return the expected physical column types for a field, or [] if unknown."""
        field = self._fields.get(field_name)
        return list(field.expected_types) if field else []

    def get_conflicting_categories(self, field_name: str) -> list[FieldCategory]:
        """Return categories this field cannot map to."""
        field = self._fields.get(field_name)
        return list(field.conflicting_categories) if field else []

    def get_default_aggregation(self, field_name: str) -> str:
        """Return the default SQL aggregation for a field (defaults to 'sum')."""
        field = self._fields.get(field_name)
        return field.default_aggregation if field else "sum"

    # ------------------------------------------------------------------ #
    # AI prompt helpers
    # ------------------------------------------------------------------ #

    def get_vocabulary_for_prompt(self) -> list[dict]:
        """
        Return a compact representation of all fields suitable for injection
        into AI prompts. Includes name, category, aliases, and description.
        """
        return [
            {
                "name": f.name,
                "category": f.category.value,
                "aliases": list(f.aliases),
                "description": f.description,
                "expected_types": list(f.expected_types),
            }
            for f in self._fields.values()
        ]

    # ------------------------------------------------------------------ #
    # Introspection
    # ------------------------------------------------------------------ #

    def __len__(self) -> int:
        return len(self._fields)

    def __contains__(self, name: str) -> bool:
        return name in self._fields

    def __iter__(self) -> Iterator[FieldDefinition]:
        return iter(self._fields.values())

    def __repr__(self) -> str:
        return f"<BusinessFieldRegistry fields={len(self._fields)}>"
