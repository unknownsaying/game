"""
Scene Management System
Handles scene transitions, loading, and lifetime
"""

from typing import Dict, Optional, Type, Any
from enum import Enum
import pygame
import numpy as np

class TransitionType(Enum):
    """Scene transition effects"""
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    ZOOM = "zoom"
    NONE = "none"

class SceneTransition:
    """Manages transition between scenes"""
    
    def __init__(self, duration: float = 0.5, 
                 transition_type: TransitionType = TransitionType.FADE):
        self.duration = duration
        self.type = transition_type
        self.progress = 0.0
        self.active = False
        self.from_scene = None
        self.to_scene = None
        
    def start(self, from_scene, to_scene):
        """Start transition between scenes"""
        self.active = True
        self.progress = 0.0
        self.from_scene = from_scene
        self.to_scene = to_scene
    
    def update(self, dt: float):
        """Update transition progress"""
        if self.active:
            self.progress += dt / self.duration
            if self.progress >= 1.0:
                self.progress = 1.0
                self.active = False
    
    def get_alpha(self) -> float:
        """Get current transition alpha"""
        # Smooth step function for easing
        t = np.clip(self.progress, 0.0, 1.0)
        return t * t * (3 - 2 * t)  # Smoothstep
    
    def render(self, screen: pygame.Surface):
        """Render transition effect"""
        if not self.active:
            return
        
        alpha = self.get_alpha()
        width, height = screen.get_size()
        
        if self.type == TransitionType.FADE:
            # Create fade overlay
            overlay = pygame.Surface((width, height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(int(255 * alpha))
            screen.blit(overlay, (0, 0))
            
        elif self.type == TransitionType.SLIDE_LEFT:
            offset = int(width * (1 - alpha))
            screen.blit(screen, (-offset, 0))
            
        elif self.type == TransitionType.SLIDE_RIGHT:
            offset = int(width * (1 - alpha))
            screen.blit(screen, (offset, 0))
            
        elif self.type == TransitionType.ZOOM:
            # Zoom effect using scale
            scale_factor = 1.0 + alpha * 0.5
            scaled = pygame.transform.scale(
                screen,
                (int(width * scale_factor), int(height * scale_factor))
            )
            x = (width - scaled.get_width()) // 2
            y = (height - scaled.get_height()) // 2
            screen.fill((0, 0, 0))
            screen.blit(scaled, (x, y))

class Scene:
    """Base scene class"""
    
    def __init__(self, engine, name: str):
        self.engine = engine
        self.name = name
        self.entities = []
        self.camera = None
        self.is_active = False
        self.time_scale = 1.0
        self.local_time = 0.0
        
    def on_enter(self):
        """Called when scene becomes active"""
        pass
    
    def on_exit(self):
        """Called when scene is removed"""
        pass
    
    def on_pause(self):
        """Called when scene is paused"""
        pass
    
    def on_resume(self):
        """Called when scene is resumed"""
        pass
    
    def handle_event(self, event: pygame.event.Event):
        """Handle input events"""
        for entity in self.entities:
            if hasattr(entity, 'handle_event'):
                entity.handle_event(event)
    
    def update(self, dt: float):
        """Update scene logic"""
        scaled_dt = dt * self.time_scale
        self.local_time += scaled_dt
        
        for entity in self.entities:
            entity.update(scaled_dt)
    
    def render(self, screen: pygame.Surface):
        """Render scene"""
        for entity in self.entities:
            entity.render(screen)
    
    def add_entity(self, entity):
        """Add entity to scene"""
        self.entities.append(entity)
    
    def remove_entity(self, entity):
        """Remove entity from scene"""
        if entity in self.entities:
            self.entities.remove(entity)
    
    def get_entities_by_tag(self, tag: str) -> list:
        """Get all entities with a specific tag"""
        return [e for e in self.entities if hasattr(e, 'tag') and e.tag == tag]

class SceneManager:
    """Manages scene lifecycle and transitions"""
    
    def __init__(self, engine):
        self.engine = engine
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.current_scene_name: str = ""
        self.transition = SceneTransition()
        self.scene_history = []
        
    def add_scene(self, scene: Scene):
        """Register a scene"""
        self.scenes[scene.name] = scene
        
    def load_scene(self, scene_name: str):
        """Load and activate a scene"""
        if scene_name not in self.scenes:
            raise ValueError(f"Scene '{scene_name}' not found")
        
        # Transition from current scene
        if self.current_scene:
            self.transition.start(self.current_scene, self.scenes[scene_name])
            self.current_scene.on_exit()
            self.scene_history.append(self.current_scene_name)
        
        # Activate new scene
        self.current_scene = self.scenes[scene_name]
        self.current_scene_name = scene_name
        self.current_scene.on_enter()
        
    def reload_current_scene(self):
        """Reload current scene"""
        if self.current_scene_name:
            self.load_scene(self.current_scene_name)
    
    def go_back(self):
        """Return to previous scene"""
        if self.scene_history:
            previous = self.scene_history.pop()
            self.load_scene(previous)
    
    def handle_event(self, event):
        """Forward events to current scene"""
        if self.current_scene and not self.transition.active:
            self.current_scene.handle_event(event)
    
    def update(self, dt: float):
        """Update current scene and transition"""
        self.transition.update(dt)
        
        if self.current_scene and not self.transition.active:
            self.current_scene.update(dt)
    
    def render(self, screen: pygame.Surface):
        """Render current scene and transition"""
        if self.current_scene:
            self.current_scene.render(screen)
        
        if self.transition.active:
            self.transition.render(screen)