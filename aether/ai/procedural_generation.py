"""
Procedural Content Generation
Perlin noise, cellular automata, L-systems, dungeon generation
"""

import numpy as np
import math
import random
from typing import List, Tuple, Dict

class PerlinNoise:
    """Classic Perlin noise implementation"""
    def __init__(self, seed: int = 42):
        random.seed(seed)
        # Permutation table
        self.perm = list(range(256))
        random.shuffle(self.perm)
        self.perm += self.perm  # double for wrapping
    
    def _fade(self, t: float) -> float:
        # 6t^5 - 15t^4 + 10t^3
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        return a + t * (b - a)
    
    def _grad(self, hash: int, x: float, y: float) -> float:
        h = hash & 3
        u = x if h < 2 else -x
        v = y if h < 2 else -y
        return u + v
    
    def noise2d(self, x: float, y: float) -> float:
        # Determine grid cell coordinates
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        # Relative coordinates within cell
        xf = x - math.floor(x)
        yf = y - math.floor(y)
        # Compute fade curves
        u = self._fade(xf)
        v = self._fade(yf)
        
        # Hash coordinates of the 4 corners
        aa = self.perm[self.perm[X] + Y]
        ab = self.perm[self.perm[X] + Y + 1]
        ba = self.perm[self.perm[X + 1] + Y]
        bb = self.perm[self.perm[X + 1] + Y + 1]
        
        # Blend
        x1 = self._lerp(self._grad(aa, xf, yf), self._grad(ba, xf - 1, yf), u)
        x2 = self._lerp(self._grad(ab, xf, yf - 1), self._grad(bb, xf - 1, yf - 1), u)
        return self._lerp(x1, x2, v)
    
    def fbm(self, x: float, y: float, octaves: int = 6, lacunarity: float = 2.0, gain: float = 0.5) -> float:
        """Fractal Brownian Motion"""
        value = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0
        
        for i in range(octaves):
            value += amplitude * self.noise2d(x * frequency, y * frequency)
            max_value += amplitude
            amplitude *= gain
            frequency *= lacunarity
        
        return value / max_value

class CellularAutomata:
    """Cellular automata for cave generation"""
    @staticmethod
    def generate(width: int, height: int, fill_prob: float = 0.45, 
                iterations: int = 4, neighbor_threshold: int = 4) -> np.ndarray:
        grid = np.random.rand(height, width) < fill_prob
        for _ in range(iterations):
            new_grid = grid.copy()
            for y in range(height):
                for x in range(width):
                    # Count alive neighbors (8-neighborhood)
                    neighbors = 0
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = (x + dx) % width, (y + dy) % height
                            neighbors += grid[ny, nx]
                    if grid[y, x]:
                        new_grid[y, x] = neighbors >= neighbor_threshold
                    else:
                        new_grid[y, x] = neighbors > neighbor_threshold
            grid = new_grid
        return grid

class LSystem:
    """Lindenmayer system for plant-like structures"""
    def __init__(self, axiom: str, rules: Dict[str, str], angle: float = 25.0):
        self.axiom = axiom
        self.rules = rules
        self.angle = angle * math.pi / 180
    
    def generate(self, iterations: int) -> str:
        current = self.axiom
        for _ in range(iterations):
            next_str = ""
            for ch in current:
                next_str += self.rules.get(ch, ch)
            current = next_str
        return current
    
    def to_lines(self, sequence: str, start_pos: Tuple[float, float] = (0,0), 
                start_angle: float = 90, step: float = 10) -> List[Tuple[Tuple[float,float], Tuple[float,float]]]:
        """Convert L-system string to list of line segments (for rendering)"""
        stack = []
        pos = list(start_pos)
        angle = start_angle * math.pi / 180
        lines = []
        
        for cmd in sequence:
            if cmd == 'F' or cmd == 'G':  # move forward drawing
                new_x = pos[0] + step * math.cos(angle)
                new_y = pos[1] - step * math.sin(angle)  # invert y for screen
                lines.append(((pos[0], pos[1]), (new_x, new_y)))
                pos = [new_x, new_y]
            elif cmd == 'f':  # move forward without drawing
                pos[0] += step * math.cos(angle)
                pos[1] -= step * math.sin(angle)
            elif cmd == '+':  # turn right
                angle -= self.angle
            elif cmd == '-':  # turn left
                angle += self.angle
            elif cmd == '[':  # push state
                stack.append((pos.copy(), angle))
            elif cmd == ']':  # pop state
                pos, angle = stack.pop()
        return lines

class DungeonGenerator:
    """Generate dungeon layouts using BSP or random walk"""
    @staticmethod
    def bsp_dungeon(width: int, height: int, min_room_size: int = 5, max_depth: int = 4) -> np.ndarray:
        """Binary Space Partitioning dungeon"""
        grid = np.zeros((height, width), dtype=int)
        rooms = []
        
        def split_region(x, y, w, h, depth):
            if depth >= max_depth or w < min_room_size*2 or h < min_room_size*2:
                # Create room in this region
                room_w = random.randint(min_room_size, w-2)
                room_h = random.randint(min_room_size, h-2)
                room_x = x + random.randint(1, w - room_w - 1)
                room_y = y + random.randint(1, h - room_h - 1)
                rooms.append((room_x, room_y, room_w, room_h))
                for i in range(room_y, room_y+room_h):
                    for j in range(room_x, room_x+room_w):
                        grid[i, j] = 1
                return
            
            # Decide split orientation
            if w > h * 1.2:  # wider than tall
                split_vertical = True
            elif h > w * 1.2:
                split_vertical = False
            else:
                split_vertical = random.random() > 0.5
            
            if split_vertical:
                split = random.randint(min_room_size, w - min_room_size)
                split_region(x, y, split, h, depth+1)
                split_region(x+split, y, w-split, h, depth+1)
            else:
                split = random.randint(min_room_size, h - min_room_size)
                split_region(x, y, w, split, depth+1)
                split_region(x, y+split, w, h-split, depth+1)
        
        split_region(0, 0, width, height, 0)
        
        # Connect rooms with corridors (simple nearest neighbor)
        centers = [(x + w//2, y + h//2) for (x, y, w, h) in rooms]
        for i in range(len(centers)-1):
            x1, y1 = centers[i]
            x2, y2 = centers[i+1]
            # L-shaped corridor
            if random.random() < 0.5:
                DungeonGenerator._carve_corridor(grid, x1, y1, x2, y1)
                DungeonGenerator._carve_corridor(grid, x2, y1, x2, y2)
            else:
                DungeonGenerator._carve_corridor(grid, x1, y1, x1, y2)
                DungeonGenerator._carve_corridor(grid, x1, y2, x2, y2)
        return grid
    
    @staticmethod
    def _carve_corridor(grid, x1, y1, x2, y2):
        if x1 == x2:
            for y in range(min(y1,y2), max(y1,y2)+1):
                if 0 <= y < grid.shape[0] and 0 <= x1 < grid.shape[1]:
                    grid[y, x1] = 1
        else:
            for x in range(min(x1,x2), max(x1,x2)+1):
                if 0 <= y1 < grid.shape[0] and 0 <= x < grid.shape[1]:
                    grid[y1, x] = 1

class TerrainGenerator:
    """Heightmap terrain generation using noise"""
    @staticmethod
    def generate(size: int, noise: PerlinNoise = None, scale: float = 100.0, 
                octaves: int = 6) -> np.ndarray:
        if noise is None:
            noise = PerlinNoise()
        terrain = np.zeros((size, size))
        for y in range(size):
            for x in range(size):
                nx = x / scale
                ny = y / scale
                terrain[y, x] = noise.fbm(nx, ny, octaves)
        # Normalize to [0,1]
        terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min() + 1e-8)
        return terrain