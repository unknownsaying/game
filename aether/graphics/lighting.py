"""
2D Dynamic Lighting System with Normal Maps and Shadow Casting
"""

import pygame
import numpy as np
from typing import List, Tuple, Optional
import math
from dataclasses import dataclass
from enum import Enum

class LightType(Enum):
    """Types of light sources"""
    POINT = "point"
    SPOT = "spot"
    DIRECTIONAL = "directional"
    AREA = "area"

@dataclass
class LightMaterial:
    """Material properties for light interaction"""
    ambient: float = 0.1
    diffuse: float = 0.7
    specular: float = 0.3
    shininess: float = 32.0
    normal_map: Optional[pygame.Surface] = None

class Light:
    """Dynamic light source"""
    
    def __init__(self, position: np.ndarray, color: Tuple[int, int, int],
                 intensity: float = 1.0, light_type: LightType = LightType.POINT):
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32) / 255.0
        self.intensity = intensity
        self.type = light_type
        
        # Point light properties
        self.radius = 300.0
        self.falloff = 2.0  # 1 = linear, 2 = quadratic
        
        # Spot light properties
        self.direction = np.array([1.0, 0.0])
        self.cone_angle = math.radians(30)
        self.cone_feather = math.radians(10)
        
        # Animation
        self.flicker = False
        self.flicker_speed = 5.0
        self.flicker_amount = 0.2
        self.flicker_offset = random.uniform(0, 2 * math.pi)
        
        # Shadow casting
        self.cast_shadows = True
        self.shadow_resolution = 512  # For shadow maps
        
        # Visibility
        self.visible = True
        self.enabled = True
        
    def get_intensity_at(self, point: np.ndarray, 
                         normal: np.ndarray = None) -> Tuple[np.ndarray, float]:
        """Calculate light intensity and color at a point"""
        if not self.enabled:
            return np.zeros(3), 0.0
        
        to_light = self.position - point
        distance = np.linalg.norm(to_light)
        
        if self.type == LightType.POINT:
            return self._point_light_intensity(to_light, distance, normal)
        elif self.type == LightType.SPOT:
            return self._spot_light_intensity(to_light, distance, normal)
        elif self.type == LightType.DIRECTIONAL:
            return self._directional_light_intensity(normal)
        
        return np.zeros(3), 0.0
    
    def _point_light_intensity(self, to_light: np.ndarray, 
                               distance: float, normal: np.ndarray = None):
        """Calculate point light intensity"""
        if distance > self.radius:
            return np.zeros(3), 0.0
        
        # Distance falloff (inverse square)
        attenuation = 1.0 / (1.0 + distance / self.radius) ** self.falloff
        
        # Normal contribution
        if normal is not None:
            light_dir = to_light / max(distance, 0.001)
            n_dot_l = max(0, np.dot(normal, light_dir))
            attenuation *= n_dot_l
        
        # Flicker
        if self.flicker:
            flicker = 1.0 + self.flicker_amount * math.sin(
                pygame.time.get_ticks() * 0.001 * self.flicker_speed + self.flicker_offset
            )
            attenuation *= flicker
        
        intensity = attenuation * self.intensity
        color = self.color * intensity
        
        return color, intensity
    
    def _spot_light_intensity(self, to_light: np.ndarray, 
                             distance: float, normal: np.ndarray = None):
        """Calculate spot light intensity"""
        point_intensity, point_color = self._point_light_intensity(
            to_light, distance, normal
        )
        
        if point_intensity == 0:
            return np.zeros(3), 0.0
        
        # Spot cone
        light_dir = to_light / max(distance, 0.001)
        spot_dot = np.dot(-light_dir, self.direction)
        
        outer_cone = math.cos(self.cone_angle)
        inner_cone = math.cos(self.cone_angle - self.cone_feather)
        
        # Smooth transition between inner and outer cone
        spot_factor = np.clip(
            (spot_dot - outer_cone) / (inner_cone - outer_cone),
            0, 1
        )
        
        return point_color * spot_factor, point_intensity * spot_factor
    
    def _directional_light_intensity(self, normal: np.ndarray = None):
        """Calculate directional light intensity"""
        if normal is not None:
            n_dot_l = max(0, np.dot(normal, -self.direction))
            intensity = n_dot_l * self.intensity
        else:
            intensity = self.intensity
        
        return self.color * intensity, intensity

class ShadowCaster:
    """Generates and manages shadow maps"""
    
    def __init__(self, resolution: Tuple[int, int] = (1024, 1024)):
        self.resolution = resolution
        self.shadow_map = pygame.Surface(resolution, pygame.SRCALPHA)
        self.occluders = []  # List of (position, radius) for shadow casting
        
    def add_occluder(self, position: np.ndarray, radius: float):
        """Add shadow casting object"""
        self.occluders.append((position, radius))
    
    def clear_occluders(self):
        """Clear all occluders"""
        self.occluders.clear()
    
    def calculate_shadows(self, light: Light, target_surface: pygame.Surface):
        """Calculate shadows for a light source (simplified 2D shadow mapping)"""
        if not light.cast_shadows or not self.occluders:
            return
        
        # Create shadow surface
        shadow_surf = pygame.Surface(target_surface.get_size(), pygame.SRCALPHA)
        
        for occluder_pos, occluder_radius in self.occluders:
            # Calculate shadow projection
            to_occluder = occluder_pos - light.position
            occluder_distance = np.linalg.norm(to_occluder)
            
            if occluder_distance == 0:
                continue
            
            # Shadow direction
            shadow_dir = to_occluder / occluder_distance
            
            # Calculate shadow end point
            shadow_length = min(occluder_distance * 2, light.radius)
            shadow_end = occluder_pos + shadow_dir * shadow_length
            
            # Calculate shadow width based on occluder size and distance
            shadow_width = occluder_radius * (1 + shadow_length / max(occluder_distance, 0.1))
            
            # Draw shadow polygon
            perpendicular = np.array([-shadow_dir[1], shadow_dir[0]])
            
            p1 = occluder_pos + perpendicular * shadow_width
            p2 = occluder_pos - perpendicular * shadow_width
            p3 = shadow_end - perpendicular * shadow_width * 2
            p4 = shadow_end + perpendicular * shadow_width * 2
            
            # Draw shadow with gradient
            points = [
                tuple(p1.astype(int)),
                tuple(p2.astype(int)),
                tuple(p3.astype(int)),
                tuple(p4.astype(int))
            ]
            
            # Create shadow gradient
            shadow_gradient = pygame.Surface(
                (shadow_length * 2, shadow_width * 4), 
                pygame.SRCALPHA
            )
            
            for i in range(int(shadow_length * 2)):
                alpha = int(180 * (1 - i / (shadow_length * 2)))
                if alpha > 0:
                    pygame.draw.line(
                        shadow_gradient,
                        (0, 0, 0, alpha),
                        (i, 0),
                        (i, shadow_width * 4)
                    )
            
            shadow_surf.blit(shadow_gradient, (0, 0),
                           special_flags=pygame.BLEND_RGBA_MULT)
        
        # Apply shadow to target
        target_surface.blit(shadow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

class LightSystem:
    """
    Manages dynamic 2D lighting
    """
    
    def __init__(self, engine):
        self.engine = engine
        self.lights: List[Light] = []
        self.shadow_caster = ShadowCaster()
        self.ambient_color = np.array([0.1, 0.1, 0.15])  # Dark blue ambient
        self.ambient_intensity = 0.2
        
        # Light rendering surface
        self.light_surface = None
        self.normal_surface = None
        
    def add_light(self, light: Light):
        """Add light source"""
        self.lights.append(light)
    
    def remove_light(self, light: Light):
        """Remove light source"""
        if light in self.lights:
            self.lights.remove(light)
    
    def clear_lights(self):
        """Remove all lights"""
        self.lights.clear()
    
    def render(self, screen: pygame.Surface, 
              normal_map: Optional[pygame.Surface] = None):
        """Render all lights onto the screen"""
        width, height = screen.get_size()
        
        # Create light accumulation surface
        if self.light_surface is None or self.light_surface.get_size() != (width, height):
            self.light_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        self.light_surface.fill((0, 0, 0, 0))
        
        # Ambient light
        ambient = (int(self.ambient_color[0] * 255 * self.ambient_intensity),
                  int(self.ambient_color[1] * 255 * self.ambient_intensity),
                  int(self.ambient_color[2] * 255 * self.ambient_intensity))
        self.light_surface.fill(ambient)
        
        # Render each light
        for light in self.lights:
            if not light.visible or not light.enabled:
                continue
            
            self._render_single_light(light, normal_map)
        
        # Apply light surface to screen using multiply blending
        screen.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    
    def _render_single_light(self, light: Light, 
                            normal_map: Optional[pygame.Surface]):
        """Render a single light source"""
        # Create light texture
        light_size = int(light.radius * 2)
        if light_size <= 0:
            return
        
        light_surf = pygame.Surface((light_size, light_size), pygame.SRCALPHA)
        
        center = np.array([light_size // 2, light_size // 2])
        
        # Render light gradient
        for y in range(light_size):
            for x in range(light_size):
                point = np.array([x, y])
                world_point = point + light.position - center
                
                # Get normal from normal map if available
                normal = None
                if normal_map and 0 <= x < normal_map.get_width() and 0 <= y < normal_map.get_height():
                    normal_color = normal_map.get_at((int(world_point[0]), int(world_point[1])))
                    normal = np.array([
                        normal_color[0] / 255.0 * 2 - 1,
                        normal_color[1] / 255.0 * 2 - 1,
                        normal_color[2] / 255.0
                    ])
                
                color, intensity = light.get_intensity_at(world_point, normal)
                
                if intensity > 0:
                    alpha = min(255, int(intensity * 255))
                    final_color = (
                        min(255, int(color[0] * 255)),
                        min(255, int(color[1] * 255)),
                        min(255, int(color[2] * 255)),
                        alpha
                    )
                    if alpha > 0:
                        light_surf.set_at((x, y), final_color)
        
        # Apply shadows
        if light.cast_shadows:
            self.shadow_caster.calculate_shadows(light, light_surf)
        
        # Blend light onto accumulation surface
        self.light_surface.blit(
            light_surf,
            (light.position[0] - center[0], light.position[1] - center[1]),
            special_flags=pygame.BLEND_RGBA_ADD
        )