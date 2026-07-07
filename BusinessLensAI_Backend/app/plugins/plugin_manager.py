"""
BusinessLens AI — Plugin Manager

Discovers, loads, and provides access to the active domain plugin.
Called once at app startup.
"""

from __future__ import annotations

from app.core.exceptions import PluginError
from app.core.logging_config import get_logger
from app.plugins.base_plugin import BaseDomainPlugin
from app.registry.field_registry import BusinessFieldRegistry

logger = get_logger(__name__)

# Registry of all available plugins: name → class path
_PLUGIN_REGISTRY: dict[str, str] = {
    "retail": "app.plugins.domains.retail.plugin.RetailPlugin",
    "food_delivery": "app.plugins.domains.food_delivery.plugin.FoodDeliveryPlugin",
    "warehouse": "app.plugins.domains.warehouse.plugin.WarehousePlugin",
}


class PluginManager:
    """
    Manages the active domain plugin lifecycle.

    At startup:
    1. `load_plugin(name)` is called from the app lifespan.
    2. The plugin populates the BusinessFieldRegistry.
    3. All engines access the plugin via `get_active_plugin()`.
    """

    def __init__(self, registry: BusinessFieldRegistry) -> None:
        self._registry = registry
        self._active_plugin: BaseDomainPlugin | None = None

    def load_plugin(self, plugin_name: str) -> BaseDomainPlugin:
        """
        Dynamically import and instantiate the named plugin.
        Registers the plugin's fields into the BusinessFieldRegistry.
        """
        plugin_path = _PLUGIN_REGISTRY.get(plugin_name)
        if not plugin_path:
            available = ", ".join(_PLUGIN_REGISTRY.keys())
            raise PluginError(
                f"Unknown domain plugin: '{plugin_name}'. "
                f"Available plugins: {available}"
            )

        module_path, class_name = plugin_path.rsplit(".", 1)
        try:
            import importlib
            module = importlib.import_module(module_path)
            plugin_class = getattr(module, class_name)
            plugin: BaseDomainPlugin = plugin_class()
        except NotImplementedError:
            raise PluginError(
                f"Plugin '{plugin_name}' is a stub — not yet implemented. "
                "It is planned for a future release."
            )
        except Exception as exc:
            raise PluginError(
                f"Failed to load plugin '{plugin_name}': {exc}"
            ) from exc

        # Register fields into the registry
        plugin.register_fields(self._registry)
        self._active_plugin = plugin

        # Push plugin metadata so AI prompts have domain context
        self._registry.set_active_plugin_metadata({
            "domain": plugin.name,
            "display_name": plugin.display_name,
            "description": getattr(plugin, "description", ""),
            "version": plugin.version,
        })

        logger.info(
            "Domain plugin loaded: name=%s display=%s version=%s fields=%d",
            plugin.name,
            plugin.display_name,
            plugin.version,
            len(self._registry),
        )
        return plugin

    def get_active_plugin(self) -> BaseDomainPlugin:
        """Return the currently loaded domain plugin."""
        if self._active_plugin is None:
            raise PluginError(
                "No domain plugin is loaded. "
                "Call load_plugin() during app lifespan startup."
            )
        return self._active_plugin

    def list_available_plugins(self) -> list[str]:
        """Return names of all registered plugins (including stubs)."""
        return list(_PLUGIN_REGISTRY.keys())
