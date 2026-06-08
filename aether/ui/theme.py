"""
AetherEngine Advanced UI Theme System
Complex theming engine with CSS-like styling, dynamic themes,
animations, gradients, shadows, and comprehensive visual customization
"""

import pygame
import json
import math
import colorsys
from typing import Dict, List, Tuple, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
import copy

# ============================================================================
# Color Utilities
# ============================================================================

class Color:
    """Advanced color handling with various color spaces"""
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color string to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex string"""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    @staticmethod
    def lerp(color1: Tuple[int, int, int], color2: Tuple[int, int, int], 
             t: float) -> Tuple[int, int, int]:
        """Linear interpolation between two colors"""
        t = max(0.0, min(1.0, t))
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))
    
    @staticmethod
    def rgba(color: Tuple[int, int, int], alpha: int = 255) -> Tuple[int, int, int, int]:
        """Convert RGB to RGBA"""
        return (*color, alpha)
    
    @staticmethod
    def with_alpha(color: Tuple[int, int, int, int], alpha: int) -> Tuple[int, int, int, int]:
        """Change alpha of RGBA color"""
        return (*color[:3], alpha)
    
    @staticmethod
    def lighten(color: Tuple[int, int, int], amount: float = 0.1) -> Tuple[int, int, int]:
        """Lighten a color by amount (0.0 to 1.0)"""
        return Color.lerp(color, (255, 255, 255), amount)
    
    @staticmethod
    def darken(color: Tuple[int, int, int], amount: float = 0.1) -> Tuple[int, int, int]:
        """Darken a color by amount (0.0 to 1.0)"""
        return Color.lerp(color, (0, 0, 0), amount)
    
    @staticmethod
    def saturate(color: Tuple[int, int, int], amount: float = 0.1) -> Tuple[int, int, int]:
        """Saturate/desaturate a color"""
        r, g, b = [c/255.0 for c in color]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        s = max(0.0, min(1.0, s + amount))
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return tuple(int(c*255) for c in (r, g, b))
    
    @staticmethod
    def multiply(color: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Multiply color brightness"""
        return tuple(min(255, int(c * factor)) for c in color)
    
    @staticmethod
    def blend_normal(bg: Tuple[int, int, int], fg: Tuple[int, int, int], 
                    alpha: float) -> Tuple[int, int, int]:
        """Normal alpha blending"""
        alpha = max(0.0, min(1.0, alpha))
        return tuple(int(b * (1-alpha) + f * alpha) for b, f in zip(bg, fg))
    
    @staticmethod
    def blend_additive(bg: Tuple[int, int, int], fg: Tuple[int, int, int], 
                      alpha: float) -> Tuple[int, int, int]:
        """Additive blending"""
        return tuple(min(255, b + int(f * alpha)) for b, f in zip(bg, fg))
    
    @staticmethod
    def blend_multiply(bg: Tuple[int, int, int], fg: Tuple[int, int, int], 
                      alpha: float) -> Tuple[int, int, int]:
        """Multiply blending"""
        blended = tuple(b * f // 255 for b, f in zip(bg, fg))
        return tuple(int(b * (1-alpha) + bl * alpha) for b, bl in zip(bg, blended))
    
    @staticmethod
    def generate_palette(base_color: Tuple[int, int, int], 
                        variations: int = 5) -> List[Tuple[int, int, int]]:
        """Generate a color palette from a base color"""
        palette = []
        for i in range(variations):
            t = i / (variations - 1)
            if t < 0.5:
                color = Color.lighten(base_color, (0.5 - t) * 0.4)
            else:
                color = Color.darken(base_color, (t - 0.5) * 0.4)
            palette.append(color)
        return palette

# ============================================================================
# Style Properties
# ============================================================================

class BorderStyle(Enum):
    """Border styles"""
    NONE = auto()
    SOLID = auto()
    DASHED = auto()
    DOTTED = auto()
    DOUBLE = auto()
    GROOVE = auto()
    RIDGE = auto()
    INSET = auto()
    OUTSET = auto()
    GLOW = auto()

class TextAlign(Enum):
    """Text alignment"""
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()
    JUSTIFY = auto()

class OverflowMode(Enum):
    """Overflow handling"""
    VISIBLE = auto()
    HIDDEN = auto()
    SCROLL = auto()
    CLIP = auto()

class GradientType(Enum):
    """Gradient types"""
    NONE = auto()
    LINEAR = auto()
    RADIAL = auto()
    CONICAL = auto()
    DIAGONAL = auto()

class BlendMode(Enum):
    """Blend modes for rendering"""
    NORMAL = auto()
    ADDITIVE = auto()
    MULTIPLY = auto()
    SCREEN = auto()
    OVERLAY = auto()
    SOFT_LIGHT = auto()

@dataclass
class StyleState:
    """Style properties for a specific widget state"""
    # Background
    background_color: Optional[Tuple[int, int, int, int]] = None
    background_image: Optional[pygame.Surface] = None
    background_gradient: Optional[Tuple[GradientType, Tuple[Tuple, Tuple]]] = None
    
    # Border
    border_color: Optional[Tuple[int, int, int, int]] = None
    border_width: int = 0
    border_radius: int = 0
    border_style: BorderStyle = BorderStyle.NONE
    border_top_width: Optional[int] = None
    border_right_width: Optional[int] = None
    border_bottom_width: Optional[int] = None
    border_left_width: Optional[int] = None
    border_top_left_radius: Optional[int] = None
    border_top_right_radius: Optional[int] = None
    border_bottom_left_radius: Optional[int] = None
    border_bottom_right_radius: Optional[int] = None
    
    # Text
    text_color: Optional[Tuple[int, int, int, int]] = None
    text_size: Optional[int] = None
    text_font: Optional[str] = None
    text_align: TextAlign = TextAlign.LEFT
    text_bold: bool = False
    text_italic: bool = False
    text_underline: bool = False
    text_strikethrough: bool = False
    text_shadow: bool = False
    text_shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 100)
    text_shadow_offset: Tuple[int, int] = (2, 2)
    text_line_spacing: float = 1.2
    text_letter_spacing: int = 0
    
    # Shadow
    box_shadow: bool = False
    box_shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 100)
    box_shadow_offset: Tuple[int, int] = (3, 3)
    box_shadow_blur: int = 5
    box_shadow_spread: int = 0
    
    # Inner shadow
    inner_shadow: bool = False
    inner_shadow_color: Tuple[int, int, int, int] = (0, 0, 0, 50)
    inner_shadow_offset: Tuple[int, int] = (1, 1)
    inner_shadow_blur: int = 3
    
    # Padding & Margin
    padding_top: int = 0
    padding_right: int = 0
    padding_bottom: int = 0
    padding_left: int = 0
    margin_top: int = 0
    margin_right: int = 0
    margin_bottom: int = 0
    margin_left: int = 0
    
    # Sizing
    width: Optional[int] = None
    height: Optional[int] = None
    min_width: Optional[int] = None
    max_width: Optional[int] = None
    min_height: Optional[int] = None
    max_height: Optional[int] = None
    
    # Positioning
    position: Optional[str] = None  # relative, absolute
    top: Optional[int] = None
    right: Optional[int] = None
    bottom: Optional[int] = None
    left: Optional[int] = None
    z_index: int = 0
    
    # Visual effects
    opacity: float = 1.0
    blur: int = 0
    blend_mode: BlendMode = BlendMode.NORMAL
    overflow: OverflowMode = OverflowMode.VISIBLE
    visible: bool = True
    
    # Transform
    rotation: float = 0.0  # degrees
    scale: Tuple[float, float] = (1.0, 1.0)
    translate: Tuple[int, int] = (0, 0)
    
    # Cursor
    cursor: Optional[str] = None  # pointer, text, wait, etc.
    
    # Transition
    transition_duration: float = 0.0
    transition_easing: str = "linear"
    
    def merge(self, other: 'StyleState') -> 'StyleState':
        """Merge another style state, overwriting non-None values"""
        merged = StyleState()
        for attr in self.__dataclass_fields__:
            other_val = getattr(other, attr)
            if other_val is not None or isinstance(other_val, bool):
                setattr(merged, attr, other_val)
            else:
                setattr(merged, attr, getattr(self, attr))
        return merged
    
    def copy(self) -> 'StyleState':
        """Deep copy the style state"""
        return copy.deepcopy(self)

@dataclass
class WidgetStyle:
    """Complete widget style with state variations"""
    default: StyleState = field(default_factory=StyleState)
    hover: Optional[StyleState] = None
    pressed: Optional[StyleState] = None
    focused: Optional[StyleState] = None
    disabled: Optional[StyleState] = None
    selected: Optional[StyleState] = None
    checked: Optional[StyleState] = None
    
    # Animations
    animations: Dict[str, 'StyleAnimation'] = field(default_factory=dict)
    
    def get_state(self, state: str) -> StyleState:
        """Get style for a specific state"""
        state_styles = {
            'hover': self.hover,
            'pressed': self.pressed,
            'focused': self.focused,
            'disabled': self.disabled,
            'selected': self.selected,
            'checked': self.checked
        }
        
        if state in state_styles and state_styles[state] is not None:
            return self.default.merge(state_styles[state])
        return self.default

class StyleAnimation:
    """Animation for style transitions"""
    
    def __init__(self, property_name: str, start_value: Any, end_value: Any,
                 duration: float = 0.3, easing: str = "ease_in_out",
                 delay: float = 0.0, repeat: int = 0):
        self.property_name = property_name
        self.start_value = start_value
        self.end_value = end_value
        self.duration = duration
        self.easing = easing
        self.delay = delay
        self.repeat = repeat
        
        self.current_time = 0.0
        self.current_value = start_value
        self.playing = False
        self.finished = False
        self._repeat_count = 0
    
    def update(self, dt: float):
        """Update animation"""
        if not self.playing:
            return
        
        if self.delay > 0:
            self.delay -= dt
            return
        
        self.current_time += dt
        progress = min(1.0, self.current_time / self.duration)
        
        # Apply easing
        progress = self._apply_easing(progress)
        
        # Interpolate
        self.current_value = self._interpolate(progress)
        
        if progress >= 1.0:
            if self.repeat > 0 and self._repeat_count < self.repeat:
                self.current_time = 0.0
                self._repeat_count += 1
            else:
                self.finished = True
                self.playing = False
    
    def _apply_easing(self, t: float) -> float:
        """Apply easing function"""
        if self.easing == "linear":
            return t
        elif self.easing == "ease_in":
            return t * t
        elif self.easing == "ease_out":
            return 1 - (1 - t) ** 2
        elif self.easing == "ease_in_out":
            return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2
        elif self.easing == "bounce_out":
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
        elif self.easing == "elastic_out":
            if t == 0 or t == 1:
                return t
            return math.pow(2, -10 * t) * math.sin((t - 1) * 5 * math.pi) + 1
        return t
    
    def _interpolate(self, t: float) -> Any:
        """Interpolate between start and end values"""
        if isinstance(self.start_value, (int, float)):
            return self.start_value + (self.end_value - self.start_value) * t
        elif isinstance(self.start_value, tuple) and len(self.start_value) in (3, 4):
            return tuple(int(a + (b - a) * t) for a, b in zip(self.start_value, self.end_value))
        return self.end_value if t > 0.5 else self.start_value
    
    def play(self):
        """Start playing the animation"""
        self.playing = True
        self.current_time = 0.0
        self.finished = False

# ============================================================================
# Theme System
# ============================================================================

class Theme:
    """
    Complete UI theme with comprehensive styling
    Supports CSS-like cascading, inheritance, and dynamic updates
    """
    
    def __init__(self, name: str = "Default"):
        self.name = name
        self.author = "AetherEngine"
        self.version = "1.0.0"
        self.description = "Default theme"
        
        # Color palette
        self.colors = self._create_default_palette()
        
        # Typography
        self.typography = self._create_default_typography()
        
        # Widget styles
        self.styles: Dict[str, WidgetStyle] = self._create_default_styles()
        
        # Global properties
        self.global_style = StyleState()
        
        # Icon set
        self.icons: Dict[str, pygame.Surface] = {}
        
        # Sound set
        self.sounds: Dict[str, Any] = {}
        
        # Animations
        self.global_animations: Dict[str, StyleAnimation] = {}
        
        # Custom properties (CSS variables-like)
        self.custom_properties: Dict[str, Any] = {}
    
    def _create_default_palette(self) -> Dict[str, Tuple[int, int, int]]:
        """Create default color palette"""
        return {
            # Primary colors
            'primary': (0, 120, 255),
            'primary_light': (51, 153, 255),
            'primary_dark': (0, 85, 204),
            'primary_text': (255, 255, 255),
            
            # Secondary colors
            'secondary': (108, 117, 125),
            'secondary_light': (160, 165, 170),
            'secondary_dark': (80, 88, 94),
            'secondary_text': (255, 255, 255),
            
            # Accent colors
            'accent': (255, 193, 7),
            'accent_light': (255, 210, 70),
            'accent_dark': (204, 153, 0),
            'accent_text': (33, 37, 41),
            
            # Semantic colors
            'success': (40, 167, 69),
            'info': (23, 162, 184),
            'warning': (255, 193, 7),
            'error': (220, 53, 69),
            'danger': (220, 53, 69),
            
            # Neutral colors
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'gray_100': (248, 249, 250),
            'gray_200': (233, 236, 239),
            'gray_300': (222, 226, 230),
            'gray_400': (206, 212, 218),
            'gray_500': (173, 181, 189),
            'gray_600': (108, 117, 125),
            'gray_700': (73, 80, 87),
            'gray_800': (52, 58, 64),
            'gray_900': (33, 37, 41),
            
            # Surface colors
            'surface': (255, 255, 255),
            'surface_variant': (245, 245, 245),
            'surface_raised': (255, 255, 255),
            'surface_sunken': (240, 240, 240),
            
            # Background
            'background': (248, 249, 250),
            'background_dark': (33, 37, 41),
            
            # Text
            'text_primary': (33, 37, 41),
            'text_secondary': (108, 117, 125),
            'text_disabled': (173, 181, 189),
            'text_inverse': (255, 255, 255),
            
            # Border
            'border': (222, 226, 230),
            'border_light': (233, 236, 239),
            'border_dark': (173, 181, 189),
            
            # Overlay
            'overlay': (0, 0, 0),
            'overlay_light': (255, 255, 255),
        }
    
    def _create_default_typography(self) -> Dict[str, Dict[str, Any]]:
        """Create default typography settings"""
        return {
            'h1': {'size': 48, 'weight': 'bold', 'line_height': 1.2},
            'h2': {'size': 36, 'weight': 'bold', 'line_height': 1.3},
            'h3': {'size': 28, 'weight': 'bold', 'line_height': 1.3},
            'h4': {'size': 22, 'weight': 'bold', 'line_height': 1.4},
            'h5': {'size': 18, 'weight': 'bold', 'line_height': 1.4},
            'h6': {'size': 16, 'weight': 'bold', 'line_height': 1.4},
            'body': {'size': 16, 'weight': 'normal', 'line_height': 1.5},
            'body_small': {'size': 14, 'weight': 'normal', 'line_height': 1.5},
            'caption': {'size': 12, 'weight': 'normal', 'line_height': 1.5},
            'button': {'size': 16, 'weight': 'medium', 'line_height': 1.0},
            'input': {'size': 16, 'weight': 'normal', 'line_height': 1.5},
            'label': {'size': 14, 'weight': 'medium', 'line_height': 1.5},
            'code': {'size': 14, 'weight': 'normal', 'line_height': 1.5, 'family': 'monospace'},
        }
    
    def _create_default_styles(self) -> Dict[str, WidgetStyle]:
        """Create default widget styles"""
        styles = {}
        
        # Button style
        button_style = WidgetStyle()
        button_style.default = StyleState(
            background_color=Color.rgba(self.colors['primary']),
            border_radius=8,
            border_width=0,
            text_color=Color.rgba(self.colors['primary_text']),
            text_size=16,
            text_align=TextAlign.CENTER,
            padding_top=12,
            padding_bottom=12,
            padding_left=24,
            padding_right=24,
            box_shadow=True,
            box_shadow_color=(0, 0, 0, 30),
            box_shadow_offset=(0, 2),
            box_shadow_blur=4,
            cursor='pointer',
            transition_duration=0.2,
            transition_easing="ease_in_out"
        )
        button_style.hover = StyleState(
            background_color=Color.rgba(self.colors['primary_light']),
            box_shadow_color=(0, 0, 0, 50),
            box_shadow_offset=(0, 4),
            box_shadow_blur=8
        )
        button_style.pressed = StyleState(
            background_color=Color.rgba(self.colors['primary_dark']),
            box_shadow_offset=(0, 1),
            box_shadow_blur=2,
            translate=(0, 2)
        )
        button_style.disabled = StyleState(
            background_color=Color.rgba(self.colors['gray_400']),
            text_color=Color.rgba(self.colors['text_disabled']),
            box_shadow=False,
            cursor='default'
        )
        styles['button'] = button_style
        
        # Secondary button
        secondary_button = copy.deepcopy(button_style)
        secondary_button.default.background_color = Color.rgba(self.colors['secondary'])
        secondary_button.hover.background_color = Color.rgba(self.colors['secondary_light'])
        secondary_button.pressed.background_color = Color.rgba(self.colors['secondary_dark'])
        styles['button_secondary'] = secondary_button
        
        # Accent button
        accent_button = copy.deepcopy(button_style)
        accent_button.default.background_color = Color.rgba(self.colors['accent'])
        accent_button.default.text_color = Color.rgba(self.colors['accent_text'])
        accent_button.hover.background_color = Color.rgba(self.colors['accent_light'])
        accent_button.pressed.background_color = Color.rgba(self.colors['accent_dark'])
        styles['button_accent'] = accent_button
        
        # Danger button
        danger_button = copy.deepcopy(button_style)
        danger_button.default.background_color = Color.rgba(self.colors['danger'])
        danger_button.hover.background_color = Color.rgba(Color.lighten(self.colors['danger'], 0.1))
        danger_button.pressed.background_color = Color.rgba(Color.darken(self.colors['danger'], 0.1))
        styles['button_danger'] = danger_button
        
        # Outline button
        outline_button = WidgetStyle()
        outline_button.default = StyleState(
            background_color=(0, 0, 0, 0),
            border_color=Color.rgba(self.colors['primary']),
            border_width=2,
            border_radius=8,
            border_style=BorderStyle.SOLID,
            text_color=Color.rgba(self.colors['primary']),
            text_size=16,
            text_align=TextAlign.CENTER,
            padding_top=10,
            padding_bottom=10,
            padding_left=22,
            padding_right=22,
            cursor='pointer',
            transition_duration=0.2
        )
        outline_button.hover = StyleState(
            background_color=Color.rgba(self.colors['primary'], 20),
            border_color=Color.rgba(self.colors['primary_light'])
        )
        outline_button.pressed = StyleState(
            background_color=Color.rgba(self.colors['primary'], 40)
        )
        styles['button_outline'] = outline_button
        
        # Text input style
        input_style = WidgetStyle()
        input_style.default = StyleState(
            background_color=Color.rgba(self.colors['white']),
            border_color=Color.rgba(self.colors['border']),
            border_width=1,
            border_radius=6,
            border_style=BorderStyle.SOLID,
            text_color=Color.rgba(self.colors['text_primary']),
            text_size=16,
            text_align=TextAlign.LEFT,
            padding_top=10,
            padding_bottom=10,
            padding_left=12,
            padding_right=12,
            cursor='text',
            transition_duration=0.2,
            min_height=42
        )
        input_style.focused = StyleState(
            border_color=Color.rgba(self.colors['primary']),
            border_width=2,
            box_shadow=True,
            box_shadow_color=Color.rgba(self.colors['primary'], 25),
            box_shadow_offset=(0, 0),
            box_shadow_blur=8,
            box_shadow_spread=2
        )
        input_style.hover = StyleState(
            border_color=Color.rgba(self.colors['border_dark'])
        )
        input_style.disabled = StyleState(
            background_color=Color.rgba(self.colors['gray_200']),
            text_color=Color.rgba(self.colors['text_disabled']),
            cursor='default'
        )
        input_style.error = StyleState(
            border_color=Color.rgba(self.colors['error']),
            box_shadow_color=Color.rgba(self.colors['error'], 25)
        )
        styles['input'] = input_style
        
        # Panel style
        panel_style = WidgetStyle()
        panel_style.default = StyleState(
            background_color=Color.rgba(self.colors['surface']),
            border_radius=12,
            box_shadow=True,
            box_shadow_color=(0, 0, 0, 20),
            box_shadow_offset=(0, 2),
            box_shadow_blur=10,
            padding_top=20,
            padding_bottom=20,
            padding_left=20,
            padding_right=20
        )
        styles['panel'] = panel_style
        
        # Card style
        card_style = WidgetStyle()
        card_style.default = StyleState(
            background_color=Color.rgba(self.colors['surface']),
            border_radius=10,
            border_width=1,
            border_color=Color.rgba(self.colors['border_light']),
            box_shadow=True,
            box_shadow_color=(0, 0, 0, 15),
            box_shadow_offset=(0, 1),
            box_shadow_blur=6,
            padding_top=16,
            padding_bottom=16,
            padding_left=16,
            padding_right=16,
            transition_duration=0.3
        )
        card_style.hover = StyleState(
            box_shadow_color=(0, 0, 0, 30),
            box_shadow_offset=(0, 4),
            box_shadow_blur=12,
            translate=(0, -2)
        )
        styles['card'] = card_style
        
        # Label style
        label_style = WidgetStyle()
        label_style.default = StyleState(
            text_color=Color.rgba(self.colors['text_primary']),
            text_size=14,
            text_align=TextAlign.LEFT,
            padding_top=4,
            padding_bottom=4
        )
        styles['label'] = label_style
        
        # Title style
        styles['title'] = WidgetStyle()
        styles['title'].default = StyleState(
            text_color=Color.rgba(self.colors['text_primary']),
            text_size=28,
            text_align=TextAlign.LEFT,
            text_bold=True,
            padding_bottom=8
        )
        
        # Subtitle style
        styles['subtitle'] = WidgetStyle()
        styles['subtitle'].default = StyleState(
            text_color=Color.rgba(self.colors['text_secondary']),
            text_size=18,
            text_align=TextAlign.LEFT,
            padding_bottom=12
        )
        
        # Progress bar style
        progress_style = WidgetStyle()
        progress_style.default = StyleState(
            background_color=Color.rgba(self.colors['gray_200']),
            border_radius=10,
            height=20,
            overflow=OverflowMode.HIDDEN
        )
        styles['progress_bar'] = progress_style
        
        # Progress fill style
        styles['progress_fill'] = WidgetStyle()
        styles['progress_fill'].default = StyleState(
            background_color=Color.rgba(self.colors['primary']),
            background_gradient=(GradientType.LINEAR, 
                               (self.colors['primary'], self.colors['primary_light'])),
            border_radius=10,
            height=20,
            transition_duration=0.3
        )
        
        # Slider style
        slider_style = WidgetStyle()
        slider_style.default = StyleState(
            background_color=Color.rgba(self.colors['gray_200']),
            border_radius=4,
            height=6,
            cursor='pointer'
        )
        styles['slider'] = slider_style
        
        # Slider thumb style
        styles['slider_thumb'] = WidgetStyle()
        styles['slider_thumb'].default = StyleState(
            background_color=Color.rgba(self.colors['primary']),
            border_radius=12,
            width=24,
            height=24,
            box_shadow=True,
            box_shadow_color=(0, 0, 0, 30),
            box_shadow_offset=(0, 2),
            box_shadow_blur=4
        )
        styles['slider_thumb'].hover.hover = StyleState(
            box_shadow_color=(0, 0, 0, 50),
            box_shadow_blur=8,
            scale=(1.1, 1.1)
        )
        
        # Checkbox style
        checkbox_style = WidgetStyle()
        checkbox_style.default = StyleState(
            background_color=Color.rgba(self.colors['white']),
            border_color=Color.rgba(self.colors['border_dark']),
            border_width=2,
            border_radius=4,
            width=20,
            height=20,
            cursor='pointer',
            transition_duration=0.2
        )
        checkbox_style.checked = StyleState(
            background_color=Color.rgba(self.colors['primary']),
            border_color=Color.rgba(self.colors['primary']),
            inner_shadow=True,
            inner_shadow_color=Color.rgba(self.colors['white'], 50)
        )
        checkbox_style.hover = StyleState(
            border_color=Color.rgba(self.colors['primary'])
        )
        styles['checkbox'] = checkbox_style
        
        # Radio button style
        radio_style = WidgetStyle()
        radio_style.default = StyleState(
            background_color=Color.rgba(self.colors['white']),
            border_color=Color.rgba(self.colors['border_dark']),
            border_width=2,
            border_radius=10,
            width=20,
            height=20,
            cursor='pointer'
        )
        radio_style.checked = StyleState(
            border_color=Color.rgba(self.colors['primary']),
            border_width=6
        )
        styles['radio'] = radio_style
        
        # Toggle switch style
        toggle_style = WidgetStyle()
        toggle_style.default = StyleState(
            background_color=Color.rgba(self.colors['gray_300']),
            border_radius=15,
            width=50,
            height=28,
            cursor='pointer',
            transition_duration=0.3
        )
        toggle_style.checked = StyleState(
            background_color=Color.rgba(self.colors['primary'])
        )
        styles['toggle'] = toggle_style
        
        # Toggle knob style
        styles['toggle_knob'] = WidgetStyle()
        styles['toggle_knob'].default = StyleState(
            background_color=Color.rgba(self.colors['white']),
            border_radius=12,
            width=24,
            height=24,
            box_shadow=True,
            box_shadow_color=(0, 0, 0, 20),
            box_shadow_offset=(0, 1),
            box_shadow_blur=3,
            transition_duration=0.3
        )
        
        # Dropdown/Menu style
        menu_style = WidgetStyle()
        menu_style.default = StyleState(
            background_color=Color.rgba(self.colors['surface']),
            border_radius=8,
            border_width=1,
            border_color=Color.rgba(self.colors['border']),
            box_shadow=True,
            box_shadow_color=(0, 0, 0, 20),
            box_shadow_offset=(0, 4),
            box_shadow_blur=12,
            padding_top=8,
            padding_bottom=8,
            overflow=OverflowMode.HIDDEN
        )
        styles['menu'] = menu_style
        
        # Menu item style
        menu_item_style = WidgetStyle()
        menu_item_style.default = StyleState(
            background_color=(0, 0, 0, 0),
            text_color=Color.rgba(self.colors['text_primary']),
            text_size=15,
            text_align=TextAlign.LEFT,
            padding_top=10,
            padding_bottom=10,
            padding_left=16,
            padding_right=16,
            cursor='pointer',
            transition_duration=0.15
        )
        menu_item_style.hover = StyleState(
            background_color=Color.rgba(self.colors['primary'], 15)
        )
        menu_item_style.selected = StyleState(
            background_color=Color.rgba(self.colors['primary'], 25),
            text_color=Color.rgba(self.colors['primary'])
        )
        styles['menu_item'] = menu_item_style
        
        # Scrollbar style
        scrollbar_style = WidgetStyle()
        scrollbar_style.default = StyleState(
            background_color=Color.rgba(self.colors['gray_200']),
            border_radius=4,
            width=8
        )
        scrollbar_style.hover = StyleState(
            background_color=Color.rgba(self.colors['gray_400'])
        )
        styles['scrollbar'] = scrollbar_style
        
        # Scrollbar thumb
        scroll_thumb_style = WidgetStyle()
        scroll_thumb_style.default = StyleState(
            background_color=Color.rgba(self.colors['gray_500']),
            border_radius=4,
            width=8,
            cursor='pointer',
            transition_duration=0.1
        )
        scroll_thumb_style.hover = StyleState(
            background_color=Color.rgba(self.colors['gray_600'])
        )
        styles['scrollbar_thumb'] = scroll_thumb_style
        
        # Tooltip style
        tooltip_style = WidgetStyle()
        tooltip_style.default = StyleState(
            background_color=Color.rgba(self.colors['gray_800']),
            text_color=Color.rgba(self.colors['text_inverse']),
            text_size=13,
            border_radius=6,
            padding_top=8,
            padding_bottom=8,
            padding_left=12,
            padding_right=12,
            box_shadow=True,
            box_shadow_color=(0, 0, 0, 40),
            box_shadow_offset=(0, 2),
            box_shadow_blur=8,
            opacity=0.95
        )
        styles['tooltip'] = tooltip_style
        
        # Modal/Overlay style
        overlay_style = WidgetStyle()
        overlay_style.default = StyleState(
            background_color=Color.rgba(self.colors['overlay'], 128),
            z_index=1000
        )
        styles['overlay'] = overlay_style
        
        # Tab style
        tab_style = WidgetStyle()
        tab_style.default = StyleState(
            background_color=(0, 0, 0, 0),
            text_color=Color.rgba(self.colors['text_secondary']),
            text_size=15,
            text_align=TextAlign.CENTER,
            padding_top=12,
            padding_bottom=12,
            padding_left=20,
            padding_right=20,
            border_bottom_width=2,
            border_bottom_color=(0, 0, 0, 0),
            cursor='pointer',
            transition_duration=0.2
        )
        tab_style.selected = StyleState(
            text_color=Color.rgba(self.colors['primary']),
            border_bottom_color=Color.rgba(self.colors['primary'])
        )
        tab_style.hover = StyleState(
            text_color=Color.rgba(self.colors['text_primary'])
        )
        styles['tab'] = tab_style
        
        return styles
    
    def get_style(self, style_name: str) -> Optional[WidgetStyle]:
        """Get a widget style by name"""
        return self.styles.get(style_name)
    
    def set_color(self, name: str, color: Tuple[int, int, int]):
        """Set a color in the palette"""
        self.colors[name] = color
        self._regenerate_styles()
    
    def _regenerate_styles(self):
        """Regenerate all styles with updated colors"""
        self.styles = self._create_default_styles()
    
    def load_from_file(self, filepath: str):
        """Load theme from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.name = data.get('name', self.name)
            self.author = data.get('author', self.author)
            self.version = data.get('version', self.version)
            
            # Load colors
            if 'colors' in data:
                for name, hex_color in data['colors'].items():
                    self.colors[name] = Color.hex_to_rgb(hex_color)
            
            # Regenerate styles with new colors
            self._regenerate_styles()
            
        except Exception as e:
            print(f"Error loading theme: {e}")
    
    def save_to_file(self, filepath: str):
        """Save theme to JSON file"""
        data = {
            'name': self.name,
            'author': self.author,
            'version': self.version,
            'colors': {name: Color.rgb_to_hex(color) 
                      for name, color in self.colors.items()}
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving theme: {e}")

# ============================================================================
# Pre-built Themes
# ============================================================================

class DarkTheme(Theme):
    """Professional dark theme"""
    
    def __init__(self):
        super().__init__("Dark")
        self.description = "Professional dark theme for extended use"
        
        self.colors.update({
            'primary': (100, 180, 255),
            'primary_light': (140, 200, 255),
            'primary_dark': (60, 140, 220),
            'primary_text': (20, 25, 35),
            
            'secondary': (150, 155, 165),
            'secondary_light': (180, 185, 195),
            'secondary_dark': (120, 125, 135),
            
            'accent': (255, 200, 50),
            'accent_light': (255, 220, 100),
            'accent_dark': (220, 170, 30),
            'accent_text': (20, 25, 35),
            
            'white': (240, 245, 250),
            'black': (10, 15, 20),
            'gray_100': (30, 35, 45),
            'gray_200': (40, 45, 55),
            'gray_300': (50, 55, 65),
            'gray_400': (70, 75, 85),
            'gray_500': (100, 105, 115),
            'gray_600': (130, 135, 145),
            'gray_700': (160, 165, 175),
            'gray_800': (200, 205, 215),
            'gray_900': (230, 235, 245),
            
            'surface': (25, 30, 40),
            'surface_variant': (35, 40, 50),
            'surface_raised': (40, 45, 55),
            'surface_sunken': (20, 25, 35),
            
            'background': (18, 22, 30),
            'background_dark': (12, 16, 22),
            
            'text_primary': (235, 240, 250),
            'text_secondary': (150, 160, 175),
            'text_disabled': (80, 90, 100),
            'text_inverse': (20, 25, 35),
            
            'border': (50, 55, 65),
            'border_light': (60, 65, 75),
            'border_dark': (35, 40, 50),
            
            'overlay': (10, 15, 25),
            'overlay_light': (230, 235, 245),
            
            'success': (80, 220, 100),
            'info': (80, 200, 240),
            'warning': (255, 200, 50),
            'error': (255, 90, 90),
            'danger': (255, 90, 90),
        })
        
        self._regenerate_styles()

class NeonTheme(Theme):
    """Vibrant neon theme"""
    
    def __init__(self):
        super().__init__("Neon")
        self.description = "High-contrast neon theme with glowing effects"
        
        self.colors.update({
            'primary': (0, 255, 255),  # Cyan
            'primary_light': (100, 255, 255),
            'primary_dark': (0, 200, 200),
            'primary_text': (10, 10, 30),
            
            'secondary': (255, 0, 255),  # Magenta
            'secondary_light': (255, 100, 255),
            'secondary_dark': (200, 0, 200),
            
            'accent': (255, 255, 0),  # Yellow
            'accent_light': (255, 255, 100),
            'accent_dark': (200, 200, 0),
            'accent_text': (10, 10, 10),
            
            'background': (10, 10, 30),
            'background_dark': (5, 5, 15),
            
            'surface': (15, 15, 40),
            'surface_variant': (20, 20, 50),
            'surface_raised': (25, 25, 55),
            
            'text_primary': (220, 255, 255),
            'text_secondary': (180, 220, 255),
            'text_disabled': (60, 60, 100),
            
            'border': (0, 255, 255, 100),
            'border_light': (100, 255, 255, 150),
            'border_dark': (0, 180, 180, 80),
            
            'success': (0, 255, 100),
            'info': (0, 200, 255),
            'warning': (255, 200, 0),
            'error': (255, 50, 50),
        })
        
        self._regenerate_styles()
        
        # Add glow effects
        for style_name in ['button', 'button_accent', 'button_outline']:
            if style_name in self.styles:
                style = self.styles[style_name]
                style.default.box_shadow = True
                style.default.box_shadow_color = Color.with_alpha(style.default.background_color[:3], 100)
                style.default.box_shadow_blur = 15
                style.default.border_style = BorderStyle.GLOW

class NatureTheme(Theme):
    """Natural, earthy theme"""
    
    def __init__(self):
        super().__init__("Nature")
        self.description = "Calm, nature-inspired theme with earthy tones"
        
        self.colors.update({
            'primary': (76, 175, 80),  # Green
            'primary_light': (129, 199, 132),
            'primary_dark': (56, 142, 60),
            'primary_text': (255, 255, 255),
            
            'secondary': (121, 85, 72),  # Brown
            'secondary_light': (161, 136, 127),
            'secondary_dark': (93, 64, 55),
            
            'accent': (255, 183, 77),  # Orange
            'accent_light': (255, 204, 128),
            'accent_dark': (245, 150, 40),
            'accent_text': (50, 35, 20),
            
            'background': (232, 245, 233),  # Light green
            'background_dark': (27, 94, 32),  # Dark green
            
            'surface': (255, 255, 255),
            'surface_variant': (241, 248, 233),
            'surface_raised': (255, 255, 255),
            'surface_sunken': (232, 245, 233),
            
            'text_primary': (33, 37, 41),
            'text_secondary': (97, 97, 97),
            'text_disabled': (158, 158, 158),
            
            'border': (200, 230, 201),
            'border_light': (220, 240, 221),
            'border_dark': (165, 214, 167),
            
            'success': (76, 175, 80),
            'info': (3, 169, 244),
            'warning': (255, 152, 0),
            'error': (244, 67, 54),
        })
        
        self._regenerate_styles()
        
        # Add rounded, organic feel
        for style_name in self.styles:
            style = self.styles[style_name]
            style.default.border_radius = 12 if 'button' in style_name else 8

class MinimalTheme(Theme):
    """Clean, minimal theme"""
    
    def __init__(self):
        super().__init__("Minimal")
        self.description = "Clean minimal theme with focus on content"
        
        self.colors.update({
            'primary': (30, 30, 30),
            'primary_light': (60, 60, 60),
            'primary_dark': (0, 0, 0),
            'primary_text': (255, 255, 255),
            
            'secondary': (240, 240, 240),
            'secondary_light': (255, 255, 255),
            'secondary_dark': (220, 220, 220),
            
            'accent': (0, 120, 255),
            'accent_text': (255, 255, 255),
            
            'background': (255, 255, 255),
            'background_dark': (245, 245, 245),
            
            'surface': (255, 255, 255),
            'surface_variant': (250, 250, 250),
            
            'text_primary': (20, 20, 20),
            'text_secondary': (120, 120, 120),
            
            'border': (230, 230, 230),
            'border_light': (240, 240, 240),
            'border_dark': (200, 200, 200),
        })
        
        self._regenerate_styles()
        
        # Remove shadows for flat design
        for style_name in self.styles:
            style = self.styles[style_name]
            style.default.box_shadow = False
            style.default.border_radius = 4

# ============================================================================
# Theme Manager
# ============================================================================

class ThemeManager:
    """
    Manages multiple themes and provides theme switching
    with smooth transitions
    """
    
    def __init__(self):
        self.themes: Dict[str, Theme] = {}
        self.current_theme: Optional[Theme] = None
        self.previous_theme: Optional[Theme] = None
        self.transition_progress: float = 1.0
        self.transition_duration: float = 0.5
        self.transitioning: bool = False
        
        # Register built-in themes
        self.register_theme(Theme("Default"))
        self.register_theme(DarkTheme())
        self.register_theme(NeonTheme())
        self.register_theme(NatureTheme())
        self.register_theme(MinimalTheme())
        
        # Set default
        self.set_theme("Dark", animated=False)
    
    def register_theme(self, theme: Theme):
        """Register a theme"""
        self.themes[theme.name] = theme
    
    def set_theme(self, theme_name: str, animated: bool = True):
        """Switch to a theme"""
        if theme_name not in self.themes:
            return
        
        if self.current_theme:
            self.previous_theme = self.current_theme
        
        self.current_theme = self.themes[theme_name]
        
        if animated and self.previous_theme:
            self.transitioning = True
            self.transition_progress = 0.0
        else:
            self.transition_progress = 1.0
    
    def update(self, dt: float):
        """Update theme transitions"""
        if self.transitioning:
            self.transition_progress += dt / self.transition_duration
            if self.transition_progress >= 1.0:
                self.transition_progress = 1.0
                self.transitioning = False
    
    def get_color(self, color_name: str) -> Tuple[int, int, int]:
        """Get current color with transition support"""
        if not self.current_theme:
            return (255, 0, 255)  # Magenta error color
        
        current_color = self.current_theme.colors.get(color_name, (255, 0, 255))
        
        if self.transitioning and self.previous_theme:
            previous_color = self.previous_theme.colors.get(color_name, current_color)
            t = self.transition_progress
            return Color.lerp(previous_color, current_color, t)
        
        return current_color
    
    def get_style(self, style_name: str) -> Optional[WidgetStyle]:
        """Get current widget style"""
        if not self.current_theme:
            return None
        return self.current_theme.get_style(style_name)
    
    def list_themes(self) -> List[str]:
        """Get list of available theme names"""
        return list(self.themes.keys())

# ============================================================================
# Style Renderer
# ============================================================================

class StyleRenderer:
    """
    Renders styled widgets with all effects
    Handles gradients, shadows, borders, and text rendering
    """
    
    def __init__(self):
        self._surface_cache: Dict[str, pygame.Surface] = {}
        self._font_cache: Dict[str, pygame.font.Font] = {}
    
    def render_background(self, style: StyleState, rect: pygame.Rect, 
                         screen: pygame.Surface):
        """Render widget background with all effects"""
        if not style.visible or style.opacity <= 0:
            return
        
        # Create surface for the widget
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        
        # Render shadow
        if style.box_shadow:
            self._render_box_shadow(surface, rect.size, style)
        
        # Render background
        bg_color = style.background_color
        if bg_color and bg_color[3] > 0:  # Has alpha
            if style.background_gradient:
                self._render_gradient(surface, rect.size, style)
            else:
                pygame.draw.rect(surface, bg_color, surface.get_rect(),
                               border_radius=style.border_radius)
        
        # Render inner shadow
        if style.inner_shadow:
            self._render_inner_shadow(surface, rect.size, style)
        
        # Render border
        if style.border_width > 0 and style.border_color:
            self._render_border(surface, rect.size, style)
        
        # Apply opacity
        if style.opacity < 1.0:
            surface.set_alpha(int(style.opacity * 255))
        
        # Apply blur
        if style.blur > 0:
            surface = self._apply_blur(surface, style.blur)
        
        # Apply rotation
        if style.rotation != 0:
            surface = pygame.transform.rotate(surface, style.rotation)
        
        # Apply scale
        if style.scale != (1.0, 1.0):
            new_size = (int(surface.get_width() * style.scale[0]),
                       int(surface.get_height() * style.scale[1]))
            surface = pygame.transform.scale(surface, new_size)
        
        # Apply translation
        pos = (rect.x + style.translate[0], rect.y + style.translate[1])
        
        # Blit with blend mode
        if style.blend_mode == BlendMode.NORMAL:
            screen.blit(surface, pos)
        elif style.blend_mode == BlendMode.ADDITIVE:
            screen.blit(surface, pos, special_flags=pygame.BLEND_RGBA_ADD)
        elif style.blend_mode == BlendMode.MULTIPLY:
            screen.blit(surface, pos, special_flags=pygame.BLEND_RGB_MULT)
    
    def render_text(self, text: str, style: StyleState, rect: pygame.Rect,
                   screen: pygame.Surface):
        """Render styled text"""
        if not text or not style.text_color:
            return
        
        font = self._get_font(style)
        text_surface = font.render(text, True, style.text_color[:3])
        
        # Text shadow
        if style.text_shadow:
            shadow_surface = font.render(text, True, style.text_shadow_color[:3])
            shadow_surface.set_alpha(style.text_shadow_color[3])
            shadow_pos = (rect.x + style.text_shadow_offset[0],
                         rect.y + style.text_shadow_offset[1])
            screen.blit(shadow_surface, shadow_pos)
        
        # Text alignment
        if style.text_align == TextAlign.CENTER:
            text_rect = text_surface.get_rect(center=rect.center)
            text_rect.x += style.translate[0]
            text_rect.y += style.translate[1]
        elif style.text_align == TextAlign.RIGHT:
            text_rect = text_surface.get_rect(midright=rect.midright)
            text_rect.x += style.translate[0]
            text_rect.y += style.translate[1]
        else:
            text_rect = text_surface.get_rect(topleft=rect.topleft)
            text_rect.x += style.translate[0] + style.padding_left
            text_rect.y += style.translate[1] + style.padding_top
        
        screen.blit(text_surface, text_rect)
    
    def _render_box_shadow(self, surface: pygame.Surface, size: Tuple[int, int],
                          style: StyleState):
        """Render box shadow effect"""
        shadow_surf = pygame.Surface(
            (size[0] + style.box_shadow_blur * 2 + style.box_shadow_spread * 2,
             size[1] + style.box_shadow_blur * 2 + style.box_shadow_spread * 2),
            pygame.SRCALPHA
        )
        
        shadow_rect = pygame.Rect(
            style.box_shadow_blur + style.box_shadow_spread,
            style.box_shadow_blur + style.box_shadow_spread,
            size[0] + style.box_shadow_spread * 2,
            size[1] + style.box_shadow_spread * 2
        )
        
        pygame.draw.rect(shadow_surf, style.box_shadow_color, shadow_rect,
                        border_radius=style.border_radius + style.box_shadow_spread)
        
        if style.box_shadow_blur > 0:
            shadow_surf = self._apply_blur(shadow_surf, style.box_shadow_blur)
        
        pos = (style.box_shadow_offset[0] + style.translate[0],
               style.box_shadow_offset[1] + style.translate[1])
        surface.blit(shadow_surf, pos)
    
    def _render_inner_shadow(self, surface: pygame.Surface, size: Tuple[int, int],
                           style: StyleState):
        """Render inner shadow effect"""
        inner = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(inner, style.inner_shadow_color, inner.get_rect(),
                        border_radius=style.border_radius)
        
        if style.inner_shadow_blur > 0:
            inner = self._apply_blur(inner, style.inner_shadow_blur)
        
        # Create inverted mask
        mask = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(),
                        border_radius=style.border_radius)
        
        # Subtract inner shadow from mask
        mask.blit(inner, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        
        surface.blit(mask, (0, 0))
    
    def _render_gradient(self, surface: pygame.Surface, size: Tuple[int, int],
                        style: StyleState):
        """Render gradient background"""
        if not style.background_gradient:
            return
        
        grad_type, (color1, color2) = style.background_gradient
        width, height = size
        
        gradient_surf = pygame.Surface(size, pygame.SRCALPHA)
        
        for i in range(max(width, height)):
            t = i / max(width, height) if max(width, height) > 0 else 0
            
            if grad_type == GradientType.LINEAR:
                color = Color.lerp(color1, color2, t)
                pygame.draw.line(gradient_surf, color, (0, i), (width, i))
            elif grad_type == GradientType.RADIAL:
                center = (width // 2, height // 2)
                radius = int(math.sqrt(width**2 + height**2) / 2)
                color = Color.lerp(color1, color2, t)
                pygame.draw.circle(gradient_surf, color, center, int(radius * (1-t)))
            elif grad_type == GradientType.DIAGONAL:
                color = Color.lerp(color1, color2, t)
                pygame.draw.line(gradient_surf, color, (i, 0), (0, i))
        
        surface.blit(gradient_surf, (0, 0))
    
    def _render_border(self, surface: pygame.Surface, size: Tuple[int, int],
                      style: StyleState):
        """Render border"""
        border_surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(border_surf, style.border_color, border_surf.get_rect(),
                        width=style.border_width,
                        border_radius=style.border_radius)
        surface.blit(border_surf, (0, 0))
    
    def _get_font(self, style: StyleState) -> pygame.font.Font:
        """Get or create font"""
        font_key = f"{style.text_font}_{style.text_size}_{style.text_bold}_{style.text_italic}"
        
        if font_key not in self._font_cache:
            font_size = style.text_size or 16
            font_name = style.text_font or None
            
            try:
                if font_name:
                    font = pygame.font.Font(font_name, font_size)
                else:
                    font = pygame.font.Font(None, font_size)
            except:
                font = pygame.font.Font(None, font_size)
            
            font.set_bold(style.text_bold)
            font.set_italic(style.text_italic)
            
            self._font_cache[font_key] = font
        
        return self._font_cache[font_key]
    
    def _apply_blur(self, surface: pygame.Surface, blur_amount: int) -> pygame.Surface:
        """Apply Gaussian blur to surface (simplified)"""
        if blur_amount <= 0:
            return surface
        
        scale = max(1, blur_amount // 2)
        small_size = (surface.get_width() // scale, surface.get_height() // scale)
        small = pygame.transform.smoothscale(surface, small_size)
        
        return pygame.transform.smoothscale(small, surface.get_size())
    
    def clear_cache(self):
        """Clear render caches"""
        self._surface_cache.clear()
        self._font_cache.clear()


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Core
    'Theme', 'ThemeManager', 'StyleRenderer',
    
    # Pre-built themes
    'DarkTheme', 'NeonTheme', 'NatureTheme', 'MinimalTheme',
    
    # Style types
    'StyleState', 'WidgetStyle', 'StyleAnimation',
    
    # Enums
    'BorderStyle', 'TextAlign', 'OverflowMode', 'GradientType', 'BlendMode',
    
    # Utilities
    'Color',
]