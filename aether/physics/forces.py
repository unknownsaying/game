"""
Force Generators for Physics Simulation
Gravity, springs, buoyancy, drag, and more
"""

import numpy as np
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
import math

class ForceGenerator:
    """Base class for force generators"""
    
    def __init__(self):
        self.enabled = True
    
    def apply_force(self, body: 'RigidBody2D', dt: float):
        """Apply force to a rigid body"""
        pass

class GravityForce(ForceGenerator):
    """Gravity force generator"""
    
    def __init__(self, gravity: np.ndarray = None):
        super().__init__()
        self.gravity = gravity if gravity is not None else np.array([0.0, 9.81])
    
    def apply_force(self, body: 'RigidBody2D', dt: float):
        if not body.use_gravity or body.is_static:
            return
        
        force = self.gravity * body.mass
        body.add_force(force)

class SpringForce(ForceGenerator):
    """Spring force between two bodies or body and anchor"""
    
    def __init__(self, anchor: np.ndarray, spring_constant: float,
                 rest_length: float, damping: float = 0.0,
                 body_b: 'RigidBody2D' = None):
        super().__init__()
        self.anchor = np.array(anchor)
        self.spring_constant = spring_constant
        self.rest_length = rest_length
        self.damping = damping
        self.body_b = body_b
    
    def apply_force(self, body: 'RigidBody2D', dt: float):
        if body.is_static:
            return
        
        if self.body_b:
            # Spring between two bodies
            displacement = body.position - self.body_b.position
        else:
            # Spring to anchor point
            displacement = body.position - self.anchor
        
        distance = np.linalg.norm(displacement)
        
        if distance < 1e-6:
            return
        
        direction = displacement / distance
        
        # Hooke's law: F = -k * (x - rest_length)
        spring_force = -self.spring_constant * (distance - self.rest_length)
        
        # Damping: F_damp = -damping * velocity
        if self.body_b:
            rel_velocity = body.velocity - self.body_b.velocity
        else:
            rel_velocity = body.velocity
        
        damping_force = -self.damping * np.dot(rel_velocity, direction)
        
        total_force = (spring_force + damping_force) * direction
        body.add_force(total_force)
        
        if self.body_b and not self.body_b.is_static:
            self.body_b.add_force(-total_force)

class BuoyancyForce(ForceGenerator):
    """Buoyancy force for fluid simulation"""
    
    def __init__(self, fluid_height: float, fluid_density: float = 1.0,
                 fluid_drag: float = 0.5):
        super().__init__()
        self.fluid_height = fluid_height
        self.fluid_density = fluid_density
        self.fluid_drag = fluid_drag
    
    def apply_force(self, body: 'RigidBody2D', dt: float):
        if body.is_static:
            return
        
        # Simplified: object is a sphere
        if hasattr(body, 'radius'):
            radius = body.radius
            volume = math.pi * radius * radius
        else:
            return
        
        # Calculate submerged depth
        water_surface = self.fluid_height
        object_bottom = body.position[1] + radius
        
        if object_bottom <= water_surface:
            return  # Not submerged
        
        object_top = body.position[1] - radius
        submerged_depth = min(object_bottom - water_surface, 2 * radius)
        
        # Submerged fraction (0 to 1)
        submerged_fraction = submerged_depth / (2 * radius)
        submerged_fraction = max(0.0, min(1.0, submerged_fraction))
        
        # Buoyancy force
        buoyancy_force = np.array([0.0, -self.fluid_density * volume * 9.81 * submerged_fraction])
        body.add_force(buoyancy_force)
        
        # Drag force
        velocity_squared = np.linalg.norm(body.velocity) ** 2
        if velocity_squared > 0:
            drag_dir = -body.velocity / np.sqrt(velocity_squared)
            drag_force = drag_dir * self.fluid_drag * velocity_squared * submerged_fraction
            body.add_force(drag_force)

class DragForce(ForceGenerator):
    """Aerodynamic drag force"""
    
    def __init__(self, drag_coefficient: float = 0.47, 
                 fluid_density: float = 1.225,
                 cross_section_area: float = 1.0):
        super().__init__()
        self.drag_coefficient = drag_coefficient
        self.fluid_density = fluid_density
        self.cross_section_area = cross_section_area
    
    def apply_force(self, body: 'RigidBody2D', dt: float):
        if body.is_static:
            return
        
        velocity_magnitude = np.linalg.norm(body.velocity)
        if velocity_magnitude < 1e-6:
            return
        
        # Drag equation: F = 0.5 * rho * v^2 * Cd * A
        drag_magnitude = 0.5 * self.fluid_density * velocity_magnitude ** 2 * \
                        self.drag_coefficient * self.cross_section_area
        
        drag_direction = -body.velocity / velocity_magnitude
        drag_force = drag_direction * drag_magnitude
        
        body.add_force(drag_force)

class PointAttractionForce(ForceGenerator):
    """Attraction/repulsion to a point"""
    
    def __init__(self, point: np.ndarray, strength: float,
                 max_distance: float = float('inf'), falloff: float = 2.0):
        super().__init__()
        self.point = np.array(point)
        self.strength = strength
        self.max_distance = max_distance
        self.falloff = falloff
    
    def apply_force(self, body: 'RigidBody2D', dt: float):
        if body.is_static:
            return
        
        to_point = self.point - body.position
        distance = np.linalg.norm(to_point)
        
        if distance > self.max_distance or distance < 0.01:
            return
        
        direction = to_point / distance
        
        # Force with distance falloff
        force_magnitude = self.strength * body.mass / (distance ** self.falloff)
        force = direction * force_magnitude
        
        body.add_force(force)

class BungeeForce(ForceGenerator):
    """Bungee cord force (spring only when extended)"""
    
    def __init__(self, anchor: np.ndarray, spring_constant: float,
                 rest_length: float):
        super().__init__()
        self.spring = SpringForce(anchor, spring_constant, rest_length)
    
    def apply_force(self, body: 'RigidBody2D', dt: float):
        displacement = body.position - self.spring.anchor
        distance = np.linalg.norm(displacement)
        
        # Only apply force when extended
        if distance > self.spring.rest_length:
            self.spring.apply_force(body, dt)

class ForceField:
    """Spatial force field affecting multiple bodies"""
    
    def __init__(self, center: np.ndarray, radius: float, strength: float,
                 field_type: str = "radial"):
        self.center = np.array(center)
        self.radius = radius
        self.strength = strength
        self.field_type = field_type
        self.enabled = True
    
    def get_force_at(self, position: np.ndarray, body: 'RigidBody2D' = None) -> np.ndarray:
        """Get force vector at a position"""
        to_center = self.center - position
        distance = np.linalg.norm(to_center)
        
        if distance > self.radius or distance < 0.001:
            return np.zeros(2)
        
        direction = to_center / distance
        influence = 1.0 - (distance / self.radius)  # Linear falloff
        
        if self.field_type == "radial":
            return direction * self.strength * influence
        elif self.field_type == "vortex":
            perpendicular = np.array([-direction[1], direction[0]])
            return perpendicular * self.strength * influence
        elif self.field_type == "turbulent":
            noise = np.random.randn(2)
            noise = noise / (np.linalg.norm(noise) + 0.001)
            return noise * self.strength * influence
        
        return np.zeros(2)
    
    def apply_force(self, body: 'RigidBody2D', dt: float):
        if self.enabled and not body.is_static:
            force = self.get_force_at(body.position, body)
            body.add_force(force * body.mass)