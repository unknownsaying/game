"""
AetherEngine AI System
Comprehensive AI framework with behavior trees, neural networks,
reinforcement learning, pathfinding, and decision making
"""

import numpy as np
import math
import random
import pickle
import json
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import heapq
import time

from system import (
    System, SystemConfig, SystemPriority, SystemState,
    Entity, EntityQuery, SystemManager
)

# ============================================================================
# AI Core Types and Enums
# ============================================================================

class AIState(Enum):
    """AI agent states"""
    IDLE = "idle"
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    FLEE = "flee"
    SEARCH = "search"
    INTERACT = "interact"
    DEAD = "dead"

class BehaviorStatus(Enum):
    """Behavior tree node execution status"""
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"

class PersonalityTrait(Enum):
    """AI personality traits"""
    AGGRESSION = "aggression"
    CAUTION = "caution"
    CURIOSITY = "curiosity"
    LOYALTY = "loyalty"
    INTELLIGENCE = "intelligence"

# ============================================================================
# Utility Functions
# ============================================================================

def sigmoid(x: float) -> float:
    """Sigmoid activation function"""
    return 1.0 / (1.0 + math.exp(-max(-500, min(500, x))))

def relu(x: float) -> float:
    """ReLU activation function"""
    return max(0.0, x)

def tanh(x: float) -> float:
    """Hyperbolic tangent activation"""
    return math.tanh(x)

def softmax(x: np.ndarray) -> np.ndarray:
    """Softmax function"""
    exp_x = np.exp(x - np.max(x))
    return exp_x / exp_x.sum()

def gaussian(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    """Gaussian function"""
    return math.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

# ============================================================================
# AI Configurations
# ============================================================================

@dataclass
class AIConfig:
    """Configuration for AI agents"""
    # Perception
    vision_range: float = 300.0
    vision_angle: float = math.radians(120)  # Field of view
    hearing_range: float = 500.0
    
    # Movement
    move_speed: float = 150.0
    rotation_speed: float = math.radians(180)
    acceleration: float = 300.0
    
    # Combat
    attack_range: float = 50.0
    attack_cooldown: float = 1.0
    damage: float = 10.0
    max_health: float = 100.0
    
    # Behavior
    reaction_time: float = 0.3
    memory_duration: float = 10.0
    patrol_radius: float = 200.0
    
    # Personality (0.0 to 1.0)
    aggression: float = 0.5
    caution: float = 0.5
    curiosity: float = 0.5
    
    # Decision making
    decision_interval: float = 0.1
    max_options: int = 5
    
    # Learning
    learning_enabled: bool = False
    learning_rate: float = 0.01
    discount_factor: float = 0.95

# ============================================================================
# Blackboard - Shared Knowledge
# ============================================================================

class Blackboard:
    """
    Shared knowledge base for AI agents
    Allows agents to share information and coordinate
    """
    
    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.events: Dict[str, List[float]] = defaultdict(list)  # event -> timestamps
        self.tags: Dict[str, Set[str]] = defaultdict(set)  # tag -> entity IDs
        self._lock = threading.Lock() if 'threading' in dir() else None
    
    def set(self, key: str, value: Any):
        """Set a value in the blackboard"""
        self.data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the blackboard"""
        return self.data.get(key, default)
    
    def add_event(self, event_type: str, location: Any = None):
        """Record an event"""
        self.events[event_type].append(time.time())
        if location is not None:
            self.set(f"event_{event_type}_location", location)
    
    def get_recent_events(self, event_type: str, max_age: float = 5.0) -> int:
        """Get number of recent events of a type"""
        now = time.time()
        timestamps = self.events.get(event_type, [])
        return sum(1 for t in timestamps if now - t < max_age)
    
    def tag_entity(self, entity_id: str, tag: str):
        """Tag an entity for coordination"""
        self.tags[tag].add(entity_id)
    
    def get_tagged_entities(self, tag: str) -> Set[str]:
        """Get entities with a specific tag"""
        return self.tags.get(tag, set())
    
    def clear(self):
        """Clear all blackboard data"""
        self.data.clear()
        self.events.clear()
        self.tags.clear()

# ============================================================================
# Perception System
# ============================================================================

class PerceptionSystem:
    """
    AI Perception - senses the environment
    Handles vision, hearing, and memory
    """
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.known_entities: Dict[str, float] = {}  # entity_id -> last_seen_time
        self.entity_positions: Dict[str, np.ndarray] = {}
        self.memory: deque = deque(maxlen=100)
        self.awareness_level: float = 0.0  # 0.0 = unaware, 1.0 = fully alert
    
    def update_perception(self, 
                         agent_position: np.ndarray,
                         agent_rotation: float,
                         entities: List[Entity],
                         dt: float):
        """Update what the agent can perceive"""
        now = time.time()
        
        # Clean old memories
        expired = []
        for entity_id, last_seen in self.known_entities.items():
            if now - last_seen > self.config.memory_duration:
                expired.append(entity_id)
        for entity_id in expired:
            del self.known_entities[entity_id]
            if entity_id in self.entity_positions:
                del self.entity_positions[entity_id]
        
        # Check each entity
        for entity in entities:
            if not entity.active:
                continue
            
            # Get entity position
            entity_pos = self._get_entity_position(entity)
            if entity_pos is None:
                continue
            
            # Check visibility
            if self._can_see(agent_position, agent_rotation, entity_pos):
                self.known_entities[entity.id] = now
                self.entity_positions[entity.id] = entity_pos
                self.memory.append({
                    'type': 'sight',
                    'entity_id': entity.id,
                    'position': entity_pos.copy(),
                    'timestamp': now
                })
    
    def _get_entity_position(self, entity: Entity) -> Optional[np.ndarray]:
        """Extract position from entity"""
        if hasattr(entity, 'transform'):
            return entity.transform.position.copy()
        return None
    
    def _can_see(self, agent_pos: np.ndarray, agent_rot: float, 
                target_pos: np.ndarray) -> bool:
        """Check if agent can see the target"""
        # Calculate distance
        direction = target_pos - agent_pos
        distance = np.linalg.norm(direction)
        
        # Check range
        if distance > self.config.vision_range:
            return False
        
        # Check angle (field of view)
        if self.config.vision_angle < 2 * math.pi:
            agent_forward = np.array([math.cos(agent_rot), math.sin(agent_rot)])
            angle = math.acos(np.dot(agent_forward, direction) / (max(0.001, distance)))
            
            if angle > self.config.vision_angle / 2:
                return False
        
        return True
    
    def get_known_entities(self) -> List[str]:
        """Get list of known entity IDs"""
        now = time.time()
        return [eid for eid, t in self.known_entities.items() 
                if now - t < self.config.memory_duration]
    
    def get_last_known_position(self, entity_id: str) -> Optional[np.ndarray]:
        """Get last known position of an entity"""
        return self.entity_positions.get(entity_id)

# ============================================================================
# Behavior Tree
# ============================================================================

class BehaviorNode:
    """Base class for behavior tree nodes"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.parent: Optional['BehaviorNode'] = None
        self.children: List['BehaviorNode'] = []
        self.status = BehaviorStatus.RUNNING
    
    def execute(self, context: Dict[str, Any]) -> BehaviorStatus:
        """Execute the node"""
        raise NotImplementedError
    
    def add_child(self, child: 'BehaviorNode'):
        """Add a child node"""
        child.parent = self
        self.children.append(child)
    
    def reset(self):
        """Reset node state"""
        self.status = BehaviorStatus.RUNNING
        for child in self.children:
            child.reset()

class Sequence(BehaviorNode):
    """Execute children in sequence until one fails"""
    
    def execute(self, context: Dict[str, Any]) -> BehaviorStatus:
        for child in self.children:
            self.status = child.execute(context)
            if self.status != BehaviorStatus.SUCCESS:
                return self.status
        return BehaviorStatus.SUCCESS

class Selector(BehaviorNode):
    """Execute children until one succeeds"""
    
    def execute(self, context: Dict[str, Any]) -> BehaviorStatus:
        for child in self.children:
            self.status = child.execute(context)
            if self.status != BehaviorStatus.FAILURE:
                return self.status
        return BehaviorStatus.FAILURE

class Parallel(BehaviorNode):
    """Execute all children in parallel"""
    
    def __init__(self, name: str = "", required_successes: int = 1):
        super().__init__(name)
        self.required_successes = required_successes
    
    def execute(self, context: Dict[str, Any]) -> BehaviorStatus:
        successes = 0
        failures = 0
        
        for child in self.children:
            status = child.execute(context)
            if status == BehaviorStatus.SUCCESS:
                successes += 1
            elif status == BehaviorStatus.FAILURE:
                failures += 1
        
        if successes >= self.required_successes:
            return BehaviorStatus.SUCCESS
        if failures > len(self.children) - self.required_successes:
            return BehaviorStatus.FAILURE
        return BehaviorStatus.RUNNING

class Condition(BehaviorNode):
    """Check a condition"""
    
    def __init__(self, condition_fn: Callable[[Dict[str, Any]], bool], name: str = ""):
        super().__init__(name)
        self.condition_fn = condition_fn
    
    def execute(self, context: Dict[str, Any]) -> BehaviorStatus:
        return BehaviorStatus.SUCCESS if self.condition_fn(context) else BehaviorStatus.FAILURE

class Action(BehaviorNode):
    """Perform an action"""
    
    def __init__(self, action_fn: Callable[[Dict[str, Any]], BehaviorStatus], name: str = ""):
        super().__init__(name)
        self.action_fn = action_fn
    
    def execute(self, context: Dict[str, Any]) -> BehaviorStatus:
        return self.action_fn(context)

class Decorator(BehaviorNode):
    """Decorator node that modifies child behavior"""
    
    def __init__(self, child: BehaviorNode, name: str = ""):
        super().__init__(name)
        self.add_child(child)

class Inverter(Decorator):
    """Invert child's result"""
    
    def execute(self, context: Dict[str, Any]) -> BehaviorStatus:
        status = self.children[0].execute(context)
        if status == BehaviorStatus.SUCCESS:
            return BehaviorStatus.FAILURE
        elif status == BehaviorStatus.FAILURE:
            return BehaviorStatus.SUCCESS
        return status

class Repeater(Decorator):
    """Repeat child N times"""
    
    def __init__(self, child: BehaviorNode, times: int = -1, name: str = ""):
        super().__init__(child, name)
        self.times = times
        self._count = 0
    
    def execute(self, context: Dict[str, Any]) -> BehaviorStatus:
        if self.times >= 0 and self._count >= self.times:
            return BehaviorStatus.SUCCESS
        
        status = self.children[0].execute(context)
        if status == BehaviorStatus.SUCCESS:
            self._count += 1
            if self.times < 0 or self._count < self.times:
                return BehaviorStatus.RUNNING
            self._count = 0
            return BehaviorStatus.SUCCESS
        elif status == BehaviorStatus.FAILURE:
            self._count = 0
            return BehaviorStatus.FAILURE
        return status
    
    def reset(self):
        super().reset()
        self._count = 0

class BehaviorTree:
    """Complete behavior tree"""
    
    def __init__(self, root: BehaviorNode = None):
        self.root = root
        self.blackboard: Dict[str, Any] = {}
    
    def execute(self) -> BehaviorStatus:
        """Execute the behavior tree"""
        if self.root:
            return self.root.execute(self.blackboard)
        return BehaviorStatus.FAILURE
    
    def reset(self):
        """Reset the entire tree"""
        if self.root:
            self.root.reset()

# ============================================================================
# Finite State Machine
# ============================================================================

class FSMState:
    """State in a finite state machine"""
    
    def __init__(self, name: str):
        self.name = name
        self.enter: Optional[Callable] = None
        self.update: Optional[Callable[[float], None]] = None
        self.exit: Optional[Callable] = None
        self.transitions: List['FSMTransition'] = []

class FSMTransition:
    """Transition between FSM states"""
    
    def __init__(self, target: FSMState, condition: Callable[[], bool]):
        self.target = target
        self.condition = condition

class FiniteStateMachine:
    """Finite State Machine for AI behavior"""
    
    def __init__(self):
        self.states: Dict[str, FSMState] = {}
        self.current_state: Optional[FSMState] = None
        self.previous_state: Optional[FSMState] = None
    
    def add_state(self, state: FSMState):
        """Add a state to the machine"""
        self.states[state.name] = state
    
    def add_transition(self, from_state: str, to_state: str, 
                      condition: Callable[[], bool]):
        """Add a transition between states"""
        if from_state in self.states and to_state in self.states:
            self.states[from_state].transitions.append(
                FSMTransition(self.states[to_state], condition)
            )
    
    def set_state(self, state_name: str):
        """Force a state change"""
        if state_name not in self.states:
            return
        
        if self.current_state:
            if self.current_state.exit:
                self.current_state.exit()
            self.previous_state = self.current_state
        
        self.current_state = self.states[state_name]
        if self.current_state.enter:
            self.current_state.enter()
    
    def update(self, dt: float):
        """Update the state machine"""
        if not self.current_state:
            return
        
        # Check transitions
        for transition in self.current_state.transitions:
            if transition.condition():
                self.set_state(transition.target.name)
                break
        
        # Update current state
        if self.current_state and self.current_state.update:
            self.current_state.update(dt)

# ============================================================================
# Pathfinding
# ============================================================================

class PathNode:
    """Node for pathfinding"""
    def __init__(self, position: Tuple[int, int], g: float = float('inf'),
                 h: float = 0.0, parent: Optional['PathNode'] = None):
        self.position = position
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent
    
    def __lt__(self, other):
        return self.f < other.f

class Pathfinder:
    """A* pathfinding with support for dynamic obstacles"""
    
    def __init__(self, grid: np.ndarray):
        self.grid = grid
        self.height, self.width = grid.shape
        self.dynamic_obstacles: Set[Tuple[int, int]] = set()
    
    def set_grid(self, grid: np.ndarray):
        """Update the navigation grid"""
        self.grid = grid
        self.height, self.width = grid.shape
    
    def add_obstacle(self, position: Tuple[int, int]):
        """Add a dynamic obstacle"""
        self.dynamic_obstacles.add(position)
    
    def remove_obstacle(self, position: Tuple[int, int]):
        """Remove a dynamic obstacle"""
        self.dynamic_obstacles.discard(position)
    
    def is_walkable(self, position: Tuple[int, int]) -> bool:
        """Check if a position is walkable"""
        x, y = position
        if not (0 <= x < self.height and 0 <= y < self.width):
            return False
        if position in self.dynamic_obstacles:
            return False
        return self.grid[x, y] >= 0
    
    def find_path(self, start: Tuple[int, int], 
                 goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find path using A* algorithm"""
        if not self.is_walkable(goal):
            return []
        
        open_list = []
        closed_set = set()
        
        start_node = PathNode(start, g=0, h=self._heuristic(start, goal))
        heapq.heappush(open_list, start_node)
        
        while open_list:
            current = heapq.heappop(open_list)
            
            if current.position == goal:
                # Reconstruct path
                path = []
                while current:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]
            
            closed_set.add(current.position)
            
            # Check neighbors
            for neighbor_pos in self._get_neighbors(current.position):
                if neighbor_pos in closed_set:
                    continue
                
                if not self.is_walkable(neighbor_pos):
                    continue
                
                # Calculate costs
                move_cost = 1.414 if neighbor_pos[0] != current.position[0] and \
                                     neighbor_pos[1] != current.position[1] else 1.0
                g = current.g + move_cost
                
                # Check if this path is better
                neighbor_node = PathNode(
                    neighbor_pos,
                    g=g,
                    h=self._heuristic(neighbor_pos, goal),
                    parent=current
                )
                
                # Find existing node in open list
                existing = None
                for node in open_list:
                    if node.position == neighbor_pos:
                        existing = node
                        break
                
                if existing:
                    if g < existing.g:
                        existing.g = g
                        existing.f = g + existing.h
                        existing.parent = current
                else:
                    heapq.heappush(open_list, neighbor_node)
        
        return []  # No path found
    
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Octile distance heuristic"""
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)
    
    def _get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get 8-directional neighbors"""
        x, y = position
        neighbors = []
        for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            neighbors.append((x+dx, y+dy))
        return neighbors
    
    def smooth_path(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Smooth path using line of sight"""
        if len(path) <= 2:
            return path
        
        smoothed = [path[0]]
        i = 0
        while i < len(path) - 1:
            for j in range(len(path) - 1, i, -1):
                if self._line_of_sight(path[i], path[j]):
                    smoothed.append(path[j])
                    i = j
                    break
            else:
                i += 1
                smoothed.append(path[i])
        
        return smoothed
    
    def _line_of_sight(self, p1: Tuple[int, int], 
                      p2: Tuple[int, int]) -> bool:
        """Check line of sight between two points"""
        x0, y0 = p1
        x1, y1 = p2
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            if not self.is_walkable((x0, y0)):
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

# ============================================================================
# Neural Network
# ============================================================================

class Layer:
    """Neural network layer"""
    
    def __init__(self, input_size: int, output_size: int, 
                 activation: str = "relu"):
        # Xavier initialization
        limit = math.sqrt(6.0 / (input_size + output_size))
        self.weights = np.random.uniform(-limit, limit, (input_size, output_size))
        self.biases = np.zeros((1, output_size))
        self.activation = activation
        
        # Cache for backpropagation
        self.input = None
        self.output = None
        self.z = None  # Pre-activation
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass"""
        self.input = x
        self.z = np.dot(x, self.weights) + self.biases
        
        if self.activation == "sigmoid":
            self.output = 1.0 / (1.0 + np.exp(-np.clip(self.z, -500, 500)))
        elif self.activation == "relu":
            self.output = np.maximum(0, self.z)
        elif self.activation == "tanh":
            self.output = np.tanh(self.z)
        elif self.activation == "softmax":
            exp_z = np.exp(self.z - np.max(self.z, axis=1, keepdims=True))
            self.output = exp_z / np.sum(exp_z, axis=1, keepdims=True)
        else:
            self.output = self.z
        
        return self.output
    
    def backward(self, grad_output: np.ndarray, 
                learning_rate: float) -> np.ndarray:
        """Backward pass"""
        if self.activation == "sigmoid":
            grad_z = grad_output * self.output * (1 - self.output)
        elif self.activation == "relu":
            grad_z = grad_output * (self.z > 0).astype(float)
        elif self.activation == "tanh":
            grad_z = grad_output * (1 - self.output ** 2)
        else:
            grad_z = grad_output
        
        grad_weights = np.dot(self.input.T, grad_z)
        grad_biases = np.sum(grad_z, axis=0, keepdims=True)
        grad_input = np.dot(grad_z, self.weights.T)
        
        self.weights -= learning_rate * grad_weights
        self.biases -= learning_rate * grad_biases
        
        return grad_input

class NeuralNetwork:
    """Multi-layer neural network"""
    
    def __init__(self, layer_sizes: List[int], 
                 activations: List[str] = None):
        self.layers = []
        if activations is None:
            activations = ["relu"] * (len(layer_sizes) - 2) + ["linear"]
        
        for i in range(len(layer_sizes) - 1):
            self.layers.append(Layer(layer_sizes[i], layer_sizes[i+1], activations[i]))
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass through all layers"""
        for layer in self.layers:
            x = layer.forward(x)
        return x
    
    def backward(self, loss_grad: np.ndarray, learning_rate: float):
        """Backward pass through all layers"""
        grad = loss_grad
        for layer in reversed(self.layers):
            grad = layer.backward(grad, learning_rate)
    
    def train(self, X: np.ndarray, y: np.ndarray, 
              epochs: int = 100, learning_rate: float = 0.01,
              batch_size: int = 32) -> List[float]:
        """Train the network"""
        losses = []
        n_samples = X.shape[0]
        
        for epoch in range(epochs):
            # Shuffle data
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            
            epoch_loss = 0
            for start in range(0, n_samples, batch_size):
                end = min(start + batch_size, n_samples)
                X_batch = X_shuffled[start:end]
                y_batch = y_shuffled[start:end]
                
                # Forward
                predictions = self.forward(X_batch)
                
                # MSE Loss
                loss = np.mean((predictions - y_batch) ** 2)
                epoch_loss += loss * (end - start)
                
                # Backward
                loss_grad = 2 * (predictions - y_batch) / (end - start)
                self.backward(loss_grad, learning_rate)
            
            avg_loss = epoch_loss / n_samples
            losses.append(avg_loss)
        
        return losses
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        return self.forward(X)
    
    def save(self, filepath: str):
        """Save network to file"""
        with open(filepath, 'wb') as f:
            pickle.dump(self.layers, f)
    
    @classmethod
    def load(cls, filepath: str) -> 'NeuralNetwork':
        """Load network from file"""
        nn = cls.__new__(cls)
        with open(filepath, 'rb') as f:
            nn.layers = pickle.load(f)
        return nn

# ============================================================================
# Reinforcement Learning
# ============================================================================

class QLearningAgent:
    """Q-Learning agent"""
    
    def __init__(self, state_size: int, action_size: int,
                 learning_rate: float = 0.1, discount: float = 0.95,
                 epsilon: float = 1.0, epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01):
        self.state_size = state_size
        self.action_size = action_size
        self.lr = learning_rate
        self.gamma = discount
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_table = np.zeros((state_size, action_size))
    
    def choose_action(self, state: int) -> int:
        """Choose action using epsilon-greedy policy"""
        if np.random.random() < self.epsilon:
            return np.random.randint(self.action_size)
        return np.argmax(self.q_table[state])
    
    def learn(self, state: int, action: int, reward: float,
             next_state: int, done: bool):
        """Update Q-values"""
        current_q = self.q_table[state, action]
        
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(self.q_table[next_state])
        
        self.q_table[state, action] += self.lr * (target - current_q)
        
        if done:
            self.epsilon = max(self.epsilon_min, 
                             self.epsilon * self.epsilon_decay)

# ============================================================================
# AI Agent
# ============================================================================

class AIAgent:
    """
    Complete AI Agent that combines all AI systems
    Can be attached to any entity for intelligent behavior
    """
    
    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        self.perception = PerceptionSystem(self.config)
        self.behavior_tree: Optional[BehaviorTree] = None
        self.state_machine: Optional[FiniteStateMachine] = None
        self.pathfinder: Optional[Pathfinder] = None
        self.neural_network: Optional[NeuralNetwork] = None
        self.q_agent: Optional[QLearningAgent] = None
        self.blackboard = Blackboard()
        
        # Current state
        self.current_path: List[Tuple[int, int]] = []
        self.target_entity: Optional[str] = None
        self.state = AIState.IDLE
        self.health = self.config.max_health
        
        # Timers
        self.attack_cooldown_timer = 0.0
        self.decision_timer = 0.0
        
        # Setup default behavior tree
        self._setup_default_behavior_tree()
        self._setup_default_state_machine()
    
    def _setup_default_behavior_tree(self):
        """Setup default combat behavior tree"""
        # Root: Selector for priority-based behavior
        root = Selector("Root")
        
        # Death check
        death_seq = Sequence("Death")
        death_seq.add_child(Condition(
            lambda ctx: ctx.get('health', 100) <= 0,
            "IsDead"
        ))
        death_seq.add_child(Action(
            lambda ctx: self._action_die(ctx),
            "Die"
        ))
        root.add_child(death_seq)
        
        # Combat sequence
        combat_seq = Sequence("Combat")
        combat_seq.add_child(Condition(
            lambda ctx: self._has_target(ctx),
            "HasTarget"
        ))
        combat_seq.add_child(Condition(
            lambda ctx: self._is_target_in_range(ctx),
            "InRange"
        ))
        combat_seq.add_child(Action(
            lambda ctx: self._action_attack(ctx),
            "Attack"
        ))
        root.add_child(combat_seq)
        
        # Chase sequence
        chase_seq = Sequence("Chase")
        chase_seq.add_child(Condition(
            lambda ctx: self._has_target(ctx),
            "HasTarget"
        ))
        chase_seq.add_child(Action(
            lambda ctx: self._action_chase(ctx),
            "Chase"
        ))
        root.add_child(chase_seq)
        
        # Idle action
        root.add_child(Action(
            lambda ctx: self._action_idle(ctx),
            "Idle"
        ))
        
        self.behavior_tree = BehaviorTree(root)
    
    def _setup_default_state_machine(self):
        """Setup default state machine"""
        self.state_machine = FiniteStateMachine()
        
        # Create states
        idle_state = FSMState("idle")
        idle_state.update = lambda dt: self._update_idle(dt)
        
        patrol_state = FSMState("patrol")
        patrol_state.update = lambda dt: self._update_patrol(dt)
        
        chase_state = FSMState("chase")
        chase_state.update = lambda dt: self._update_chase(dt)
        
        attack_state = FSMState("attack")
        attack_state.update = lambda dt: self._update_attack(dt)
        
        flee_state = FSMState("flee")
        flee_state.update = lambda dt: self._update_flee(dt)
        
        # Add states
        for state in [idle_state, patrol_state, chase_state, attack_state, flee_state]:
            self.state_machine.add_state(state)
        
        # Add transitions
        self.state_machine.add_transition("idle", "patrol",
            lambda: random.random() < 0.01)
        self.state_machine.add_transition("patrol", "chase",
            lambda: self._has_target(self.behavior_tree.blackboard))
        self.state_machine.add_transition("chase", "attack",
            lambda: self._is_target_in_range(self.behavior_tree.blackboard))
        self.state_machine.add_transition("attack", "flee",
            lambda: self.health < self.config.max_health * 0.2)
    
    def update(self, dt: float, agent_position: np.ndarray,
              agent_rotation: float, entities: List[Entity]):
        """Update AI agent"""
        # Update perception
        self.perception.update_perception(agent_position, agent_rotation, entities, dt)
        
        # Update timers
        self.attack_cooldown_timer = max(0, self.attack_cooldown_timer - dt)
        
        # Update blackboard
        self.behavior_tree.blackboard['position'] = agent_position
        self.behavior_tree.blackboard['rotation'] = agent_rotation
        self.behavior_tree.blackboard['health'] = self.health
        self.behavior_tree.blackboard['dt'] = dt
        self.behavior_tree.blackboard['entities'] = entities
        
        # Execute behavior tree
        self.behavior_tree.execute()
        
        # Update state machine
        self.state_machine.update(dt)
    
    def _has_target(self, context: Dict) -> bool:
        """Check if agent has a target"""
        return self.target_entity is not None
    
    def _is_target_in_range(self, context: Dict) -> bool:
        """Check if target is in attack range"""
        if not self.target_entity:
            return False
        
        target_pos = self.perception.get_last_known_position(self.target_entity)
        if target_pos is None:
            return False
        
        agent_pos = context.get('position', np.zeros(2))
        distance = np.linalg.norm(target_pos - agent_pos)
        return distance <= self.config.attack_range
    
    def _action_attack(self, context: Dict) -> BehaviorStatus:
        """Attack action"""
        if self.attack_cooldown_timer > 0:
            return BehaviorStatus.RUNNING
        
        self.attack_cooldown_timer = self.config.attack_cooldown
        self.state = AIState.ATTACK
        return BehaviorStatus.SUCCESS
    
    def _action_chase(self, context: Dict) -> BehaviorStatus:
        """Chase action"""
        self.state = AIState.CHASE
        return BehaviorStatus.RUNNING
    
    def _action_idle(self, context: Dict) -> BehaviorStatus:
        """Idle action"""
        self.state = AIState.IDLE
        return BehaviorStatus.RUNNING
    
    def _action_die(self, context: Dict) -> BehaviorStatus:
        """Death action"""
        self.state = AIState.DEAD
        return BehaviorStatus.SUCCESS
    
    def _update_idle(self, dt: float):
        """Update idle state"""
        pass
    
    def _update_patrol(self, dt: float):
        """Update patrol state"""
        pass
    
    def _update_chase(self, dt: float):
        """Update chase state"""
        pass
    
    def _update_attack(self, dt: float):
        """Update attack state"""
        pass
    
    def _update_flee(self, dt: float):
        """Update flee state"""
        pass
    
    def take_damage(self, damage: float):
        """Take damage"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.state = AIState.DEAD

# ============================================================================
# AI System - Engine Integration
# ============================================================================

class AISystem(System):
    """
    Main AI System that integrates with the engine
    Manages all AI agents and provides AI services
    """
    
    def __init__(self, engine: SystemManager):
        super().__init__(engine, SystemConfig(
            name="AISystem",
            priority=SystemPriority.HIGH,
            dependencies=["InputSystem"],
            tags={"ai", "intelligence"}
        ))
        
        self.agents: Dict[str, AIAgent] = {}
        self.shared_blackboard = Blackboard()
        self.nav_grid: Optional[np.ndarray] = None
        self.pathfinder: Optional[Pathfinder] = None
        
    def _on_initialize(self):
        """Initialize AI system"""
        logger.info("AI System initialized")
        
        # Subscribe to events
        self.engine.event_bus.subscribe("entity_created", self._on_entity_created)
        self.engine.event_bus.subscribe("entity_destroyed", self._on_entity_destroyed)
    
    def _on_entity_created(self, event_type: str, data: Any):
        """Handle entity creation"""
        pass
    
    def _on_entity_destroyed(self, event_type: str, data: Any):
        """Handle entity destruction"""
        if isinstance(data, Entity) and data.id in self.agents:
            del self.agents[data.id]
    
    def create_agent(self, entity_id: str, config: AIConfig = None) -> AIAgent:
        """Create an AI agent for an entity"""
        agent = AIAgent(config)
        self.agents[entity_id] = agent
        return agent
    
    def get_agent(self, entity_id: str) -> Optional[AIAgent]:
        """Get AI agent for an entity"""
        return self.agents.get(entity_id)
    
    def set_nav_grid(self, grid: np.ndarray):
        """Set navigation grid"""
        self.nav_grid = grid
        self.pathfinder = Pathfinder(grid)
    
    def _on_update(self, dt: float):
        """Update all AI agents"""
        # Query entities with AI components
        query = EntityQuery().with_tag("ai_controlled")
        ai_entities = self.engine.entity_manager.query(query)
        
        for entity in ai_entities:
            if entity.id in self.agents:
                agent = self.agents[entity.id]
                
                # Get entity transform
                position = np.zeros(2)
                rotation = 0.0
                if hasattr(entity, 'transform'):
                    position = entity.transform.position
                    rotation = entity.transform.rotation
                
                # Update agent
                agent.update(dt, position, rotation, 
                           self.engine.entity_manager.get_all_entities())
    
    def find_path(self, start: Tuple[int, int], 
                 goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find path using navigation grid"""
        if self.pathfinder:
            path = self.pathfinder.find_path(start, goal)
            return self.pathfinder.smooth_path(path)
        return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get AI system statistics"""
        stats = super().get_performance_stats()
        stats['active_agents'] = len(self.agents)
        stats['has_nav_grid'] = self.nav_grid is not None
        return stats