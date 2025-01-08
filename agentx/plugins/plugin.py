"""
Plugin system for AgentX framework.
Provides base classes and decorators for creating plugins.
"""
from typing import Type, Dict, Any, Optional
from abc import ABC, abstractmethod

class Plugin(ABC):
    """Base class for all plugins."""
    
    @abstractmethod
    def initialize(self, client: Any) -> None:
        """Initialize the plugin with the client instance."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup resources when plugin is disabled."""
        pass

class PluginRegistry:
    """Registry for managing plugins."""
    
    _plugins: Dict[str, Type[Plugin]] = {}
    
    @classmethod
    def register(cls, plugin_class: Type[Plugin]) -> Type[Plugin]:
        """Register a plugin class."""
        plugin_name = plugin_class.__name__
        cls._plugins[plugin_name] = plugin_class
        return plugin_class
    
    @classmethod
    def get_plugin(cls, name: str) -> Optional[Type[Plugin]]:
        """Get a plugin class by name."""
        return cls._plugins.get(name)
    
    @classmethod
    def list_plugins(cls) -> Dict[str, Type[Plugin]]:
        """List all registered plugins."""
        return cls._plugins.copy()

def register_plugin(plugin_class: Type[Plugin]) -> Type[Plugin]:
    """Decorator to register a plugin."""
    return PluginRegistry.register(plugin_class)
