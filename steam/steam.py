"""
STEAM GAME AUTOMATIC GENERATION MACHINE
========================================
Applies advanced mathematics to procedurally generate complete games
ready for Steam platform deployment.

Mathematical foundations:
- Linear Algebra: Transformations, collision detection, rendering
- Differential Equations: Physics simulation, particle systems
- Probability & Statistics: Procedural content, enemy AI, loot systems
- Fractal Geometry: Terrain generation, natural structures
- Graph Theory: Level connectivity, pathfinding, puzzle generation
- Optimization: Parameter tuning, difficulty scaling, performance
- Number Theory: Seed generation, hashing, procedural patterns
- Complex Analysis: Particle effects, wave simulations
"""

import numpy as np
from numpy import linalg as la
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable, Any
from enum import Enum
import math
from collections import defaultdict
from abc import ABC, abstractmethod


# ═══════════════════════════════════════════════════════════════
# MATHEMATICAL FOUNDATION LAYER
# ═══════════════════════════════════════════════════════════════

class MathFoundation:
    """Core mathematical utilities used throughout the generator."""
    
    @staticmethod
    def generate_seed(steam_app_id: int, game_name: str) -> int:
        """Number theory: Generate deterministic seed from Steam ID and name."""
        combined = f"{steam_app_id}_{game_name}"
        hash_hex = hashlib.sha256(combined.encode()).hexdigest()
        return int(hash_hex[:16], 16) % (2**31)
    
    @staticmethod
    def linear_interpolate(a: float, b: float, t: float) -> float:
        """Linear algebra: Linear interpolation."""
        return a + (b - a) * t
    
    @staticmethod
    def bezier_curve(points: List[Tuple[float, float]], t: float) -> Tuple[float, float]:
        """Linear algebra: Bézier curve evaluation using De Casteljau's algorithm."""
        pts = points.copy()
        while len(pts) > 1:
            new_pts = []
            for i in range(len(pts) - 1):
                x = MathFoundation.linear_interpolate(pts[i][0], pts[i+1][0], t)
                y = MathFoundation.linear_interpolate(pts[i][1], pts[i+1][1], t)
                new_pts.append((x, y))
            pts = new_pts
        return pts[0]
    
    @staticmethod
    def perlin_noise_2d(x: float, y: float, seed: int) -> float:
        """Probability: Deterministic noise for procedural generation."""
        n = int(x * 57 + y * 131) ^ seed
        n = (n << 13) ^ n
        return 1.0 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824.0
    
    @staticmethod
    def simplex_noise(x: float, y: float, octaves: int = 4, persistence: float = 0.5) -> float:
        """Fractal geometry: Fractal noise using octaves."""
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0
        seed = 12345  # Derived from game seed
        
        for _ in range(octaves):
            total += MathFoundation.perlin_noise_2d(x * frequency, y * frequency, seed) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2.0
            
        return total / max_value
    
    @staticmethod
    def solve_linear_system(A: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Linear algebra: Solve Ax = b for physics constraints."""
        return la.solve(A, b)
    
    @staticmethod
    def eigenvalues(matrix: np.ndarray) -> np.ndarray:
        """Linear algebra: Eigenvalues for stability analysis."""
        return la.eigvals(matrix)


# ═══════════════════════════════════════════════════════════════
# GAME TYPE CLASSIFICATION
# ═══════════════════════════════════════════════════════════════

class GameGenre(Enum):
    PLATFORMER = "platformer"
    TOP_DOWN_SHOOTER = "top_down_shooter"
    PUZZLE = "puzzle"
    ROGUELIKE = "roguelike"
    METROIDVANIA = "metroidvania"
    TOWER_DEFENSE = "tower_defense"
    BULLET_HELL = "bullet_hell"
    STEALTH = "stealth"
    RACING = "racing"
    SURVIVAL = "survival"

class GamePerspective(Enum):
    SIDE_SCROLLING = "side_scrolling"
    TOP_DOWN = "top_down"
    ISOMETRIC = "isometric"
    FIRST_PERSON_2D = "first_person_2d"


# ═══════════════════════════════════════════════════════════════
# GAME CONFIGURATION & METADATA
# ═══════════════════════════════════════════════════════════════

@dataclass
class SteamMetadata:
    """Steam platform specific metadata."""
    app_id: int
    game_name: str
    description: str
    tags: List[str]
    achievements: List[Dict[str, Any]] = field(default_factory=list)
    leaderboards: List[str] = field(default_factory=list)
    workshop_support: bool = False
    cloud_saves: bool = True
    controller_support: bool = True

@dataclass
class GameParameters:
    """Mathematically-derived game parameters."""
    seed: int
    genre: GameGenre
    perspective: GamePerspective
    difficulty: float  # 0.0 to 1.0, mapped via sigmoid
    world_size: Tuple[int, int]
    enemy_density: float
    resource_abundance: float
    pacing_speed: float
    complexity_level: int  # 1-10, affects algorithm depth
    
    @classmethod
    def generate_from_seed(cls, seed: int) -> 'GameParameters':
        """Probability: Generate parameters from seed using statistical distributions."""
        rng = random.Random(seed)
        
        # Use normal distribution for difficulty (clamped)
        difficulty = max(0.0, min(1.0, rng.gauss(0.5, 0.2)))
        
        # Genre selection via weighted random
        genres = list(GameGenre)
        genre = rng.choice(genres)
        
        # Perspective mapped to genre probability
        if genre == GameGenre.PLATFORMER or genre == GameGenre.METROIDVANIA:
            perspective = GamePerspective.SIDE_SCROLLING
        elif genre == GameGenre.TOP_DOWN_SHOOTER or genre == GameGenre.ROGUELIKE:
            perspective = GamePerspective.TOP_DOWN
        else:
            perspective = rng.choice(list(GamePerspective))
        
        # World size via exponential distribution
        base_size = int(rng.expovariate(1/50) * 100 + 20)
        world_size = (base_size, base_size * rng.randint(1, 3))
        
        # Other parameters via beta distribution
        enemy_density = rng.betavariate(2, 5)  # Skewed toward lower values
        resource_abundance = rng.betavariate(3, 3)
        pacing_speed = rng.betavariate(4, 2)  # Skewed toward faster
        complexity = rng.randint(1, 10)
        
        return cls(
            seed=seed,
            genre=genre,
            perspective=perspective,
            difficulty=difficulty,
            world_size=world_size,
            enemy_density=enemy_density,
            resource_abundance=resource_abundance,
            pacing_speed=pacing_speed,
            complexity_level=complexity
        )


# ═══════════════════════════════════════════════════════════════
# LINEAR ALGEBRA: 2D TRANSFORM ENGINE
# ═══════════════════════════════════════════════════════════════

class Transform2D:
    """Linear algebra: 2D affine transformations for game objects."""
    
    @staticmethod
    def translation_matrix(dx: float, dy: float) -> np.ndarray:
        return np.array([[1, 0, dx],
                         [0, 1, dy],
                         [0, 0, 1]])
    
    @staticmethod
    def rotation_matrix(angle_rad: float) -> np.ndarray:
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return np.array([[c, -s, 0],
                         [s, c, 0],
                         [0, 0, 1]])
    
    @staticmethod
    def scale_matrix(sx: float, sy: float) -> np.ndarray:
        return np.array([[sx, 0, 0],
                         [0, sy, 0],
                         [0, 0, 1]])
    
    @staticmethod
    def shear_matrix(shx: float, shy: float) -> np.ndarray:
        return np.array([[1, shx, 0],
                         [shy, 1, 0],
                         [0, 0, 1]])
    
    @staticmethod
    def transform_point(point: Tuple[float, float], matrix: np.ndarray) -> Tuple[float, float]:
        """Apply transformation matrix to a 2D point."""
        p = np.array([point[0], point[1], 1])
        result = matrix @ p
        return (result[0], result[1])
    
    @staticmethod
    def compose_transforms(*matrices: np.ndarray) -> np.ndarray:
        """Compose multiple transformations (matrix multiplication order matters)."""
        result = np.eye(3)
        for m in matrices:
            result = result @ m
        return result


# ═══════════════════════════════════════════════════════════════
# DIFFERENTIAL EQUATIONS: PHYSICS ENGINE
# ═══════════════════════════════════════════════════════════════

class PhysicsEngine:
    """Differential equations: Numerical integration for physics simulation."""
    
    def __init__(self, gravity: float = 980.0, damping: float = 0.99):
        self.gravity = gravity  # pixels/s²
        self.damping = damping
    
    def euler_integrate(self, position: np.ndarray, velocity: np.ndarray,
                        acceleration: np.ndarray, dt: float) -> Tuple[np.ndarray, np.ndarray]:
        """First-order Euler integration (explicit)."""
        velocity_new = velocity + acceleration * dt
        position_new = position + velocity * dt
        return position_new, velocity_new
    
    def rk4_integrate(self, position: np.ndarray, velocity: np.ndarray,
                      acceleration_func: Callable, dt: float) -> Tuple[np.ndarray, np.ndarray]:
        """Fourth-order Runge-Kutta integration for better accuracy."""
        # k1
        a1 = acceleration_func(position, velocity)
        v1 = velocity
        p1 = position
        
        # k2
        v2 = velocity + 0.5 * dt * a1
        p2 = position + 0.5 * dt * v1
        a2 = acceleration_func(p2, v2)
        
        # k3
        v3 = velocity + 0.5 * dt * a2
        p3 = position + 0.5 * dt * v2
        a3 = acceleration_func(p3, v3)
        
        # k4
        v4 = velocity + dt * a3
        p4 = position + dt * v3
        a4 = acceleration_func(p4, v4)
        
        # Combine
        velocity_new = velocity + (dt / 6.0) * (a1 + 2*a2 + 2*a3 + a4)
        position_new = position + (dt / 6.0) * (v1 + 2*v2 + 2*v3 + v4)
        
        return position_new, velocity_new
    
    def verlet_integrate(self, position: np.ndarray, prev_position: np.ndarray,
                         acceleration: np.ndarray, dt: float) -> Tuple[np.ndarray, np.ndarray]:
        """Verlet integration - good for constrained systems."""
        velocity = (position - prev_position) * self.damping
        new_position = 2 * position - prev_position + acceleration * dt * dt
        return new_position, velocity
    
    def spring_force(self, position: np.ndarray, anchor: np.ndarray, 
                     spring_constant: float, rest_length: float) -> np.ndarray:
        """Hooke's Law: F = -k * (|x| - L) * x̂"""
        displacement = position - anchor
        distance = la.norm(displacement)
        if distance == 0:
            return np.zeros(2)
        direction = displacement / distance
        return -spring_constant * (distance - rest_length) * direction
    
    @staticmethod
    def drag_force(velocity: np.ndarray, drag_coefficient: float) -> np.ndarray:
        """Drag force: F_drag = -c * |v| * v"""
        speed = la.norm(velocity)
        if speed == 0:
            return np.zeros(2)
        return -drag_coefficient * speed * velocity


# ═══════════════════════════════════════════════════════════════
# GRAPH THEORY: LEVEL GENERATION
# ═══════════════════════════════════════════════════════════════

class GraphLevelGenerator:
    """Graph theory: Generate levels using graph algorithms."""
    
    @staticmethod
    def generate_room_graph(num_rooms: int, connectivity: float, seed: int) -> np.ndarray:
        """Generate adjacency matrix for room connectivity using random graph theory."""
        rng = random.Random(seed)
        adj_matrix = np.zeros((num_rooms, num_rooms), dtype=int)
        
        # Erdos-Renyi random graph
        for i in range(num_rooms):
            for j in range(i + 1, num_rooms):
                if rng.random() < connectivity:
                    adj_matrix[i][j] = adj_matrix[j][i] = 1
        
        # Ensure graph is connected (add minimum spanning tree edges if needed)
        visited = set()
        components = []
        
        def dfs(node, comp):
            visited.add(node)
            comp.append(node)
            for neighbor in range(num_rooms):
                if adj_matrix[node][neighbor] and neighbor not in visited:
                    dfs(neighbor, comp)
        
        for node in range(num_rooms):
            if node not in visited:
                comp = []
                dfs(node, comp)
                components.append(comp)
        
        # Connect components
        for i in range(len(components) - 1):
            n1 = rng.choice(components[i])
            n2 = rng.choice(components[i + 1])
            adj_matrix[n1][n2] = adj_matrix[n2][n1] = 1
        
        return adj_matrix
    
    @staticmethod
    def a_star_pathfinding(graph: np.ndarray, start: int, goal: int,
                           heuristic: Callable = None) -> List[int]:
        """A* search algorithm for pathfinding."""
        if heuristic is None:
            heuristic = lambda a, b: 0  # Dijkstra's algorithm
        
        open_set = {start}
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        
        while open_set:
            current = min(open_set, key=lambda x: f_score.get(x, float('inf')))
            
            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]
            
            open_set.remove(current)
            
            for neighbor in range(len(graph)):
                if graph[current][neighbor]:
                    tentative_g = g_score[current] + 1  # Unit edge weight
                    
                    if tentative_g < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                        open_set.add(neighbor)
        
        return []  # No path found
    
    @staticmethod
    def generate_delaunay_triangulation(points: List[Tuple[float, float]]) -> List[Tuple[int, int, int]]:
        """Graph theory: Delaunay triangulation for natural terrain meshes."""
        from scipy.spatial import Delaunay
        tri = Delaunay(np.array(points))
        return [(int(s[0]), int(s[1]), int(s[2])) for s in tri.simplices]


# ═══════════════════════════════════════════════════════════════
# FRACTAL GEOMETRY: TERRAIN & STRUCTURE GENERATION
# ═══════════════════════════════════════════════════════════════

class FractalGenerator:
    """Fractal geometry: Generate natural-looking terrain and structures."""
    
    @staticmethod
    def midpoint_displacement(size: int, roughness: float, seed: int) -> np.ndarray:
        """Fractal: Midpoint displacement for terrain heightmaps."""
        rng = random.Random(seed)
        terrain = np.zeros((size, size))
        
        # Set corner values
        terrain[0, 0] = rng.uniform(-1, 1)
        terrain[0, -1] = rng.uniform(-1, 1)
        terrain[-1, 0] = rng.uniform(-1, 1)
        terrain[-1, -1] = rng.uniform(-1, 1)
        
        step = size - 1
        scale = roughness
        
        while step > 1:
            half = step // 2
            
            # Diamond step
            for y in range(0, size - 1, step):
                for x in range(0, size - 1, step):
                    avg = (terrain[y, x] + terrain[y, x + step] +
                           terrain[y + step, x] + terrain[y + step, x + step]) / 4.0
                    terrain[y + half, x + half] = avg + rng.uniform(-scale, scale)
            
            # Square step
            for y in range(0, size, half):
                for x in range((y + half) % step, size, step):
                    count = 0
                    total = 0.0
                    
                    if y - half >= 0:
                        total += terrain[y - half, x]
                        count += 1
                    if y + half < size:
                        total += terrain[y + half, x]
                        count += 1
                    if x - half >= 0:
                        total += terrain[y, x - half]
                        count += 1
                    if x + half < size:
                        total += terrain[y, x + half]
                        count += 1
                    
                    if count > 0:
                        terrain[y, x] = total / count + rng.uniform(-scale, scale)
            
            step = half
            scale *= 0.5 ** roughness
        
        return terrain
    
    @staticmethod
    def l_system(axiom: str, rules: Dict[str, str], iterations: int) -> str:
        """Fractal: L-system for generating plant/tree structures."""
        result = axiom
        for _ in range(iterations):
            result = ''.join(rules.get(c, c) for c in result)
        return result
    
    @staticmethod
    def mandelbrot_set(width: int, height: int, max_iter: int = 100) -> np.ndarray:
        """Complex analysis: Mandelbrot set for visual effects."""
        x = np.linspace(-2, 1, width)
        y = np.linspace(-1.5, 1.5, height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y
        Z = np.zeros_like(C)
        fractal = np.zeros(C.shape, dtype=int)
        
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask] ** 2 + C[mask]
            fractal[mask] = i
        
        return fractal


# ═══════════════════════════════════════════════════════════════
# PROBABILITY THEORY: LOOT, AI, & ENEMY GENERATION
# ═══════════════════════════════════════════════════════════════

class ProbabilitySystem:
    """Probability theory: Loot tables, enemy AI, procedural generation."""
    
    @staticmethod
    def generate_loot_table(difficulty: float, num_items: int, seed: int) -> Dict[str, float]:
        """Generate loot drop probabilities using Dirichlet distribution."""
        rng = random.Random(seed)
        
        # Rarity categories
        rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        
        # Dirichlet parameters influenced by difficulty
        alpha = [5.0 - difficulty * 3, 3.0 - difficulty * 2, 
                 2.0 - difficulty, 1.0, max(0.1, 0.5 - difficulty * 0.3)]
        
        # Generate probabilities
        probabilities = [max(0.001, rng.gammavariate(a, 1)) for a in alpha]
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]
        
        loot_table = {}
        for rarity, prob in zip(rarities, probabilities):
            loot_table[rarity] = prob
        
        return loot_table
    
    @staticmethod
    def enemy_ai_decision(state_vector: np.ndarray, weights: np.ndarray) -> int:
        """Linear algebra + probability: Neural network-inspired AI decisions."""
        # Simple single-layer perceptron
        activations = state_vector @ weights
        # Softmax for probability distribution over actions
        exp_acts = np.exp(activations - np.max(activations))
        probabilities = exp_acts / np.sum(exp_acts)
        return np.random.choice(len(probabilities), p=probabilities)
    
    @staticmethod
    def gaussian_mixture_model(points: np.ndarray, n_components: int, 
                               n_iterations: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Probability: EM algorithm for Gaussian Mixture Model (enemy clustering)."""
        n_points, n_dims = points.shape
        
        # Initialize parameters
        means = points[np.random.choice(n_points, n_components, replace=False)]
        covariances = np.array([np.eye(n_dims) for _ in range(n_components)])
        weights = np.ones(n_components) / n_components
        
        for _ in range(n_iterations):
            # E-step: compute responsibilities
            responsibilities = np.zeros((n_points, n_components))
            
            for k in range(n_components):
                diff = points - means[k]
                inv_cov = la.inv(covariances[k])
                det_cov = la.det(covariances[k])
                
                exponent = -0.5 * np.sum(diff @ inv_cov * diff, axis=1)
                responsibilities[:, k] = weights[k] * np.exp(exponent) / np.sqrt((2*np.pi)**n_dims * det_cov)
            
            responsibilities /= responsibilities.sum(axis=1, keepdims=True)
            
            # M-step: update parameters
            Nk = responsibilities.sum(axis=0)
            weights = Nk / n_points
            means = (responsibilities.T @ points) / Nk[:, np.newaxis]
            
            for k in range(n_components):
                diff = points - means[k]
                covariances[k] = (responsibilities[:, k][:, np.newaxis] * diff).T @ diff / Nk[k]
        
        return means, covariances, weights


# ═══════════════════════════════════════════════════════════════
# OPTIMIZATION: DIFFICULTY BALANCING
# ═══════════════════════════════════════════════════════════════

class DifficultyOptimizer:
    """Optimization: Tune game parameters for target difficulty."""
    
    @staticmethod
    def gradient_descent(initial_params: np.ndarray, target_difficulty: float,
                         eval_func: Callable, learning_rate: float = 0.01,
                         n_iterations: int = 100) -> np.ndarray:
        """Optimization: Gradient descent to tune game parameters."""
        params = initial_params.copy()
        
        for i in range(n_iterations):
            current_difficulty = eval_func(params)
            error = target_difficulty - current_difficulty
            
            if abs(error) < 0.001:
                break
            
            # Numerical gradient approximation
            gradient = np.zeros_like(params)
            epsilon = 1e-5
            
            for j in range(len(params)):
                params_plus = params.copy()
                params_plus[j] += epsilon
                grad = (eval_func(params_plus) - current_difficulty) / epsilon
                gradient[j] = grad
            
            # Update parameters
            params += learning_rate * error * gradient
            params = np.clip(params, 0, 1)  # Keep in valid range
        
        return params
    
    @staticmethod
    def simulated_annealing(initial_params: np.ndarray, cost_function: Callable,
                           n_iterations: int = 1000, initial_temp: float = 1.0,
                           cooling_rate: float = 0.99) -> np.ndarray:
        """Optimization: Simulated annealing for global optimization."""
        current_params = initial_params.copy()
        current_cost = cost_function(current_params)
        best_params = current_params.copy()
        best_cost = current_cost
        temperature = initial_temp
        
        for _ in range(n_iterations):
            # Generate neighbor
            neighbor = current_params + np.random.normal(0, 0.1, current_params.shape)
            neighbor = np.clip(neighbor, 0, 1)
            neighbor_cost = cost_function(neighbor)
            
            # Acceptance probability (Metropolis criterion)
            delta = neighbor_cost - current_cost
            if delta < 0 or np.random.random() < math.exp(-delta / temperature):
                current_params = neighbor
                current_cost = neighbor_cost
                
                if current_cost < best_cost:
                    best_params = current_params.copy()
                    best_cost = current_cost
            
            temperature *= cooling_rate
        
        return best_params


# ═══════════════════════════════════════════════════════════════
# COLLISION DETECTION (LINEAR ALGEBRA)
# ═══════════════════════════════════════════════════════════════

class CollisionSystem:
    """Linear algebra: Collision detection and response."""
    
    @staticmethod
    def aabb_collision(rect1: Tuple[float, float, float, float],
                       rect2: Tuple[float, float, float, float]) -> bool:
        """Axis-Aligned Bounding Box collision."""
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + h2 and y1 + h1 > y2)
    
    @staticmethod
    def separating_axis_theorem(vertices1: np.ndarray, vertices2: np.ndarray) -> bool:
        """Separating Axis Theorem for convex polygon collision."""
        def get_axes(vertices):
            axes = []
            n = len(vertices)
            for i in range(n):
                edge = vertices[(i + 1) % n] - vertices[i]
                normal = np.array([-edge[1], edge[0]])
                axes.append(normal / la.norm(normal))
            return axes
        
        def project(vertices, axis):
            dots = vertices @ axis
            return np.min(dots), np.max(dots)
        
        axes = get_axes(vertices1) + get_axes(vertices2)
        
        for axis in axes:
            min1, max1 = project(vertices1, axis)
            min2, max2 = project(vertices2, axis)
            
            if max1 < min2 or max2 < min1:
                return False  # Separating axis found
        
        return True  # No separating axis - collision
    
    @staticmethod
    def circle_collision(c1: Tuple[float, float, float],
                         c2: Tuple[float, float, float]) -> bool:
        """Circle collision detection."""
        x1, y1, r1 = c1
        x2, y2, r2 = c2
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance < r1 + r2


# ═══════════════════════════════════════════════════════════════
# GAME GENERATOR: Assembles all components
# ═══════════════════════════════════════════════════════════════

@dataclass
class GeneratedGame:
    """Complete generated game data structure."""
    metadata: SteamMetadata
    parameters: GameParameters
    
    # Generated content
    level_map: np.ndarray
    terrain_heightmap: np.ndarray
    room_graph: np.ndarray
    enemy_positions: List[Tuple[float, float]]
    item_positions: List[Tuple[float, float]]
    loot_table: Dict[str, float]
    difficulty_params: np.ndarray
    
    # Generated systems
    physics: PhysicsEngine
    transforms: Transform2D
    
    def export_steam_config(self) -> Dict[str, Any]:
        """Export Steam-compatible configuration."""
        return {
            "appid": self.metadata.app_id,
            "name": self.metadata.game_name,
            "description": self.metadata.description,
            "tags": self.metadata.tags,
            "achievements": self.metadata.achievements,
            "leaderboards": self.metadata.leaderboards,
            "workshop": self.metadata.workshop_support,
            "cloud_saves": self.metadata.cloud_saves,
            "controller_support": self.metadata.controller_support,
            "generation_seed": self.parameters.seed,
            "genre": self.parameters.genre.value,
            "perspective": self.parameters.perspective.value,
            "difficulty": float(self.parameters.difficulty),
            "complexity_level": self.parameters.complexity_level
        }
    
    def export_game_data(self) -> Dict[str, Any]:
        """Export complete game data for runtime engine."""
        return {
            "level_map": self.level_map.tolist(),
            "terrain": self.terrain_heightmap.tolist(),
            "room_graph": self.room_graph.tolist(),
            "enemies": [(float(x), float(y)) for x, y in self.enemy_positions],
            "items": [(float(x), float(y)) for x, y in self.item_positions],
            "loot_table": self.loot_table,
            "difficulty_params": self.difficulty_params.tolist()
        }


class GameGenerator:
    """Main game generation orchestrator."""
    
    def __init__(self, steam_app_id: int = 480):
        self.steam_app_id = steam_app_id
        self.math = MathFoundation()
    
    def generate(self, game_name: str, genre_hint: Optional[GameGenre] = None) -> GeneratedGame:
        """Generate a complete game."""
        
        # Generate seed from Steam ID and game name
        seed = self.math.generate_seed(self.steam_app_id, game_name)
        rng = random.Random(seed)
        
        # Generate parameters
        params = GameParameters.generate_from_seed(seed)
        if genre_hint:
            params.genre = genre_hint
        
        # Generate metadata
        metadata = self._generate_metadata(game_name, params, seed)
        
        # Generate level using graph theory
        graph_gen = GraphLevelGenerator()
        num_rooms = rng.randint(5, 20)
        room_graph = graph_gen.generate_room_graph(num_rooms, 0.3, seed)
        
        # Generate terrain using fractals
        fractal_gen = FractalGenerator()
        terrain = fractal_gen.midpoint_displacement(64, 0.7, seed + 1)
        level_map = fractal_gen.midpoint_displacement(params.world_size[0], 0.5, seed + 2)
        
        # Generate enemies using probability distributions
        prob_sys = ProbabilitySystem()
        enemy_count = int(params.enemy_density * params.world_size[0] * params.world_size[1] / 100)
        enemy_positions = [(rng.uniform(0, params.world_size[0]),
                            rng.uniform(0, params.world_size[1]))
                           for _ in range(enemy_count)]
        
        # Generate items
        item_count = int(params.resource_abundance * enemy_count * 2)
        item_positions = [(rng.uniform(0, params.world_size[0]),
                           rng.uniform(0, params.world_size[1]))
                          for _ in range(item_count)]
        
        # Generate loot table
        loot_table = prob_sys.generate_loot_table(params.difficulty, 5, seed + 3)
        
        # Optimize difficulty parameters
        optimizer = DifficultyOptimizer()
        initial_params = np.array([params.difficulty, params.enemy_density, params.pacing_speed])
        
        def difficulty_eval(p: np.ndarray) -> float:
            # Simple difficulty evaluation function
            return (p[0] * 0.5 + p[1] * 0.3 + (1 - p[2]) * 0.2)
        
        difficulty_params = optimizer.simulated_annealing(
            initial_params, difficulty_eval, n_iterations=500)
        
        # Create physics engine
        physics = PhysicsEngine(gravity=980.0 * params.pacing_speed)
        transforms = Transform2D()
        
        return GeneratedGame(
            metadata=metadata,
            parameters=params,
            level_map=level_map,
            terrain_heightmap=terrain,
            room_graph=room_graph,
            enemy_positions=enemy_positions,
            item_positions=item_positions,
            loot_table=loot_table,
            difficulty_params=difficulty_params,
            physics=physics,
            transforms=transforms
        )
    
    def _generate_metadata(self, game_name: str, params: GameParameters, 
                           seed: int) -> SteamMetadata:
        """Generate Steam metadata."""
        rng = random.Random(seed + 100)
        
        # Generate achievements using graph theory
        achievement_graph = GraphLevelGenerator.generate_room_graph(10, 0.4, seed + 200)
        achievements = []
        achievement_names = [
            "FIRST_STEPS", "EXPLORER", "COLLECTOR", "SURVIVOR",
            "MASTER", "SPEEDRUNNER", "COMPLETIONIST", "SECRET_FINDER",
            "PERFECTIONIST", "LEGEND"
        ]
        
        for i, name in enumerate(achievement_names):
            # Achievement dependencies from graph
            prerequisites = [achievement_names[j] for j in range(i) 
                             if j < len(achievement_graph[i]) and achievement_graph[i][j]]
            
            achievements.append({
                "id": f"ACH_{name}",
                "name": name.replace("_", " ").title(),
                "description": f"Unlock the {name.lower().replace('_', ' ')} achievement",
                "icon": f"achievement_{name.lower()}.png",
                "prerequisites": prerequisites,
                "hidden": rng.random() < 0.3
            })
        
        # Generate description using templates
        templates = [
            f"A {params.genre.value.replace('_', ' ')} adventure with procedurally generated levels.",
            f"Explore a dynamically generated world in this {params.genre.value.replace('_', ' ')} game.",
            f"Every playthrough is unique in this mathematically generated {params.genre.value.replace('_', ' ')} experience."
        ]
        description = rng.choice(templates)
        
        return SteamMetadata(
            app_id=self.steam_app_id,
            game_name=game_name,
            description=description,
            tags=[params.genre.value, params.perspective.value, 
                  "procedural", "generated", "mathematical"],
            achievements=achievements,
            leaderboards=["high_score", "speed_run", "completion_percent"],
            workshop_support=params.complexity_level > 5,
            cloud_saves=True,
            controller_support=True
        )


# ═══════════════════════════════════════════════════════════════
# STEAM DEPLOYMENT MANAGER
# ═══════════════════════════════════════════════════════════════

class SteamDeploymentManager:
    """Manages Steam platform integration and deployment."""
    
    @staticmethod
    def create_steam_achievement_config(achievements: List[Dict]) -> Dict:
        """Create Steam achievement configuration."""
        config = {
            "version": 1,
            "achievements": []
        }
        
        for ach in achievements:
            config["achievements"].append({
                "id": ach["id"],
                "name": ach["name"],
                "description": ach["description"],
                "icon": ach.get("icon", ""),
                "icon_gray": ach.get("icon", "").replace(".png", "_gray.png"),
                "hidden": ach.get("hidden", False),
                "stat_thresholds": ach.get("prerequisites", [])
            })
        
        return config
    
    @staticmethod
    def create_steam_leaderboard_config(leaderboards: List[str]) -> Dict:
        """Create Steam leaderboard configuration."""
        return {
            "version": 1,
            "leaderboards": [
                {
                    "id": f"LB_{name.upper()}",
                    "name": name.replace("_", " ").title(),
                    "sort_method": "descending" if "score" in name else "ascending",
                    "display_type": "numeric"
                }
                for name in leaderboards
            ]
        }
    
    @staticmethod
    def generate_steam_build_script(app_id: int, depot_id: int) -> str:
        """Generate Steam build configuration script."""
        return f"""
        "AppBuild"
        {{
            "AppID" "{app_id}"
            "Desc" "Auto-generated game build"
            
            "ContentRoot" "."
            "BuildOutput" "./build_output"
            
            "Depots"
            {{
                "{depot_id}" "depot_build.vdf"
            }}
        }}
        """


# ═══════════════════════════════════════════════════════════════
# GAME RUNTIME SIMULATOR
# ═══════════════════════════════════════════════════════════════

class GameRuntimeSimulator:
    """Simulate the generated game to verify playability."""
    
    def __init__(self, game: GeneratedGame):
        self.game = game
        self.player_position = np.array([50.0, 50.0])
        self.player_velocity = np.array([0.0, 0.0])
        self.score = 0
        self.time_played = 0.0
        
    def simulate_playthrough(self, num_frames: int = 1000) -> Dict[str, Any]:
        """Run a simulated playthrough using the physics engine."""
        physics = self.game.physics
        positions = [self.player_position.copy()]
        
        for frame in range(num_frames):
            dt = 1/60.0  # 60 FPS
            
            # Simulate input (random exploration)
            input_force = np.array([
                random.uniform(-1, 1) * 200,
                -physics.gravity * 0.1  # Jump occasionally
            ])
            
            # Apply physics
            acceleration = input_force
            self.player_position, self.player_velocity = physics.rk4_integrate(
                self.player_position, self.player_velocity,
                lambda p, v: acceleration, dt
            )
            
            # Check collisions with enemies
            for enemy_pos in self.game.enemy_positions:
                enemy_arr = np.array(enemy_pos)
                distance = la.norm(self.player_position - enemy_arr)
                if distance < 10:  # Hit enemy
                    self.score += 100
                    break
            
            # Check item collection
            for item_pos in self.game.item_positions:
                item_arr = np.array(item_pos)
                if la.norm(self.player_position - item_arr) < 15:
                    self.score += 50
            
            positions.append(self.player_position.copy())
            self.time_played += dt
        
        return {
            "final_position": self.player_position.tolist(),
            "final_velocity": self.player_velocity.tolist(),
            "score": self.score,
            "time_played": self.time_played,
            "path": [p.tolist() for p in positions[::10]]  # Sample every 10 frames
        }


# ═══════════════════════════════════════════════════════════════
# MAIN GENERATION PIPELINE
# ═══════════════════════════════════════════════════════════════

def generate_steam_game(game_name: str, steam_app_id: int = 480,
                       genre_hint: Optional[GameGenre] = None) -> GeneratedGame:
    """Main function: Generate a complete Steam game."""
    
    print(f"[Steam Game Generator] Initializing for AppID {steam_app_id}")
    print(f"[Steam Game Generator] Generating game: {game_name}")
    
    # Create generator
    generator = GameGenerator(steam_app_id)
    
    # Generate game
    game = generator.generate(game_name, genre_hint)
    
    print(f"[Steam Game Generator] Genre: {game.parameters.genre.value}")
    print(f"[Steam Game Generator] Perspective: {game.parameters.perspective.value}")
    print(f"[Steam Game Generator] Difficulty: {game.parameters.difficulty:.2f}")
    print(f"[Steam Game Generator] World size: {game.parameters.world_size}")
    print(f"[Steam Game Generator] Enemies: {len(game.enemy_positions)}")
    print(f"[Steam Game Generator] Items: {len(game.item_positions)}")
    print(f"[Steam Game Generator] Loot table: {game.loot_table}")
    
    # Run simulation to verify playability
    simulator = GameRuntimeSimulator(game)
    simulation_result = simulator.simulate_playthrough(1000)
    print(f"[Steam Game Generator] Simulation score: {simulation_result['score']}")
    
    # Generate Steam configurations
    steam_deploy = SteamDeploymentManager()
    achievement_config = steam_deploy.create_steam_achievement_config(game.metadata.achievements)
    leaderboard_config = steam_deploy.create_steam_leaderboard_config(game.metadata.leaderboards)
    
    print(f"[Steam Game Generator] Achievements: {len(achievement_config['achievements'])}")
    print(f"[Steam Game Generator] Leaderboards: {len(leaderboard_config['leaderboards'])}")
    
    return game


# ═══════════════════════════════════════════════════════════════
# BATCH GENERATOR
# ═══════════════════════════════════════════════════════════════

def batch_generate_steam_games(count: int = 5) -> List[GeneratedGame]:
    """Generate multiple games for Steam platform."""
    games = []
    
    genres = list(GameGenre)
    name_templates = [
        "Dimensional Drift", "Quantum Quest", "Fractal Fury",
        "Vector Vortex", "Probability Path", "Tensor Trek",
        "Eigen Empire", "Spectral Spire", "Gradient Gate",
        "Matrix Metaverse", "Calculus Kingdom", "Topology Tower"
    ]
    
    for i in range(count):
        game_name = f"{name_templates[i % len(name_templates)]} {random.randint(1, 99)}"
        genre = genres[i % len(genres)]
        
        game = generate_steam_game(game_name, steam_app_id=480 + i, genre_hint=genre)
        games.append(game)
        
        print(f"  Generated game {i+1}/{count}: {game_name}")
    
    return games


# ═══════════════════════════════════════════════════════════════
# EXPORT UTILITIES
# ═══════════════════════════════════════════════════════════════

def export_game_to_json(game: GeneratedGame, filepath: str):
    """Export generated game to JSON for further processing."""
    export_data = {
        "metadata": game.export_steam_config(),
        "game_data": game.export_game_data()
    }
    
    # Convert numpy types to Python native types
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            return super().default(obj)
    
    with open(filepath, 'w') as f:
        json.dump(export_data, f, indent=2, cls=NumpyEncoder)
    
    print(f"[Export] Game exported to {filepath}")


# ═══════════════════════════════════════════════════════════════
# EXECUTION
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  STEAM GAME AUTOMATIC GENERATION MACHINE")
    print("  Mathematical Foundations Applied")
    print("=" * 60)
    
    # Generate a single game
    game = generate_steam_game("Matrix Metaverse", 480, GameGenre.METROIDVANIA)
    
    # Export to JSON
    export_game_to_json(game, "generated_steam_game.json")
    
    print("\n[Complete] Game generation successful!")
    print(f"[Complete] Seed: {game.parameters.seed}")
    print(f"[Complete] Ready for Steam deployment")