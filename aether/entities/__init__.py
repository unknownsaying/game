"""AetherEngine Entity System"""

from .entity import Entity, Transform
from .components import (
    SpriteRenderer, RigidBody, BoxCollider2D,
    AudioSource, AIAgent, HealthComponent, InventoryComponent
)
from .prefabs import PrefabManager, PlayerPrefab, EnemyPrefab

__all__ = [
    'Entity', 'Transform',
    'SpriteRenderer', 'RigidBody', 'BoxCollider2D',
    'AudioSource', 'AIAgent', 'HealthComponent', 'InventoryComponent',
    'PrefabManager', 'PlayerPrefab', 'EnemyPrefab'
]