"""
Advanced Animation System with Interpolation and Blending
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import math

class EasingType(Enum):
    """Animation easing types"""
    LINEAR = "linear"
    QUAD_IN = "quad_in"
    QUAD_OUT = "quad_out"
    QUAD_IN_OUT = "quad_in_out"
    CUBIC_IN = "cubic_in"
    CUBIC_OUT = "cubic_out"
    CUBIC_IN_OUT = "cubic_in_out"
    ELASTIC_OUT = "elastic_out"
    BOUNCE_OUT = "bounce_out"
    BACK_OUT = "back_out"

class Easing:
    """Easing functions for smooth animations"""
    
    @staticmethod
    def apply(t: float, easing_type: EasingType) -> float:
        """Apply easing to a value between 0 and 1"""
        t = max(0.0, min(1.0, t))
        
        if easing_type == EasingType.LINEAR:
            return t
        elif easing_type == EasingType.QUAD_IN:
            return t * t
        elif easing_type == EasingType.QUAD_OUT:
            return 1 - (1 - t) * (1 - t)
        elif easing_type == EasingType.QUAD_IN_OUT:
            return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2
        elif easing_type == EasingType.CUBIC_IN:
            return t * t * t
        elif easing_type == EasingType.CUBIC_OUT:
            return 1 - (1 - t) ** 3
        elif easing_type == EasingType.CUBIC_IN_OUT:
            return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
        elif easing_type == EasingType.ELASTIC_OUT:
            if t == 0 or t == 1:
                return t
            return math.pow(2, -10 * t) * math.sin((t - 1) * 5 * math.pi) + 1
        elif easing_type == EasingType.BOUNCE_OUT:
            if t < 1 / 2.75:
                return 7.5625 * t * t
            elif t < 2 / 2.75:
                t -= 1.5 / 2.75
                return 7.5625 * t * t + 0.75
            elif t < 2.5 / 2.75:
                t -= 2.25 / 2.75
                return 7.5625 * t * t + 0.9375
            else:
                t -= 2.625 / 2.75
                return 7.5625 * t * t + 0.984375
        elif easing_type == EasingType.BACK_OUT:
            c1 = 1.70158
            c3 = c1 + 1
            return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
        
        return t

@dataclass
class Keyframe:
    """Animation keyframe"""
    time: float
    value: any
    easing: EasingType = EasingType.LINEAR

class AnimationTrack:
    """Single animation track (property)"""
    
    def __init__(self, property_name: str):
        self.property_name = property_name
        self.keyframes: List[Keyframe] = []
        
    def add_keyframe(self, time: float, value: any, 
                    easing: EasingType = EasingType.LINEAR):
        """Add keyframe"""
        self.keyframes.append(Keyframe(time, value, easing))
        self.keyframes.sort(key=lambda k: k.time)
    
    def get_value(self, time: float) -> any:
        """Get interpolated value at time"""
        if not self.keyframes:
            return None
        
        # Before first keyframe
        if time <= self.keyframes[0].time:
            return self.keyframes[0].value
        
        # After last keyframe
        if time >= self.keyframes[-1].time:
            return self.keyframes[-1].value
        
        # Find surrounding keyframes
        for i in range(len(self.keyframes) - 1):
            k1 = self.keyframes[i]
            k2 = self.keyframes[i + 1]
            
            if k1.time <= time <= k2.time:
                # Calculate interpolation factor
                duration = k2.time - k1.time
                t = (time - k1.time) / duration if duration > 0 else 0
                
                # Apply easing
                t = Easing.apply(t, k2.easing)
                
                # Interpolate based on value type
                return self._interpolate(k1.value, k2.value, t)
        
        return self.keyframes[-1].value
    
    def _interpolate(self, v1, v2, t: float):
        """Interpolate between values"""
        if isinstance(v1, (int, float)):
            return v1 + (v2 - v1) * t
        elif isinstance(v1, np.ndarray):
            return v1 + (v2 - v1) * t
        elif isinstance(v1, (tuple, list)):
            return type(v1)(
                a + (b - a) * t for a, b in zip(v1, v2)
            )
        elif t < 0.5:
            return v1
        else:
            return v2

class Animation:
    """Complete animation with multiple tracks"""
    
    def __init__(self, name: str):
        self.name = name
        self.tracks: Dict[str, AnimationTrack] = {}
        self.duration = 0.0
        self.loop = False
    
    def add_track(self, property_name: str) -> AnimationTrack:
        """Add animation track"""
        track = AnimationTrack(property_name)
        self.tracks[property_name] = track
        return track
    
    def get_track(self, property_name: str) -> Optional[AnimationTrack]:
        """Get animation track"""
        return self.tracks.get(property_name)
    
    def sample(self, time: float) -> Dict[str, any]:
        """Sample all tracks at given time"""
        values = {}
        for name, track in self.tracks.items():
            values[name] = track.get_value(time)
        return values
    
    def get_duration(self):
        """Calculate animation duration"""
        max_time = 0.0
        for track in self.tracks.values():
            if track.keyframes:
                last_keyframe = track.keyframes[-1]
                max_time = max(max_time, last_keyframe.time)
        self.duration = max_time
        return self.duration

class AnimationController:
    """Controls animation playback"""
    
    def __init__(self, target=None):
        self.target = target
        self.animations: Dict[str, Animation] = {}
        self.current_animation: Optional[str] = None
        self.current_time = 0.0
        self.speed = 1.0
        self.playing = False
        self.mixer = AnimationMixer()
    
    def add_animation(self, animation: Animation):
        """Add animation"""
        self.animations[animation.name] = animation
    
    def play(self, name: str, loop: bool = False):
        """Play animation by name"""
        if name in self.animations:
            self.current_animation = name
            self.animations[name].loop = loop
            self.current_time = 0.0
            self.playing = True
    
    def stop(self):
        """Stop animation"""
        self.playing = False
    
    def update(self, dt: float):
        """Update animation"""
        if not self.playing or not self.current_animation:
            return
        
        animation = self.animations.get(self.current_animation)
        if not animation:
            return
        
        self.current_time += dt * self.speed
        
        # Loop check
        duration = animation.get_duration()
        if duration > 0:
            if self.current_time >= duration:
                if animation.loop:
                    self.current_time = self.current_time % duration
                else:
                    self.current_time = duration
                    self.playing = False
        
        # Apply animation to target
        if self.target:
            values = animation.sample(self.current_time)
            self.mixer.apply(self.target, values)

class AnimationMixer:
    """Blends multiple animation values"""
    
    def __init__(self):
        self.blend_weight = 1.0
    
    def apply(self, target, values: Dict[str, any]):
        """Apply animation values to target"""
        for property_name, value in values.items():
            if hasattr(target, property_name):
                current = getattr(target, property_name)
                
                # Blend with current value
                blended = self._blend(current, value, self.blend_weight)
                setattr(target, property_name, blended)
    
    def _blend(self, current, target, weight):
        """Blend between current and target values"""
        if isinstance(current, (int, float)):
            return current + (target - current) * weight
        elif isinstance(current, np.ndarray):
            return current + (target - current) * weight
        return target if weight > 0.5 else current