"""
Event bus system for AgentX framework.
Provides a centralized event handling mechanism for plugins and core functionality.
"""
from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    """Base class for all events in the system."""
    name: str
    timestamp: datetime
    data: Dict[str, Any]

class EventBus:
    """
    Central event bus for the AgentX framework.
    Handles event subscription and publishing.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        
    def subscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        """
        Subscribe to an event.
        
        Args:
            event_name: Name of the event to subscribe to
            handler: Callback function to handle the event
        """
        if not callable(handler):
            raise ValueError("Event handler must be callable")
        self._subscribers.setdefault(event_name, []).append(handler)
        
    def unsubscribe(self, event_name: str, handler: Callable[[Event], None]) -> None:
        """
        Unsubscribe from an event.
        
        Args:
            event_name: Name of the event to unsubscribe from
            handler: Handler to remove
        """
        if event_name in self._subscribers:
            self._subscribers[event_name] = [
                h for h in self._subscribers[event_name] if h != handler
            ]
            
    def publish(self, event_name: str, **data) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event_name: Name of the event to publish
            **data: Event data as keyword arguments
        """
        event = Event(
            name=event_name,
            timestamp=datetime.now(),
            data=data
        )
        
        for handler in self._subscribers.get(event_name, []):
            try:
                handler(event)
            except Exception as e:
                # Log error but don't stop event propagation
                print(f"Error in event handler for {event_name}: {e}")
