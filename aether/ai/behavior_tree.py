"""
Advanced Behavior Tree System
Hierarchical task planning for game AI
"""

from typing import Dict, Any, List, Callable, Optional
from enum import Enum
import random

class BTStatus(Enum):
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3

class Node:
    """Base node for behavior tree"""
    def __init__(self, name: str = ""):
        self.name = name
        self.parent = None
        self.children = []
    
    def execute(self, context: Dict[str, Any]) -> BTStatus:
        raise NotImplementedError
    
    def add_child(self, child: 'Node'):
        child.parent = self
        self.children.append(child)

class Sequence(Node):
    """Execute children in order until one fails"""
    def __init__(self, name: str = "", children: List[Node] = None):
        super().__init__(name)
        if children:
            for child in children:
                self.add_child(child)
    
    def execute(self, context: Dict[str, Any]) -> BTStatus:
        for child in self.children:
            status = child.execute(context)
            if status != BTStatus.SUCCESS:
                return status
        return BTStatus.SUCCESS

class Selector(Node):
    """Execute children until one succeeds"""
    def __init__(self, name: str = "", children: List[Node] = None):
        super().__init__(name)
        if children:
            for child in children:
                self.add_child(child)
    
    def execute(self, context: Dict[str, Any]) -> BTStatus:
        for child in self.children:
            status = child.execute(context)
            if status != BTStatus.FAILURE:
                return status
        return BTStatus.FAILURE

class Condition(Node):
    """Check a condition"""
    def __init__(self, condition_fn: Callable[[Dict[str, Any]], bool], name: str = ""):
        super().__init__(name)
        self.condition_fn = condition_fn
    
    def execute(self, context: Dict[str, Any]) -> BTStatus:
        return BTStatus.SUCCESS if self.condition_fn(context) else BTStatus.FAILURE

class Action(Node):
    """Perform an action"""
    def __init__(self, action_fn: Callable[[Dict[str, Any]], BTStatus], name: str = ""):
        super().__init__(name)
        self.action_fn = action_fn
    
    def execute(self, context: Dict[str, Any]) -> BTStatus:
        return self.action_fn(context)

class Inverter(Node):
    """Invert the result of a child"""
    def __init__(self, child: Node = None, name: str = ""):
        super().__init__(name)
        if child:
            self.add_child(child)
    
    def execute(self, context: Dict[str, Any]) -> BTStatus:
        if not self.children:
            return BTStatus.FAILURE
        status = self.children[0].execute(context)
        if status == BTStatus.SUCCESS:
            return BTStatus.FAILURE
        elif status == BTStatus.FAILURE:
            return BTStatus.SUCCESS
        return status

class Repeat(Node):
    """Repeat child n times or until failure"""
    def __init__(self, child: Node, times: int = -1, name: str = ""):
        super().__init__(name)
        self.add_child(child)
        self.times = times
        self._counter = 0
    
    def execute(self, context: Dict[str, Any]) -> BTStatus:
        if self.times >= 0 and self._counter >= self.times:
            return BTStatus.SUCCESS
        
        status = self.children[0].execute(context)
        if status == BTStatus.FAILURE:
            return BTStatus.FAILURE
        elif status == BTStatus.SUCCESS:
            self._counter += 1
            if self.times < 0 or self._counter < self.times:
                return BTStatus.RUNNING
            self._counter = 0
            return BTStatus.SUCCESS
        return BTStatus.RUNNING

class RandomSelector(Selector):
    """Shuffle children and then execute like selector"""
    def execute(self, context: Dict[str, Any]) -> BTStatus:
        shuffled = self.children.copy()
        random.shuffle(shuffled)
        for child in shuffled:
            status = child.execute(context)
            if status != BTStatus.FAILURE:
                return status
        return BTStatus.FAILURE

class BehaviorTree:
    """Complete behavior tree with blackboard"""
    def __init__(self, root: Node = None):
        self.root = root
        self.blackboard = {}
    
    def update(self, dt: float):
        """Tick the tree"""
        self.blackboard['dt'] = dt
        if self.root:
            self.root.execute(self.blackboard)