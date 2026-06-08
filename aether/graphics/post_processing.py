"""
Post-Processing Effects Stack
Bloom, blur, color grading, and more
"""

import pygame
import numpy as np
from typing import List, Optional, Tuple
import math
from scipy.ndimage import gaussian_filter
from enum import Enum

class BloomEffect:
    """Bloom (glow) post-processing effect"""
    
    def __init__(self, threshold: float = 0.8, intensity: float = 1.0,
                 blur_amount: int = 5, quality: int = 4):
        self.threshold = threshold
        self.intensity = intensity
        self.blur_amount = blur_amount
        self.quality = quality
        self.enabled = True
        
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply bloom effect"""
        if not self.enabled:
            return surface
            
        width, height = surface.get_size()
        
        # Extract bright areas
        bright_pass = self._extract_bright(surface)
        
        # Downsample and blur
        blurred = self._gaussian_blur(bright_pass)
        
        # Composite back
        result = surface.copy()
        result.blit(blurred, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        return result
    
    def _extract_bright(self, surface: pygame.Surface) -> pygame.Surface:
        """Extract bright pixels above threshold"""
        arr = pygame.surfarray.array3d(surface).astype(np.float32) / 255.0
        brightness = np.max(arr, axis=2)
        mask = brightness > self.threshold
        
        bright = np.zeros_like(arr)
        bright[mask] = arr[mask]
        
        bright = (bright * 255).astype(np.uint8)
        result = pygame.surfarray.make_surface(bright)
        
        return result
    
    def _gaussian_blur(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply Gaussian blur"""
        width, height = surface.get_size()
        
        # Create scaled down versions
        scale = 4  # Blur at 1/4 resolution
        small_size = (width // scale, height // scale)
        small_surf = pygame.transform.scale(surface, small_size)
        
        # Apply horizontal and vertical blur
        for _ in range(self.quality):
            small_surf = self._h_blur(small_surf)
            small_surf = self._v_blur(small_surf)
        
        # Scale back up
        result = pygame.transform.scale(small_surf, (width, height))
        result.set_alpha(int(255 * self.intensity))
        
        return result
    
    def _h_blur(self, surface: pygame.Surface) -> pygame.Surface:
        """Horizontal blur pass"""
        width, height = surface.get_size()
        result = surface.copy()
        
        for y in range(height):
            for x in range(self.blur_amount, width - self.blur_amount):
                avg = np.zeros(3)
                count = 0
                
                for dx in range(-self.blur_amount, self.blur_amount + 1):
                    color = surface.get_at((x + dx, y))
                    if color[3] > 0:
                        avg += np.array(color[:3])
                        count += 1
                
                if count > 0:
                    avg = (avg / count).astype(int)
                    result.set_at((x, y), (*avg, surface.get_at((x, y))[3]))
        
        return result
    
    def _v_blur(self, surface: pygame.Surface) -> pygame.Surface:
        """Vertical blur pass"""
        width, height = surface.get_size()
        result = surface.copy()
        
        for x in range(width):
            for y in range(self.blur_amount, height - self.blur_amount):
                avg = np.zeros(3)
                count = 0
                
                for dy in range(-self.blur_amount, self.blur_amount + 1):
                    color = surface.get_at((x, y + dy))
                    if color[3] > 0:
                        avg += np.array(color[:3])
                        count += 1
                
                if count > 0:
                    avg = (avg / count).astype(int)
                    result.set_at((x, y), (*avg, surface.get_at((x, y))[3]))
        
        return result

class BlurEffect:
    """Directional and radial blur effects"""
    
    def __init__(self, amount: float = 1.0, direction: Tuple[float, float] = None):
        self.amount = amount
        self.direction = direction  # None for radial blur
        self.enabled = True
        self.quality = 8  # Number of samples
    
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply blur effect"""
        if not self.enabled or self.amount == 0:
            return surface
        
        if self.direction:
            return self._directional_blur(surface)
        else:
            return self._radial_blur(surface)
    
    def _directional_blur(self, surface: pygame.Surface) -> pygame.Surface:
        """Motion blur in a direction"""
        result = surface.copy()
        result.set_alpha(255 // self.quality)
        
        blend_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        for i in range(1, self.quality + 1):
            offset_x = self.direction[0] * self.amount * i / self.quality
            offset_y = self.direction[1] * self.amount * i / self.quality
            
            blend_surf.blit(surface, (0, 0))
            blend_surf.blit(result, (offset_x, offset_y))
            result.blit(blend_surf, (0, 0))
        
        return result
    
    def _radial_blur(self, surface: pygame.Surface) -> pygame.Surface:
        """Zoom/radial blur"""
        width, height = surface.get_size()
        center = np.array([width/2, height/2])
        result = surface.copy()
        
        for i in range(1, self.quality):
            scale = 1.0 + (self.amount * i / self.quality)
            scaled = pygame.transform.scale(
                surface,
                (int(width * scale), int(height * scale))
            )
            
            # Center the scaled image
            offset = np.array([
                (scaled.get_width() - width) // 2,
                (scaled.get_height() - height) // 2
            ])
            
            temp = pygame.Surface((width, height), pygame.SRCALPHA)
            temp.blit(scaled, -offset)
            temp.set_alpha(128 // self.quality)
            
            result.blit(temp, (0, 0))
        
        return result

class ColorGradingEffect:
    """Color grading with LUT support"""
    
    def __init__(self):
        self.brightness = 0.0
        self.contrast = 1.0
        self.saturation = 1.0
        self.hue_shift = 0.0
        self.color_temperature = 0.0  # -1 cool, 0 neutral, 1 warm
        self.enabled = True
        
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply color grading"""
        if not self.enabled:
            return surface
        
        arr = pygame.surfarray.array3d(surface).astype(np.float32) / 255.0
        
        # Apply brightness
        arr += self.brightness
        
        # Apply contrast
        arr = (arr - 0.5) * self.contrast + 0.5
        
        # Apply saturation
        gray = np.mean(arr, axis=2, keepdims=True)
        arr = gray + (arr - gray) * self.saturation
        
        # Apply color temperature
        if self.color_temperature != 0:
            if self.color_temperature > 0:  # Warm
                arr[:,:,0] *= 1.0 + self.color_temperature * 0.1
                arr[:,:,2] *= 1.0 - self.color_temperature * 0.1
            else:  # Cool
                arr[:,:,2] *= 1.0 - self.color_temperature * 0.1
                arr[:,:,0] *= 1.0 + self.color_temperature * 0.1
        
        # Apply hue shift
        if self.hue_shift != 0:
            arr = self._shift_hue(arr, self.hue_shift)
        
        # Clamp
        arr = np.clip(arr, 0, 1)
        
        result = pygame.surfarray.make_surface((arr * 255).astype(np.uint8))
        return result
    
    def _shift_hue(self, rgb: np.ndarray, shift: float) -> np.ndarray:
        """Shift hue of RGB image"""
        # Convert RGB to HSV-like
        max_val = np.max(rgb, axis=2)
        min_val = np.min(rgb, axis=2)
        diff = max_val - min_val
        
        # Calculate hue (simplified)
        hue = np.zeros_like(max_val)
        
        # Red is max
        mask_r = (max_val == rgb[:,:,0]) & (diff > 0)
        hue[mask_r] = (60 * ((rgb[:,:,1][mask_r] - rgb[:,:,2][mask_r]) / diff[mask_r]) + 360) % 360
        
        # Green is max
        mask_g = (max_val == rgb[:,:,1]) & (diff > 0)
        hue[mask_g] = (60 * ((rgb[:,:,2][mask_g] - rgb[:,:,0][mask_g]) / diff[mask_g]) + 120) % 360
        
        # Blue is max
        mask_b = (max_val == rgb[:,:,2]) & (diff > 0)
        hue[mask_b] = (60 * ((rgb[:,:,0][mask_b] - rgb[:,:,1][mask_b]) / diff[mask_b]) + 240) % 360
        
        # Shift hue
        hue = (hue + shift * 360) % 360
        hue /= 360
        
        # Convert back to RGB (simplified)
        saturation = np.where(max_val > 0, diff / max_val, 0)
        
        c = saturation
        x = c * (1 - np.abs(hue * 6 % 2 - 1))
        m = max_val - c
        
        h6 = hue * 6
        result = np.zeros_like(rgb)
        
        mask = h6 < 1
        result[mask,0] = c[mask] + m[mask]
        result[mask,1] = x[mask] + m[mask]
        result[mask,2] = m[mask]
        
        mask = (h6 >= 1) & (h6 < 2)
        result[mask,0] = x[mask] + m[mask]
        result[mask,1] = c[mask] + m[mask]
        result[mask,2] = m[mask]
        
        mask = (h6 >= 2) & (h6 < 3)
        result[mask,0] = m[mask]
        result[mask,1] = c[mask] + m[mask]
        result[mask,2] = x[mask] + m[mask]
        
        mask = (h6 >= 3) & (h6 < 4)
        result[mask,0] = m[mask]
        result[mask,1] = x[mask] + m[mask]
        result[mask,2] = c[mask] + m[mask]
        
        mask = (h6 >= 4) & (h6 < 5)
        result[mask,0] = x[mask] + m[mask]
        result[mask,1] = m[mask]
        result[mask,2] = c[mask] + m[mask]
        
        mask = h6 >= 5
        result[mask,0] = c[mask] + m[mask]
        result[mask,1] = m[mask]
        result[mask,2] = x[mask] + m[mask]
        
        return result

class ChromaticAberrationEffect:
    """Chromatic aberration (color fringing) effect"""
    
    def __init__(self, amount: float = 1.0):
        self.amount = amount
        self.enabled = True
    
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply chromatic aberration"""
        if not self.enabled or self.amount == 0:
            return surface
        
        width, height = surface.get_size()
        center = np.array([width/2, height/2])
        result = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Split into color channels
        arr = pygame.surfarray.array3d(surface)
        
        # Red channel offset
        red_surf = pygame.Surface((width, height))
        red_arr = np.zeros((width, height, 3), dtype=np.uint8)
        red_arr[:,:,0] = arr[:,:,0]
        pygame.surfarray.blit_array(red_surf, red_arr)
        
        # Blue channel offset
        blue_surf = pygame.Surface((width, height))
        blue_arr = np.zeros((width, height, 3), dtype=np.uint8)
        blue_arr[:,:,2] = arr[:,:,2]
        pygame.surfarray.blit_array(blue_surf, blue_arr)
        
        # Offset red channel away from center
        red_offset = (red_surf.get_rect().center - np.array([width/2, height/2])) * self.amount * 0.5
        
        # Offset blue channel toward center
        blue_offset = (blue_surf.get_rect().center - np.array([width/2, height/2])) * -self.amount * 0.5
        
        # Composite
        result.blit(surface, (0, 0))
        result.blit(red_surf, red_offset)
        result.blit(blue_surf, blue_offset)
        
        return result

class PostProcessingStack:
    """Stack of post-processing effects"""
    
    def __init__(self):
        self.effects: List = []
        
        # Default effects
        self.bloom = BloomEffect(threshold=0.7, intensity=0.5)
        self.color_grading = ColorGradingEffect()
        self.chromatic_aberration = ChromaticAberrationEffect(amount=0.5)
        
        self.add_effect(self.bloom)
        self.add_effect(self.color_grading)
    
    def add_effect(self, effect):
        """Add effect to stack"""
        self.effects.append(effect)
    
    def remove_effect(self, effect):
        """Remove effect from stack"""
        if effect in self.effects:
            self.effects.remove(effect)
    
    def apply(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply all effects in order"""
        result = surface
        for effect in self.effects:
            if hasattr(effect, 'enabled') and effect.enabled:
                result = effect.apply(result)
        return result