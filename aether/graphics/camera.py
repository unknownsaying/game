"""
Advanced Camera System with Smooth Movement, Shake, and Zoom
"""

import pygame
import numpy as np
from typing import Optional, Tuple
from dataclasses import dataclass
import math
import random

@dataclass
class CameraConfig:
    """Camera configuration"""
    smoothing: float = 5.0
    zoom_smoothing: float = 3.0
    min_zoom: float = 0.1
    max_zoom: float = 5.0
    dead_zone: Tuple[float, float] = (0.1, 0.1)  # Percentage of screen

class Camera:
    """Individual camera with transforms"""
    
    def __init__(self, width: int, height: int, config: Optional[CameraConfig] = None):
        self.width = width
        self.height = height
        self.config = config or CameraConfig()
        
        # Position and transform
        self.position = np.array([width/2, height/2], dtype=float)
        self.target_position = self.position.copy()
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.rotation = 0.0
        self.target_rotation = 0.0
        
        # Effects
        self.shake_intensity = 0.0
        self.shake_decay = 5.0
        self.shake_offset = np.array([0.0, 0.0])
        
        # Boundaries
        self.bounds = None  # Optional (min_x, min_y, max_x, max_y)
        
    def move_to(self, x: float, y: float, instant: bool = False):
        """Set target position"""
        self.target_position = np.array([x, y])
        if instant:
            self.position = self.target_position.copy()
    
    def move_by(self, dx: float, dy: float):
        """Move by delta"""
        self.target_position += np.array([dx, dy])
    
    def zoom_to(self, zoom: float, instant: bool = False):
        """Set target zoom"""
        self.target_zoom = np.clip(zoom, self.config.min_zoom, self.config.max_zoom)
        if instant:
            self.zoom = self.target_zoom
    
    def rotate_to(self, angle: float, instant: bool = False):
        """Set target rotation in degrees"""
        self.target_rotation = angle
        if instant:
            self.rotation = angle
    
    def shake(self, intensity: float, duration: float = 0.5):
        """Add camera shake"""
        self.shake_intensity = intensity
        self.shake_decay = intensity / duration
    
    def update(self, dt: float):
        """Update camera transforms"""
        # Smooth position
        self.position += (self.target_position - self.position) * self.config.smoothing * dt
        
        # Smooth zoom
        self.zoom += (self.target_zoom - self.zoom) * self.config.zoom_smoothing * dt
        
        # Smooth rotation
        self.rotation += (self.target_rotation - self.rotation) * self.config.zoom_smoothing * dt
        
        # Update shake
        if self.shake_intensity > 0:
            self.shake_offset = np.array([
                random.uniform(-1, 1) * self.shake_intensity,
                random.uniform(-1, 1) * self.shake_intensity
            ])
            self.shake_intensity -= self.shake_decay * dt
            
            if self.shake_intensity < 0:
                self.shake_intensity = 0
                self.shake_offset = np.array([0.0, 0.0])
        
        # Apply boundaries
        if self.bounds:
            self._apply_bounds()
    
    def _apply_bounds(self):
        """Keep camera within bounds"""
        min_x, min_y, max_x, max_y = self.bounds
        half_w = self.width / (2 * self.zoom)
        half_h = self.height / (2 * self.zoom)
        
        self.position[0] = np.clip(self.position[0], min_x + half_w, max_x - half_w)
        self.position[1] = np.clip(self.position[1], min_y + half_h, max_y - half_h)
    
    def get_transform(self) -> Tuple[np.ndarray, float, float]:
        """Get current transform (position, zoom, rotation)"""
        return self.position + self.shake_offset, self.zoom, self.rotation
    
    def world_to_screen(self, world_pos: np.ndarray) -> np.ndarray:
        """Convert world coordinates to screen coordinates"""
        pos, zoom, rot = self.get_transform()
        
        # Translate relative to camera
        relative = world_pos - pos
        
        # Apply zoom
        scaled = relative * zoom
        
        # Apply rotation if needed
        if rot != 0:
            angle = math.radians(rot)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            scaled = np.array([
                scaled[0] * cos_a - scaled[1] * sin_a,
                scaled[0] * sin_a + scaled[1] * cos_a
            ])
        
        # Center on screen
        screen_pos = scaled + np.array([self.width/2, self.height/2])
        return screen_pos
    
    def screen_to_world(self, screen_pos: np.ndarray) -> np.ndarray:
        """Convert screen coordinates to world coordinates"""
        pos, zoom, rot = self.get_transform()
        
        # Uncenter
        centered = screen_pos - np.array([self.width/2, self.height/2])
        
        # Reverse rotation
        if rot != 0:
            angle = math.radians(-rot)
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            centered = np.array([
                centered[0] * cos_a - centered[1] * sin_a,
                centered[0] * sin_a + centered[1] * cos_a
            ])
        
        # Unscale
        unscaled = centered / zoom
        
        return unscaled + pos

class CameraSystem:
    """Manages multiple cameras"""
    
    def __init__(self, engine):
        self.engine = engine
        self.cameras = {}
        self.active_camera: Optional[Camera] = None
        
        # Create default camera
        default_camera = Camera(
            engine.config.width,
            engine.config.height
        )
        self.add_camera("main", default_camera)
        self.set_active("main")
    
    def add_camera(self, name: str, camera: Camera):
        """Add a camera"""
        self.cameras[name] = camera
    
    def set_active(self, name: str):
        """Set active camera"""
        if name in self.cameras:
            self.active_camera = self.cameras[name]
    
    def get_active(self) -> Optional[Camera]:
        """Get active camera"""
        return self.active_camera
    
    def begin_frame(self):
        """Setup camera for rendering frame"""
        if self.active_camera:
            self.active_camera.update(self.engine.delta_time)
    
    def end_frame(self):
        """Cleanup after frame"""
        pass