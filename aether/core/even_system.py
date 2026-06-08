"""
Event System with Priority Queue and Event Filtering
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import heapq
import uuid
import pygame

class EventPriority(Enum):
    """Event priority levels"""
    LOWEST = 0
    LOW = 25
    NORMAL = 50
    HIGH = 75
    HIGHEST = 100
    CRITICAL = 200

@dataclass
class GameEvent:
    """Game event data structure"""
    type: str
    data: Any = None
    source: Any = None
    timestamp: float = 0.0
    priority: EventPriority = EventPriority.NORMAL
    id: str = ""
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def __lt__(self, other):
        # Higher priority events come first
        return self.priority.value > other.priority.value

class EventFilter:
    """Filter for event subscriptions"""
    
    def __init__(self, event_type: str = None, source: Any = None):
        self.event_type = event_type
        self.source = source
    
    def matches(self, event: GameEvent) -> bool:
        """Check if event matches filter"""
        if self.event_type and event.type != self.event_type:
            return False
        if self.source is not None and event.source != self.source:
            return False
        return True

class EventSystem:
    """
    Advanced event system with:
    - Priority-based event processing
    - Event filtering
    - One-shot listeners
    - Event history
    """
    
    def __init__(self):
        self.listeners: Dict[str, List[tuple]] = {}  # event_type -> [(callback, filter, once)]
        self.global_listeners = []  # Listeners for all events
        self.event_queue = []  # Priority queue
        self.event_history = []  # Recent events
        self.max_history = 100
        
    def subscribe(self, callback: Callable, 
                  event_type: Optional[str] = None,
                  source: Any = None,
                  once: bool = False,
                  priority: int = 0) -> str:
        """Subscribe to events, returns listener ID"""
        listener_id = str(uuid.uuid4())
        event_filter = EventFilter(event_type, source)
        listener = (listener_id, callback, event_filter, once, priority)
        
        if event_type:
            if event_type not in self.listeners:
                self.listeners[event_type] = []
            self.listeners[event_type].append(listener)
        else:
            self.global_listeners.append(listener)
        
        return listener_id
    
    def unsubscribe(self, listener_id: str):
        """Remove event listener"""
        # Remove from typed listeners
        for event_type in self.listeners:
            self.listeners[event_type] = [
                l for l in self.listeners[event_type] if l[0] != listener_id
            ]
        
        # Remove from global listeners
        self.global_listeners = [
            l for l in self.global_listeners if l[0] != listener_id
        ]
    
    def emit(self, event_type: str, data: Any = None, 
             source: Any = None, 
             priority: EventPriority = EventPriority.NORMAL):
        """Emit an event"""
        event = GameEvent(
            type=event_type,
            data=data,
            source=source,
            priority=priority
        )
        
        # Add to priority queue
        heapq.heappush(self.event_queue, event)
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
    
    def process_events(self):
        """Process all queued events"""
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self._dispatch_event(event)
    
    def _dispatch_event(self, event: GameEvent):
        """Dispatch event to relevant listeners"""
        # Process typed listeners
        if event.type in self.listeners:
            self._notify_listeners(self.listeners[event.type], event)
        
        # Process global listeners
        self._notify_listeners(self.global_listeners, event)
    
    def _notify_listeners(self, listeners: list, event: GameEvent):
        """Notify matching listeners"""
        to_remove = []
        
        # Sort by priority
        sorted_listeners = sorted(listeners, key=lambda l: l[4], reverse=True)
        
        for listener in sorted_listeners:
            listener_id, callback, event_filter, once, _ = listener
            
            if event_filter.matches(event):
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event listener {listener_id}: {e}")
                
                if once:
                    to_remove.append(listener_id)
        
        # Remove one-shot listeners
        for listener_id in to_remove:
            self.unsubscribe(listener_id)
    
    def clear(self):
        """Clear all listeners and events"""
        self.listeners.clear()
        self.global_listeners.clear()
        self.event_queue.clear()
        self.event_history.clear()