"""
Concrete UI Widgets
Buttons, labels, panels, sliders, progress bars, text inputs
"""

import pygame
import re
from .ui_system import Widget, UITheme

class Button(Widget):
    def __init__(self, x, y, width, height, text="", callback=None, 
                 style: str = "default"):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.style = style
        self.hovered = False
        self.pressed = False
        self.accepts_focus = True
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.get_rect().collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and event.button == 1:
                self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.hovered:
                if self.callback:
                    self.callback()
            self.pressed = False
    
    def render(self, screen):
        if not self.visible:
            return
        theme = self.ui_system.theme
        color = theme.colors['foreground']
        if not self.enabled:
            color = theme.colors['disabled']
        elif self.pressed:
            color = theme.colors['active']
        elif self.hovered:
            color = theme.colors['hover']
        
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        if self.text:
            font = theme.get_font("normal")
            text_surf = font.render(self.text, True, theme.colors['text'])
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

class Label(Widget):
    def __init__(self, x, y, text="", font_size="normal", color=None):
        super().__init__(x, y, 0, 0)
        self.text = text
        self.font_size = font_size
        self.color = color
        self._update_surface()
    
    def set_text(self, text):
        self.text = text
        self._update_surface()
    
    def _update_surface(self):
        if self.ui_system:
            theme = self.ui_system.theme
            font = theme.get_font(self.font_size)
            self._text_surf = font.render(self.text, True, 
                                         self.color or theme.colors['text'])
            self.rect.width = self._text_surf.get_width()
            self.rect.height = self._text_surf.get_height()
    
    def render(self, screen):
        if self.visible and hasattr(self, '_text_surf'):
            screen.blit(self._text_surf, self.rect.topleft)

class Panel(Widget):
    def __init__(self, x, y, width, height, color=None):
        super().__init__(x, y, width, height)
        self.color = color
    
    def render(self, screen):
        if not self.visible:
            return
        theme = self.ui_system.theme
        bg = self.color or theme.colors['background']
        pygame.draw.rect(screen, bg, self.rect, border_radius=3)
        # Draw children
        for child in self.children:
            child.render(screen)

class Slider(Widget):
    def __init__(self, x, y, width, height=20, min_val=0, max_val=100,
                 value=0, callback=None):
        super().__init__(x, y, width, height)
        self.min = min_val
        self.max = max_val
        self.value = value
        self.callback = callback
        self.dragging = False
        self.accepts_focus = True
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.get_rect().collidepoint(event.pos):
            self.dragging = True
            self._update_value(event.pos[0])
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
    
    def _update_value(self, mouse_x):
        rel_x = (mouse_x - self.rect.x) / self.rect.width
        self.value = self.min + (self.max - self.min) * max(0, min(1, rel_x))
        if self.callback:
            self.callback(self.value)
    
    def render(self, screen):
        theme = self.ui_system.theme
        pygame.draw.rect(screen, theme.colors['background'], self.rect)
        fill_width = int((self.value - self.min) / (self.max - self.min) * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
        pygame.draw.rect(screen, theme.colors['accent'], fill_rect)
        # Thumb
        thumb_x = self.rect.x + fill_width - 5
        pygame.draw.circle(screen, theme.colors['foreground'], (thumb_x, self.rect.centery), 8)

class ProgressBar(Widget):
    def __init__(self, x, y, width, height=20, value=0.0, max_value=1.0, 
                 color=None, show_text=True):
        super().__init__(x, y, width, height)
        self.value = value
        self.max_value = max_value
        self.color = color
        self.show_text = show_text
    
    def render(self, screen):
        theme = self.ui_system.theme
        bar_rect = self.rect.copy()
        pygame.draw.rect(screen, theme.colors['background'], bar_rect)
        fill_width = int((self.value / self.max_value) * bar_rect.width)
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)
        fill_color = self.color or theme.colors['accent']
        pygame.draw.rect(screen, fill_color, fill_rect)
        if self.show_text:
            text = f"{int(self.value / self.max_value * 100)}%"
            font = theme.get_font("small")
            text_surf = font.render(text, True, theme.colors['text'])
            text_rect = text_surf.get_rect(center=bar_rect.center)
            screen.blit(text_surf, text_rect)

class TextInput(Widget):
    def __init__(self, x, y, width, height=30, placeholder="", 
                 validator=None, on_enter=None):
        super().__init__(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.validator = validator or (lambda s: True)
        self.on_enter = on_enter
        self.cursor_pos = 0
        self.accepts_focus = True
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.ui_system.focused_widget == self:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.key == pygame.K_RETURN:
                if self.on_enter:
                    self.on_enter(self.text)
        elif event.type == pygame.TEXTINPUT and self.ui_system.focused_widget == self:
            new_text = self.text[:self.cursor_pos] + event.text + self.text[self.cursor_pos:]
            if self.validator(new_text):
                self.text = new_text
                self.cursor_pos += len(event.text)
    
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def render(self, screen):
        theme = self.ui_system.theme
        bg = theme.colors['background']
        border = theme.colors['foreground']
        pygame.draw.rect(screen, bg, self.rect)
        pygame.draw.rect(screen, border, self.rect, 2)
        
        display_text = self.text if self.text else self.placeholder
        font = theme.get_font("normal")
        text_surf = font.render(display_text, True, 
                               theme.colors['text'] if self.text else (150,150,150))
        
        # Clip text if too long
        if text_surf.get_width() > self.rect.width - 10:
            # Simple scrolling - show end part
            pass
        
        screen.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))
        
        # Draw cursor
        if self.ui_system.focused_widget == self and self.cursor_visible:
            cursor_x = self.rect.x + 5 + font.size(self.text[:self.cursor_pos])[0]
            pygame.draw.line(screen, theme.colors['text'],
                           (cursor_x, self.rect.y + 5),
                           (cursor_x, self.rect.y + self.rect.height - 10), 2)

class Image(Widget):
    def __init__(self, x, y, image: pygame.Surface):
        super().__init__(x, y, image.get_width(), image.get_height())
        self.image = image
    
    def render(self, screen):
        if self.visible:
            screen.blit(self.image, self.rect.topleft)