"""
Advanced rendering pipeline with post-processing effects
"""

import pygame
import numpy as np
from typing import List, Tuple, Optional
import math

class Renderer:
    """Advanced rendering system"""
    
    def __init__(self, engine):
        self.engine = engine
        self.particle_systems = []
        self.light_sources = []
        self.post_effects = []
        
        # Create render surfaces
        self.game_surface = pygame.Surface(
            (engine.config.width, engine.config.height), 
            pygame.SRCALPHA
        )
        self.light_surface = pygame.Surface(
            (engine.config.width, engine.config.height), 
            pygame.SRCALPHA
        )
        self.effect_surface = pygame.Surface(
            (engine.config.width, engine.config.height)
        )
        
        # Default post-processing effects
        self.add_post_effect(VignetteEffect())
        self.add_post_effect(ColorGradingEffect())
        
    def render_particles(self, screen: pygame.Surface):
        """Render all particle systems"""
        for ps in self.particle_systems:
            ps.render(screen)
    
    def apply_post_processing(self, screen: pygame.Surface):
        """Apply post-processing effects"""
        for effect in self.post_effects:
            effect.apply(screen)
    
    def add_particle_system(self, ps):
        """Add particle system to renderer"""
        self.particle_systems.append(ps)
    
    def add_light_source(self, light):
        """Add light source to scene"""
        self.light_sources.append(light)
    
    def add_post_effect(self, effect):
        """Add post-processing effect"""
        self.post_effects.append(effect)

class Particle:
    """Individual particle"""
    
    def __init__(self, pos, velocity, life, color, size):
        self.pos = np.array(pos, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.active = True
    
    def update(self, dt: float):
        """Update particle"""
        self.life -= dt
        if self.life <= 0:
            self.active = False
        self.pos += self.velocity * dt
        self.velocity *= 0.98  # Friction

class ParticleSystem:
    """Particle system for effects"""
    
    def __init__(self, max_particles: int = 1000):
        self.particles: List[Particle] = []
        self.max_particles = max_particles
        self.emission_rate = 50  # particles per second
        self.emission_accum = 0.0
        
    def emit(self, position, velocity_range, life_range, 
             color, size_range, count=1):
        """Emit particles"""
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
                
            velocity = np.array([
                random.uniform(*velocity_range[0]),
                random.uniform(*velocity_range[1])
            ])
            
            life = random.uniform(*life_range)
            size = random.uniform(*size_range)
            
            self.particles.append(
                Particle(position, velocity, life, color, size)
            )
    
    def update(self, dt: float):
        """Update all particles"""
        # Remove inactive particles
        self.particles = [p for p in self.particles if p.active]
        
        # Update particles
        for particle in self.particles:
            particle.update(dt)
    
    def render(self, screen: pygame.Surface, camera_offset=(0, 0)):
        """Render particles"""
        for particle in self.particles:
            alpha = int(255 * (particle.life / particle.max_life))
            pos = particle.pos - np.array(camera_offset)
            
            # Create particle surface
            surf = pygame.Surface((particle.size*2, particle.size*2), 
                                 pygame.SRCALPHA)
            color_with_alpha = (*particle.color, alpha)
            pygame.draw.circle(surf, color_with_alpha, 
                             (particle.size, particle.size), 
                             particle.size)
            screen.blit(surf, pos - particle.size)

class Light:
    """Dynamic light source"""
    
    def __init__(self, position, color, intensity, radius):
        self.position = np.array(position)
        self.color = color
        self.intensity = intensity
        self.radius = radius
        self.flicker = False
        self.flicker_speed = 1.0
    
    def get_intensity_at(self, point: np.ndarray) -> float:
        """Calculate light intensity at a point"""
        distance = np.linalg.norm(point - self.position)
        if distance > self.radius:
            return 0.0
        
        # Inverse square falloff
        falloff = 1.0 - (distance / self.radius)
        falloff = falloff * falloff  # Quadratic falloff
        
        intensity = self.intensity * falloff
        
        if self.flicker:
            intensity *= 0.8 + 0.2 * math.sin(pygame.time.get_ticks() * 0.01 * self.flicker_speed)
        
        return max(0.0, min(1.0, intensity))

class PostProcessingEffect:
    """Base class for post-processing effects"""
    
    def apply(self, surface: pygame.Surface):
        pass

class VignetteEffect(PostProcessingEffect):
    """Darkens edges of screen"""
    
    def __init__(self, intensity: float = 0.5):
        self.intensity = intensity
    
    def apply(self, surface: pygame.Surface):
        width, height = surface.get_size()
        
        # Create vignette overlay
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        
        for y in range(height):
            for x in range(width):
                # Calculate distance from center (0 to 1)
                dx = (x - width/2) / (width/2)
                dy = (y - height/2) / (height/2)
                distance = math.sqrt(dx*dx + dy*dy)
                
                # Calculate vignette alpha
                alpha = min(255, int(255 * distance * self.intensity))
                vignette.set_at((x, y), (0, 0, 0, alpha))
        
        surface.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

class ColorGradingEffect(PostProcessingEffect):
    """Adjust color balance"""
    
    def __init__(self, contrast: float = 1.0, 
                 brightness: float = 0.0, saturation: float = 1.0):
        self.contrast = contrast
        self.brightness = brightness
        self.saturation = saturation
    
    def apply(self, surface: pygame.Surface):
        # Get pixel array
        pixels = pygame.surfarray.pixels3d(surface)
        
        # Apply color grading
        pixels = np.clip(
            (pixels - 128) * self.contrast + 128 + self.brightness * 255,
            0, 255
        ).astype(np.uint8)
        
        # Apply saturation
        if self.saturation != 1.0:
            gray = np.mean(pixels, axis=2, keepdims=True)
            pixels = (gray + (pixels - gray) * self.saturation).astype(np.uint8)
        
        # Write back
        surface_array = pygame.surfarray.pixels3d(surface)
        surface_array[:] = pixels