"""
Plugin system for AgentX framework.
Enables extensible functionality through event handlers and custom integrations.
"""
from .event_bus import EventBus, Event
from .plugin import Plugin, PluginRegistry, register_plugin

__all__ = ['EventBus', 'Event', 'Plugin', 'PluginRegistry', 'register_plugin']
