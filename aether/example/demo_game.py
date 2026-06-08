"""
Demo game showcasing engine capabilities
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.engine import AetherEngine, EngineConfig
from core.scene_manager import Scene
from entities.entity import Entity, Transform, SpriteRenderer, RigidBody
from physics.physics_world import PhysicsBody
import pygame
import numpy as np
import random

class GameScene(Scene):
    """Main game scene"""
    
    def __init__(self, engine):
        super().__init__(engine, "game")
        self.player = None
        self.enemies = []
        self.ai_enabled = True
        
    def on_enter(self):
        """Called when scene is entered"""
        # Create player
        self.player = Entity("Player", "player")
        self.player.transform.position = np.array([400, 300])
        self.player.add_component(Transform())
        
        # Add player sprite
        player_sprite = SpriteRenderer()
        player_sprite.image = self._create_circle_surface(20, (0, 100, 255))
        self.player.add_component(player_sprite)
        
        # Add physics
        player_physics = RigidBody()
        player_physics.mass = 1.0
        player_physics.drag = 0.5
        self.player.add_component(player_physics)
        
        # Create physics body
        player_body = PhysicsBody(
            self.player.transform.position.copy(),
            mass=1.0, shape='circle', radius=20
        )
        self.engine.physics.add_body(player_body)
        self.player.physics_body = player_body
        
        # Create some enemies
        for i in range(5):
            self._spawn_enemy()
        
        # Setup AI behavior tree
        if self.ai_enabled:
            self._setup_ai()
        
        # Create particle system
        from graphics.renderer import ParticleSystem
        self.ps = ParticleSystem(500)
        self.engine.renderer.add_particle_system(self.ps)
        
    def on_exit(self):
        """Called when scene is exited"""
        pass
    
    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._player_shoot()
            elif event.key == pygame.K_e:
                self._spawn_enemy()
            elif event.key == pygame.K_r:
                self.engine.scenes.reload_current_scene()
    
    def update(self, dt: float):
        """Update scene"""
        # Update player
        self._update_player(dt)
        
        # Update enemies with AI
        self._update_enemies(dt)
        
        # Update particle system
        self.ps.update(dt)
        
        # Keep Enemies inside bounds
        self._constrain_to_screen(self.player)
        for enemy in self.enemies:
            self._constrain_to_screen(enemy)
        
        # Check collisions
        self._check_collisions()
    
    def render(self, screen: pygame.Surface):
        """Render scene"""
        super().render(screen)
        
        # Draw HUD
        self._render_hud(screen)
    
    def _update_player(self, dt: float):
        """Update player movement"""
        keys = pygame.key.get_pressed()
        speed = 300
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.transform.position[0] -= speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.transform.position[0] += speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.transform.position[1] -= speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player.transform.position[1] += speed * dt
        
        # Update physics body
        self.player.physics_body.position = self.player.transform.position.copy()
    
    def _update_enemies(self, dt: float):
        """Update enemy AI behavior"""
        for enemy in self.enemies:
            # Get AI component
            ai_controller = enemy.get_component(AIController) if hasattr(enemy, 'get_component') else None
            
            if ai_controller:
                # Use AI behavior tree
                ai_controller.update(dt)
            else:
                # Simple wander behavior
                self._simple_enemy_ai(enemy, dt)
    
    def _simple_enemy_ai(self, enemy, dt: float):
        """Simple enemy AI behavior"""
        if not hasattr(enemy, 'wander_target'):
            enemy.wander_target = enemy.transform.position.copy()
            enemy.wander_timer = 0
        
        enemy.wander_timer -= dt
        
        if enemy.wander_timer <= 0:
            # New wander target
            enemy.wander_target = enemy.transform.position + np.random.randn(2) * 100
            enemy.wander_timer = random.uniform(1.0, 3.0)
        
        # Move towards wander target
        direction = enemy.wander_target - enemy.transform.position
        distance = np.linalg.norm(direction)
        
        if distance > 10:
            direction = direction / distance
            enemy.transform.position += direction * 100 * dt
    
    def _setup_ai(self):
        """Setup AI behavior trees for enemies"""
        for enemy in self.enemies:
            ai = AIController(enemy, self.player, self.engine)
            enemy.add_component(ai)
    
    def _player_shoot(self):
        """Player shooting mechanic"""
        # Emit particles
        self.ps.emit(
            position=self.player.transform.position.copy(),
            velocity_range=((-200, 200), (-200, 200)),
            life_range=(0.5, 1.5),
            color=(255, 200, 0),
            size_range=(2, 8),
            count=20
        )
    
    def _spawn_enemy(self):
        """Spawn new enemy"""
        enemy = Entity(f"Enemy_{len(self.enemies)}", "enemy")
        
        # Random position
        x = random.randint(100, self.engine.config.width - 100)
        y = random.randint(100, self.engine.config.height - 100)
        enemy.transform.position = np.array([x, y])
        
        # Add sprite
        sprite = SpriteRenderer()
        sprite.image = self._create_circle_surface(15, (255, 50, 50))
        enemy.add_component(sprite)
        
        self.enemies.append(enemy)
        self.add_entity(enemy)
        
        # Add AI if enabled
        if self.ai_enabled and hasattr(self, 'player') and self.player:
            ai = AIController(enemy, self.player, self.engine)
            enemy.add_component(ai)
    
    def _create_circle_surface(self, radius, color):
        """Create a circle surface"""
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (radius, radius), radius)
        return surf
    
    def _constrain_to_screen(self, entity):
        """Keep entity within screen bounds"""
        pos = entity.transform.position
        pos[0] = max(20, min(pos[0], self.engine.config.width - 20))
        pos[1] = max(20, min(pos[1], self.engine.config.height - 20))
    
    def _check_collisions(self):
        """Check collisions between entities"""
        for enemy in self.enemies[:]:
            distance = np.linalg.norm(
                enemy.transform.position - self.player.transform.position
            )
            
            if distance < 35:  # Collision radius
                # Damage player
                self._on_player_hit(enemy)
    
    def _on_player_hit(self, enemy):
        """Handle player being hit"""
        # Emit damage particles
        self.ps.emit(
            position=self.player.transform.position.copy(),
            velocity_range=((-300, 300), (-300, 300)),
            life_range=(0.3, 0.8),
            color=(255, 255, 255),
            size_range=(3, 6),
            count=30
        )
        
        # Remove enemy
        enemy.destroy()
        self.enemies.remove(enemy)
        self.remove_entity(enemy)
        
        # Spawn new enemy
        self._spawn_enemy()
    
    def _render_hud(self, screen):
        """Render HUD elements"""
        font = pygame.font.Font(None, 36)
        
        # Score/Status
        status_text = f"Enemies: {len(self.enemies)}"
        text_surface = font.render(status_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # Controls hint
        controls = [
            "WASD/Arrows: Move",
            "Space: Shoot",
            "E: Spawn Enemy",
            "R: Reset",
            "F2: Pause",
            "F3: Debug"
        ]
        
        for i, control in enumerate(controls):
            control_surface = font.render(control, True, (150, 150, 150))
            screen.blit(control_surface, 
                       (10, self.engine.config.height - 30 * (len(controls) - i)))

class AIController:
    """AI controller using behavior tree"""
    
    def __init__(self, entity, target, engine):
        self.entity = entity
        self.target = target
        self.engine = engine
        self.state = "idle"
        self.timer = 0
        
        # Setup behavior tree
        self.bt = self.engine.ai.create_behavior_tree(f"enemy_{id(self)}")
        
        # Build tree
        root = BehaviorTree.Selector("Root")
        
        # Chase sequence
        chase_seq = BehaviorTree.Sequence("Chase")
        chase_seq.add_child(
            BehaviorTree.Condition(
                lambda ctx: self._is_target_near(ctx),
                "NearTarget"
            )
        )
        chase_seq.add_child(
            BehaviorTree.Action(
                lambda ctx: self._chase_target(ctx),
                "ChaseTarget"
            )
        )
        
        # Wander sequence
        wander_seq = BehaviorTree.Sequence("Wander")
        wander_seq.add_child(
            BehaviorTree.Action(
                lambda ctx: self._wander(ctx),
                "WanderAround"
            )
        )
        
        root.add_child(chase_seq)
        root.add_child(wander_seq)
        
        self.bt.set_root(root)
    
    def update(self, dt):
        """Update AI controller"""
        self.bt.update(dt)
    
    def _is_target_near(self, context):
        """Check if target is nearby"""
        distance = np.linalg.norm(
            self.entity.transform.position - self.target.transform.position
        )
        return distance < 300
    
    def _chase_target(self, context):
        """Chase target behavior"""
        direction = self.target.transform.position - self.entity.transform.position
        distance = np.linalg.norm(direction)
        
        if distance > 50:
            direction = direction / distance
            self.entity.transform.position += direction * 200 * context.get('dt', 0.016)
        return True
    
    def _wander(self, context):
        """Wander behavior"""
        dt = context.get('dt', 0.016)
        self.timer -= dt
        
        if self.timer <= 0:
            self.wander_target = self.entity.transform.position + np.random.randn(2) * 100
            self.timer = random.uniform(1.0, 3.0)
        
        direction = self.wander_target - self.entity.transform.position
        distance = np.linalg.norm(direction)
        
        if distance > 10:
            direction = direction / distance
            self.entity.transform.position += direction * 100 * dt
        return True

def main():
    """Main entry point"""
    # Configure engine
    config = EngineConfig(
        title="AetherEngine Demo",
        width=1280,
        height=720,
        fps=60,
        debug_mode=False,
        enable_ai=True
    )
    
    # Create engine
    engine = AetherEngine(config)
    
    # Add game scene
    engine.scenes.add_scene(GameScene(engine))
    
    # Run engine
    engine.run("game")

if __name__ == "__main__":
    main()