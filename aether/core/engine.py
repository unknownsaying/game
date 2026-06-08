"""
AetherEngine - Advanced AI-Integrated Game Engine
Core engine orchestration module
"""

import pygame
import numpy as np
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import logging
import time
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AetherEngine")

@dataclass
class EngineConfig:
    """Engine configuration settings"""
    width: int = 1280
    height: int = 720
    title: str = "AetherEngine Game"
    fps: int = 60
    vsync: bool = True
    fullscreen: bool = False
    debug_mode: bool = False
    physics_scale: float = 100.0  # pixels per meter
    enable_ai: bool = True
    enable_raytracing: bool = False
    max_particles: int = 10000
    asset_path: str = "assets/"
    save_path: str = "saves/"

class AetherEngine:
    """Main engine class orchestrating all systems"""
    
    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig()
        self.running = False
        self.paused = False
        self.delta_time = 0.0
        self.time_scale = 1.0
        self.frame_count = 0
        self.total_time = 0.0
        
        # Initialize Pygame
        pygame.init()
        pygame.mixer.init()
        
        # Setup display
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        if self.config.fullscreen:
            flags |= pygame.FULLSCREEN
        if self.config.vsync:
            flags |= pygame.SCALED
            
        self.screen = pygame.display.set_mode(
            (self.config.width, self.config.height), flags
        )
        pygame.display.set_caption(self.config.title)
        self.clock = pygame.time.Clock()
        
        # Initialize subsystems
        self.systems = {}
        self._initialize_systems()
        
        # Performance monitoring
        self.performance_stats = {
            'fps': 0, 'frame_time': 0, 
            'update_time': 0, 'render_time': 0
        }
        
        # Event callbacks
        self.event_handlers = []
        self.update_callbacks = []
        self.render_callbacks = []
        
        logger.info("AetherEngine initialized successfully")
        
    def _initialize_systems(self):
        """Initialize all engine subsystems"""
        from core.resource_manager import ResourceManager
        from core.scene_manager import SceneManager
        from core.event_system import EventSystem
        from graphics.renderer import Renderer
        from graphics.camera import CameraSystem
        from physics.physics_world import PhysicsWorld
        from audio.audio_manager import AudioManager
        from ai.ai_manager import AIManager
        from ui.ui_system import UISystem
        
        # Resource & Asset Management
        self.resources = ResourceManager(self.config.asset_path)
        
        # Scene Management
        self.scenes = SceneManager(self)
        
        # Event System
        self.events = EventSystem()
        
        # Rendering Pipeline
        self.renderer = Renderer(self)
        self.camera = CameraSystem(self)
        
        # Physics Engine
        self.physics = PhysicsWorld(self.config.physics_scale)
        
        # Audio System
        self.audio = AudioManager()
        
        # AI System
        if self.config.enable_ai:
            self.ai = AIManager(self)
        
        # UI System
        self.ui = UISystem(self)
        
        # Store all systems for easy access
        self.systems = {
            'resources': self.resources,
            'scenes': self.scenes,
            'events': self.events,
            'renderer': self.renderer,
            'camera': self.camera,
            'physics': self.physics,
            'audio': self.audio,
            'ai': self.ai if self.config.enable_ai else None,
            'ui': self.ui
        }
        
    def run(self, start_scene: str = "main"):
        """Main engine loop"""
        self.running = True
        self.scenes.load_scene(start_scene)
        
        logger.info(f"Engine started with scene: {start_scene}")
        
        while self.running:
            frame_start = time.perf_counter()
            
            # Calculate delta time
            self.delta_time = self.clock.tick(self.config.fps) / 1000.0
            self.delta_time *= self.time_scale
            
            # Performance tracking
            self.total_time += self.delta_time
            self.frame_count += 1
            
            # Process events
            self._handle_events()
            
            # Update
            update_start = time.perf_counter()
            if not self.paused:
                self._update()
            self.performance_stats['update_time'] = time.perf_counter() - update_start
            
            # Render
            render_start = time.perf_counter()
            self._render()
            self.performance_stats['render_time'] = time.perf_counter() - render_start
            
            # Display frame
            pygame.display.flip()
            
            # Update performance stats
            frame_time = time.perf_counter() - frame_start
            self.performance_stats['fps'] = 1.0 / frame_time if frame_time > 0 else 0
            self.performance_stats['frame_time'] = frame_time * 1000  # ms
            
            # Debug overlay
            if self.config.debug_mode:
                self._render_debug_overlay()
                
        self.shutdown()
        
    def _handle_events(self):
        """Process all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                elif event.key == pygame.K_F3:
                    self.config.debug_mode = not self.config.debug_mode
                elif event.key == pygame.K_F2:
                    self.paused = not self.paused
                elif event.key == pygame.K_F5:
                    self.scenes.reload_current_scene()
            
            # Dispatch to scene
            self.scenes.handle_event(event)
            
            # Custom event handlers
            for handler in self.event_handlers:
                handler(event)
                
    def _update(self):
        """Update all systems"""
        # Update physics
        self.physics.update(self.delta_time)
        
        # Update AI
        if self.config.enable_ai:
            self.ai.update(self.delta_time)
        
        # Update scene
        self.scenes.update(self.delta_time)
        
        # Update UI
        self.ui.update(self.delta_time)
        
        # Custom update callbacks
        for callback in self.update_callbacks:
            callback(self.delta_time)
            
    def _render(self):
        """Render pipeline"""
        # Clear screen
        self.screen.fill((20, 20, 30))
        
        # Camera transformations
        self.camera.begin_frame()
        
        # Render scene
        self.scenes.render(self.screen)
        
        # Render physics debug
        if self.config.debug_mode:
            self.physics.render_debug(self.screen, self.camera)
        
        # Camera end frame
        self.camera.end_frame()
        
        # Particle systems
        self.renderer.render_particles(self.screen)
        
        # Post-processing effects
        self.renderer.apply_post_processing(self.screen)
        
        # Render UI (screen space, no camera transform)
        self.ui.render(self.screen)
        
        # Custom render callbacks
        for callback in self.render_callbacks:
            callback(self.screen)
            
    def _render_debug_overlay(self):
        """Render debug information"""
        import pygame.gfxdraw
        
        # Semi-transparent overlay
        overlay = pygame.Surface((300, 120), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (10, 10))
        
        # Debug text
        font = pygame.font.Font(None, 24)
        debug_info = [
            f"FPS: {self.performance_stats['fps']:.1f}",
            f"Frame: {self.performance_stats['frame_time']:.1f}ms",
            f"Update: {self.performance_stats['update_time']*1000:.1f}ms",
            f"Render: {self.performance_stats['render_time']*1000:.1f}ms",
            f"Scene: {self.scenes.current_scene_name}"
        ]
        
        for i, text in enumerate(debug_info):
            surface = font.render(text, True, (100, 255, 100))
            self.screen.blit(surface, (20, 20 + i * 25))
            
    def register_event_handler(self, handler: Callable):
        """Register custom event handler"""
        self.event_handlers.append(handler)
        
    def register_update_callback(self, callback: Callable):
        """Register update callback"""
        self.update_callbacks.append(callback)
        
    def register_render_callback(self, callback: Callable):
        """Register render callback"""
        self.render_callbacks.append(callback)
        
    def quit(self):
        """Shutdown engine"""
        logger.info("Shutting down engine...")
        self.running = False
        
    def shutdown(self):
        """Clean shutdown of all systems"""
        self.audio.cleanup()
        pygame.quit()
        logger.info("Engine shutdown complete")