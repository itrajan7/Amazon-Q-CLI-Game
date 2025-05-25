"""
Guard AI module for Pixel Heist game.
Handles guard behavior, patrolling, and player detection.
"""

import pygame
import math
from enum import Enum
import random

class GuardState(Enum):
    """Enum for guard states."""
    PATROLLING = 0
    SUSPICIOUS = 1
    INVESTIGATING = 2
    ALERTED = 3
    SEARCHING = 4

class Guard(pygame.sprite.Sprite):
    """Guard class for enemy NPCs."""
    
    def __init__(self, x, y, patrol_points=None, sprite_sheet=None):
        super().__init__()
        
        # Position and movement
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.patrol_points = patrol_points or [(x, y)]
        self.current_patrol_point = 0
        self.patrol_wait_time = 2.0  # seconds to wait at each point
        self.wait_timer = 0
        
        # Movement settings
        self.walk_speed = 1.5
        self.run_speed = 3.0
        self.current_speed = self.walk_speed
        
        # State management
        self.state = GuardState.PATROLLING
        self.state_timer = 0
        self.suspicion_level = 0  # 0-100
        self.alert_position = None  # Position of last known player sighting
        
        # Vision properties
        self.view_distance = 150
        self.view_angle = 90  # degrees
        self.view_direction = 0  # degrees (0 is right, 90 is down)
        
        # Animation
        self.frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        
        # Create placeholder image if no sprite sheet provided
        if sprite_sheet:
            self.load_animations(sprite_sheet)
        else:
            self.image = pygame.Surface((32, 32))
            self.image.fill((200, 0, 0))  # Red placeholder
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Vision cone surface (for rendering)
        self.vision_surf = pygame.Surface((self.view_distance * 2, 
                                         self.view_distance * 2), 
                                        pygame.SRCALPHA)
        self.update_vision_cone()
    
    def load_animations(self, sprite_sheet_path):
        """Load guard animations from sprite sheet."""
        try:
            sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
            self.animations = {state: [] for state in GuardState}
            
            # Example animation loading (adjust based on actual sprite sheet)
            sprite_width, sprite_height = 32, 32
            
            # Load animations for each state
            for state in GuardState:
                frames = []
                for i in range(4):  # 4 frames per state
                    rect = pygame.Rect(i * sprite_width, 
                                     state.value * sprite_height,
                                     sprite_width, sprite_height)
                    image = pygame.Surface((sprite_width, sprite_height), 
                                        pygame.SRCALPHA)
                    image.blit(sheet, (0, 0), rect)
                    frames.append(image)
                self.animations[state] = frames
            
            self.image = self.animations[GuardState.PATROLLING][0]
            
        except Exception as e:
            print(f"Error loading guard animations: {e}")
            # Fallback to placeholder
            self.image = pygame.Surface((32, 32))
            self.image.fill((200, 0, 0))
    
    def update_vision_cone(self):
        """Update the vision cone surface."""
        self.vision_surf.fill((0, 0, 0, 0))
        
        # Convert view direction to radians
        direction_rad = math.radians(self.view_direction)
        half_angle_rad = math.radians(self.view_angle / 2)
        
        # Create points for vision cone polygon
        points = [(self.view_distance, self.view_distance)]  # Center point
        
        # Add arc points
        num_points = 20
        for i in range(num_points + 1):
            angle = direction_rad - half_angle_rad + (i * 2 * half_angle_rad / num_points)
            x = self.view_distance + math.cos(angle) * self.view_distance
            y = self.view_distance + math.sin(angle) * self.view_distance
            points.append((x, y))
        
        # Draw vision cone
        pygame.draw.polygon(self.vision_surf, (255, 255, 0, 64), points)
    
    def update_animation(self, dt):
        """Update guard animation based on current state."""
        if not hasattr(self, 'animations'):
            return
            
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame = (self.frame + 1) % len(self.animations[self.state])
            
        self.image = self.animations[self.state][self.frame]
    
    def update(self, dt, player=None, walls=None):
        """Update guard state and position."""
        # Update state timer
        self.state_timer += dt
        
        # Handle different states
        if self.state == GuardState.PATROLLING:
            self.handle_patrol(dt)
        elif self.state == GuardState.SUSPICIOUS:
            self.handle_suspicious(dt)
        elif self.state == GuardState.INVESTIGATING:
            self.handle_investigation(dt)
        elif self.state == GuardState.ALERTED:
            self.handle_alert(dt, player)
        elif self.state == GuardState.SEARCHING:
            self.handle_search(dt)
        
        # Move guard
        self.move(dt, walls)
        
        # Check for player detection
        if player:
            self.check_player_detection(player)
        
        # Update animation
        self.update_animation(dt)
    
    def move(self, dt, walls=None):
        """Move guard based on current velocity."""
        # Store old position for collision checking
        old_position = self.position.copy()
        
        # Update position
        self.position += self.velocity * dt * self.current_speed
        self.rect.center = (int(self.position.x), int(self.position.y))
        
        # Handle collisions
        if walls:
            collisions = pygame.sprite.spritecollide(self, walls, False)
            if collisions:
                self.position = old_position
                self.rect.center = (int(self.position.x), int(self.position.y))
                self.velocity = pygame.math.Vector2(0, 0)
    
    def handle_patrol(self, dt):
        """Handle patrol state behavior."""
        if self.wait_timer > 0:
            self.wait_timer -= dt
            self.velocity = pygame.math.Vector2(0, 0)
            return
            
        target = pygame.math.Vector2(self.patrol_points[self.current_patrol_point])
        direction = target - self.position
        
        if direction.length() < 2:  # Close enough to target
            self.wait_timer = self.patrol_wait_time
            self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
        else:
            direction = direction.normalize()
            self.velocity = direction
            self.view_direction = math.degrees(math.atan2(direction.y, direction.x))
    
    def handle_suspicious(self, dt):
        """Handle suspicious state behavior."""
        # Look around for a few seconds
        if self.state_timer > 3.0:
            self.state = GuardState.PATROLLING
            self.state_timer = 0
        else:
            # Rotate view back and forth
            self.view_direction = math.sin(self.state_timer * 2) * 45
            self.velocity = pygame.math.Vector2(0, 0)
    
    def handle_investigation(self, dt):
        """Handle investigation state behavior."""
        if not self.alert_position:
            self.state = GuardState.PATROLLING
            return
            
        direction = pygame.math.Vector2(self.alert_position) - self.position
        
        if direction.length() < 5:  # Reached investigation point
            self.state = GuardState.SUSPICIOUS
            self.state_timer = 0
            self.alert_position = None
        else:
            self.velocity = direction.normalize()
            self.view_direction = math.degrees(math.atan2(direction.y, direction.x))
    
    def handle_alert(self, dt, player):
        """Handle alert state behavior."""
        if not player:
            self.state = GuardState.SEARCHING
            self.state_timer = 0
            return
            
        # Chase player
        direction = player.position - self.position
        self.velocity = direction.normalize()
        self.view_direction = math.degrees(math.atan2(direction.y, direction.x))
        self.current_speed = self.run_speed
    
    def handle_search(self, dt):
        """Handle search state behavior."""
        # Search for a while, then return to patrol
        if self.state_timer > 10.0:
            self.state = GuardState.PATROLLING
            self.state_timer = 0
            self.current_speed = self.walk_speed
        else:
            # Random movement during search
            if random.random() < 0.02:  # Occasionally change direction
                angle = random.uniform(0, 360)
                self.velocity = pygame.math.Vector2(
                    math.cos(math.radians(angle)),
                    math.sin(math.radians(angle))
                )
                self.view_direction = angle
    
    def check_player_detection(self, player):
        """Check if guard can see the player."""
        # Get vector to player
        to_player = player.position - self.position
        distance = to_player.length()
        
        # Check if player is within view distance
        if distance > self.view_distance:
            return False
        
        # Check if player is within view angle
        angle = math.degrees(math.atan2(to_player.y, to_player.x))
        angle_diff = abs((angle - self.view_direction + 180) % 360 - 180)
        
        if angle_diff > self.view_angle / 2:
            return False
        
        # Calculate detection probability based on distance and player's state
        detection_chance = 1.0 - (distance / self.view_distance)
        detection_chance *= 1.0 + (player.noise_level / 100)
        
        if player.is_crouching:
            detection_chance *= 0.5
        
        # Random check for detection
        if random.random() < detection_chance:
            self.alert(player.position)
            return True
            
        return False
    
    def alert(self, position):
        """Alert the guard to a position."""
        self.alert_position = position
        self.state = GuardState.ALERTED
        self.state_timer = 0
        self.current_speed = self.run_speed
        self.suspicion_level = 100
    
    def draw_vision_cone(self, surface, camera_offset=(0, 0)):
        """Draw the guard's vision cone."""
        # Update vision cone
        self.update_vision_cone()
        
        # Calculate position accounting for camera offset
        pos = (self.position.x - self.view_distance - camera_offset[0],
               self.position.y - self.view_distance - camera_offset[1])
        
        # Draw vision cone
        surface.blit(self.vision_surf, pos)
