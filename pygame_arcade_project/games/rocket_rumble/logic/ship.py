"""
Ship class for Rocket Rumble game.
Handles ship movement, combat, and abilities.
"""

import pygame
import math
from enum import Enum

class ShipType(Enum):
    """Types of ships available in the game."""
    SPEEDSTER = 1  # Fast but fragile
    TANK = 2      # Slow but high HP
    SNIPER = 3    # Long-range but low fire rate
    BALANCED = 4  # All-rounder

class Ship(pygame.sprite.Sprite):
    """Player ship class."""
    
    # Ship type configurations
    SHIP_CONFIGS = {
        ShipType.SPEEDSTER: {
            'speed': 8.0,
            'health': 75,
            'fire_rate': 0.3,
            'damage': 15,
            'boost_power': 2.0,
            'color': (0, 255, 255)  # Cyan
        },
        ShipType.TANK: {
            'speed': 4.0,
            'health': 150,
            'fire_rate': 0.5,
            'damage': 20,
            'boost_power': 1.2,
            'color': (255, 0, 0)  # Red
        },
        ShipType.SNIPER: {
            'speed': 5.0,
            'health': 85,
            'fire_rate': 0.8,
            'damage': 35,
            'boost_power': 1.5,
            'color': (255, 255, 0)  # Yellow
        },
        ShipType.BALANCED: {
            'speed': 6.0,
            'health': 100,
            'fire_rate': 0.4,
            'damage': 20,
            'boost_power': 1.7,
            'color': (0, 255, 0)  # Green
        }
    }
    
    def __init__(self, x, y, ship_type=ShipType.BALANCED, sprite_sheet=None):
        super().__init__()
        
        # Ship configuration
        self.ship_type = ship_type
        self.config = self.SHIP_CONFIGS[ship_type]
        
        # Position and movement
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        self.angle = 0  # Angle in degrees (0 is right)
        self.angular_velocity = 0
        
        # Stats
        self.max_health = self.config['health']
        self.health = self.max_health
        self.shield = 0
        self.max_shield = 50
        
        # Combat
        self.fire_rate = self.config['fire_rate']
        self.fire_timer = 0
        self.damage = self.config['damage']
        
        # Movement
        self.speed = self.config['speed']
        self.boost_power = self.config['boost_power']
        self.is_boosting = False
        self.boost_fuel = 100
        self.max_boost_fuel = 100
        self.boost_regen_rate = 10  # Per second
        
        # Create ship image
        if sprite_sheet:
            self.load_sprites(sprite_sheet)
        else:
            self.create_default_ship()
        
        self.original_image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Particle effects
        self.thrust_particles = []
        self.boost_particles = []
        
        # Cooldowns and abilities
        self.abilities = {
            'missile': {
                'ready': True,
                'cooldown': 5.0,
                'timer': 0
            },
            'shield': {
                'ready': True,
                'cooldown': 8.0,
                'timer': 0,
                'active': False,
                'duration': 3.0
            },
            'emp': {
                'ready': True,
                'cooldown': 12.0,
                'timer': 0
            }
        }
    
    def create_default_ship(self):
        """Create a default ship sprite."""
        size = 32
        points = [
            (size, size//2),           # Nose
            (0, 0),                    # Back left
            (size//4, size//2),        # Middle indent
            (0, size),                 # Back right
        ]
        
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, self.config['color'], points)
        
        # Add engine glow
        glow_points = [
            (size//4, size//2),        # Middle
            (0, size//4),              # Top
            (0, 3*size//4)             # Bottom
        ]
        pygame.draw.polygon(self.image, (255, 165, 0), glow_points)  # Orange glow
    
    def update(self, dt, arena_rect):
        """Update ship state."""
        # Update position
        self.position += self.velocity * dt
        self.velocity += self.acceleration * dt
        
        # Apply drag
        drag = 0.98
        self.velocity *= drag
        
        # Keep in arena bounds
        self.position.x = max(0, min(arena_rect.width, self.position.x))
        self.position.y = max(0, min(arena_rect.height, self.position.y))
        
        # Update rect position
        self.rect.center = self.position
        
        # Update image rotation
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        # Update boost
        if not self.is_boosting and self.boost_fuel < self.max_boost_fuel:
            self.boost_fuel = min(
                self.max_boost_fuel,
                self.boost_fuel + self.boost_regen_rate * dt
            )
        
        # Update abilities
        for ability in self.abilities.values():
            if not ability['ready']:
                ability['timer'] += dt
                if ability['timer'] >= ability['cooldown']:
                    ability['ready'] = True
                    ability['timer'] = 0
        
        # Update shield
        if self.abilities['shield']['active']:
            self.abilities['shield']['timer'] += dt
            if self.abilities['shield']['timer'] >= self.abilities['shield']['duration']:
                self.abilities['shield']['active'] = False
                self.abilities['shield']['ready'] = False
                self.abilities['shield']['timer'] = 0
        
        # Update particles
        self.update_particles(dt)
    
    def thrust(self, amount):
        """Apply thrust in current direction."""
        thrust_vector = pygame.math.Vector2()
        thrust_vector.from_polar((amount * self.speed, -self.angle))
        self.acceleration = thrust_vector
        
        # Add thrust particles
        if amount > 0:
            self.add_thrust_particles()
    
    def rotate(self, direction):
        """Rotate the ship. Direction should be -1 (left) or 1 (right)."""
        rotation_speed = 180  # degrees per second
        self.angle += direction * rotation_speed * 0.016  # Assuming 60 FPS
        self.angle %= 360
    
    def boost(self):
        """Activate boost if enough fuel."""
        if self.boost_fuel > 0:
            self.is_boosting = True
            self.boost_fuel = max(0, self.boost_fuel - 2)
            self.velocity *= self.boost_power
            self.add_boost_particles()
        else:
            self.is_boosting = False
    
    def fire_primary(self):
        """Fire primary weapon if cooldown is ready."""
        if self.fire_timer <= 0:
            self.fire_timer = self.fire_rate
            # Create bullet (implemented in game manager)
            return True
        return False
    
    def fire_missile(self):
        """Fire homing missile if ready."""
        if self.abilities['missile']['ready']:
            self.abilities['missile']['ready'] = False
            self.abilities['missile']['timer'] = 0
            # Create missile (implemented in game manager)
            return True
        return False
    
    def activate_shield(self):
        """Activate shield if ready."""
        if self.abilities['shield']['ready']:
            self.abilities['shield']['active'] = True
            self.shield = self.max_shield
            return True
        return False
    
    def fire_emp(self):
        """Fire EMP blast if ready."""
        if self.abilities['emp']['ready']:
            self.abilities['emp']['ready'] = False
            self.abilities['emp']['timer'] = 0
            # Create EMP effect (implemented in game manager)
            return True
        return False
    
    def take_damage(self, amount):
        """Take damage, accounting for shield."""
        if self.abilities['shield']['active']:
            # Damage shield first
            shield_damage = min(self.shield, amount)
            self.shield -= shield_damage
            amount -= shield_damage
        
        if amount > 0:
            self.health = max(0, self.health - amount)
            if self.health == 0:
                return True  # Ship destroyed
        
        return False
    
    def heal(self, amount):
        """Heal the ship."""
        self.health = min(self.max_health, self.health + amount)
    
    def add_thrust_particles(self):
        """Add thrust particle effects."""
        # Calculate particle spawn position
        angle_rad = math.radians(self.angle)
        offset = 20
        spawn_x = self.position.x - math.cos(angle_rad) * offset
        spawn_y = self.position.y - math.sin(angle_rad) * offset
        
        # Add new particle
        particle = {
            'pos': pygame.math.Vector2(spawn_x, spawn_y),
            'vel': pygame.math.Vector2(-math.cos(angle_rad) * 2, -math.sin(angle_rad) * 2),
            'lifetime': 0.5,
            'timer': 0,
            'color': (255, 165, 0)  # Orange
        }
        self.thrust_particles.append(particle)
    
    def add_boost_particles(self):
        """Add boost particle effects."""
        angle_rad = math.radians(self.angle)
        offset = 25
        spawn_x = self.position.x - math.cos(angle_rad) * offset
        spawn_y = self.position.y - math.sin(angle_rad) * offset
        
        # Add new particle
        particle = {
            'pos': pygame.math.Vector2(spawn_x, spawn_y),
            'vel': pygame.math.Vector2(-math.cos(angle_rad) * 4, -math.sin(angle_rad) * 4),
            'lifetime': 0.8,
            'timer': 0,
            'color': (0, 255, 255)  # Cyan
        }
        self.boost_particles.append(particle)
    
    def update_particles(self, dt):
        """Update particle effects."""
        # Update thrust particles
        for particle in self.thrust_particles[:]:
            particle['timer'] += dt
            if particle['timer'] >= particle['lifetime']:
                self.thrust_particles.remove(particle)
            else:
                particle['pos'] += particle['vel']
        
        # Update boost particles
        for particle in self.boost_particles[:]:
            particle['timer'] += dt
            if particle['timer'] >= particle['lifetime']:
                self.boost_particles.remove(particle)
            else:
                particle['pos'] += particle['vel']
    
    def draw_particles(self, surface):
        """Draw particle effects."""
        # Draw thrust particles
        for particle in self.thrust_particles:
            alpha = 255 * (1 - particle['timer'] / particle['lifetime'])
            color = (*particle['color'], int(alpha))
            pygame.draw.circle(
                surface,
                color,
                particle['pos'],
                2
            )
        
        # Draw boost particles
        for particle in self.boost_particles:
            alpha = 255 * (1 - particle['timer'] / particle['lifetime'])
            color = (*particle['color'], int(alpha))
            pygame.draw.circle(
                surface,
                color,
                particle['pos'],
                3
            )
    
    def draw(self, surface):
        """Draw the ship and its effects."""
        # Draw particles
        self.draw_particles(surface)
        
        # Draw ship
        surface.blit(self.image, self.rect)
        
        # Draw shield if active
        if self.abilities['shield']['active']:
            shield_radius = max(self.rect.width, self.rect.height)
            shield_surface = pygame.Surface(
                (shield_radius * 2, shield_radius * 2),
                pygame.SRCALPHA
            )
            alpha = int(128 * (1 - self.abilities['shield']['timer'] / self.abilities['shield']['duration']))
            pygame.draw.circle(
                shield_surface,
                (0, 255, 255, alpha),  # Cyan with alpha
                (shield_radius, shield_radius),
                shield_radius,
                2
            )
            surface.blit(
                shield_surface,
                (self.rect.centerx - shield_radius, self.rect.centery - shield_radius)
            )
