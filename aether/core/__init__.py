"""
AetherEngine Core Module
Provides foundational systems for game engine operation
"""

from .engine import AetherEngine, EngineConfig
from .scene_manager import Scene, SceneManager
from .event_system import EventSystem, GameEvent
from .resource_manager import ResourceManager

__all__ = [
    'AetherEngine',
    'EngineConfig',
    'Scene',
    'SceneManager',
    'EventSystem',
    'GameEvent',
    'ResourceManager'
]