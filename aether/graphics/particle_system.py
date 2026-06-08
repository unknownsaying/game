"""
Advanced Particle System with GPU Optimization
Supports complex behaviors, forces, and rendering techniques
"""

import pygame
import numpy as np
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
import random
import math
from enum import Enum

class ParticleBlendMode(Enum):
    """Particle blending modes"""
    ALPHA = "alpha"
    ADDITIVE = "additive"
    MULTIPLY = "multiply"
    SCREEN = "screen"

class ParticleShape(Enum):
    """Particle shapes"""
    CIRCLE = "circle"
    SQUARE = "square"
    STAR = "star"
    TRAIL = "trail"
    TEXTURE = "texture"

@dataclass
class ParticleData:
    """Store particle data in Structure of Arrays format for cache efficiency"""
    
    def __init__(self, max_particles: int):
        # Position
        self.positions = np.zeros((max_particles, 2), dtype=np.float32)
        self.prev_positions = np.zeros((max_particles, 2), dtype=np.float32)
        
        # Velocity
        self.velocities = np.zeros((max_particles, 2), dtype=np.float32)
        
        # Life
        self.lifetimes = np.zeros(max_particles, dtype=np.float32)
        self.max_lifetimes = np.zeros(max_particles, dtype=np.float32)
        
        # Visual
        self.sizes = np.zeros(max_particles, dtype=np.float32)
        self.start_sizes = np.zeros(max_particles, dtype=np.float32)
        self.end_sizes = np.zeros(max_particles, dtype=np.float32)
        
        self.colors = np.zeros((max_particles, 4), dtype=np.float32)  # RGBA
        self.start_colors = np.zeros((max_particles, 4), dtype=np.float32)
        self.end_colors = np.zeros((max_particles, 4), dtype=np.float32)
        
        # Rotation
        self.rotations = np.zeros(max_particles, dtype=np.float32)
        self.angular_velocities = np.zeros(max_particles, dtype=np.float32)
        
        # Custom data
        self.custom_data = np.zeros((max_particles, 4), dtype=np.float32)
        
        # Active flags
        self.active = np.zeros(max_particles, dtype=bool)
        
        self.count = 0

class ForceField:
    """Force field affecting particles"""
    
    def __init__(self, position: np.ndarray, strength: float, 
                 radius: float, force_type: str = "radial"):
        self.position = np.array(position, dtype=np.float32)
        self.strength = strength
        self.radius = radius
        self.force_type = force_type
    
    def apply(self, positions: np.ndarray, velocities: np.ndarray, 
              active: np.ndarray, dt: float):
        """Apply force to particles"""
        if not np.any(active):
            return
        
        # Vector from particles to force center
        to_center = self.position - positions[active]
        distances = np.linalg.norm(to_center, axis=1)
        
        # Avoid division by zero
        distances = np.maximum(distances, 0.001)
        
        # Normalize
        directions = to_center / distances[:, np.newaxis]
        
        # Calculate influence
        influence = np.maximum(0, 1 - distances / self.radius)
        
        if self.force_type == "radial":
            # Attract or repel
            force = directions * influence[:, np.newaxis] * self.strength * dt
        elif self.force_type == "vortex":
            # Rotate around center
            perpendicular = np.column_stack([-directions[:, 1], directions[:, 0]])
            force = perpendicular * influence[:, np.newaxis] * self.strength * dt
        elif self.force_type == "turbulence":
            # Random perturbation
            noise = np.random.randn(np.sum(active), 2)
            force = noise * influence[:, np.newaxis] * self.strength * dt
        else:
            force = np.zeros_like(directions)
        
        velocities[active] += force

class ParticleEmitter:
    """Controls particle emission parameters"""
    
    def __init__(self, position: np.ndarray):
        self.position = np.array(position, dtype=np.float32)
        
        # Emission
        self.emission_rate = 50.0  # Particles per second
        self.emission_accumulator = 0.0
        self.burst_count = 0
        self.max_particles = 1000
        
        # Shape
        self.shape = ParticleShape.CIRCLE
        self.emission_shape = "point"  # point, circle, box, cone
        self.emission_radius = 10.0
        
        # Lifetime
        self.min_lifetime = 0.5
        self.max_lifetime = 2.0
        
        # Speed
        self.min_speed = 50.0
        self.max_speed = 200.0
        self.angle = 0.0  # Base emission angle
        self.spread = math.pi * 2  # Full circle
        
        # Size
        self.start_size = 10.0
        self.end_size = 0.0
        
        # Color
        self.start_color = np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        self.end_color = np.array([1.0, 1.0, 1.0, 0.0], dtype=np.float32)
        
        # Physics
        self.gravity = np.array([0.0, 100.0], dtype=np.float32)
        self.damping = 0.98
        self.rotation_speed = 0.0
        
        # Rendering
        self.blend_mode = ParticleBlendMode.ALPHA
        self.texture = None
        self.use_soft_particles = False
    
    def emit(self, data: ParticleData, dt: float, transform: Optional[Callable] = None):
        """Emit particles this frame"""
        self.emission_accumulator += self.emission_rate * dt
        
        particles_to_emit = int(self.emission_accumulator)
        self.emission_accumulator -= particles_to_emit
        
        # Burst emission
        if self.burst_count > 0:
            particles_to_emit += self.burst_count
            self.burst_count = 0
        
        for _ in range(particles_to_emit):
            if data.count >= self.max_particles:
                break
            
            # Find inactive slot
            inactive_indices = np.where(~data.active)[0]
            if len(inactive_indices) == 0:
                break
            
            idx = inactive_indices[0]
            
            # Generate emission position
            if self.emission_shape == "point":
                pos = self.position.copy()
            elif self.emission_shape == "circle":
                angle = random.uniform(0, 2 * math.pi)
                radius = random.uniform(0, self.emission_radius)
                pos = self.position + np.array([
                    math.cos(angle) * radius,
                    math.sin(angle) * radius
                ])
            elif self.emission_shape == "box":
                pos = self.position + np.array([
                    random.uniform(-self.emission_radius, self.emission_radius),
                    random.uniform(-self.emission_radius, self.emission_radius)
                ])
            
            # Generate velocity
            angle = self.angle + random.uniform(-self.spread / 2, self.spread / 2)
            speed = random.uniform(self.min_speed, self.max_speed)
            velocity = np.array([
                math.cos(angle) * speed,
                math.sin(angle) * speed
            ])
            
            # Set particle data
            data.positions[idx] = pos
            data.prev_positions[idx] = pos
            data.velocities[idx] = velocity
            data.lifetimes[idx] = random.uniform(self.min_lifetime, self.max_lifetime)
            data.max_lifetimes[idx] = data.lifetimes[idx]
            data.sizes[idx] = self.start_size
            data.start_sizes[idx] = self.start_size
            data.end_sizes[idx] = self.end_size
            data.colors[idx] = self.start_color
            data.start_colors[idx] = self.start_color
            data.end_colors[idx] = self.end_color
            data.rotations[idx] = 0.0
            data.angular_velocities[idx] = self.rotation_speed
            data.active[idx] = True
            data.count += 1

class AdvancedParticleSystem:
    """
    Advanced particle system with:
    - Structure of Arrays for cache efficiency
    - Force fields
    - GPU-friendly data layout
    - Multiple emitters
    - Advanced rendering
    """
    
    def __init__(self, max_particles: int = 10000):
        self.data = ParticleData(max_particles)
        self.emitters: List[ParticleEmitter] = []
        self.force_fields: List[ForceField] = []
        self.max_particles = max_particles
        
        # Pre-allocate rendering surfaces
        self.particle_surfaces = {}
        
        # Statistics
        self.active_count = 0
        self.total_emitted = 0
        
    def add_emitter(self, emitter: ParticleEmitter):
        """Add particle emitter"""
        emitter.max_particles = self.max_particles // max(1, len(self.emitters) + 1)
        self.emitters.append(emitter)
    
    def add_force_field(self, force_field: ForceField):
        """Add force field"""
        self.force_fields.append(force_field)
    
    def update(self, dt: float):
        """Update all particles"""
        # Emit new particles
        for emitter in self.emitters:
            emitter.emit(self.data, dt)
        
        # Update existing particles
        active_mask = self.data.active
        
        if not np.any(active_mask):
            return
        
        # Store previous positions for trails
        self.data.prev_positions[active_mask] = self.data.positions[active_mask].copy()
        
        # Apply velocities
        self.data.positions[active_mask] += self.data.velocities[active_mask] * dt
        
        # Apply gravity (per emitter)
        for emitter in self.emitters:
            self.data.velocities[active_mask] += emitter.gravity * dt
        
        # Apply force fields
        for force_field in self.force_fields:
            force_field.apply(
                self.data.positions,
                self.data.velocities,
                active_mask,
                dt
            )
        
        # Apply damping
        for emitter in self.emitters:
            self.data.velocities[active_mask] *= emitter.damping
        
        # Update rotations
        self.data.rotations[active_mask] += self.data.angular_velocities[active_mask] * dt
        
        # Update lifetimes
        self.data.lifetimes[active_mask] -= dt
        
        # Kill expired particles
        expired = self.data.lifetimes <= 0
        self.data.active[expired] = False
        self.data.count -= np.sum(expired)
        
        # Update sizes (smooth interpolation)
        life_ratio = np.clip(
            1 - self.data.lifetimes[active_mask] / self.data.max_lifetimes[active_mask],
            0, 1
        )
        self.data.sizes[active_mask] = (
            self.data.start_sizes[active_mask] + 
            (self.data.end_sizes[active_mask] - self.data.start_sizes[active_mask]) * life_ratio
        )
        
        # Update colors (smooth interpolation)
        self.data.colors[active_mask] = (
            self.data.start_colors[active_mask] + 
            (self.data.end_colors[active_mask] - self.data.start_colors[active_mask]) * 
            life_ratio[:, np.newaxis]
        )
        
        # Clamp colors
        self.data.colors = np.clip(self.data.colors, 0, 1)
        
        # Update statistics
        self.active_count = self.data.count
        self.total_emitted += len(self.emitters)
    
    def render(self, screen: pygame.Surface, camera_offset: np.ndarray = None):
        """Render all active particles"""
        if camera_offset is None:
            camera_offset = np.array([0.0, 0.0])
        
        active_mask = self.data.active
        
        if not np.any(active_mask):
            return
        
        # Get active particle data
        positions = self.data.positions[active_mask] - camera_offset
        sizes = self.data.sizes[active_mask]
        colors = self.data.colors[active_mask]
        rotations = self.data.rotations[active_mask]
        
        # Sort by blend mode for proper rendering
        for emitter in self.emitters:
            if emitter.blend_mode == ParticleBlendMode.ADDITIVE:
                # Use additive blending surface
                for pos, size, color, rot in zip(positions, sizes, colors, rotations):
                    if size < 1:
                        continue
                    
                    # Create particle surface
                    surf_size = int(size * 2)
                    if surf_size < 2:
                        surf_size = 2
                    
                    particle_surf = pygame.Surface(
                        (surf_size, surf_size), 
                        pygame.SRCALPHA
                    )
                    
                    # Draw particle shape
                    if emitter.shape == ParticleShape.CIRCLE:
                        color_255 = tuple(int(c * 255) for c in color)
                        pygame.draw.circle(
                            particle_surf,
                            color_255,
                            (surf_size // 2, surf_size // 2),
                            int(size)
                        )
                    elif emitter.shape == ParticleShape.STAR:
                        self._draw_star(particle_surf, color, size, surf_size)
                    else:
                        color_255 = tuple(int(c * 255) for c in color)
                        rect = pygame.Rect(0, 0, int(size), int(size))
                        rect.center = (surf_size // 2, surf_size // 2)
                        pygame.draw.rect(particle_surf, color_255, rect)
                    
                    # Apply rotation
                    if rot != 0:
                        particle_surf = pygame.transform.rotate(
                            particle_surf, math.degrees(rot)
                        )
                    
                    # Draw with additive blending
                    screen.blit(
                        particle_surf,
                        pos - np.array([surf_size // 2, surf_size // 2]),
                        special_flags=pygame.BLEND_RGBA_ADD
                    )
            else:
                # Standard alpha blending
                for pos, size, color, rot in zip(positions, sizes, colors, rotations):
                    if size < 1:
                        continue
                    
                    surf_size = int(size * 2)
                    if surf_size < 2:
                        surf_size = 2
                    
                    particle_surf = pygame.Surface(
                        (surf_size, surf_size), 
                        pygame.SRCALPHA
                    )
                    
                    color_255 = tuple(int(c * 255) for c in color)
                    
                    if emitter.shape == ParticleShape.CIRCLE:
                        pygame.draw.circle(
                            particle_surf,
                            color_255,
                            (surf_size // 2, surf_size // 2),
                            int(size)
                        )
                    else:
                        rect = pygame.Rect(0, 0, int(size), int(size))
                        rect.center = (surf_size // 2, surf_size // 2)
                        pygame.draw.rect(particle_surf, color_255, rect)
                    
                    if rot != 0:
                        particle_surf = pygame.transform.rotate(
                            particle_surf, math.degrees(rot)
                        )
                    
                    screen.blit(
                        particle_surf,
                        pos - np.array([surf_size // 2, surf_size // 2])
                    )
    
    def _draw_star(self, surface: pygame.Surface, color: np.ndarray, 
                   size: float, surf_size: int):
        """Draw star shape for particle"""
        points = []
        center = np.array([surf_size // 2, surf_size // 2])
        
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            radius = size if i % 2 == 0 else size * 0.4
            point = center + np.array([
                math.cos(angle) * radius,
                math.sin(angle) * radius
            ])
            points.append(tuple(point.astype(int)))
        
        color_255 = tuple(int(c * 255) for c in color)
        pygame.draw.polygon(surface, color_255, points)
    
    def clear(self):
        """Clear all particles"""
        self.data.active.fill(False)
        self.data.count = 0