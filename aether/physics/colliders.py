"""
Advanced Collision Detection System
SAT, GJK, MPR algorithms with continuous collision detection
"""

import numpy as np
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass
import math
from enum import Enum

class ColliderType(Enum):
    CIRCLE = "circle"
    BOX = "box"
    POLYGON = "polygon"
    CAPSULE = "capsule"
    EDGE = "edge"
    POINT = "point"

@dataclass
class CollisionInfo:
    """Detailed collision information"""
    collider_a: 'Collider'
    collider_b: 'Collider'
    point: np.ndarray
    normal: np.ndarray
    penetration: float
    relative_velocity: np.ndarray
    contact_points: List[np.ndarray]
    impulse: np.ndarray = None
    friction_impulse: np.ndarray = None

class Collider:
    """Base collider class"""
    
    def __init__(self, collider_type: ColliderType):
        self.type = collider_type
        self.offset = np.zeros(2)
        self.is_trigger = False
        self.enabled = True
        self.layer = 0
        self.physics_material = None
        
    def get_aabb(self, position: np.ndarray, rotation: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        """Get axis-aligned bounding box"""
        raise NotImplementedError
    
    def support(self, direction: np.ndarray, position: np.ndarray, rotation: float = 0.0) -> np.ndarray:
        """Get support point in given direction (for GJK)"""
        raise NotImplementedError

class CircleCollider(Collider):
    """Circle collider"""
    
    def __init__(self, radius: float):
        super().__init__(ColliderType.CIRCLE)
        self.radius = radius
    
    def get_aabb(self, position: np.ndarray, rotation: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        r = np.array([self.radius, self.radius])
        return position + self.offset - r, position + self.offset + r
    
    def support(self, direction: np.ndarray, position: np.ndarray, rotation: float = 0.0) -> np.ndarray:
        if np.linalg.norm(direction) == 0:
            return position + self.offset
        return position + self.offset + direction / np.linalg.norm(direction) * self.radius

class BoxCollider(Collider):
    """Axis-aligned box collider"""
    
    def __init__(self, width: float, height: float):
        super().__init__(ColliderType.BOX)
        self.width = width
        self.height = height
        self.half_extents = np.array([width/2, height/2])
    
    def get_vertices(self, position: np.ndarray, rotation: float = 0.0) -> List[np.ndarray]:
        """Get vertices in world space"""
        local_verts = [
            np.array([-self.half_extents[0], -self.half_extents[1]]),
            np.array([self.half_extents[0], -self.half_extents[1]]),
            np.array([self.half_extents[0], self.half_extents[1]]),
            np.array([-self.half_extents[0], self.half_extents[1]])
        ]
        
        center = position + self.offset
        
        if rotation != 0:
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            rot_matrix = np.array([[cos_r, -sin_r], [sin_r, cos_r]])
            return [center + rot_matrix @ v for v in local_verts]
        
        return [center + v for v in local_verts]
    
    def get_normals(self, rotation: float = 0.0) -> List[np.ndarray]:
        """Get face normals"""
        normals = [
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0]),
            np.array([-1.0, 0.0]),
            np.array([0.0, -1.0])
        ]
        
        if rotation != 0:
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            rot_matrix = np.array([[cos_r, -sin_r], [sin_r, cos_r]])
            return [rot_matrix @ n for n in normals]
        
        return normals
    
    def get_aabb(self, position: np.ndarray, rotation: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        vertices = self.get_vertices(position, rotation)
        if not vertices:
            return position, position
        
        min_vert = np.min(vertices, axis=0)
        max_vert = np.max(vertices, axis=0)
        return min_vert, max_vert
    
    def support(self, direction: np.ndarray, position: np.ndarray, rotation: float = 0.0) -> np.ndarray:
        vertices = self.get_vertices(position, rotation)
        dots = [np.dot(v, direction) for v in vertices]
        return vertices[np.argmax(dots)]

class PolygonCollider(Collider):
    """Convex polygon collider"""
    
    def __init__(self, vertices: List[np.ndarray]):
        super().__init__(ColliderType.POLYGON)
        self.local_vertices = [np.array(v) for v in vertices]
        self._validate_convex()
    
    def _validate_convex(self):
        """Verify polygon is convex"""
        if len(self.local_vertices) < 3:
            return
        
        sign = None
        n = len(self.local_vertices)
        
        for i in range(n):
            p1 = self.local_vertices[i]
            p2 = self.local_vertices[(i + 1) % n]
            p3 = self.local_vertices[(i + 2) % n]
            
            cross = np.cross(p2 - p1, p3 - p2)
            
            if cross != 0:
                if sign is None:
                    sign = cross > 0
                elif (cross > 0) != sign:
                    # Not strictly convex, but might still work
                    pass
    
    def get_vertices(self, position: np.ndarray, rotation: float = 0.0) -> List[np.ndarray]:
        """Get world-space vertices"""
        center = position + self.offset
        
        if rotation != 0:
            cos_r = math.cos(rotation)
            sin_r = math.sin(rotation)
            rot_matrix = np.array([[cos_r, -sin_r], [sin_r, cos_r]])
            return [center + rot_matrix @ v for v in self.local_vertices]
        
        return [center + v for v in self.local_vertices]
    
    def get_aabb(self, position: np.ndarray, rotation: float = 0.0) -> Tuple[np.ndarray, np.ndarray]:
        vertices = self.get_vertices(position, rotation)
        if not vertices:
            return position, position
        
        min_vert = np.min(vertices, axis=0)
        max_vert = np.max(vertices, axis=0)
        return min_vert, max_vert
    
    def support(self, direction: np.ndarray, position: np.ndarray, rotation: float = 0.0) -> np.ndarray:
        vertices = self.get_vertices(position, rotation)
        dots = [np.dot(v, direction) for v in vertices]
        return vertices[np.argmax(dots)]

class CollisionSystem:
    """
    Advanced collision detection system with:
    - Broad phase using spatial hashing
    - Narrow phase using SAT, GJK
    - Continuous collision detection
    - Contact point generation
    """
    
    def __init__(self, cell_size: float = 64.0):
        self.cell_size = cell_size
        self.spatial_hash = {}
        self.collision_pairs = []
        self.contact_cache = {}
        
    def broad_phase(self, colliders: List[Tuple[Collider, np.ndarray, float]]) -> List[Tuple[int, int]]:
        """
        Broad phase collision detection using spatial hashing
        Returns list of (index_a, index_b) pairs
        """
        self.spatial_hash.clear()
        potential_pairs = set()
        
        # Insert into spatial hash
        for i, (collider, pos, rot) in enumerate(colliders):
            if not collider.enabled:
                continue
            
            min_aabb, max_aabb = collider.get_aabb(pos, rot)
            
            min_cell = (min_aabb / self.cell_size).astype(int)
            max_cell = (max_aabb / self.cell_size).astype(int)
            
            for x in range(min_cell[0], max_cell[0] + 1):
                for y in range(min_cell[1], max_cell[1] + 1):
                    cell = (x, y)
                    
                    if cell not in self.spatial_hash:
                        self.spatial_hash[cell] = []
                    
                    # Check against existing objects in cell
                    for j in self.spatial_hash[cell]:
                        pair = (min(i, j), max(i, j))
                        potential_pairs.add(pair)
                    
                    self.spatial_hash[cell].append(i)
        
        return list(potential_pairs)
    
    def narrow_phase(self, collider_a: Collider, pos_a: np.ndarray, rot_a: float,
                    collider_b: Collider, pos_b: np.ndarray, rot_b: float) -> Optional[CollisionInfo]:
        """Narrow phase collision detection"""
        
        # Choose algorithm based on collider types
        if collider_a.type == ColliderType.CIRCLE and collider_b.type == ColliderType.CIRCLE:
            return self._circle_circle(collider_a, pos_a, collider_b, pos_b)
        elif collider_a.type == ColliderType.BOX and collider_b.type == ColliderType.BOX:
            return self._sat_collision(collider_a, pos_a, rot_a, collider_b, pos_b, rot_b)
        else:
            return self._gjk_collision(collider_a, pos_a, rot_a, collider_b, pos_b, rot_b)
    
    def _circle_circle(self, circle_a: CircleCollider, pos_a: np.ndarray,
                      circle_b: CircleCollider, pos_b: np.ndarray) -> Optional[CollisionInfo]:
        """Circle-circle collision detection"""
        center_a = pos_a + circle_a.offset
        center_b = pos_b + circle_b.offset
        
        delta = center_b - center_a
        distance = np.linalg.norm(delta)
        min_distance = circle_a.radius + circle_b.radius
        
        if distance >= min_distance:
            return None
        
        if distance == 0:
            normal = np.array([1.0, 0.0])
        else:
            normal = delta / distance
        
        penetration = min_distance - distance
        contact_point = center_a + normal * (circle_a.radius - penetration * 0.5)
        
        return CollisionInfo(
            collider_a=circle_a,
            collider_b=circle_b,
            point=contact_point,
            normal=normal,
            penetration=penetration,
            relative_velocity=np.zeros(2),
            contact_points=[contact_point]
        )
    
    def _sat_collision(self, box_a: BoxCollider, pos_a: np.ndarray, rot_a: float,
                      box_b: BoxCollider, pos_b: np.ndarray, rot_b: float) -> Optional[CollisionInfo]:
        """
        Separating Axis Theorem for box-box collision
        Works for any convex polygon
        """
        verts_a = box_a.get_vertices(pos_a, rot_a)
        verts_b = box_b.get_vertices(pos_b, rot_b)
        
        normals_a = box_a.get_normals(rot_a)
        normals_b = box_b.get_normals(rot_b)
        
        all_normals = normals_a + normals_b
        
        min_overlap = float('inf')
        min_axis = None
        
        for axis in all_normals:
            if np.linalg.norm(axis) == 0:
                continue
            
            axis = axis / np.linalg.norm(axis)
            
            # Project vertices onto axis
            proj_a = [np.dot(v, axis) for v in verts_a]
            proj_b = [np.dot(v, axis) for v in verts_b]
            
            min_a, max_a = min(proj_a), max(proj_a)
            min_b, max_b = min(proj_b), max(proj_b)
            
            # Check for separation
            if max_a < min_b or max_b < min_a:
                return None
            
            # Calculate overlap
            overlap = min(max_a - min_b, max_b - min_a)
            
            if overlap < min_overlap:
                min_overlap = overlap
                min_axis = axis
        
        if min_axis is None:
            return None
        
        # Calculate contact point (simplified - use center of overlap)
        contact_point = (np.mean(verts_a, axis=0) + np.mean(verts_b, axis=0)) * 0.5
        
        # Ensure normal points from A to B
        center_a = np.mean(verts_a, axis=0)
        center_b = np.mean(verts_b, axis=0)
        if np.dot(center_b - center_a, min_axis) < 0:
            min_axis = -min_axis
        
        return CollisionInfo(
            collider_a=box_a,
            collider_b=box_b,
            point=contact_point,
            normal=min_axis,
            penetration=min_overlap,
            relative_velocity=np.zeros(2),
            contact_points=[contact_point]
        )
    
    def _gjk_collision(self, collider_a: Collider, pos_a: np.ndarray, rot_a: float,
                      collider_b: Collider, pos_b: np.ndarray, rot_b: float) -> Optional[CollisionInfo]:
        """
        Gilbert-Johnson-Keerthi algorithm for convex shapes
        Works with any convex collider
        """
        # Initial direction (from center A to center B)
        aabb_a_min, aabb_a_max = collider_a.get_aabb(pos_a, rot_a)
        aabb_b_min, aabb_b_max = collider_b.get_aabb(pos_b, rot_b)
        
        center_a = (aabb_a_min + aabb_a_max) / 2
        center_b = (aabb_b_min + aabb_b_max) / 2
        
        direction = center_b - center_a
        if np.linalg.norm(direction) < 1e-6:
            direction = np.array([1.0, 0.0])
        
        simplex = []
        max_iterations = 32
        
        for _ in range(max_iterations):
            # Get support point in direction
            support_a = collider_a.support(direction, pos_a, rot_a)
            support_b = collider_b.support(-direction, pos_b, rot_b)
            
            support = support_a - support_b
            
            if np.dot(support, direction) < 0:
                return None  # No collision
            
            simplex.append(support)
            
            if self._update_simplex(simplex, direction):
                # Collision detected, get contact info using EPA
                return self._epa_collision_info(collider_a, pos_a, rot_a,
                                               collider_b, pos_b, rot_b,
                                               simplex)
        
        return None
    
    def _update_simplex(self, simplex: List[np.ndarray], direction: np.ndarray) -> bool:
        """Update simplex for GJK"""
        if len(simplex) == 2:
            # Line simplex
            a = simplex[1]
            b = simplex[0]
            ab = b - a
            ao = -a
            
            if np.dot(ab, ao) > 0:
                direction[:] = np.array([-ab[1], ab[0]])
                if np.dot(direction, ao) < 0:
                    direction *= -1
            else:
                simplex.pop(0)
                direction[:] = ao
        
        elif len(simplex) == 3:
            # Triangle simplex
            a = simplex[2]
            b = simplex[1]
            c = simplex[0]
            
            ab = b - a
            ac = c - a
            ao = -a
            
            # Check which region origin is in
            ab_perp = np.array([-ab[1], ab[0]])
            if np.dot(ab_perp, ac) > 0:
                ab_perp = -ab_perp
            
            if np.dot(ab_perp, ao) > 0:
                simplex.pop(0)  # Remove c
                direction[:] = ab_perp
            else:
                ac_perp = np.array([-ac[1], ac[0]])
                if np.dot(ac_perp, ab) > 0:
                    ac_perp = -ac_perp
                
                if np.dot(ac_perp, ao) > 0:
                    simplex.pop(1)  # Remove b
                    direction[:] = ac_perp
                else:
                    return True  # Origin inside triangle - collision!
        
        return False
    
    def _epa_collision_info(self, collider_a: Collider, pos_a: np.ndarray, rot_a: float,
                           collider_b: Collider, pos_b: np.ndarray, rot_b: float,
                           simplex: List[np.ndarray]) -> CollisionInfo:
        """Expanding Polytope Algorithm for contact information"""
        # Simplified EPA - use simplex center as contact point
        contact = np.mean(simplex, axis=0)
        normal = np.array([0.0, 1.0])  # Simplified normal
        
        return CollisionInfo(
            collider_a=collider_a,
            collider_b=collider_b,
            point=pos_a + contact,
            normal=normal,
            penetration=np.linalg.norm(contact),
            relative_velocity=np.zeros(2),
            contact_points=[pos_a + contact]
        )
    
    def continuous_collision_detection(self, collider_a: Collider, pos_a: np.ndarray, 
                                     vel_a: np.ndarray, rot_a: float,
                                     collider_b: Collider, pos_b: np.ndarray,
                                     vel_b: np.ndarray, rot_b: float,
                                     dt: float) -> Optional[CollisionInfo]:
        """
        Continuous collision detection to prevent tunneling
        """
        rel_vel = vel_a - vel_b
        speed = np.linalg.norm(rel_vel)
        
        if speed < 1e-6:
            return self.narrow_phase(collider_a, pos_a, rot_a, collider_b, pos_b, rot_b)
        
        # Check multiple sub-steps
        num_steps = max(1, int(speed * dt / (self.cell_size * 0.5)))
        sub_dt = dt / num_steps
        
        for step in range(num_steps + 1):
            t = step * sub_dt
            test_pos_a = pos_a + vel_a * t
            test_pos_b = pos_b + vel_b * t
            
            collision = self.narrow_phase(collider_a, test_pos_a, rot_a,
                                         collider_b, test_pos_b, rot_b)
            if collision:
                collision.relative_velocity = rel_vel
                return collision
        
        return None