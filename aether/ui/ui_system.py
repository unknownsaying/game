"""
UI System with layout management, theming, and event handling
"""

import pygame
from typing import Dict, List, Optional, Tuple
import weakref

class UITheme:
    """Defines visual styles"""
    def __init__(self):
        self.colors = {
            'background': (50, 50, 50),
            'foreground': (200, 200, 200),
            'accent': (0, 120, 255),
            'text': (255, 255, 255),
            'hover': (70, 70, 70),
            'active': (100, 100, 100),
            'disabled': (100, 100, 100, 128)
        }
        self.default_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
    
    def get_font(self, size: str = "normal") -> pygame.font.Font:
        if size == "small":
            return self.small_font
        elif size == "large":
            return self.large_font
        return self.default_font

class UISystem:
    """Manages UI widgets and input event routing"""
    def __init__(self, engine):
        self.engine = engine
        self.widgets: List['Widget'] = []
        self.theme = UITheme()
        self.focused_widget: Optional['Widget'] = None
        self.hovered_widget: Optional['Widget'] = None
        self.debug = False
    
    def add_widget(self, widget: 'Widget'):
        widget.ui_system = self
        self.widgets.append(widget)
    
    def remove_widget(self, widget: 'Widget'):
        if widget in self.widgets:
            self.widgets.remove(widget)
    
    def handle_event(self, event: pygame.event.Event):
        # Find widget under mouse for hover
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            mouse_pos = pygame.mouse.get_pos()
            self.hovered_widget = None
            for widget in reversed(self.widgets):
                if widget.enabled and widget.visible:
                    if widget.get_rect().collidepoint(mouse_pos):
                        self.hovered_widget = widget
                        break
        
        # Dispatch event to focused widget and hovered widget
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered_widget:
            self.focused_widget = self.hovered_widget
        
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            if self.hovered_widget:
                self.hovered_widget.handle_event(event)
        
        if event.type in (pygame.KEYDOWN, pygame.KEYUP, pygame.TEXTINPUT):
            if self.focused_widget and self.focused_widget.accepts_focus:
                self.focused_widget.handle_event(event)
    
    def update(self, dt: float):
        for widget in self.widgets:
            widget.update(dt)
    
    def render(self, screen: pygame.Surface):
        for widget in self.widgets:
            widget.render(screen)
        
        if self.debug:
            for widget in self.widgets:
                rect = widget.get_rect()
                pygame.draw.rect(screen, (0, 255, 0), rect, 2)

class Widget:
    """Base UI widget"""
    def __init__(self, x: int = 0, y: int = 0, width: int = 100, height: int = 30):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
        self.enabled = True
        self.parent = None
        self.children = []
        self.ui_system = None
        self.accepts_focus = False
        self.tooltip = None
    
    def get_rect(self) -> pygame.Rect:
        return self.rect
    
    def handle_event(self, event: pygame.event.Event):
        pass
    
    def update(self, dt: float):
        pass
    
    def render(self, screen: pygame.Surface):
        pass