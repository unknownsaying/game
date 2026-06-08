"""
Reinforcement Learning Algorithms
Q-Learning, Deep Q-Network, Policy Gradient
"""

import numpy as np
import random
from collections import deque
from typing import List, Tuple, Any
import pickle

from .neural_network import NeuralNetwork

class QLearner:
    """Tabular Q-Learning"""
    def __init__(self, state_space: int, action_space: int,
                 learning_rate: float = 0.1, discount: float = 0.95,
                 epsilon: float = 1.0, epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01):
        self.state_space = state_space
        self.action_space = action_space
        self.lr = learning_rate
        self.gamma = discount
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_table = np.zeros((state_space, action_space))
    
    def choose_action(self, state: int) -> int:
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.action_space)
        return np.argmax(self.q_table[state])
    
    def learn(self, state: int, action: int, reward: float, next_state: int, done: bool):
        current_q = self.q_table[state, action]
        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(self.q_table[next_state])
        self.q_table[state, action] += self.lr * (target - current_q)
        if done:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def save(self, filename: str):
        np.save(filename, self.q_table)
    
    def load(self, filename: str):
        self.q_table = np.load(filename)

class ReplayBuffer:
    """Experience replay buffer"""
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int) -> List[Tuple]:
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))
    
    def __len__(self):
        return len(self.buffer)

class DeepQLearner:
    """Deep Q-Network with experience replay and target network"""
    def __init__(self, state_size: int, action_size: int,
                 hidden_layers: List[int] = [128, 128],
                 learning_rate: float = 0.001, discount: float = 0.99,
                 epsilon: float = 1.0, epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01, batch_size: int = 64,
                 memory_size: int = 10000, target_update_freq: int = 100):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = discount
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.update_counter = 0
        
        # Networks
        layer_sizes = [state_size] + hidden_layers + [action_size]
        activations = ["relu"] * len(hidden_layers) + ["linear"]
        self.q_network = NeuralNetwork(layer_sizes, activations)
        self.target_network = NeuralNetwork(layer_sizes, activations)
        self.target_network.layers = pickle.loads(pickle.dumps(self.q_network.layers))  # deep copy
        
        self.memory = ReplayBuffer(memory_size)
    
    def choose_action(self, state: np.ndarray) -> int:
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.action_size)
        state = state.reshape(1, -1)
        q_values = self.q_network.predict(state)
        return np.argmax(q_values[0])
    
    def learn(self):
        if len(self.memory) < self.batch_size:
            return
        
        batch = self.memory.sample(self.batch_size)
        states = np.array([x[0] for x in batch])
        actions = np.array([x[1] for x in batch])
        rewards = np.array([x[2] for x in batch])
        next_states = np.array([x[3] for x in batch])
        dones = np.array([x[4] for x in batch])
        
        # Get Q values
        q_values = self.q_network.predict(states)
        next_q_values = self.target_network.predict(next_states)
        
        # Create targets
        targets = q_values.copy()
        for i in range(self.batch_size):
            if dones[i]:
                targets[i, actions[i]] = rewards[i]
            else:
                targets[i, actions[i]] = rewards[i] + self.gamma * np.max(next_q_values[i])
        
        # Train network
        self.q_network.train(states, targets, epochs=1, learning_rate=0.001, batch_size=self.batch_size)
        
        self.update_counter += 1
        # Update target network
        if self.update_counter % self.target_update_freq == 0:
            self.target_network.layers = pickle.loads(pickle.dumps(self.q_network.layers))
        
        # Decay epsilon
        if np.mean(dones) > 0:
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.push(state, action, reward, next_state, done)
    
    def save(self, path: str):
        self.q_network.save(path + "_q.pkl")
        self.target_network.save(path + "_target.pkl")
    
    def load(self, path: str):
        self.q_network.load(path + "_q.pkl")
        self.target_network.load(path + "_target.pkl")