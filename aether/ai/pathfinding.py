"""
Advanced Pathfinding Algorithms
A*, NavMesh, Flow Fields, with heuristic tuning
"""

import numpy as np
import heapq
from typing import List, Tuple, Dict, Set, Optional
import math
from dataclasses import dataclass
from collections import defaultdict

class AStarPathfinder:
    """A* pathfinding with multiple heuristics and smoothing"""
    
    def __init__(self, grid: np.ndarray, 
                 heuristic_type: str = "octile",
                 weight: float = 1.0):
        """
        grid: 2D array where 0 = walkable, positive values = cost
        heuristic_type: "manhattan", "euclidean", "octile", "chebyshev"
        """
        self.grid = grid
        self.height, self.width = grid.shape
        self.heuristic_type = heuristic_type
        self.weight = weight  # >1 makes it greedy, <1 more Dijkstra-like
        
    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        if self.heuristic_type == "manhattan":
            return dx + dy
        elif self.heuristic_type == "euclidean":
            return math.sqrt(dx*dx + dy*dy)
        elif self.heuristic_type == "octile":
            return max(dx, dy) + (math.sqrt(2)-1) * min(dx, dy)
        elif self.heuristic_type == "chebyshev":
            return max(dx, dy)
        return 0
    
    def neighbors(self, node: Tuple[int, int]) -> List[Tuple[int, int, float]]:
        x, y = node
        moves = []
        # 8-directional
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.height and 0 <= ny < self.width:
                if self.grid[nx, ny] >= 0:  # not blocked
                    cost = self.grid[nx, ny] + (math.sqrt(2) if dx and dy else 1.0)
                    moves.append((nx, ny, cost))
        return moves
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        open_set = [(0, start)]
        came_from = {}
        g_score = defaultdict(lambda: float('inf'))
        g_score[start] = 0
        f_score = defaultdict(lambda: float('inf'))
        f_score[start] = self.heuristic(start, goal) * self.weight
        
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return self.smooth_path(path)
            
            for neighbor_x, neighbor_y, move_cost in self.neighbors(current):
                tentative_g = g_score[current] + move_cost
                if tentative_g < g_score[(neighbor_x, neighbor_y)]:
                    came_from[(neighbor_x, neighbor_y)] = current
                    g_score[(neighbor_x, neighbor_y)] = tentative_g
                    f_score[(neighbor_x, neighbor_y)] = tentative_g + self.heuristic((neighbor_x, neighbor_y), goal) * self.weight
                    heapq.heappush(open_set, (f_score[(neighbor_x, neighbor_y)], (neighbor_x, neighbor_y)))
        return []  # no path
    
    def smooth_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Simple line-of-sight smoothing"""
        if len(path) <= 2:
            return path
        smoothed = [path[0]]
        i = 0
        while i < len(path) - 1:
            # Look farthest visible node
            for j in range(len(path)-1, i, -1):
                if self._line_of_sight(path[i], path[j]):
                    smoothed.append(path[j])
                    i = j
                    break
            else:
                i += 1
                smoothed.append(path[i])
        return smoothed
    
    def _line_of_sight(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> bool:
        """Bresenham line check"""
        x0, y0 = p1
        x1, y1 = p2
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            if self.grid[x0, y0] < 0:  # blocked
                return False
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return True

class NavMesh:
    """Navigation mesh using convex polygons"""
    def __init__(self, vertices: List[np.ndarray], polygons: List[List[int]]):
        self.vertices = [np.array(v) for v in vertices]
        self.polygons = polygons  # each polygon is list of vertex indices
        self.adjacency = self._build_adjacency()
    
    def _build_adjacency(self) -> Dict[int, List[int]]:
        adj = defaultdict(list)
        # Find shared edges
        for i, poly1 in enumerate(self.polygons):
            for j, poly2 in enumerate(self.polygons):
                if i >= j:
                    continue
                # Check if they share at least two vertices
                common = set(poly1) & set(poly2)
                if len(common) >= 2:
                    adj[i].append(j)
                    adj[j].append(i)
        return adj
    
    def find_path(self, start_poly: int, end_poly: int) -> List[int]:
        """A* over polygons using centroid distances"""
        centroids = {}
        for i, poly in enumerate(self.polygons):
            verts = [self.vertices[idx] for idx in poly]
            centroids[i] = np.mean(verts, axis=0)
        
        open_set = [(0, start_poly)]
        came_from = {}
        g_score = {start_poly: 0}
        f_score = {start_poly: np.linalg.norm(centroids[start_poly] - centroids[end_poly])}
        
        while open_set:
            _, current = heapq.heappop(open_set)
            if current == end_poly:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_poly)
                path.reverse()
                return path
            
            for neighbor in self.adjacency.get(current, []):
                tentative_g = g_score[current] + np.linalg.norm(centroids[current] - centroids[neighbor])
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + np.linalg.norm(centroids[neighbor] - centroids[end_poly])
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return []

class FlowField:
    """Vector field pathfinding for groups"""
    def __init__(self, grid: np.ndarray):
        self.grid = grid
        self.height, self.width = grid.shape
        self.flow_field = np.zeros((self.height, self.width, 2))
    
    def compute(self, goal: Tuple[int, int]):
        """Compute flow field using Dijkstra-like wavefront propagation"""
        self.flow_field.fill(0)
        # Distance field
        dist = np.full((self.height, self.width), np.inf)
        dist[goal] = 0
        queue = [goal]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.height and 0 <= ny < self.width and self.grid[nx, ny] >= 0:
                    new_dist = dist[x,y] + (1.414 if dx and dy else 1.0)
                    if new_dist < dist[nx, ny]:
                        dist[nx, ny] = new_dist
                        queue.append((nx, ny))
        
        # Compute flow vectors as negative gradient
        for x in range(self.height):
            for y in range(self.width):
                if dist[x,y] == np.inf:
                    continue
                min_neighbor = (x,y)
                min_dist = dist[x,y]
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < self.height and 0 <= ny < self.width and dist[nx, ny] < min_dist:
                        min_dist = dist[nx, ny]
                        min_neighbor = (nx, ny)
                direction = np.array([min_neighbor[0]-x, min_neighbor[1]-y], dtype=float)
                norm = np.linalg.norm(direction)
                if norm > 0:
                    direction /= norm
                self.flow_field[x,y] = direction