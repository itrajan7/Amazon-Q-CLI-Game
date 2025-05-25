"""
Power-up system for Rocket Rumble game.
"""

import pygame
import random
import math
from enum import Enum

class PowerUpType(Enum):
    """Types of power-ups available in the game."""
    HEALTH = 1
    SHIELD = 2
    SPEED = 3
    MULTI_SHOT = 4
    INVINCIBILITY = 5

class PowerUp(pygame.sprite.Sprite):
    """Power-up item that can be collected by ships."""
    
    # Power-up configurations
    POWERUP_CONFIGS = {
        PowerUpType.HEALTH: {
            'color': (0, 255, 0),  # Green
            'duration': 0,  # Instant effect
            'value': 50,  # Health points
            'name': 'Health'
        },
        PowerUpType.SHIELD: {
            'color': (0, 255, 255),  # Cyan
            'duration': 10.0,  # Seconds
            'value': 100,  # Shield points
            'name': 'Shield'
        },
        PowerUpType.SPEED: {
            'color': (255, 255, 0),  # Yellow
            'duration': 5.0,  # Seconds
            'value': 1.5,  # Speed multiplier
            'name': 'Speed Boost'
        },
        PowerUpType.MULTI_SHOT: {
            'color': (255, 0, 255),  # Magenta
            'duration': 8.0,  # Seconds
            'value': 3,  # Number of shots
            'name': 'Multi-Shot'
        },
        PowerUpType.INVINCIBILITY: {
            'color': (255, 165, 0),  # Orange
            'duration': 3.0,  # Seconds
            'value': 0,  # No specific value
            'name': 'Invincibility'
        }
    }
    
    def __init__(self, x, y, powerup_type=None):
        super().__init__()
        
        # Randomly select type if not specified
        if powerup_type is None:
            powerup_type = random.choice(list(PowerUpType))
        
        self.type = powerup_type
        self.config = self.POWERUP_CONFIGS[powerup_type]
        
        # Create power-up image
        self.size = 20
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.original_image = self.image.copy()
        
        # Draw power-up
        self.draw_powerup()
        
        # Position and movement
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(x, y)
        self.rect.center = self.position
        
        # Animation
        self.angle = 0
        self.pulse_scale = 1.0
        self.pulse_direction = 0.1
        self.hover_offset = 0
        self.hover_speed = 2
        self.original_y = y
    
    def draw_powerup(self):
        """Draw the power-up based on its type."""
        # Clear image
        self.image.fill((0, 0, 0, 0))
        
        # Draw outer circle
        pygame.draw.circle(
            self.image,
            self.config['color'],
            (self.size // 2, self.size // 2),
            self.size // 2,
            2
        )
        
        # Draw inner shape based on type
        if self.type == PowerUpType.HEALTH:
            # Draw plus sign
            pygame.draw.rect(
                self.image,
                self.config['color'],
                (self.size // 2 - 2, self.size // 4, 4, self.size // 2)
            )
            pygame.draw.rect(
                self.image,
                self.config['color'],
                (self.size // 4, self.size // 2 - 2, self.size // 2, 4)
            )
        
        elif self.type == PowerUpType.SHIELD:
            # Draw shield shape
            pygame.draw.circle(
                self.image,
                self.config['color'],
                (self.size // 2, self.size // 2),
                self.size // 3,
                1
            )
        
        elif self.type == PowerUpType.SPEED:
            # Draw lightning bolt
            points = [
                (self.size // 2, self.size // 4),
                (self.size // 3, self.size // 2),
                (self.size // 2, self.size // 2),
                (self.size // 2, 3 * self.size // 4),
                (2 * self.size // 3, self.size // 2),
                (self.size // 2, self.size // 2)
            ]
            pygame.draw.lines(
                self.image,
                self.config['color'],
                False,
                points,
                2
            )
        
        elif self.type == PowerUpType.MULTI_SHOT:
            # Draw three dots
            pygame.draw.circle(
                self.image,
                self.config['color'],
                (self.size // 2, self.size // 2),
                2
            )
            pygame.draw.circle(
                self.image,
                self.config['color'],
                (self.size // 3, self.size // 2),
                2
            )
            pygame.draw.circle(
                self.image,
                self.config['color'],
                (2 * self.size // 3, self.size // 2),
                2
            )
        
        elif self.type == PowerUpType.INVINCIBILITY:
            # Draw star shape
            points = []
            for i in range(5):
                angle = math.pi / 2 + i * 2 * math.pi / 5
                points.append((
                    self.size // 2 + int(self.size // 3 * math.cos(angle)),
                    self.size // 2 - int(self.size // 3 * math.sin(angle))
                ))
                angle += math.pi / 5
                points.append((
                    self.size // 2 + int(self.size // 6 * math.cos(angle)),
                    self.size // 2 - int(self.size // 6 * math.sin(angle))
                ))
            
            pygame.draw.polygon(
                self.image,
                self.config['color'],
                points,
                1
            )
        
        # Store original image for rotation
        self.original_image = self.image.copy()
    
    def update(self, dt):
        """Update power-up animation."""
        # Rotate
        self.angle = (self.angle + 60 * dt) % 360
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Pulse size
        self.pulse_scale += self.pulse_direction * dt
        if self.pulse_scale > 1.2:
            self.pulse_scale = 1.2
            self.pulse_direction = -0.1
        elif self.pulse_scale < 0.8:
            self.pulse_scale = 0.8
            self.pulse_direction = 0.1
        
        scaled_size = int(self.size * self.pulse_scale)
        self.image = pygame.transform.scale(
            self.image,
            (scaled_size, scaled_size)
        )
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Hover effect
        self.hover_offset = math.sin(pygame.time.get_ticks() * 0.003) * 3
        self.position.y = self.original_y + self.hover_offset
        self.rect.center = self.position
    
    def apply(self, ship):
        """Apply power-up effect to a ship."""
        if self.type == PowerUpType.HEALTH:
            ship.heal(self.config['value'])
            return None  # No active effect
        
        elif self.type == PowerUpType.SHIELD:
            ship.shield = self.config['value']
            ship.abilities['shield']['active'] = True
            return {
                'type': self.type,
                'duration': self.config['duration'],
                'timer': 0,
                'effect': lambda s: setattr(s.abilities['shield'], 'active', False)
            }
        
        elif self.type == PowerUpType.SPEED:
            original_speed = ship.speed
            ship.speed *= self.config['value']
            return {
                'type': self.type,
                'duration': self.config['duration'],
                'timer': 0,
                'effect': lambda s: setattr(s, 'speed', original_speed)
            }
        
        elif self.type == PowerUpType.MULTI_SHOT:
            return {
                'type': self.type,
                'duration': self.config['duration'],
                'timer': 0,
                'value': self.config['value'],
                'effect': lambda s: None  # Handled in game manager
            }
        
        elif self.type == PowerUpType.INVINCIBILITY:
            return {
                'type': self.type,
                'duration': self.config['duration'],
                'timer': 0,
                'effect': lambda s: None  # Handled in game manager
            }

class PowerUpManager:
    """Manages power-up spawning and collection."""
    
    def __init__(self, arena_rect):
        self.arena_rect = arena_rect
        self.powerups = pygame.sprite.Group()
        self.spawn_timer = 0
        self.spawn_interval = 10.0  # Seconds between spawns
        self.max_powerups = 5
    
    def update(self, dt):
        """Update power-ups and spawn new ones."""
        # Update existing power-ups
        for powerup in self.powerups:
            powerup.update(dt)
        
        # Spawn new power-ups
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.powerups) < self.max_powerups:
            self.spawn_timer = 0
            self.spawn_powerup()
    
    def spawn_powerup(self, powerup_type=None, position=None):
        """Spawn a new power-up."""
        if position is None:
            # Random position away from edges
            margin = 50
            x = random.randint(margin, self.arena_rect.width - margin)
            y = random.randint(margin, self.arena_rect.height - margin)
        else:
            x, y = position
        
        powerup = PowerUp(x, y, powerup_type)
        self.powerups.add(powerup)
        return powerup
    
    def check_collection(self, ship):
        """Check if ship collects any power-ups."""
        collected = pygame.sprite.spritecollide(ship, self.powerups, True)
        
        active_effects = []
        for powerup in collected:
            effect = powerup.apply(ship)
            if effect:
                active_effects.append(effect)
        
        return active_effects
    
    def draw(self, surface):
        """Draw all power-ups."""
        for powerup in self.powerups:
            surface.blit(powerup.image, powerup.rect)
