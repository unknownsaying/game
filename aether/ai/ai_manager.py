"""
Advanced AI System with multiple techniques
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import random
from collections import defaultdict
import math

class AIManager:
    """Manages all AI subsystems"""
    
    def __init__(self, engine):
        self.engine = engine
        self.behavior_trees = {}
        self.pathfinders = {}
        self.state_machines = {}
        self.neural_networks = {}
        self.nlp_models = {}
        
        # Initialize GPU-accelerated computation if available
        self.use_gpu = self._check_gpu_available()
        
    def _check_gpu_available(self) -> bool:
        """Check if GPU acceleration is available"""
        try:
            import cupy
            return True
        except ImportError:
            return False
    
    def update(self, dt: float):
        """Update all AI systems"""
        # Update behavior trees
        for bt in self.behavior_trees.values():
            bt.update(dt)
        
        # Update state machines
        for sm in self.state_machines.values():
            sm.update(dt)
    
    def create_behavior_tree(self, name: str) -> 'BehaviorTree':
        """Create new behavior tree"""
        bt = BehaviorTree()
        self.behavior_trees[name] = bt
        return bt
    
    def create_pathfinder(self, name: str, grid_map: np.ndarray) -> 'AStarPathfinder':
        """Create pathfinding instance"""
        pf = AStarPathfinder(grid_map)
        self.pathfinders[name] = pf
        return pf
    
    def create_neural_network(self, name: str, layers: List[int]) -> 'NeuralNetwork':
        """Create neural network"""
        nn = NeuralNetwork(layers)
        self.neural_networks[name] = nn
        return nn

class BehaviorTree:
    """Hierarchical behavior tree for complex AI behaviors"""
    
    class Node:
        def __init__(self, name=""):
            self.name = name
            self.children = []
            self.parent = None
        
        def execute(self, context: Dict) -> bool:
            return True
        
        def add_child(self, child):
            child.parent = self
            self.children.append(child)
    
    class Sequence(Node):
        """Execute children in order until one fails"""
        def execute(self, context):
            for child in self.children:
                if not child.execute(context):
                    return False
            return True
    
    class Selector(Node):
        """Execute children until one succeeds"""
        def execute(self, context):
            for child in self.children:
                if child.execute(context):
                    return True
            return False
    
    class Condition(Node):
        """Check a condition"""
        def __init__(self, condition_fn, name=""):
            super().__init__(name)
            self.condition = condition_fn
        
        def execute(self, context):
            return self.condition(context)
    
    class Action(Node):
        """Perform an action"""
        def __init__(self, action_fn, name=""):
            super().__init__(name)
            self.action = action_fn
        
        def execute(self, context):
            self.action(context)
            return True
    
    class Inverter(Node):
        """Invert child's result"""
        def __init__(self, child=None, name=""):
            super().__init__(name)
            if child:
                self.add_child(child)
        
        def execute(self, context):
            if self.children:
                return not self.children[0].execute(context)
            return True
    
    def __init__(self):
        self.root = self.Selector("Root")
        self.blackboard = {}
    
    def update(self, dt: float):
        """Execute behavior tree"""
        self.blackboard['dt'] = dt
        self.root.execute(self.blackboard)
    
    def set_root(self, node: Node):
        self.root = node

class AStarPathfinder:
    """A* pathfinding algorithm"""
    
    def __init__(self, grid: np.ndarray):
        self.grid = grid  # 0 = walkable, 1 = obstacle
        self.grid_height, self.grid_width = grid.shape
    
    def find_path(self, start: Tuple[int, int], 
                  goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find shortest path using A*"""
        
        def heuristic(a, b):
            # Manhattan distance
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        def get_neighbors(pos):
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0),
                           (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                nx, ny = pos[0] + dx, pos[1] + dy
                if 0 <= nx < self.grid_height and 0 <= ny < self.grid_width:
                    if self.grid[nx, ny] == 0:  # Walkable
                        neighbors.append((nx, ny))
            return neighbors
        
        open_set = {start}
        came_from = {}
        g_score = defaultdict(lambda: float('inf'))
        g_score[start] = 0
        f_score = defaultdict(lambda: float('inf'))
        f_score[start] = heuristic(start, goal)
        
        while open_set:
            current = min(open_set, key=lambda x: f_score[x])
            
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            open_set.remove(current)
            
            for neighbor in get_neighbors(current):
                tentative_g = g_score[current] + 1
                
                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
        
        return []  # No path found

class NeuralNetwork:
    """Simple neural network for game AI"""
    
    def __init__(self, layers: List[int]):
        self.layers = layers
        self.weights = []
        self.biases = []
        
        # Initialize weights with Xavier initialization
        for i in range(len(layers) - 1):
            limit = np.sqrt(6 / (layers[i] + layers[i+1]))
            w = np.random.uniform(-limit, limit, (layers[i], layers[i+1]))
            b = np.zeros((1, layers[i+1]))
            self.weights.append(w)
            self.biases.append(b)
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass"""
        activation = x
        for i in range(len(self.weights)):
            z = np.dot(activation, self.weights[i]) + self.biases[i]
            activation = self._sigmoid(z)  # Could use ReLU for hidden layers
        return activation
    
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Sigmoid activation function"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def train(self, X: np.ndarray, y: np.ndarray, 
              epochs: int = 1000, learning_rate: float = 0.1):
        """Train using backpropagation"""
        for epoch in range(epochs):
            # Forward pass
            layer_outputs = [X]
            for i in range(len(self.weights)):
                z = np.dot(layer_outputs[-1], self.weights[i]) + self.biases[i]
                layer_outputs.append(self._sigmoid(z))
            
            # Backward pass
            error = y - layer_outputs[-1]
            deltas = [error * self._sigmoid_derivative(layer_outputs[-1])]
            
            for i in range(len(self.weights) - 1, 0, -1):
                error = np.dot(deltas[0], self.weights[i].T)
                delta = error * self._sigmoid_derivative(layer_outputs[i])
                deltas.insert(0, delta)
            
            # Update weights
            for i in range(len(self.weights)):
                self.weights[i] += learning_rate * np.dot(layer_outputs[i].T, deltas[i])
                self.biases[i] += learning_rate * np.sum(deltas[i], axis=0, keepdims=True)
    
    def _sigmoid_derivative(self, x: np.ndarray) -> np.ndarray:
        """Derivative of sigmoid"""
        return x * (1 - x)

class StateMachine:
    """Finite State Machine for AI behavior"""
    
    def __init__(self):
        self.states = {}
        self.current_state = None
        self.variables = {}
    
    def add_state(self, name: str, enter_fn=None, update_fn=None, exit_fn=None):
        """Add a state to the machine"""
        self.states[name] = {
            'enter': enter_fn or (lambda: None),
            'update': update_fn or (lambda dt: None),
            'exit': exit_fn or (lambda: None),
            'transitions': []
        }
    
    def add_transition(self, from_state: str, to_state: str, condition_fn):
        """Add transition between states"""
        self.states[from_state]['transitions'].append({
            'target': to_state,
            'condition': condition_fn
        })
    
    def set_state(self, state_name: str):
        """Change current state"""
        if self.current_state and self.current_state in self.states:
            self.states[self.current_state]['exit']()
        self.current_state = state_name
        self.states[self.current_state]['enter']()
    
    def update(self, dt: float):
        """Update current state and check transitions"""
        if not self.current_state:
            return
        
        # Check transitions
        state = self.states[self.current_state]
        for transition in state['transitions']:
            if transition['condition'](self.variables):
                self.set_state(transition['target'])
                break
        
        # Update current state
        self.states[self.current_state]['update'](dt)

class ReinforcementLearner:
    """Q-Learning agent for game AI"""
    
    def __init__(self, state_size: int, action_size: int, 
                 learning_rate: float = 0.1, discount_factor: float = 0.95,
                 exploration_rate: float = 1.0, exploration_decay: float = 0.995):
        self.state_size = state_size
        self.action_size = action_size
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        self.epsilon_decay = exploration_decay
        self.epsilon_min = 0.01
        
        # Q-table
        self.q_table = {}
    
    def get_action(self, state: tuple, explore: bool = True) -> int:
        """Choose action using epsilon-greedy policy"""
        if explore and random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.action_size)
        
        return np.argmax(self.q_table[state])
    
    def learn(self, state: tuple, action: int, reward: float, 
              next_state: tuple, done: bool = False):
        """Update Q-values using Q-learning algorithm"""
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.action_size)
        
        if next_state not in self.q_table:
            self.q_table[next_state] = np.zeros(self.action_size)
        
        current_q = self.q_table[state][action]
        
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(self.q_table[next_state])
        
        self.q_table[state][action] += self.lr * (target - current_q)
        
        if done:
            self.epsilon = max(self.epsilon_min, 
                             self.epsilon * self.epsilon_decay)
    
    def save_model(self, filepath: str):
        """Save Q-table to file"""
        np.save(filepath, self.q_table)
    
    def load_model(self, filepath: str):
        """Load Q-table from file"""
        self.q_table = np.load(filepath, allow_pickle=True).item()