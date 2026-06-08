"""
Finite State Machine with Hierarchical and Pushdown Automata
"""

from typing import Dict, Any, Callable, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class State:
    """Individual state"""
    def __init__(self, name: str):
        self.name = name
        self.on_enter: Optional[Callable] = None
        self.on_update: Optional[Callable[[float], None]] = None
        self.on_exit: Optional[Callable] = None
        self.transitions: List['Transition'] = []
        self.parent_machine = None
    
    def enter(self):
        if self.on_enter:
            self.on_enter()
    
    def update(self, dt: float):
        if self.on_update:
            self.on_update(dt)
    
    def exit(self):
        if self.on_exit:
            self.on_exit()

class Transition:
    """Transition between states"""
    def __init__(self, target: State, condition: Callable[[], bool]):
        self.target = target
        self.condition = condition

class StateMachine:
    """Standard finite state machine"""
    def __init__(self):
        self.states: Dict[str, State] = {}
        self.current_state: Optional[State] = None
        self.previous_state: Optional[State] = None
    
    def add_state(self, state: State):
        self.states[state.name] = state
        state.parent_machine = self
    
    def add_transition(self, from_state: str, to_state: str, condition: Callable[[], bool]):
        if from_state in self.states and to_state in self.states:
            self.states[from_state].transitions.append(
                Transition(self.states[to_state], condition)
            )
    
    def set_state(self, state_name: str):
        if state_name in self.states:
            if self.current_state:
                self.current_state.exit()
                self.previous_state = self.current_state
            self.current_state = self.states[state_name]
            self.current_state.enter()
    
    def update(self, dt: float):
        if not self.current_state:
            return
        # Check transitions
        for trans in self.current_state.transitions:
            if trans.condition():
                self.set_state(trans.target.name)
                break
        self.current_state.update(dt)

class HierarchicalStateMachine(StateMachine):
    """States can contain sub-machines"""
    def __init__(self):
        super().__init__()
        self.sub_machines: Dict[str, StateMachine] = {}
    
    def add_sub_machine(self, state_name: str, machine: StateMachine):
        self.sub_machines[state_name] = machine
    
    def update(self, dt: float):
        super().update(dt)
        # Update sub-machine of current state
        if self.current_state and self.current_state.name in self.sub_machines:
            self.sub_machines[self.current_state.name].update(dt)