"""
Bullet and projectile classes for Rocket Rumble game.
"""

import pygame
import math
from enum import Enum

class ProjectileType(Enum):
    """Types of projectiles in the game."""
    LASER = 1
    MISSILE = 2
    PLASMA = 3
    EMP = 4

class Projectile(pygame.sprite.Sprite):
    """Base class for all projectiles."""
    
    def __init__(self, x, y, angle, speed, damage, color, size=4):
        super().__init__()
        
        # Create the projectile image
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        
        self.rect = self.image.get_rect()
        self.position = pygame.math.Vector2(x, y)
        self.rect.center = self.position
        
        # Movement
        self.velocity = pygame.math.Vector2()
        self.velocity.from_polar((speed, -angle))  # Convert angle to velocity
        
        self.damage = damage
        self.lifetime = 2.0  # Seconds before despawning
        self.timer = 0
        
        # Trail effect
        self.trail = []
        self.max_trail_length = 10
    
    def update(self, dt, arena_rect):
        """Update projectile position and lifetime."""
        # Update position
        self.position += self.velocity * dt
        self.rect.center = self.position
        
        # Update lifetime
        self.timer += dt
        if self.timer >= self.lifetime:
            self.kill()
        
        # Check if out of bounds
        if not arena_rect.colliderect(self.rect):
            self.kill()
        
        # Update trail
        self.trail.append(self.position.copy())
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
    
    def draw(self, surface):
        """Draw the projectile and its trail."""
        # Draw trail
        if len(self.trail) > 1:
            pygame.draw.lines(
                surface,
                pygame.Color(*self.image.get_at((2, 2))),  # Use projectile color
                False,
                [(int(pos.x), int(pos.y)) for pos in self.trail],
                2
            )
        
        # Draw projectile
        surface.blit(self.image, self.rect)

class Laser(Projectile):
    """Basic laser projectile."""
    
    def __init__(self, x, y, angle, damage):
        super().__init__(
            x, y, angle,
            speed=600,  # Pixels per second
            damage=damage,
            color=(255, 0, 0),  # Red
            size=4
        )
        self.lifetime = 1.0
        self.max_trail_length = 5

class Missile(Projectile):
    """Homing missile projectile."""
    
    def __init__(self, x, y, angle, damage):
        super().__init__(
            x, y, angle,
            speed=300,  # Slower than laser
            damage=damage * 2,  # Double damage
            color=(255, 165, 0),  # Orange
            size=6
        )
        self.lifetime = 3.0
        self.max_trail_length = 15
        self.turn_rate = 180  # Degrees per second
        self.target = None
        self.max_tracking_distance = 400
    
    def update(self, dt, arena_rect):
        """Update missile position and tracking."""
        if self.target:
            # Calculate angle to target
            to_target = self.target.position - self.position
            target_angle = math.degrees(math.atan2(-to_target.y, to_target.x))
            
            # Calculate current angle
            current_angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))
            
            # Calculate angle difference
            angle_diff = (target_angle - current_angle + 180) % 360 - 180
            
            # Turn towards target
            turn_amount = min(abs(angle_diff), self.turn_rate * dt)
            if angle_diff < 0:
                turn_amount = -turn_amount
            
            # Update velocity direction
            speed = self.velocity.length()
            angle = math.radians(current_angle + turn_amount)
            self.velocity.x = math.cos(angle) * speed
            self.velocity.y = -math.sin(angle) * speed
            
            # Stop tracking if too far
            if to_target.length() > self.max_tracking_distance:
                self.target = None
        
        super().update(dt, arena_rect)
    
    def set_target(self, target):
        """Set the missile's target."""
        self.target = target

class Plasma(Projectile):
    """Plasma burst projectile."""
    
    def __init__(self, x, y, angle, damage):
        super().__init__(
            x, y, angle,
            speed=400,
            damage=damage * 1.5,
            color=(0, 255, 255),  # Cyan
            size=8
        )
        self.lifetime = 1.5
        self.max_trail_length = 8
        self.pulse_timer = 0
        self.pulse_rate = 0.1  # Seconds per pulse
    
    def update(self, dt, arena_rect):
        """Update plasma projectile with pulsing effect."""
        super().update(dt, arena_rect)
        
        # Update pulse effect
        self.pulse_timer += dt
        if self.pulse_timer >= self.pulse_rate:
            self.pulse_timer = 0
            current_size = self.image.get_width()
            new_size = current_size + 2 if current_size < 12 else 8
            
            # Create new pulsing image
            self.image = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
            pygame.draw.circle(
                self.image,
                (0, 255, 255),
                (new_size//2, new_size//2),
                new_size//2
            )
            self.rect = self.image.get_rect(center=self.rect.center)

class EMP(Projectile):
    """EMP blast projectile."""
    
    def __init__(self, x, y):
        super().__init__(
            x, y, 0,  # Angle doesn't matter for EMP
            speed=0,  # Stationary
            damage=0,  # No direct damage
            color=(128, 0, 255),  # Purple
            size=10
        )
        self.lifetime = 0.5
        self.radius = 10
        self.max_radius = 200
        self.expansion_rate = 800  # Pixels per second
    
    def update(self, dt, arena_rect):
        """Update EMP blast radius."""
        self.timer += dt
        
        # Expand radius
        self.radius = min(
            self.max_radius,
            self.radius + self.expansion_rate * dt
        )
        
        # Create new image for current size
        size = int(self.radius * 2)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            self.image,
            (128, 0, 255, 128),  # Semi-transparent purple
            (size//2, size//2),
            self.radius,
            4  # Ring thickness
        )
        self.rect = self.image.get_rect(center=self.position)
        
        # Kill if lifetime exceeded
        if self.timer >= self.lifetime:
            self.kill()
    
    def get_affected_area(self):
        """Get the rect representing the affected area."""
        return pygame.Rect(
            self.position.x - self.radius,
            self.position.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
