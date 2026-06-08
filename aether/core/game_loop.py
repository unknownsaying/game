"""
Advanced Game Loop with Fixed Timestep, Variable Rendering
Implements sophisticated timing and interpolation
"""

import time
from typing import Callable, Optional
from dataclasses import dataclass
import numpy as np
from collections import deque

@dataclass
class GameLoopConfig:
    """Game loop configuration"""
    target_fps: int = 60
    fixed_timestep: float = 1/60
    max_frame_time: float = 0.25  # Prevent spiral of death
    interpolation_enabled: bool = True
    performance_window: int = 120  # Frames for averaging

class GameLoop:
    """
    Advanced game loop with:
    - Fixed timestep updates for physics
    - Variable rendering with interpolation
    - Frame time smoothing
    - Performance monitoring
    """
    
    def __init__(self, config: Optional[GameLoopConfig] = None):
        self.config = config or GameLoopConfig()
        
        # Timing
        self.current_time = time.perf_counter()
        self.accumulator = 0.0
        self.frame_time = 0.0
        self.alpha = 0.0  # Interpolation factor
        
        # Performance tracking
        self.frame_times = deque(maxlen=self.config.performance_window)
        self.update_times = deque(maxlen=self.config.performance_window)
        self.render_times = deque(maxlen=self.config.performance_window)
        
        # Statistics
        self.stats = {
            'avg_fps': 0.0,
            'avg_frame_ms': 0.0,
            'avg_update_ms': 0.0,
            'avg_render_ms': 0.0,
            'frame_count': 0,
            'total_time': 0.0
        }
        
        # Callbacks
        self.update_callback: Optional[Callable] = None
        self.render_callback: Optional[Callable] = None
        self.interpolate_callback: Optional[Callable] = None
        
        self._running = False
        
    def start(self):
        """Start the game loop"""
        self._running = True
        self.current_time = time.perf_counter()
        
        while self._running:
            new_time = time.perf_counter()
            frame_time = new_time - self.current_time
            self.current_time = new_time
            
            # Prevent spiral of death
            if frame_time > self.config.max_frame_time:
                frame_time = self.config.max_frame_time
            
            # Update performance metrics
            self.frame_times.append(frame_time)
            self.accumulator += frame_time * self._get_time_scale()
            
            # Fixed timestep updates
            update_start = time.perf_counter()
            while self.accumulator >= self.config.fixed_timestep:
                if self.update_callback:
                    self.update_callback(self.config.fixed_timestep)
                self.accumulator -= self.config.fixed_timestep
            self.update_times.append(time.perf_counter() - update_start)
            
            # Calculate interpolation
            if self.config.interpolation_enabled:
                self.alpha = self.accumulator / self.config.fixed_timestep
                if self.interpolate_callback:
                    self.interpolate_callback(self.alpha)
            
            # Render
            render_start = time.perf_counter()
            if self.render_callback:
                self.render_callback(self.alpha)
            self.render_times.append(time.perf_counter() - render_start)
            
            # Update statistics
            self._update_statistics()
    
    def stop(self):
        """Stop the game loop"""
        self._running = False
    
    def _get_time_scale(self) -> float:
        """Get current time scale (1.0 = normal)"""
        return 1.0  # Could be modified for slow-motion effects
    
    def _update_statistics(self):
        """Update performance statistics using exponential moving average"""
        self.stats['frame_count'] += 1
        self.stats['total_time'] += self.frame_time
        
        if len(self.frame_times) > 0:
            # Exponential moving average for smoother values
            alpha = 2.0 / (len(self.frame_times) + 1)
            
            avg_frame = sum(self.frame_times) / len(self.frame_times)
            self.stats['avg_fps'] = (1 - alpha) * self.stats['avg_fps'] + alpha * (1.0 / avg_frame)
            self.stats['avg_frame_ms'] = avg_frame * 1000
            
            if len(self.update_times) > 0:
                avg_update = sum(self.update_times) / len(self.update_times)
                self.stats['avg_update_ms'] = avg_update * 1000
            
            if len(self.render_times) > 0:
                avg_render = sum(self.render_times) / len(self.render_times)
                self.stats['avg_render_ms'] = avg_render * 1000
    
    def get_performance_report(self) -> dict:
        """Get detailed performance report"""
        return {
            **self.stats,
            'frame_time_variance': np.var(self.frame_times) if len(self.frame_times) > 1 else 0,
            'frame_time_std': np.std(self.frame_times) if len(self.frame_times) > 1 else 0,
            'percentile_99': np.percentile(self.frame_times, 99) * 1000 if len(self.frame_times) > 0 else 0
        }