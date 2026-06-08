"""
Prefab System for Entity Templates
Pre-built entity configurations for quick instantiation
"""

import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import pygame
import math

from .entity import Entity
from .components import (
    Transform, SpriteRenderer, RigidBody,
    Collider2D, AIAgent, HealthComponent,
    AudioSource
)
from physics.colliders import CircleCollider, BoxCollider
from ai.behavior_tree import BehaviorTree
from ai.state_machine import StateMachine

@dataclass
class Prefab:
    """Base prefab template"""
    name: str = "Prefab"
    components: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def instantiate(self, position: np.ndarray = None, **overrides) -> Entity:
        """Create entity from prefab"""
        entity = Entity(self.name)
        
        # Add tags
        for tag in self.tags:
            entity.tag = tag
        
        # Add components
        for comp_name, comp_data in self.components.items():
            entity.add_component(comp_data)
        
        # Set position if provided
        if position is not None and entity.transform:
            entity.transform.position = position.copy()
        
        # Apply overrides
        for key, value in overrides.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        return entity

class PlayerPrefab(Prefab):
    """Player entity prefab"""
    
    def __init__(self):
        super().__init__(
            name="Player",
            tags=["player", "controllable"]
        )
        
        self.components = {
            'transform': Transform(position=np.zeros(2)),
            'sprite': SpriteRenderer(
                sprite=self._create_player_sprite(),
                opacity=255,
                pivot=(0.5, 0.5)
            ),
            'rigidbody': RigidBody(
                mass=1.0,
                use_gravity=True,
                linear_damping=0.1
            ),
            'collider': Collider2D(
                collider=CircleCollider(radius=20.0),
                is_trigger=False
            ),
            'health': HealthComponent(
                max_health=100.0,
                current_health=100.0,
                armor=10.0
            )
        }
    
    def _create_player_sprite(self) -> pygame.Surface:
        """Create default player sprite"""
        surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 100, 255), (5, 5, 30, 30))
        pygame.draw.circle(surf, (255, 255, 255), (20, 20), 5)
        return surf

class EnemyPrefab(Prefab):
    """Enemy entity prefab"""
    
    def __init__(self, enemy_type: str = "basic"):
        super().__init__(
            name=f"Enemy_{enemy_type}",
            tags=["enemy", enemy_type]
        )
        
        # Choose stats based on type
        if enemy_type == "basic":
            health = 50.0
            speed = 100.0
            color = (255, 50, 50)
            size = 30
        elif enemy_type == "fast":
            health = 30.0
            speed = 200.0
            color = (255, 150, 0)
            size = 25
        elif enemy_type == "tank":
            health = 150.0
            speed = 50.0
            color = (150, 50, 150)
            size = 45
        else:
            health = 50.0
            speed = 100.0
            color = (255, 50, 50)
            size = 30
        
        self.components = {
            'transform': Transform(position=np.zeros(2)),
            'sprite': SpriteRenderer(
                sprite=self._create_enemy_sprite(size, color),
                opacity=255
            ),
            'rigidbody': RigidBody(
                mass=1.0,
                use_gravity=False,
                linear_damping=0.1
            ),
            'collider': Collider2D(
                collider=CircleCollider(radius=size/2),
                is_trigger=False
            ),
            'health': HealthComponent(
                max_health=health,
                current_health=health
            ),
            'ai': AIAgent(speed=speed)
        }
    
    def _create_enemy_sprite(self, size: int, color: Tuple[int, int, int]) -> pygame.Surface:
        """Create enemy sprite"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (size//2, size//2), size//2)
        pygame.draw.circle(surf, (0, 0, 0), (size//2 - 5, size//2 - 3), 3)
        pygame.draw.circle(surf, (0, 0, 0), (size//2 + 5, size//2 - 3), 3)
        return surf

class BulletPrefab(Prefab):
    """Bullet/projectile prefab"""
    
    def __init__(self):
        super().__init__(
            name="Bullet",
            tags=["projectile", "bullet"]
        )
        
        self.components = {
            'transform': Transform(position=np.zeros(2)),
            'sprite': SpriteRenderer(
                sprite=self._create_bullet_sprite(),
                opacity=255
            ),
            'rigidbody': RigidBody(
                mass=0.1,
                use_gravity=False,
                linear_damping=0.0
            ),
            'collider': Collider2D(
                collider=CircleCollider(radius=5.0),
                is_trigger=True
            )
        }
    
    def _create_bullet_sprite(self) -> pygame.Surface:
        """Create bullet sprite"""
        surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.circle(surf, (255, 255, 100), (5, 5), 3)
        return surf

class PickupPrefab(Prefab):
    """Pickup item prefab"""
    
    def __init__(self, pickup_type: str = "health"):
        super().__init__(
            name=f"Pickup_{pickup_type}",
            tags=["pickup", pickup_type]
        )
        
        if pickup_type == "health":
            color = (0, 255, 0)
            value = 25.0
        elif pickup_type == "armor":
            color = (0, 150, 255)
            value = 15.0
        elif pickup_type == "gold":
            color = (255, 215, 0)
            value = 10.0
        else:
            color = (255, 255, 255)
            value = 0.0
        
        self.components = {
            'transform': Transform(position=np.zeros(2)),
            'sprite': SpriteRenderer(
                sprite=self._create_pickup_sprite(color),
                opacity=255
            ),
            'collider': Collider2D(
                collider=CircleCollider(radius=15.0),
                is_trigger=True
            )
        }
        
        self.pickup_value = value
    
    def _create_pickup_sprite(self, color: Tuple[int, int, int]) -> pygame.Surface:
        """Create pickup sprite"""
        surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (15, 15), 12)
        pygame.draw.circle(surf, (255, 255, 255), (15, 15), 10, 2)
        return surf

class PrefabManager:
    """Manages prefab creation and pooling"""
    
    def __init__(self):
        self.prefabs: Dict[str, Prefab] = {}
        self.pools: Dict[str, List[Entity]] = {}
        
        # Register default prefabs
        self.register_prefab("player", PlayerPrefab())
        self.register_prefab("enemy_basic", EnemyPrefab("basic"))
        self.register_prefab("enemy_fast", EnemyPrefab("fast"))
        self.register_prefab("enemy_tank", EnemyPrefab("tank"))
        self.register_prefab("bullet", BulletPrefab())
        self.register_prefab("pickup_health", PickupPrefab("health"))
        self.register_prefab("pickup_gold", PickupPrefab("gold"))
    
    def register_prefab(self, name: str, prefab: Prefab):
        """Register a prefab"""
        self.prefabs[name] = prefab
        self.pools[name] = []
    
    def instantiate(self, prefab_name: str, position: np.ndarray = None, 
                   use_pool: bool = True, **overrides) -> Optional[Entity]:
        """Create entity from prefab, optionally using object pool"""
        if prefab_name not in self.prefabs:
            print(f"Prefab '{prefab_name}' not found")
            return None
        
        # Try to get from pool
        if use_pool and self.pools[prefab_name]:
            entity = self.pools[prefab_name].pop()
            entity.active = True
            
            if position is not None and entity.transform:
                entity.transform.position = position.copy()
            
            # Apply overrides
            for key, value in overrides.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            return entity
        
        # Create new entity
        prefab = self.prefabs[prefab_name]
        return prefab.instantiate(position, **overrides)
    
    def return_to_pool(self, prefab_name: str, entity: Entity):
        """Return entity to object pool"""
        if prefab_name in self.pools:
            entity.active = False
            
            # Reset entity state
            if entity.transform:
                entity.transform.position = np.zeros(2)
                entity.transform.rotation = 0.0
            
            if hasattr(entity, 'rigidbody') and entity.rigidbody:
                entity.rigidbody.body.velocity *= 0
                entity.rigidbody.body.angular_velocity = 0
            
            self.pools[prefab_name].append(entity)
    
    def clear_pools(self):
        """Clear all object pools"""
        for pool in self.pools.values():
            pool.clear()