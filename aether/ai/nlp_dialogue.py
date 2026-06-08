"""
NLP Dialogue System
Intent classification, entity extraction, text generation using Markov chains and simple NNs
"""

import numpy as np
import re
from typing import List, Dict, Tuple, Optional
import random
import json
from collections import defaultdict, Counter

class IntentClassifier:
    """Simple bag-of-words intent classifier"""
    def __init__(self):
        self.intents = {}  # intent_name -> list of example phrases
        self.vocab = set()
        self.word_to_idx = {}
        self.intent_to_idx = {}
        self.weights = None  # simple logistic regression weights
    
    def add_intent(self, name: str, examples: List[str]):
        self.intents[name] = examples
        for phrase in examples:
            words = self._tokenize(phrase)
            self.vocab.update(words)
    
    def build(self):
        # Create vocabulary mapping
        self.word_to_idx = {word: i for i, word in enumerate(sorted(self.vocab))}
        self.intent_to_idx = {intent: i for i, intent in enumerate(self.intents.keys())}
        # Train simple classifier (multinomial logistic regression via SGD)
        n_features = len(self.vocab)
        n_classes = len(self.intents)
        self.weights = np.random.randn(n_features, n_classes) * 0.01
        self.biases = np.zeros(n_classes)
        
        # Prepare training data
        X = []
        y = []
        for intent, examples in self.intents.items():
            for phrase in examples:
                bow = self._bow(phrase)
                X.append(bow)
                y.append(self.intent_to_idx[intent])
        X = np.array(X)
        y = np.array(y)
        
        # Train softmax regression
        learning_rate = 0.1
        epochs = 100
        for _ in range(epochs):
            logits = np.dot(X, self.weights) + self.biases
            exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
            probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
            
            # One-hot encoding of y
            y_onehot = np.zeros((len(y), n_classes))
            y_onehot[np.arange(len(y)), y] = 1
            
            error = probs - y_onehot
            grad_w = np.dot(X.T, error) / len(y)
            grad_b = np.mean(error, axis=0)
            
            self.weights -= learning_rate * grad_w
            self.biases -= learning_rate * grad_b
    
    def classify(self, text: str) -> Tuple[str, float]:
        bow = self._bow(text)
        logits = np.dot(bow, self.weights) + self.biases
        probs = np.exp(logits - np.max(logits)) / np.sum(np.exp(logits - np.max(logits)))
        idx = np.argmax(probs)
        intent = list(self.intent_to_idx.keys())[list(self.intent_to_idx.values()).index(idx)]
        return intent, probs[idx]
    
    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\b\w+\b', text.lower())
    
    def _bow(self, text: str) -> np.ndarray:
        vec = np.zeros(len(self.vocab))
        words = self._tokenize(text)
        for word in words:
            if word in self.word_to_idx:
                vec[self.word_to_idx[word]] += 1
        return vec

class MarkovChainGenerator:
    """Text generation using Markov chains"""
    def __init__(self, order: int = 2):
        self.order = order
        self.chains = defaultdict(Counter)
        self.starts = []
    
    def train(self, corpus: List[str]):
        for text in corpus:
            tokens = text.split()
            if len(tokens) <= self.order:
                continue
            self.starts.append(tuple(tokens[:self.order]))
            for i in range(len(tokens) - self.order):
                state = tuple(tokens[i:i+self.order])
                next_word = tokens[i+self.order]
                self.chains[state][next_word] += 1
    
    def generate(self, max_length: int = 50, start: List[str] = None) -> str:
        if start and len(start) >= self.order:
            current = tuple(start[:self.order])
        elif self.starts:
            current = random.choice(self.starts)
        else:
            return ""
        
        result = list(current)
        for _ in range(max_length - self.order):
            if current not in self.chains or not self.chains[current]:
                # Fallback: pick from all possible next words based on frequency
                all_words = []
                for counter in self.chains.values():
                    all_words.extend(counter.elements())
                if not all_words:
                    break
                next_word = random.choice(all_words)
            else:
                # Weighted random choice
                words, counts = zip(*self.chains[current].items())
                total = sum(counts)
                probs = [c/total for c in counts]
                next_word = np.random.choice(words, p=probs)
            
            result.append(next_word)
            current = tuple(result[-self.order:])
        return ' '.join(result)

class DialogueSystem:
    """Full dialogue system combining intent classification and response generation"""
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.generator = MarkovChainGenerator(order=2)
        self.responses = defaultdict(list)  # intent -> list of response templates
        self.entity_extractors = {}  # entity_name -> regex pattern
    
    def add_intent(self, name: str, examples: List[str], responses: List[str]):
        self.intent_classifier.add_intent(name, examples)
        self.responses[name].extend(responses)
    
    def add_entity_extractor(self, name: str, pattern: str):
        self.entity_extractors[name] = re.compile(pattern)
    
    def build(self):
        self.intent_classifier.build()
        # Optionally train generator on all example phrases
        all_text = []
        for examples in self.intent_classifier.intents.values():
            all_text.extend(examples)
        self.generator.train(all_text)
    
    def process(self, user_input: str) -> str:
        intent, confidence = self.intent_classifier.classify(user_input)
        if confidence < 0.5:
            # Fallback: generate generic response
            return self.generator.generate(max_length=20)
        
        # Extract entities
        entities = {}
        for name, pattern in self.entity_extractors.items():
            match = pattern.search(user_input)
            if match:
                entities[name] = match.group(0)
        
        # Select response template
        if intent in self.responses and self.responses[intent]:
            template = random.choice(self.responses[intent])
            # Fill entities if any
            for key, value in entities.items():
                template = template.replace(f"{{{key}}}", value)
            return template
        return "I'm not sure how to respond to that."