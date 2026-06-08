"""
Physics simulation system with collision detection
"""

import numpy as np
from typing import List, Tuple, Optional
import pygame

class PhysicsWorld:
    """Physics simulation world"""
    
    def __init__(self, scale: float = 100.0):
        self.gravity = np.array([0.0, 9.81])
        self.scale = scale  # pixels per meter
        self.bodies: List[PhysicsBody] = []
        self.collision_pairs = []
        self.constraints = []
        
    def update(self, dt: float):
        """Step physics simulation"""
        # Sub-stepping for stability
        sub_steps = 4
        sub_dt = dt / sub_steps
        
        for _ in range(sub_steps):
            self._step(sub_dt)
    
    def _step(self, dt: float):
        """Single physics step"""
        # Update velocities (gravity, forces)
        for body in self.bodies:
            if not body.is_static:
                body.velocity += self.gravity * dt
                body.velocity += body.accumulated_forces / body.mass * dt
                body.angular_velocity += body.accumulated_torque / body.inertia * dt
                
                # Damping
                body.velocity *= (1 - body.linear_damping * dt)
                body.angular_velocity *= (1 - body.angular_damping * dt)
                
                # Clear forces
                body.accumulated_forces.fill(0)
                body.accumulated_torque = 0
        
        # Update positions
        for body in self.bodies:
            if not body.is_static:
                body.position += body.velocity * dt
                body.rotation += body.angular_velocity * dt
        
        # Detect and resolve collisions
        self._detect_collisions()
        self._resolve_collisions()
    
    def _detect_collisions(self):
        """Broad phase collision detection"""
        self.collision_pairs.clear()
        
        # Simple N^2 check, optimize with spatial hash later
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                body_a = self.bodies[i]
                body_b = self.bodies[j]
                
                if not body_a.active or not body_b.active:
                    continue
                    
                if body_a.is_static and body_b.is_static:
                    continue
                
                if self._aabb_overlap(body_a.get_aabb(), body_b.get_aabb()):
                    contact = self._detect_contact(body_a, body_b)
                    if contact:
                        self.collision_pairs.append((body_a, body_b, contact))
    
    def _aabb_overlap(self, aabb_a, aabb_b) -> bool:
        """Check AABB overlap"""
        min_a, max_a = aabb_a
        min_b, max_b = aabb_b
        
        return (min_a[0] <= max_b[0] and max_a[0] >= min_b[0] and
                min_a[1] <= max_b[1] and max_a[1] >= min_b[1])
    
    def _detect_contact(self, body_a: 'PhysicsBody', 
                        body_b: 'PhysicsBody') -> Optional[dict]:
        """Detailed collision detection"""
        # Circle-circle collision
        if body_a.shape == 'circle' and body_b.shape == 'circle':
            direction = body_b.position - body_a.position
            distance = np.linalg.norm(direction)
            min_distance = body_a.radius + body_b.radius
            
            if distance < min_distance:
                if distance == 0:
                    direction = np.array([1.0, 0.0])
                    distance = 0.01
                    
                normal = direction / distance
                penetration = min_distance - distance
                
                return {
                    'normal': normal,
                    'penetration': penetration,
                    'point': body_a.position + normal * body_a.radius
                }
        
        # Add more shape types here (box, polygon, etc.)
        
        return None
    
    def _resolve_collisions(self):
        """Resolve detected collisions"""
        for body_a, body_b, contact in self.collision_pairs:
            self._resolve_contact(body_a, body_b, contact)
    
    def _resolve_contact(self, body_a: 'PhysicsBody', 
                        body_b: 'PhysicsBody', contact: dict):
        """Resolve collision between two bodies"""
        normal = contact['normal']
        penetration = contact['penetration']
        
        # Calculate relative velocity
        relative_velocity = body_b.velocity - body_a.velocity
        velocity_along_normal = np.dot(relative_velocity, normal)
        
        # Don't resolve if objects are separating
        if velocity_along_normal > 0:
            return
        
        # Calculate restitution
        e = min(body_a.restitution, body_b.restitution)
        
        # Calculate impulse scalar
        j = -(1 + e) * velocity_along_normal
        j /= 1/body_a.mass + 1/body_b.mass
        
        # Apply impulse
        impulse = j * normal
        
        if not body_a.is_static:
            body_a.velocity -= impulse / body_a.mass
            
        if not body_b.is_static:
            body_b.velocity += impulse / body_b.mass
        
        # Position correction (separate bodies)
        correction = max(penetration - 0.01, 0.0) / (1/body_a.mass + 1/body_b.mass)
        correction *= 0.2  # Penetration slop
        
        if not body_a.is_static:
            body_a.position -= correction * normal / body_a.mass
            
        if not body_b.is_static:
            body_b.position += correction * normal / body_b.mass
    
    def add_body(self, body: 'PhysicsBody'):
        """Add physics body to world"""
        self.bodies.append(body)
    
    def remove_body(self, body: 'PhysicsBody'):
        """Remove physics body from world"""
        if body in self.bodies:
            self.bodies.remove(body)
    
    def render_debug(self, screen: pygame.Surface, camera):
        """Render physics debug visualization"""
        for body in self.bodies:
            if not body.active:
                continue
                
            pos = body.position - camera.offset
            
            if body.shape == 'circle':
                color = (0, 255, 0) if body.is_static else (255, 0, 0)
                pygame.draw.circle(screen, color, pos.astype(int), 
                                 int(body.radius), 1)
            elif body.shape == 'box':
                color = (0, 255, 0) if body.is_static else (255, 0, 0)
                rect = pygame.Rect(
                    pos[0] - body.width/2, pos[1] - body.height/2,
                    body.width, body.height
                )
                pygame.draw.rect(screen, color, rect, 1)

class PhysicsBody:
    """Physics body for simulation"""
    
    def __init__(self, position, mass=1.0, shape='circle', **kwargs):
        self.position = np.array(position, dtype=float)
        self.velocity = np.array([0.0, 0.0])
        self.rotation = 0.0
        self.angular_velocity = 0.0
        
        self.mass = mass
        self.inertia = mass  # Simplified for 2D
        
        self.shape = shape
        self.radius = kwargs.get('radius', 10)
        self.width = kwargs.get('width', 20)
        self.height = kwargs.get('height', 20)
        
        self.is_static = mass <= 0
        self.active = True
        self.restitution = 0.3
        self.friction = 0.5
        self.linear_damping = 0.01
        self.angular_damping = 0.01
        
        self.accumulated_forces = np.array([0.0, 0.0])
        self.accumulated_torque = 0.0
    
    def get_aabb(self):
        """Get axis-aligned bounding box"""
        if self.shape == 'circle':
            return (self.position - self.radius, 
                    self.position + self.radius)
        elif self.shape == 'box':
            half = np.array([self.width/2, self.height/2])
            return (self.position - half, self.position + half)
    
    def add_force(self, force: np.ndarray):
        """Add force to body"""
        self.accumulated_forces += force
    
    def add_torque(self, torque: float):
        """Add torque to body"""
        self.accumulated_torque += torque
    
    def add_impulse(self, impulse: np.ndarray, point=None):
        """Apply impulse at a point"""
        self.velocity += impulse / self.mass
        
        if point is not None:
            r = point - self.position
            self.angular_velocity += np.cross(r, impulse) / self.inertia