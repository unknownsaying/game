"""
Advanced Component System
ECS-inspired components for game entities
"""

import numpy as np
import pygame
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import math
import uuid

# Import from physics
from physics.rigidbody import RigidBody2D
from physics.colliders import CircleCollider, BoxCollider, Collider

@dataclass
class SpriteRenderer:
    """Sprite rendering component"""
    sprite: Optional[pygame.Surface] = None
    color: Tuple[int, int, int] = (255, 255, 255)
    opacity: int = 255
    visible: bool = True
    layer: int = 0
    flip_x: bool = False
    flip_y: bool = False
    blend_mode: int = pygame.BLENDMODE_NONE
    scale: Tuple[float, float] = (1.0, 1.0)
    pivot: Tuple[float, float] = (0.5, 0.5)
    
    def render(self, screen: pygame.Surface, transform: 'Transform',
              camera_offset: np.ndarray = None):
        """Render sprite to screen"""
        if not self.visible or not self.sprite:
            return
        
        pos = transform.position.copy()
        if camera_offset is not None:
            pos -= camera_offset
        
        # Apply transformations
        img = self.sprite.copy()
        
        # Scale
        if self.scale != (1.0, 1.0):
            new_size = (int(img.get_width() * self.scale[0]),
                       int(img.get_height() * self.scale[1]))
            img = pygame.transform.scale(img, new_size)
        
        # Flip
        if self.flip_x or self.flip_y:
            img = pygame.transform.flip(img, self.flip_x, self.flip_y)
        
        # Rotate
        if transform.rotation != 0:
            img = pygame.transform.rotate(img, -math.degrees(transform.rotation))
        
        # Opacity
        if self.opacity < 255:
            img.set_alpha(self.opacity)
        
        # Position with pivot
        rect = img.get_rect()
        pivot_pos = np.array([
            pos[0] - rect.width * self.pivot[0],
            pos[1] - rect.height * self.pivot[1]
        ])
        rect.topleft = pivot_pos
        
        screen.blit(img, rect, special_flags=self.blend_mode)

@dataclass
class RigidBody:
    """Physics rigidbody component"""
    body: RigidBody2D = None
    mass: float = 1.0
    use_gravity: bool = True
    is_kinematic: bool = False
    linear_damping: float = 0.01
    angular_damping: float = 0.01
    
    def __post_init__(self):
        if self.body is None:
            self.body = RigidBody2D(
                mass=self.mass,
                position=np.zeros(2)
            )
            self.body.use_gravity = self.use_gravity
            self.body.is_kinematic = self.is_kinematic
            self.body.linear_damping = self.linear_damping
            self.body.angular_damping = self.angular_damping
    
    def update(self, dt: float, transform: 'Transform'):
        """Update physics and sync to transform"""
        self.body.integrate(dt)
        transform.position = self.body.position.copy()
        transform.rotation = self.body.rotation
    
    def add_force(self, force: np.ndarray):
        """Add force to rigidbody"""
        self.body.add_force(force)
    
    def add_impulse(self, impulse: np.ndarray):
        """Add impulse to rigidbody"""
        self.body.add_impulse(impulse)

@dataclass
class Collider2D:
    """Collider component"""
    collider: Collider = None
    is_trigger: bool = False
    
    def __post_init__(self):
        if self.collider is None:
            self.collider = BoxCollider(1.0, 1.0)
    
    def check_collision(self, other: 'Collider2D', 
                       transform_a: 'Transform', transform_b: 'Transform') -> bool:
        """Check collision with another collider"""
        # Simplified AABB check
        min_a, max_a = self.collider.get_aabb(
            transform_a.position, transform_a.rotation
        )
        min_b, max_b = other.collider.get_aabb(
            transform_b.position, transform_b.rotation
        )
        
        return not (max_a[0] < min_b[0] or min_a[0] > max_b[0] or
                   max_a[1] < min_b[1] or min_a[1] > max_b[1])

@dataclass
class AudioSource:
    """Audio source component"""
    sound: Optional[pygame.mixer.Sound] = None
    channel: Optional[pygame.mixer.Channel] = None
    volume: float = 1.0
    pitch: float = 1.0
    loop: bool = False
    is_3d: bool = False
    min_distance: float = 100.0
    max_distance: float = 1000.0
    
    def play(self):
        """Play the audio source"""
        if self.sound:
            if self.channel is None:
                self.channel = pygame.mixer.find_channel()
            
            if self.channel:
                self.channel.set_volume(self.volume)
                self.channel.play(self.sound, loops=-1 if self.loop else 0)
    
    def stop(self):
        """Stop audio playback"""
        if self.channel:
            self.channel.stop()
    
    def update_3d(self, listener_position: np.ndarray, source_position: np.ndarray):
        """Update 3D audio properties"""
        if not self.is_3d or not self.channel:
            return
        
        distance = np.linalg.norm(source_position - listener_position)
        
        # Volume falloff
        if distance < self.min_distance:
            volume = 1.0
        elif distance > self.max_distance:
            volume = 0.0
        else:
            t = (distance - self.min_distance) / (self.max_distance - self.min_distance)
            volume = 1.0 - t
        
        self.channel.set_volume(self.volume * volume)

@dataclass
class AIAgent:
    """AI agent component"""
    behavior_tree: Any = None
    state_machine: Any = None
    pathfinder: Any = None
    target: Any = None
    speed: float = 100.0
    detection_radius: float = 200.0
    
    def update(self, dt: float, transform: 'Transform'):
        """Update AI behavior"""
        if self.behavior_tree:
            self.behavior_tree.update(dt)
        
        if self.state_machine:
            self.state_machine.update(dt)

@dataclass
class HealthComponent:
    """Health and damage component"""
    max_health: float = 100.0
    current_health: float = 100.0
    armor: float = 0.0
    is_alive: bool = True
    invulnerable: bool = False
    invulnerability_time: float = 0.0
    _invulnerability_timer: float = 0.0
    
    def take_damage(self, amount: float, damage_type: str = "physical") -> float:
        """Apply damage and return actual damage dealt"""
        if not self.is_alive or self.invulnerable:
            return 0.0
        
        # Armor reduction (simple formula)
        if damage_type == "physical":
            reduction = self.armor / (self.armor + 100)  # Diminishing returns
            actual_damage = amount * (1 - reduction)
        else:
            actual_damage = amount
        
        self.current_health -= actual_damage
        
        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
        
        if self.invulnerability_time > 0:
            self.invulnerable = True
            self._invulnerability_timer = self.invulnerability_time
        
        return actual_damage
    
    def heal(self, amount: float):
        """Heal the entity"""
        if self.is_alive:
            self.current_health = min(self.current_health + amount, self.max_health)
    
    def update(self, dt: float):
        """Update health component"""
        if self.invulnerable and self._invulnerability_timer > 0:
            self._invulnerability_timer -= dt
            if self._invulnerability_timer <= 0:
                self.invulnerable = False
    
    def get_health_percentage(self) -> float:
        """Get health as percentage (0-1)"""
        return self.current_health / self.max_health if self.max_health > 0 else 0

@dataclass
class InventoryComponent:
    """Inventory system component"""
    items: Dict[str, Any] = field(default_factory=dict)
    max_slots: int = 20
    gold: int = 0
    
    def add_item(self, item_id: str, item_data: Any, quantity: int = 1) -> bool:
        """Add item to inventory"""
        if item_id in self.items:
            # Stack if possible
            if hasattr(self.items[item_id], 'quantity'):
                self.items[item_id].quantity += quantity
                return True
        elif len(self.items) < self.max_slots:
            self.items[item_id] = item_data
            return True
        return False
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory"""
        if item_id not in self.items:
            return False
        
        if hasattr(self.items[item_id], 'quantity'):
            self.items[item_id].quantity -= quantity
            if self.items[item_id].quantity <= 0:
                del self.items[item_id]
        else:
            del self.items[item_id]
        
        return True
    
    def has_item(self, item_id: str) -> bool:
        """Check if item exists in inventory"""
        return item_id in self.items
    
    def get_item_count(self, item_id: str) -> int:
        """Get quantity of an item"""
        if item_id in self.items and hasattr(self.items[item_id], 'quantity'):
            return self.items[item_id].quantity
        return 1 if item_id in self.items else 0

@dataclass
class Transform:
    """Transform component (position, rotation, scale)"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(2))
    rotation: float = 0.0
    scale: np.ndarray = field(default_factory=lambda: np.ones(2))
    
    def translate(self, delta: np.ndarray):
        """Move by delta"""
        self.position += delta
    
    def rotate(self, angle: float):
        """Rotate by angle in radians"""
        self.rotation += angle
    
    def look_at(self, target: np.ndarray):
        """Face towards a target position"""
        direction = target - self.position
        self.rotation = math.atan2(direction[1], direction[0])
    
    def get_forward(self) -> np.ndarray:
        """Get forward direction vector"""
        return np.array([math.cos(self.rotation), math.sin(self.rotation)])
    
    def get_right(self) -> np.ndarray:
        """Get right direction vector"""
        forward = self.get_forward()
        return np.array([-forward[1], forward[0]])