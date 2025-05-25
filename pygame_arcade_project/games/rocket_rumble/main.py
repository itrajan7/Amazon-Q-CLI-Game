"""
Rocket Rumble - Space Shooter
A single-player space shooter with waves of enemy aircraft.
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

class Player(pygame.sprite.Sprite):
    """Player ship class."""
    
    def __init__(self, x, y):
        super().__init__()
        self.size = 50
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Create a modern-looking player ship
        points = [
            (self.size, self.size//2),     # Nose (pointing right)
            (0, 0),                        # Top back
            (self.size//4, self.size//2),  # Middle indent
            (0, self.size),                # Bottom back
        ]
        
        # Draw the ship body
        pygame.draw.polygon(self.image, (0, 255, 200), points)  # Cyan body
        
        # Add engine glow
        glow_points = [
            (self.size//4, self.size//2),  # Middle
            (0, self.size//4),             # Top
            (0, 3*self.size//4)            # Bottom
        ]
        pygame.draw.polygon(self.image, (255, 165, 0), glow_points)  # Orange glow
        
        # Add details
        pygame.draw.line(self.image, (255, 255, 255), 
                        (self.size//2, self.size//4),
                        (3*self.size//4, self.size//2), 2)
        pygame.draw.line(self.image, (255, 255, 255),
                        (self.size//2, 3*self.size//4),
                        (3*self.size//4, self.size//2), 2)
        
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(x, y)
        self.rect.center = self.position
        
        # Movement
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 300
        self.vertical_speed = 450  # Increased vertical speed
        self.drag = 0.9
        
        # Combat
        self.health = 100
        self.max_health = 100
        self.fire_delay = 0.1  # seconds
        self.fire_timer = 0
        
        # Effects
        self.hit_flash = 0
        self.engine_particles = []
    
    def update(self, dt):
        """Update player state."""
        # Get keyboard input
        keys = pygame.key.get_pressed()
        
        # Movement
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        
        # Apply movement with different speeds for horizontal and vertical
        self.velocity.x += dx * self.speed * dt
        self.velocity.y += dy * self.vertical_speed * dt
        
        # Apply drag
        self.velocity *= self.drag
        
        # Update position
        self.position += self.velocity * dt
        
        # Keep player on screen
        self.position.x = max(self.size//2, min(self.position.x, SCREEN_WIDTH - self.size//2))
        self.position.y = max(self.size//2, min(self.position.y, SCREEN_HEIGHT - self.size//2))
        
        self.rect.center = self.position
        
        # Update fire timer
        if self.fire_timer > 0:
            self.fire_timer -= dt
        
        # Update hit flash
        if self.hit_flash > 0:
            self.hit_flash -= dt
        
        # Update engine particles
        self.update_engine_particles(dt)
        
        # Add engine particles based on movement
        if abs(self.velocity.x) > 1 or abs(self.velocity.y) > 1:
            if random.random() < 0.3:
                self.add_engine_particle()
    
    def shoot(self):
        """Try to fire a bullet."""
        if self.fire_timer <= 0:
            self.fire_timer = self.fire_delay
            return Bullet(self.rect.right, self.rect.centery)
        return None
    
    def add_engine_particle(self):
        """Add a new engine particle."""
        particle = {
            'pos': pygame.math.Vector2(self.rect.left + 5, self.rect.centery + random.randint(-5, 5)),
            'vel': pygame.math.Vector2(-random.uniform(50, 100), random.uniform(-20, 20)),
            'lifetime': random.uniform(0.5, 1.0),
            'timer': 0,
            'size': random.uniform(2, 4)
        }
        self.engine_particles.append(particle)
    
    def update_engine_particles(self, dt):
        """Update engine particle effects."""
        # Update existing particles
        for particle in self.engine_particles[:]:
            particle['timer'] += dt
            if particle['timer'] >= particle['lifetime']:
                self.engine_particles.remove(particle)
            else:
                particle['pos'] += particle['vel'] * dt
    
    def draw(self, surface):
        """Draw the player ship with effects."""
        # Draw engine particles
        for particle in self.engine_particles:
            alpha = 255 * (1 - particle['timer'] / particle['lifetime'])
            pygame.draw.circle(
                surface,
                (255, 165, 0, int(alpha)),
                (int(particle['pos'].x), int(particle['pos'].y)),
                int(particle['size'])
            )
        
        # Draw ship
        if self.hit_flash > 0:
            # Create a white flash effect
            flash_image = self.image.copy()
            flash_image.fill((255, 255, 255, int(self.hit_flash * 255)), special_flags=pygame.BLEND_ADD)
            surface.blit(flash_image, self.rect)
        else:
            surface.blit(self.image, self.rect)

class Enemy(pygame.sprite.Sprite):
    """Enemy aircraft class."""
    
    def __init__(self, x, y):
        super().__init__()
        self.size = 40
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # Create a modern-looking enemy ship facing left
        points = [
            (0, self.size//2),           # Nose (pointing left)
            (self.size//2, 0),           # Top wing
            (self.size, self.size//4),    # Top back
            (self.size, 3*self.size//4),  # Bottom back
            (self.size//2, self.size),    # Bottom wing
        ]
        
        # Randomize enemy color for variety
        r = random.randint(200, 255)
        g = random.randint(0, 100)
        b = random.randint(0, 100)
        
        # Draw the ship body
        pygame.draw.polygon(self.image, (r, g, b), points)  # Reddish body with variation
        
        # Add some details
        pygame.draw.line(self.image, (200, 200, 200), 
                        (self.size//2, self.size//4),
                        (3*self.size//4, self.size//2), 3)
        pygame.draw.circle(self.image, (255, 255, 0), 
                         (3*self.size//4, self.size//2), 5)  # Engine glow
        
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(x, y)
        self.rect.center = self.position
        
        # Movement
        self.speed = random.uniform(3, 5)
        
        # Choose a movement pattern
        pattern = random.choice(['straight', 'sine', 'zigzag', 'dive'])
        self.movement_pattern = pattern
        
        # Pattern-specific variables
        self.direction = pygame.math.Vector2(-1, random.uniform(-0.2, 0.2))
        self.direction = self.direction.normalize()
        self.sine_amplitude = random.uniform(2, 5)
        self.sine_frequency = random.uniform(1, 3)
        self.sine_offset = random.uniform(0, 6.28)  # Random phase (0 to 2π)
        self.zigzag_timer = 0
        self.zigzag_interval = random.uniform(0.5, 1.5)
        self.zigzag_direction = 1
        
        # Combat
        self.health = 30
        self.damage = 20
        self.score_value = 100
        
        # Effects
        self.hit_flash = 0
        self.engine_particles = []
        
    def update(self, dt):
        """Update enemy position and effects."""
        # Apply movement pattern
        if self.movement_pattern == 'straight':
            # Simple straight movement
            self.position += self.direction * self.speed
            
        elif self.movement_pattern == 'sine':
            # Sinusoidal movement
            self.position.x -= self.speed
            self.position.y += math.sin(self.position.x * 0.01 * self.sine_frequency + self.sine_offset) * self.sine_amplitude
            
        elif self.movement_pattern == 'zigzag':
            # Zigzag movement
            self.zigzag_timer += dt
            if self.zigzag_timer >= self.zigzag_interval:
                self.zigzag_timer = 0
                self.zigzag_direction *= -1
                
            self.position.x -= self.speed
            self.position.y += self.zigzag_direction * self.speed * 0.5
            
        elif self.movement_pattern == 'dive':
            # Dive toward player's last known position
            if self.position.x > SCREEN_WIDTH * 0.7:
                # Just enter the screen normally
                self.position.x -= self.speed
            else:
                # Dive down faster
                self.position.x -= self.speed * 0.7
                self.position.y += self.speed * 1.2
        
        self.rect.center = self.position
        
        # Update hit flash effect
        if self.hit_flash > 0:
            self.hit_flash -= dt
        
        # Update engine particles
        self.update_engine_particles(dt)
        
        # Add engine particles
        if random.random() < 0.2:
            self.add_engine_particle()
        
        # Remove if off screen
        if self.rect.right < -50 or self.rect.left > SCREEN_WIDTH + 50 or \
           self.rect.bottom < -50 or self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()
    
    def add_engine_particle(self):
        """Add a new engine particle."""
        particle = {
            'pos': pygame.math.Vector2(self.rect.right - 5, self.rect.centery + random.randint(-5, 5)),
            'vel': pygame.math.Vector2(random.uniform(50, 100), random.uniform(-20, 20)),
            'lifetime': random.uniform(0.3, 0.7),
            'timer': 0,
            'size': random.uniform(1, 3)
        }
        self.engine_particles.append(particle)
    
    def update_engine_particles(self, dt):
        """Update engine particle effects."""
        # Update existing particles
        for particle in self.engine_particles[:]:
            particle['timer'] += dt
            if particle['timer'] >= particle['lifetime']:
                self.engine_particles.remove(particle)
            else:
                particle['pos'] += particle['vel'] * dt
    
    def draw(self, surface):
        """Draw the enemy with effects."""
        # Draw engine particles
        for particle in self.engine_particles:
            alpha = 255 * (1 - particle['timer'] / particle['lifetime'])
            pygame.draw.circle(
                surface,
                (255, 165, 0, int(alpha)),
                (int(particle['pos'].x), int(particle['pos'].y)),
                int(particle['size'])
            )
        
        # Draw ship
        if self.hit_flash > 0:
            # Create a white flash effect
            flash_image = self.image.copy()
            flash_image.fill((255, 255, 255, int(self.hit_flash * 255)), special_flags=pygame.BLEND_ADD)
            surface.blit(flash_image, self.rect)
        else:
            surface.blit(self.image, self.rect)

class Bullet(pygame.sprite.Sprite):
    """Player bullet class."""
    
    def __init__(self, x, y, bullet_type="standard"):
        super().__init__()
        self.bullet_type = bullet_type
        
        if bullet_type == "standard":
            # Create an energy bolt effect
            self.size = 20
            self.image = pygame.Surface((self.size, 8), pygame.SRCALPHA)
            
            # Draw energy bolt
            pygame.draw.ellipse(self.image, (0, 255, 255), (0, 0, self.size, 8))  # Cyan core
            pygame.draw.ellipse(self.image, (255, 255, 255), (self.size//4, 2, self.size//2, 4))  # White center
            
            self.speed = 800
            self.damage = 10
        
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(x, y)
        self.rect.center = self.position
        
        # Trail effect
        self.trail = []
        self.max_trail_length = 5
    
    def update(self, dt):
        """Update bullet position."""
        self.position.x += self.speed * dt
        self.rect.center = self.position
        
        # Update trail
        self.trail.append((int(self.position.x), int(self.position.y)))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        # Remove if off screen
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()
    
    def draw(self, surface):
        """Draw the bullet with trail effect."""
        # Draw trail
        if len(self.trail) > 1:
            pygame.draw.lines(
                surface,
                (0, 255, 255, 128),
                False,
                self.trail,
                2
            )
        
        # Draw bullet
        surface.blit(self.image, self.rect)

class Game:
    """Main game class."""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rocket Rumble")
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = GameState.MENU
        self.running = True
        self.score = 0
        self.wave = 1
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        
        # Create player
        self.player = Player(100, SCREEN_HEIGHT//2)
        self.all_sprites.add(self.player)
        
        # Enemy spawning
        self.spawn_timer = 0
        self.spawn_delay = 1.0  # seconds between spawns
        self.enemies_per_wave = 5
        self.enemies_spawned = 0
        
        # Load fonts
        self.title_font = pygame.font.SysFont("Arial", 48)
        self.menu_font = pygame.font.SysFont("Arial", 32)
        self.hud_font = pygame.font.SysFont("Arial", 24)
        
        # Create stars for background
        self.stars = self.create_stars()
    
    def create_stars(self):
        """Create parallax starfield."""
        stars = []
        for layer in range(3):
            layer_stars = []
            for _ in range(50):
                x = random.randint(0, SCREEN_WIDTH)
                y = random.randint(0, SCREEN_HEIGHT)
                speed = 0.5 + layer * 0.5  # Different speeds for parallax
                size = 1 + layer
                brightness = min(255, 128 + layer * 64)
                layer_stars.append({
                    'pos': pygame.math.Vector2(x, y),
                    'speed': speed,
                    'size': size,
                    'brightness': brightness
                })
            stars.append(layer_stars)
        return stars
    
    def update_stars(self, dt):
        """Update star positions."""
        for layer in self.stars:
            for star in layer:
                star['pos'].x -= star['speed']
                if star['pos'].x < 0:
                    star['pos'].x = SCREEN_WIDTH
                    star['pos'].y = random.randint(0, SCREEN_HEIGHT)
    
    def draw_stars(self):
        """Draw parallax starfield."""
        for layer in self.stars:
            for star in layer:
                brightness = int(star['brightness'])
                pygame.draw.circle(
                    self.screen,
                    (brightness, brightness, brightness),
                    (int(star['pos'].x), int(star['pos'].y)),
                    int(star['size'])
                )
    
    def spawn_enemy(self):
        """Spawn a new enemy if conditions are met."""
        if self.enemies_spawned >= self.enemies_per_wave:
            if len(self.enemies) == 0:
                # Start new wave
                self.wave += 1
                self.enemies_per_wave += 2
                self.enemies_spawned = 0
                self.spawn_delay = max(0.5, self.spawn_delay - 0.1)
            return
        
        self.spawn_timer += self.clock.get_time() / 1000.0
        if self.spawn_timer >= self.spawn_delay:
            self.spawn_timer = 0
            
            # Spawn enemy at random position on right side
            enemy = Enemy(
                SCREEN_WIDTH + 50,
                random.randint(50, SCREEN_HEIGHT - 50)
            )
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            self.enemies_spawned += 1
    
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
                    elif self.state == GameState.GAME_OVER:
                        self.state = GameState.MENU
    
    def update(self, dt):
        """Update game state."""
        # Update stars
        self.update_stars(dt)
        
        if self.state != GameState.PLAYING:
            return
        
        # Spawn enemies
        self.spawn_enemy()
        
        # Update all sprites
        for sprite in self.all_sprites:
            sprite.update(dt)
        
        # Handle shooting
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            bullet = self.player.shoot()
            if bullet:
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)
        
        # Check collisions
        self.check_collisions()
    
    def check_collisions(self):
        """Check for collisions between game objects."""
        # Bullets hitting enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets in hits.items():
            for bullet in bullets:
                enemy.health -= bullet.damage
                enemy.hit_flash = 0.1
                if enemy.health <= 0:
                    self.score += enemy.score_value
                    enemy.kill()
        
        # Enemies hitting player
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in hits:
            self.player.health -= enemy.damage
            self.player.hit_flash = 0.1
            enemy.kill()
            
            if self.player.health <= 0:
                self.game_over()
    
    def draw_menu(self):
        """Draw the main menu."""
        self.screen.fill((0, 0, 0))
        self.draw_stars()
        
        # Draw title
        title_surf = self.title_font.render("ROCKET RUMBLE", True, (0, 255, 255))
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
        self.screen.fill((0, 0, 0))
        self.draw_stars()
        
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
        score_text = self.hud_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # Draw wave number
        wave_text = self.hud_font.render(f"Wave {self.wave}", True, (255, 255, 255))
        self.screen.blit(wave_text, (10, 40))
        
        # Draw health bar
        health_width = 200
        health_height = 20
        health_rect = pygame.Rect(10, 70, health_width, health_height)
        health_fill = pygame.Rect(
            10, 70,
            health_width * (self.player.health / self.player.max_health),
            health_height
        )
        
        pygame.draw.rect(self.screen, (64, 64, 64), health_rect)
        pygame.draw.rect(self.screen, (0, 255, 0), health_fill)
        pygame.draw.rect(self.screen, (255, 255, 255), health_rect, 2)
    
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
        game_over = self.title_font.render("GAME OVER", True, (255, 0, 0))
        score_text = self.menu_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
        wave_text = self.menu_font.render(f"Waves Survived: {self.wave}", True, (255, 255, 255))
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
            wave_text,
            (SCREEN_WIDTH//2 - wave_text.get_width()//2, SCREEN_HEIGHT//2 + 50)
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
        
        pygame.display.flip()
    
    def start_game(self):
        """Start a new game."""
        self.score = 0
        self.wave = 1
        self.enemies_per_wave = 5
        self.enemies_spawned = 0
        self.spawn_delay = 1.0
        
        self.all_sprites.empty()
        self.enemies.empty()
        self.bullets.empty()
        
        self.player = Player(100, SCREEN_HEIGHT//2)
        self.all_sprites.add(self.player)
        
        self.state = GameState.PLAYING
    
    def game_over(self):
        """Handle game over state."""
        self.state = GameState.GAME_OVER
    
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
