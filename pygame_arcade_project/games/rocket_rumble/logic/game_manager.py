"""
Game manager for Rocket Rumble.
Handles game state, AI, and game flow.
"""

import pygame
import random
import math
from enum import Enum

from .ship import Ship, ShipType
from .bullet import Laser, Missile, Plasma, EMP
from .powerups import PowerUpManager, PowerUpType

class GameMode(Enum):
    """Game modes available."""
    FREE_FOR_ALL = 1
    TEAM_RUMBLE = 2
    TIME_ATTACK = 3
    SURVIVAL = 4

class Difficulty(Enum):
    """Game difficulty levels."""
    EASY = 1
    NORMAL = 2
    HARD = 3

class GameManager:
    """Manages game state and logic."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.arena_rect = pygame.Rect(0, 0, screen_width, screen_height)
        
        # Game settings
        self.mode = GameMode.FREE_FOR_ALL
        self.difficulty = Difficulty.NORMAL
        self.max_time = 180  # 3 minutes
        self.game_time = 0
        self.game_over = False
        self.victory = False
        
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.ships = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        
        # Player and enemies
        self.player_ship = None
        self.enemy_ships = []
        
        # Power-ups
        self.powerup_manager = PowerUpManager(self.arena_rect)
        
        # Scoring
        self.scores = {}
        
        # AI settings
        self.ai_update_interval = 0.5  # seconds
        self.ai_timer = 0
    
    def start_game(self, player_ship_type, num_enemies=1):
        """Start a new game."""
        # Clear existing sprites
        self.all_sprites.empty()
        self.ships.empty()
        self.projectiles.empty()
        
        # Reset game state
        self.game_time = 0
        self.game_over = False
        self.victory = False
        self.scores = {}
        
        # Create player ship
        self.player_ship = Ship(
            self.screen_width // 4,
            self.screen_height // 2,
            player_ship_type
        )
        self.ships.add(self.player_ship)
        self.all_sprites.add(self.player_ship)
        self.scores[self.player_ship] = 0
        
        # Create enemy ships
        self.enemy_ships = []
        for i in range(num_enemies):
            # Choose a different ship type than player
            enemy_types = [st for st in ShipType if st != player_ship_type]
            enemy_type = random.choice(enemy_types)
            
            # Position enemies around the arena
            angle = 2 * math.pi * i / num_enemies
            x = self.screen_width // 2 + int(self.screen_width // 3 * math.cos(angle))
            y = self.screen_height // 2 + int(self.screen_height // 3 * math.sin(angle))
            
            enemy = Ship(x, y, enemy_type)
            self.enemy_ships.append(enemy)
            self.ships.add(enemy)
            self.all_sprites.add(enemy)
            self.scores[enemy] = 0
        
        # Initialize power-ups
        self.powerup_manager = PowerUpManager(self.arena_rect)
        
        # Spawn initial power-ups
        for _ in range(3):
            self.powerup_manager.spawn_powerup()
    
    def update(self, dt):
        """Update game state."""
        if self.game_over:
            return
        
        # Update game time
        self.game_time += dt
        if self.game_time >= self.max_time and self.mode == GameMode.TIME_ATTACK:
            self.end_game()
        
        # Update all sprites
        for sprite in self.all_sprites:
            sprite.update(dt, self.arena_rect)
        
        # Update power-ups
        self.powerup_manager.update(dt)
        
        # Update AI
        self.ai_timer += dt
        if self.ai_timer >= self.ai_update_interval:
            self.ai_timer = 0
            self.update_ai()
        
        # Check collisions
        self.check_collisions()
        
        # Check game end conditions
        self.check_game_end()
    
    def update_ai(self):
        """Update AI-controlled ships."""
        for enemy in self.enemy_ships:
            if not enemy.alive():
                continue
                
            # Choose target (usually the player)
            target = self.player_ship
            
            if target and target.alive():
                # Calculate vector to target
                to_target = target.position - enemy.position
                distance = to_target.length()
                
                # Determine behavior based on distance
                if distance > 300:
                    # Move towards target
                    angle_to_target = math.degrees(math.atan2(-to_target.y, to_target.x))
                    
                    # Rotate towards target
                    angle_diff = (angle_to_target - enemy.angle + 180) % 360 - 180
                    if angle_diff > 10:
                        enemy.rotate(-1)
                    elif angle_diff < -10:
                        enemy.rotate(1)
                    else:
                        # Apply thrust if facing target
                        enemy.thrust(1)
                
                elif distance < 150:
                    # Too close, back away
                    angle_from_target = (math.degrees(math.atan2(-to_target.y, to_target.x)) + 180) % 360
                    
                    # Rotate away from target
                    angle_diff = (angle_from_target - enemy.angle + 180) % 360 - 180
                    if angle_diff > 10:
                        enemy.rotate(-1)
                    elif angle_diff < -10:
                        enemy.rotate(1)
                    else:
                        # Apply thrust if facing away
                        enemy.thrust(1)
                
                else:
                    # Good combat distance, orbit and attack
                    orbit_angle = math.degrees(math.atan2(-to_target.y, to_target.x)) + 90
                    
                    # Rotate to orbit position
                    angle_diff = (orbit_angle - enemy.angle + 180) % 360 - 180
                    if angle_diff > 10:
                        enemy.rotate(-1)
                    elif angle_diff < -10:
                        enemy.rotate(1)
                    
                    # Apply some thrust
                    enemy.thrust(0.5)
                
                # Fire weapons based on difficulty
                if self.difficulty == Difficulty.EASY:
                    # 10% chance to fire per update
                    if random.random() < 0.1:
                        self.fire_weapon(enemy)
                
                elif self.difficulty == Difficulty.NORMAL:
                    # 20% chance to fire per update
                    if random.random() < 0.2:
                        self.fire_weapon(enemy)
                    
                    # 5% chance to use special ability
                    if random.random() < 0.05:
                        ability = random.choice(['missile', 'shield', 'emp'])
                        if ability == 'missile' and enemy.fire_missile():
                            self.fire_missile(enemy, target)
                        elif ability == 'shield':
                            enemy.activate_shield()
                        elif ability == 'emp' and enemy.fire_emp():
                            self.fire_emp(enemy)
                
                elif self.difficulty == Difficulty.HARD:
                    # 30% chance to fire per update
                    if random.random() < 0.3:
                        self.fire_weapon(enemy)
                    
                    # 10% chance to use special ability
                    if random.random() < 0.1:
                        ability = random.choice(['missile', 'shield', 'emp'])
                        if ability == 'missile' and enemy.fire_missile():
                            self.fire_missile(enemy, target)
                        elif ability == 'shield':
                            enemy.activate_shield()
                        elif ability == 'emp' and enemy.fire_emp():
                            self.fire_emp(enemy)
    
    def fire_weapon(self, ship):
        """Fire ship's primary weapon."""
        if ship.fire_primary():
            # Calculate projectile spawn position
            angle_rad = math.radians(ship.angle)
            offset = 20
            spawn_x = ship.position.x + math.cos(angle_rad) * offset
            spawn_y = ship.position.y - math.sin(angle_rad) * offset
            
            # Create laser
            laser = Laser(spawn_x, spawn_y, ship.angle, ship.damage)
            self.projectiles.add(laser)
            self.all_sprites.add(laser)
            
            return laser
        return None
    
    def fire_missile(self, ship, target):
        """Fire a homing missile."""
        # Calculate spawn position
        angle_rad = math.radians(ship.angle)
        offset = 20
        spawn_x = ship.position.x + math.cos(angle_rad) * offset
        spawn_y = ship.position.y - math.sin(angle_rad) * offset
        
        # Create missile
        missile = Missile(spawn_x, spawn_y, ship.angle, ship.damage)
        missile.set_target(target)
        self.projectiles.add(missile)
        self.all_sprites.add(missile)
        
        return missile
    
    def fire_emp(self, ship):
        """Fire an EMP blast."""
        emp = EMP(ship.position.x, ship.position.y)
        self.projectiles.add(emp)
        self.all_sprites.add(emp)
        
        return emp
    
    def check_collisions(self):
        """Check for collisions between game objects."""
        # Check projectile hits on ships
        for ship in self.ships:
            hits = pygame.sprite.spritecollide(ship, self.projectiles, True)
            for projectile in hits:
                if isinstance(projectile, EMP):
                    # EMP effect: Disable abilities temporarily
                    for ability in ship.abilities.values():
                        ability['ready'] = False
                        ability['timer'] = 0
                else:
                    # Normal damage
                    destroyed = ship.take_damage(projectile.damage)
                    if destroyed:
                        # Award points to the shooter
                        if ship != self.player_ship:
                            self.scores[self.player_ship] += 100
                        else:
                            # Player was destroyed by enemy
                            for enemy in self.enemy_ships:
                                self.scores[enemy] += 50
                        
                        ship.kill()
        
        # Check power-up collection
        for ship in self.ships:
            effects = self.powerup_manager.check_collection(ship)
            if effects and ship == self.player_ship:
                # Player collected a power-up
                self.scores[ship] += 25
    
    def check_game_end(self):
        """Check if game end conditions are met."""
        # Check if player is destroyed
        if not self.player_ship.alive():
            self.game_over = True
            self.victory = False
            return
        
        # Check if all enemies are destroyed
        if all(not enemy.alive() for enemy in self.enemy_ships):
            self.game_over = True
            self.victory = True
            return
        
        # Check time limit for time attack mode
        if self.mode == GameMode.TIME_ATTACK and self.game_time >= self.max_time:
            self.game_over = True
            # Victory depends on score
            player_score = self.scores.get(self.player_ship, 0)
            enemy_scores = [self.scores.get(enemy, 0) for enemy in self.enemy_ships]
            self.victory = player_score > max(enemy_scores) if enemy_scores else True
    
    def end_game(self):
        """End the current game."""
        self.game_over = True
        
        # Determine victory based on scores
        player_score = self.scores.get(self.player_ship, 0)
        enemy_scores = [self.scores.get(enemy, 0) for enemy in self.enemy_ships]
        self.victory = player_score > max(enemy_scores) if enemy_scores else True
    
    def get_player_score(self):
        """Get the player's current score."""
        return self.scores.get(self.player_ship, 0)
    
    def get_high_score(self):
        """Get the highest score."""
        return max(self.scores.values()) if self.scores else 0
