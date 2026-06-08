"""
Advanced Sprite System with Batching and Atlasing
"""

import pygame
import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass
import math

@dataclass
class SpriteBatch:
    """Batched sprite rendering for performance"""
    texture: pygame.Surface
    positions: List[np.ndarray]
    rotations: List[float]
    scales: List[float]
    colors: List[Tuple[int, int, int, int]]
    
    def __init__(self, texture: pygame.Surface, max_sprites: int = 4096):
        self.texture = texture
        self.max_sprites = max_sprites
        self.clear()
    
    def clear(self):
        """Clear batch"""
        self.positions = []
        self.rotations = []
        self.scales = []
        self.colors = []
    
    def add_sprite(self, position: np.ndarray, rotation: float = 0.0,
                   scale: float = 1.0, color: Tuple[int, int, int, int] = (255, 255, 255, 255)):
        """Add sprite to batch"""
        if len(self.positions) < self.max_sprites:
            self.positions.append(position)
            self.rotations.append(rotation)
            self.scales.append(scale)
            self.colors.append(color)
    
    def render(self, screen: pygame.Surface, camera_offset: np.ndarray = None):
        """Render batched sprites"""
        if camera_offset is None:
            camera_offset = np.array([0.0, 0.0])
        
        for pos, rot, scale, color in zip(
            self.positions, self.rotations, self.scales, self.colors
        ):
            screen_pos = pos - camera_offset
            
            # Apply rotation and scale
            if rot != 0 or scale != 1.0:
                scaled_size = (
                    int(self.texture.get_width() * scale),
                    int(self.texture.get_height() * scale)
                )
                scaled_texture = pygame.transform.scale(self.texture, scaled_size)
                
                if rot != 0:
                    transformed = pygame.transform.rotate(scaled_texture, rot)
                else:
                    transformed = scaled_texture
            else:
                transformed = self.texture
            
            # Apply color modulation
            if color != (255, 255, 255, 255):
                transformed = transformed.copy()
                if len(color) == 4:
                    transformed.set_alpha(color[3])
                transformed.fill(color[:3], special_flags=pygame.BLEND_RGB_MULT)
            
            rect = transformed.get_rect(center=screen_pos)
            screen.blit(transformed, rect)

class Sprite:
    """Individual sprite with advanced features"""
    
    def __init__(self, image: Optional[pygame.Surface] = None):
        self.image = image
        self.visible = True
        self.opacity = 255
        self.blend_mode = pygame.BLENDMODE_NONE
        self.flip_x = False
        self.flip_y = False
        
        # Pivot point (0.0 to 1.0)
        self.pivot = np.array([0.5, 0.5])
        
        # Tinting
        self.tint_color = None
        
    def render(self, screen: pygame.Surface, position: np.ndarray,
              rotation: float = 0.0, scale: Tuple[float, float] = (1.0, 1.0)):
        """Render sprite"""
        if not self.visible or not self.image:
            return
        
        # Apply transformations
        transformed = self.image.copy()
        
        # Scale
        if scale != (1.0, 1.0):
            new_size = (
                int(transformed.get_width() * scale[0]),
                int(transformed.get_height() * scale[1])
            )
            transformed = pygame.transform.scale(transformed, new_size)
        
        # Flip
        if self.flip_x or self.flip_y:
            transformed = pygame.transform.flip(transformed, self.flip_x, self.flip_y)
        
        # Rotate
        if rotation != 0:
            transformed = pygame.transform.rotate(transformed, rotation)
        
        # Apply tint
        if self.tint_color:
            tinted = transformed.copy()
            tinted.fill(self.tint_color, special_flags=pygame.BLEND_RGB_MULT)
            transformed = tinted
        
        # Apply opacity
        if self.opacity < 255:
            transformed.set_alpha(self.opacity)
        
        # Apply pivot
        rect = transformed.get_rect()
        rect.center = position
        
        screen.blit(transformed, rect, special_flags=self.blend_mode)

class AnimatedSprite(Sprite):
    """Animated sprite with frame management"""
    
    def __init__(self, frames: List[pygame.Surface] = None):
        super().__init__()
        self.frames = frames or []
        self.current_frame = 0
        self.frame_rate = 12.0  # Frames per second
        self.frame_timer = 0.0
        self.loop = True
        self.playing = True
        self.ping_pong = False
        self.reverse = False
        
    def update(self, dt: float):
        """Update animation"""
        if not self.playing or len(self.frames) <= 1:
            return
        
        self.frame_timer += dt
        
        if self.frame_timer >= 1.0 / self.frame_rate:
            self.frame_timer -= 1.0 / self.frame_rate
            self._advance_frame()
    
    def _advance_frame(self):
        """Advance to next frame"""
        if self.reverse:
            self.current_frame -= 1
        else:
            self.current_frame += 1
        
        if self.ping_pong:
            if self.current_frame >= len(self.frames) - 1:
                self.reverse = True
            elif self.current_frame <= 0:
                self.reverse = False
        elif self.loop:
            self.current_frame = self.current_frame % len(self.frames)
        else:
            if self.current_frame >= len(self.frames):
                self.current_frame = len(self.frames) - 1
                self.playing = False
            
            if self.current_frame < 0:
                self.current_frame = 0
                self.playing = False
    
    def render(self, screen: pygame.Surface, position: np.ndarray,
              rotation: float = 0.0, scale: Tuple[float, float] = (1.0, 1.0)):
        """Render current frame"""
        if self.frames:
            self.image = self.frames[self.current_frame]
        super().render(screen, position, rotation, scale)
    
    def set_frame(self, index: int):
        """Set current frame"""
        self.current_frame = max(0, min(index, len(self.frames) - 1))
    
    def play(self):
        """Start playing"""
        self.playing = True
    
    def stop(self):
        """Stop playing"""
        self.playing = False
    
    def restart(self):
        """Restart animation"""
        self.current_frame = 0
        self.frame_timer = 0.0
        self.playing = True