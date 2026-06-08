"""
Flexible Entity Component System
"""

from typing import Dict, List, Type, Any, Optional, Set
from dataclasses import dataclass, field
import uuid
import numpy as np
import pygame

@dataclass
class Component:
    """Base component class"""
    enabled: bool = True
    _entity: Optional['Entity'] = None
    
    def on_attach(self):
        """Called when component is attached to entity"""
        pass
    
    def on_detach(self):
        """Called when component is removed"""
        pass
    
    @property
    def entity(self) -> 'Entity':
        return self._entity

class Entity:
    """Game entity composed of components"""
    
    def __init__(self, name: str = "Entity", tag: str = ""):
        self.id = uuid.uuid4()
        self.name = name
        self.tag = tag
        self.active = True
        self.layer = 0
        
        self.components: Dict[Type, Component] = {}
        self.transform = Transform()
        self.children: List[Entity] = []
        self.parent: Optional[Entity] = None
        
    def add_component(self, component: Component) -> Component:
        """Add component to entity"""
        component._entity = self
        self.components[type(component)] = component
        component.on_attach()
        return component
    
    def get_component(self, component_type: Type) -> Optional[Component]:
        """Get component by type"""
        return self.components.get(component_type)
    
    def has_component(self, component_type: Type) -> bool:
        """Check if entity has component"""
        return component_type in self.components
    
    def remove_component(self, component_type: Type):
        """Remove component"""
        if component_type in self.components:
            self.components[component_type].on_detach()
            del self.components[component_type]
    
    def update(self, dt: float):
        """Update all components"""
        if not self.active:
            return
            
        for component in self.components.values():
            if component.enabled:
                if hasattr(component, 'update'):
                    component.update(dt)
        
        # Update children
        for child in self.children:
            child.update(dt)
    
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        """Render entity"""
        if not self.active:
            return
            
        # Render order: sprite, then custom render
        for component in self.components.values():
            if component.enabled:
                if hasattr(component, 'render'):
                    component.render(screen, camera_offset)
        
        # Render children
        for child in self.children:
            child.render(screen, camera_offset)
    
    def add_child(self, child: 'Entity'):
        """Add child entity"""
        child.parent = self
        self.children.append(child)
    
    def get_position(self) -> np.ndarray:
        """Get world position"""
        pos = self.transform.position.copy()
        if self.parent:
            pos += self.parent.get_position()
        return pos
    
    def destroy(self):
        """Mark entity for destruction"""
        self.active = False
        for child in self.children:
            child.destroy()

@dataclass
class Transform(Component):
    """Transform component"""
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0]))
    rotation: float = 0.0
    scale: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0]))
    
    def update(self, dt: float):
        pass  # Base transform doesn't auto-update

@dataclass
class SpriteRenderer(Component):
    """2D sprite renderer component"""
    image: Optional[pygame.Surface] = None
    color: tuple = (255, 255, 255)
    alpha: int = 255
    flip_x: bool = False
    flip_y: bool = False
    layer: int = 0
    
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        if self.image and self._entity:
            pos = self._entity.transform.position - np.array(camera_offset)
            rotated = pygame.transform.rotate(
                self.image, -self._entity.transform.rotation
            )
            flipped = pygame.transform.flip(rotated, self.flip_x, self.flip_y)
            flipped.set_alpha(self.alpha)
            
            rect = flipped.get_rect(center=pos)
            screen.blit(flipped, rect)

@dataclass
class RigidBody(Component):
    """Physics rigidbody component"""
    velocity: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0]))
    angular_velocity: float = 0.0
    mass: float = 1.0
    drag: float = 0.1
    use_gravity: bool = True
    is_kinematic: bool = False
    
    def update(self, dt: float):
        if not self.is_kinematic and self._entity:
            # Apply drag
            self.velocity *= (1 - self.drag * dt)
            
            # Update position
            self._entity.transform.position += self.velocity * dt
            self._entity.transform.rotation += self.angular_velocity * dt
    
    def add_force(self, force: np.ndarray):
        """Apply force to rigidbody"""
        acceleration = force / self.mass
        self.velocity += acceleration
    
    def add_impulse(self, impulse: np.ndarray):
        """Apply instantaneous impulse"""
        self.velocity += impulse / self.mass