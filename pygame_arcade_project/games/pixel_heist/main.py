"""
Pixel Heist - Stealth Game
A top-down stealth heist game.
"""

import pygame
import sys
import os
import math
import random
from enum import Enum

# Add parent directory to path to import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class GameState(Enum):
    """Game state enumeration."""
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    VICTORY = 5

class Player(pygame.sprite.Sprite):
    """Player character for the heist game."""
    
    def __init__(self, x, y):
        super().__init__()
        self.size = 32
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Draw player (simple thief character)
        pygame.draw.circle(self.image, (0, 200, 0), (self.size//2, self.size//2), self.size//2)  # Green body
        pygame.draw.circle(self.image, (0, 100, 0), (self.size//2, self.size//2), self.size//2, 2)  # Outline
        pygame.draw.circle(self.image, (0, 0, 0), (self.size//2 + 5, self.size//2 - 5), 3)  # Eye
        
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(x, y)
        self.rect.center = self.position
        
        # Movement
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 200
        self.is_crouching = False
        self.is_running = False
        
        # Stealth
        self.noise_level = 0  # 0-100
        self.visibility = 0   # 0-100
        
        # Inventory
        self.loot_count = 0
    
    def update(self, dt, walls=None):
        """Update player position and state."""
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Movement
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        
        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        
        # Update player state
        self.is_running = keys[pygame.K_LSHIFT]
        self.is_crouching = keys[pygame.K_LCTRL]
        
        # Apply movement with speed modifiers
        speed = self.speed
        if self.is_running:
            speed *= 1.5
        elif self.is_crouching:
            speed *= 0.5
        
        self.velocity.x = dx * speed
        self.velocity.y = dy * speed
        
        # Update position
        old_position = self.position.copy()
        self.position += self.velocity * dt
        self.rect.center = self.position
        
        # Handle collisions with walls
        if walls:
            collisions = pygame.sprite.spritecollide(self, walls, False)
            if collisions:
                self.position = old_position
                self.rect.center = self.position
        
        # Update noise level
        if dx == 0 and dy == 0:
            self.noise_level = max(0, self.noise_level - 1)
        elif self.is_running:
            self.noise_level = min(100, self.noise_level + 2)
        elif self.is_crouching:
            self.noise_level = max(0, self.noise_level - 0.5)
        else:
            self.noise_level = min(50, self.noise_level + 0.5)
    
    def draw(self, surface):
        """Draw the player."""
        # Draw player
        surface.blit(self.image, self.rect)
        
        # Draw noise radius if making noise
        if self.noise_level > 0:
            noise_radius = self.noise_level
            noise_surf = pygame.Surface((noise_radius * 2, noise_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                noise_surf,
                (255, 255, 0, 50),  # Yellow with alpha
                (noise_radius, noise_radius),
                noise_radius
            )
            surface.blit(
                noise_surf,
                (self.position.x - noise_radius, self.position.y - noise_radius)
            )

class Guard(pygame.sprite.Sprite):
    """Guard character that patrols and detects the player."""
    
    def __init__(self, x, y, patrol_points=None):
        super().__init__()
        self.size = 32
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Draw guard (simple security character)
        pygame.draw.circle(self.image, (200, 0, 0), (self.size//2, self.size//2), self.size//2)  # Red body
        pygame.draw.circle(self.image, (100, 0, 0), (self.size//2, self.size//2), self.size//2, 2)  # Outline
        pygame.draw.circle(self.image, (0, 0, 0), (self.size//2 + 5, self.size//2 - 5), 3)  # Eye
        
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(x, y)
        self.rect.center = self.position
        
        # Movement
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 100
        
        # Patrol
        self.patrol_points = patrol_points or [(x, y)]
        self.current_point = 0
        self.wait_timer = 0
        self.wait_duration = 1.0  # seconds to wait at each point
        
        # Detection
        self.view_distance = 150
        self.view_angle = 90  # degrees
        self.view_direction = 0  # degrees (0 is right, 90 is down)
        self.alert_level = 0  # 0-100
        self.alerted = False
    
    def update(self, dt, player=None, walls=None):
        """Update guard position and state."""
        if self.alerted and player:
            # Chase player
            to_player = player.position - self.position
            distance = to_player.length()
            
            if distance > 5:
                direction = to_player.normalize()
                self.velocity = direction * self.speed * 1.5  # Move faster when alerted
                self.view_direction = math.degrees(math.atan2(direction.y, direction.x))
            else:
                self.velocity = pygame.math.Vector2(0, 0)
        else:
            # Follow patrol path
            if self.wait_timer > 0:
                self.wait_timer -= dt
                self.velocity = pygame.math.Vector2(0, 0)
            else:
                target = pygame.math.Vector2(self.patrol_points[self.current_point])
                to_target = target - self.position
                distance = to_target.length()
                
                if distance < 5:
                    # Reached patrol point, wait
                    self.wait_timer = self.wait_duration
                    self.current_point = (self.current_point + 1) % len(self.patrol_points)
                else:
                    # Move toward patrol point
                    direction = to_target.normalize()
                    self.velocity = direction * self.speed
                    self.view_direction = math.degrees(math.atan2(direction.y, direction.x))
        
        # Update position
        old_position = self.position.copy()
        self.position += self.velocity * dt
        self.rect.center = self.position
        
        # Handle collisions with walls
        if walls:
            collisions = pygame.sprite.spritecollide(self, walls, False)
            if collisions:
                self.position = old_position
                self.rect.center = self.position
        
        # Check for player detection
        if player:
            self.check_player_detection(player, walls)
    
    def check_player_detection(self, player, walls=None):
        """Check if guard can see or hear the player."""
        # Calculate vector to player
        to_player = player.position - self.position
        distance = to_player.length()
        
        # Check noise detection
        if distance <= player.noise_level + self.view_distance * 0.3:
            self.alert_level += 5
            if self.alert_level >= 100:
                self.alerted = True
            return
        
        # Check visual detection
        if distance <= self.view_distance:
            # Check if player is within view angle
            angle = math.degrees(math.atan2(to_player.y, to_player.x))
            angle_diff = abs((angle - self.view_direction + 180) % 360 - 180)
            
            if angle_diff <= self.view_angle / 2:
                # Check if there's a wall blocking the view
                if walls:
                    # Cast a ray to check for walls
                    ray_hit = self.cast_ray(self.position, player.position, walls)
                    if not ray_hit:
                        # Clear line of sight
                        self.alert_level += 10
                        if self.alert_level >= 100:
                            self.alerted = True
                else:
                    # No walls to check
                    self.alert_level += 10
                    if self.alert_level >= 100:
                        self.alerted = True
        
        # Alert level decreases over time if not detecting
        if self.alert_level > 0 and not self.alerted:
            self.alert_level -= 0.5
    
    def cast_ray(self, start, end, walls, step=5):
        """Cast a ray from start to end, checking for wall collisions."""
        direction = end - start
        distance = direction.length()
        direction = direction.normalize()
        
        for i in range(0, int(distance), step):
            point = start + direction * i
            point_rect = pygame.Rect(point.x - 1, point.y - 1, 2, 2)
            
            for wall in walls:
                if wall.rect.colliderect(point_rect):
                    return True  # Hit a wall
        
        return False  # No wall hit
    
    def draw(self, surface):
        """Draw the guard and vision cone."""
        # Draw vision cone if not alerted
        if not self.alerted:
            # Create points for vision cone
            points = [(self.position.x, self.position.y)]
            
            half_angle = self.view_angle / 2
            for i in range(21):  # 20 segments for smooth arc
                angle = math.radians(self.view_direction - half_angle + i * self.view_angle / 20)
                x = self.position.x + math.cos(angle) * self.view_distance
                y = self.position.y + math.sin(angle) * self.view_distance
                points.append((x, y))
            
            # Draw vision cone
            vision_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(vision_surf, (255, 255, 0, 50), points)
            surface.blit(vision_surf, (0, 0))
        else:
            # Draw alert indicator
            alert_radius = self.view_distance
            alert_surf = pygame.Surface((alert_radius * 2, alert_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                alert_surf,
                (255, 0, 0, 50),  # Red with alpha
                (alert_radius, alert_radius),
                alert_radius
            )
            surface.blit(
                alert_surf,
                (self.position.x - alert_radius, self.position.y - alert_radius)
            )
            
            # Draw exclamation mark
            font = pygame.font.SysFont("Arial", 24, bold=True)
            text = font.render("!", True, (255, 255, 255))
            surface.blit(text, (self.position.x - 5, self.position.y - 40))
        
        # Draw guard
        surface.blit(self.image, self.rect)

class Loot(pygame.sprite.Sprite):
    """Loot item that can be collected by the player."""
    
    def __init__(self, x, y, value=100):
        super().__init__()
        self.size = 16
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Draw loot (simple treasure)
        pygame.draw.circle(self.image, (255, 215, 0), (self.size//2, self.size//2), self.size//2)  # Gold
        pygame.draw.circle(self.image, (200, 170, 0), (self.size//2, self.size//2), self.size//2, 2)  # Outline
        
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(x, y)
        self.rect.center = self.position
        
        self.value = value
        self.collected = False
        
        # Animation
        self.hover_offset = 0
        self.original_y = y
    
    def update(self, dt):
        """Update loot animation."""
        # Hover effect
        self.hover_offset = math.sin(pygame.time.get_ticks() * 0.003) * 3
        self.position.y = self.original_y + self.hover_offset
        self.rect.center = self.position
    
    def draw(self, surface):
        """Draw the loot item."""
        surface.blit(self.image, self.rect)
        
        # Draw sparkle effect
        if random.random() < 0.1:
            sparkle_x = self.position.x + random.randint(-self.size//2, self.size//2)
            sparkle_y = self.position.y + random.randint(-self.size//2, self.size//2)
            pygame.draw.circle(surface, (255, 255, 255), (int(sparkle_x), int(sparkle_y)), 2)

class Wall(pygame.sprite.Sprite):
    """Wall obstacle for the game."""
    
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((100, 100, 100))  # Gray walls
        pygame.draw.rect(self.image, (50, 50, 50), (0, 0, width, height), 2)  # Outline
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Game:
    """Main game class for Pixel Heist."""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pixel Heist")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = GameState.MENU
        self.running = True
        self.score = 0
        self.time = 0
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.guards = pygame.sprite.Group()
        self.loots = pygame.sprite.Group()
        
        # Load fonts
        self.title_font = pygame.font.SysFont("Arial", 48)
        self.menu_font = pygame.font.SysFont("Arial", 32)
        self.hud_font = pygame.font.SysFont("Arial", 24)
        
        # Create level
        self.create_level()
    
    def create_level(self):
        """Create a simple level with walls, guards, and loot."""
        # Clear existing sprites
        self.all_sprites.empty()
        self.walls.empty()
        self.guards.empty()
        self.loots.empty()
        
        # Create outer walls
        wall_thickness = 20
        walls = [
            # Outer walls
            Wall(0, 0, SCREEN_WIDTH, wall_thickness),  # Top
            Wall(0, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH, wall_thickness),  # Bottom
            Wall(0, 0, wall_thickness, SCREEN_HEIGHT),  # Left
            Wall(SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT),  # Right
            
            # Inner walls
            Wall(200, 100, 20, 200),
            Wall(400, 300, 200, 20),
            Wall(600, 100, 20, 200),
            Wall(200, 500, 400, 20)
        ]
        
        for wall in walls:
            self.walls.add(wall)
            self.all_sprites.add(wall)
        
        # Create player
        self.player = Player(100, 100)
        self.all_sprites.add(self.player)
        
        # Create guards with patrol paths
        guard1 = Guard(300, 200, [(300, 200), (500, 200), (500, 400), (300, 400)])
        guard2 = Guard(600, 500, [(600, 500), (700, 500), (700, 300), (600, 300)])
        
        self.guards.add(guard1, guard2)
        self.all_sprites.add(guard1, guard2)
        
        # Create loot
        loot_positions = [(150, 150), (400, 200), (700, 150), (300, 500), (650, 450)]
        for i, pos in enumerate(loot_positions):
            value = (i + 1) * 100
            loot = Loot(pos[0], pos[1], value)
            self.loots.add(loot)
            self.all_sprites.add(loot)
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                    elif self.state == GameState.PAUSED:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.MENU:
                        self.running = False
                
                elif event.key == pygame.K_RETURN:
                    if self.state == GameState.MENU:
                        self.start_game()
                    elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                        self.state = GameState.MENU
    
    def update(self, dt):
        """Update game state."""
        if self.state != GameState.PLAYING:
            return
        
        # Update game time
        self.time += dt
        
        # Update player
        self.player.update(dt, self.walls)
        
        # Update guards
        for guard in self.guards:
            guard.update(dt, self.player, self.walls)
            
            # Check if player is caught
            if guard.alerted:
                if pygame.sprite.collide_rect(guard, self.player):
                    self.game_over()
        
        # Update loot
        for loot in self.loots:
            loot.update(dt)
            
            # Check collection
            if not loot.collected and pygame.sprite.collide_rect(self.player, loot):
                loot.collected = True
                self.score += loot.value
                self.player.loot_count += 1
                loot.kill()
        
        # Check victory condition
        if len(self.loots) == 0:
            self.victory()
    
    def draw_menu(self):
        """Draw the main menu."""
        self.screen.fill((0, 0, 0))
        
        # Draw title
        title_surf = self.title_font.render("PIXEL HEIST", True, (0, 255, 0))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        self.screen.blit(title_surf, title_rect)
        
        # Draw menu options
        start_text = self.menu_font.render("Press ENTER to Start", True, (255, 255, 255))
        quit_text = self.menu_font.render("Press ESC to Quit", True, (255, 255, 255))
        
        self.screen.blit(
            start_text,
            (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2)
        )
        self.screen.blit(
            quit_text,
            (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 + 50)
        )
    
    def draw_game(self):
        """Draw the game screen."""
        self.screen.fill((20, 20, 20))  # Dark background
        
        # Draw all sprites
        for sprite in self.all_sprites:
            if hasattr(sprite, 'draw'):
                sprite.draw(self.screen)
            else:
                self.screen.blit(sprite.image, sprite.rect)
        
        # Draw HUD
        self.draw_hud()
    
    def draw_hud(self):
        """Draw the heads-up display."""
        # Draw score
        score_text = self.hud_font.render(f"Loot: ${self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw time
        time_text = self.hud_font.render(f"Time: {int(self.time)}s", True, (255, 255, 255))
        self.screen.blit(time_text, (SCREEN_WIDTH - 150, 10))
        
        # Draw noise meter
        noise_text = self.hud_font.render(f"Noise: {'|' * int(self.player.noise_level / 10)}", True, (255, 255, 255))
        self.screen.blit(noise_text, (10, SCREEN_HEIGHT - 30))
        
        # Draw controls help
        controls_font = pygame.font.SysFont("Arial", 16)
        controls_text = "WASD/Arrows: Move | SHIFT: Run | CTRL: Crouch | ESC: Pause"
        controls_surf = controls_font.render(controls_text, True, (200, 200, 200))
        self.screen.blit(controls_surf, (SCREEN_WIDTH//2 - controls_surf.get_width()//2, SCREEN_HEIGHT - 20))
    
    def draw_pause(self):
        """Draw the pause screen overlay."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw pause text
        pause_text = self.title_font.render("PAUSED", True, (255, 255, 255))
        resume_text = self.menu_font.render("Press ESC to Resume", True, (255, 255, 255))
        
        self.screen.blit(
            pause_text,
            (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 50)
        )
        self.screen.blit(
            resume_text,
            (SCREEN_WIDTH//2 - resume_text.get_width()//2, SCREEN_HEIGHT//2 + 50)
        )
    
    def draw_game_over(self):
        """Draw the game over screen."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(192)
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over = self.title_font.render("BUSTED!", True, (255, 0, 0))
        score_text = self.menu_font.render(f"Loot Collected: ${self.score}", True, (255, 255, 255))
        time_text = self.menu_font.render(f"Time Survived: {int(self.time)}s", True, (255, 255, 255))
        restart_text = self.menu_font.render("Press ENTER to Return to Menu", True, (255, 255, 255))
        
        self.screen.blit(
            game_over,
            (SCREEN_WIDTH//2 - game_over.get_width()//2, SCREEN_HEIGHT//3)
        )
        self.screen.blit(
            score_text,
            (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2)
        )
        self.screen.blit(
            time_text,
            (SCREEN_WIDTH//2 - time_text.get_width()//2, SCREEN_HEIGHT//2 + 50)
        )
        self.screen.blit(
            restart_text,
            (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 100)
        )
    
    def draw_victory(self):
        """Draw the victory screen."""
        # Create semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(192)
        self.screen.blit(overlay, (0, 0))
        
        # Draw victory text
        victory = self.title_font.render("HEIST SUCCESSFUL!", True, (0, 255, 0))
        score_text = self.menu_font.render(f"Total Loot: ${self.score}", True, (255, 255, 255))
        time_text = self.menu_font.render(f"Time: {int(self.time)}s", True, (255, 255, 255))
        restart_text = self.menu_font.render("Press ENTER to Return to Menu", True, (255, 255, 255))
        
        self.screen.blit(
            victory,
            (SCREEN_WIDTH//2 - victory.get_width()//2, SCREEN_HEIGHT//3)
        )
        self.screen.blit(
            score_text,
            (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2)
        )
        self.screen.blit(
            time_text,
            (SCREEN_WIDTH//2 - time_text.get_width()//2, SCREEN_HEIGHT//2 + 50)
        )
        self.screen.blit(
            restart_text,
            (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 100)
        )
    
    def draw(self):
        """Draw the current game state."""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_game()
            self.draw_pause()
        elif self.state == GameState.GAME_OVER:
            self.draw_game()
            self.draw_game_over()
        elif self.state == GameState.VICTORY:
            self.draw_game()
            self.draw_victory()
        
        pygame.display.flip()
    
    def start_game(self):
        """Start a new game."""
        self.score = 0
        self.time = 0
        self.create_level()
        self.state = GameState.PLAYING
    
    def game_over(self):
        """Handle game over state."""
        self.state = GameState.GAME_OVER
    
    def victory(self):
        """Handle victory state."""
        self.state = GameState.VICTORY
    
    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()

def run_game():
    """Entry point for the game."""
    game = Game()
    game.run()

if __name__ == "__main__":
    run_game()
