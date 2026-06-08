"""
Neural Network Implementation
Feedforward, activation functions, backpropagation, mini-batch SGD
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
import pickle

class Activation:
    @staticmethod
    def sigmoid(x: np.ndarray) -> np.ndarray:
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    @staticmethod
    def sigmoid_derivative(x: np.ndarray) -> np.ndarray:
        s = Activation.sigmoid(x)
        return s * (1 - s)
    
    @staticmethod
    def relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)
    
    @staticmethod
    def relu_derivative(x: np.ndarray) -> np.ndarray:
        return (x > 0).astype(float)
    
    @staticmethod
    def tanh(x: np.ndarray) -> np.ndarray:
        return np.tanh(x)
    
    @staticmethod
    def tanh_derivative(x: np.ndarray) -> np.ndarray:
        return 1 - np.tanh(x) ** 2
    
    @staticmethod
    def softmax(x: np.ndarray) -> np.ndarray:
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

class Layer:
    """Fully connected layer"""
    def __init__(self, input_size: int, output_size: int, activation: str = "relu"):
        self.weights = np.random.randn(input_size, output_size) * np.sqrt(2.0 / input_size)
        self.biases = np.zeros((1, output_size))
        self.activation = activation
        
        # Cache for backprop
        self.input = None
        self.output = None
        self.z = None  # pre-activation
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        self.input = x
        self.z = np.dot(x, self.weights) + self.biases
        if self.activation == "sigmoid":
            self.output = Activation.sigmoid(self.z)
        elif self.activation == "relu":
            self.output = Activation.relu(self.z)
        elif self.activation == "tanh":
            self.output = Activation.tanh(self.z)
        elif self.activation == "softmax":
            self.output = Activation.softmax(self.z)
        else:  # linear
            self.output = self.z
        return self.output
    
    def backward(self, grad_output: np.ndarray, learning_rate: float) -> np.ndarray:
        if self.activation == "sigmoid":
            grad_z = grad_output * Activation.sigmoid_derivative(self.z)
        elif self.activation == "relu":
            grad_z = grad_output * Activation.relu_derivative(self.z)
        elif self.activation == "tanh":
            grad_z = grad_output * Activation.tanh_derivative(self.z)
        else:
            grad_z = grad_output
        
        grad_weights = np.dot(self.input.T, grad_z)
        grad_biases = np.sum(grad_z, axis=0, keepdims=True)
        grad_input = np.dot(grad_z, self.weights.T)
        
        # Update parameters
        self.weights -= learning_rate * grad_weights
        self.biases -= learning_rate * grad_biases
        
        return grad_input

class NeuralNetwork:
    """Multi-layer neural network"""
    def __init__(self, layer_sizes: List[int], activations: List[str] = None):
        self.layers = []
        if activations is None:
            activations = ["relu"] * (len(layer_sizes)-2) + ["softmax" if layer_sizes[-1] > 1 else "sigmoid"]
        
        for i in range(len(layer_sizes)-1):
            self.layers.append(Layer(layer_sizes[i], layer_sizes[i+1], activations[i]))
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        for layer in self.layers:
            x = layer.forward(x)
        return x
    
    def backward(self, loss_grad: np.ndarray, learning_rate: float):
        grad = loss_grad
        for layer in reversed(self.layers):
            grad = layer.backward(grad, learning_rate)
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, 
              learning_rate: float = 0.01, batch_size: int = 32, 
              loss_fn: str = "mse"):
        n_samples = X.shape[0]
        for epoch in range(epochs):
            # Shuffle data
            indices = np.random.permutation(n_samples)
            X_shuffled = X[indices]
            y_shuffled = y[indices]
            
            total_loss = 0
            for start in range(0, n_samples, batch_size):
                end = start + batch_size
                X_batch = X_shuffled[start:end]
                y_batch = y_shuffled[start:end]
                
                # Forward
                predictions = self.forward(X_batch)
                
                # Loss gradient
                if loss_fn == "mse":
                    loss_grad = 2 * (predictions - y_batch) / batch_size
                    batch_loss = np.mean((predictions - y_batch) ** 2)
                elif loss_fn == "cross_entropy":
                    # Expects softmax output and one-hot y
                    loss_grad = (predictions - y_batch) / batch_size
                    batch_loss = -np.mean(np.sum(y_batch * np.log(predictions + 1e-8), axis=1))
                else:
                    raise ValueError("Unknown loss function")
                
                total_loss += batch_loss * (end - start)
                
                # Backward
                self.backward(loss_grad, learning_rate)
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}, Loss: {total_loss/n_samples:.4f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.forward(X)
    
    def save(self, filepath: str):
        with open(filepath, 'wb') as f:
            pickle.dump(self.layers, f)
    
    def load(self, filepath: str):
        with open(filepath, 'rb') as f:
            self.layers = pickle.load(f)