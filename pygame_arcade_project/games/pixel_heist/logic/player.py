"""
Player module for Pixel Heist game.
Handles player movement, animations, and interactions.
"""

import pygame
import math
from enum import Enum

class PlayerState(Enum):
    """Enum for player states."""
    IDLE = 0
    WALKING = 1
    RUNNING = 2
    CROUCHING = 3
    LOOTING = 4

class Direction(Enum):
    """Enum for player direction."""
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

class Player(pygame.sprite.Sprite):
    """Player class for the thief character."""
    
    def __init__(self, x, y, sprite_sheet=None):
        super().__init__()
        
        # Player properties
        self.position = pygame.math.Vector2(x, y)
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        
        # Movement settings
        self.walk_speed = 2.0
        self.run_speed = 4.0
        self.crouch_speed = 1.0
        self.current_speed = self.walk_speed
        self.friction = 0.85
        
        # State tracking
        self.state = PlayerState.IDLE
        self.direction = Direction.DOWN
        self.is_crouching = False
        self.is_running = False
        self.is_looting = False
        
        # Noise and detection
        self.noise_level = 0  # 0-100, affects guard detection radius
        self.visibility = 0   # 0-100, affects how visible player is in light
        
        # Inventory
        self.inventory = []
        self.max_inventory = 5
        self.loot_count = 0
        
        # Animation variables
        self.frame = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        
        # Create placeholder image if no sprite sheet provided
        if sprite_sheet:
            self.load_animations(sprite_sheet)
        else:
            self.image = pygame.Surface((32, 32))
            self.image.fill((0, 200, 0))  # Green placeholder
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Collision rect (smaller than visual rect for better collision)
        self.collision_rect = pygame.Rect(0, 0, 24, 24)
        self.collision_rect.center = self.rect.center
    
    def load_animations(self, sprite_sheet_path):
        """Load player animations from sprite sheet."""
        try:
            sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
            self.animations = {
                PlayerState.IDLE: [],
                PlayerState.WALKING: [],
                PlayerState.RUNNING: [],
                PlayerState.CROUCHING: [],
                PlayerState.LOOTING: []
            }
            
            # Example of loading animations from a sprite sheet
            # This would need to be adjusted based on your actual sprite sheet layout
            sprite_width, sprite_height = 32, 32
            
            # Load idle animations for each direction
            for i in range(4):  # 4 directions
                self.animations[PlayerState.IDLE].append([])
                for j in range(2):  # 2 frames for idle
                    rect = pygame.Rect(j * sprite_width, i * sprite_height, 
                                      sprite_width, sprite_height)
                    image = pygame.Surface((sprite_width, sprite_height), pygame.SRCALPHA)
                    image.blit(sheet, (0, 0), rect)
                    self.animations[PlayerState.IDLE][i].append(image)
            
            # Similar loading would be done for other animation states
            # For now, we'll use the idle animation for all states
            for state in [PlayerState.WALKING, PlayerState.RUNNING, 
                         PlayerState.CROUCHING, PlayerState.LOOTING]:
                self.animations[state] = self.animations[PlayerState.IDLE]
            
            # Set initial image
            self.image = self.animations[PlayerState.IDLE][Direction.DOWN.value][0]
            
        except Exception as e:
            print(f"Error loading player animations: {e}")
            # Fallback to placeholder
            self.image = pygame.Surface((32, 32))
            self.image.fill((0, 200, 0))
    
    def update_animation(self, dt):
        """Update player animation based on current state and direction."""
        if not hasattr(self, 'animations'):
            return  # No animations loaded
        
        # Update animation timer
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame = (self.frame + 1) % len(self.animations[self.state][self.direction.value])
        
        # Set current frame
        self.image = self.animations[self.state][self.direction.value][self.frame]
    
    def update(self, dt, walls=None):
        """Update player position and state."""
        # Apply acceleration
        self.velocity += self.acceleration
        
        # Apply friction
        self.velocity *= self.friction
        
        # Limit velocity
        speed_limit = self.current_speed
        if self.velocity.length() > speed_limit:
            self.velocity.scale_to_length(speed_limit)
        
        # Update position
        old_position = self.position.copy()
        self.position += self.velocity
        
        # Update rect positions
        self.rect.center = (int(self.position.x), int(self.position.y))
        self.collision_rect.center = self.rect.center
        
        # Handle collisions
        if walls:
            self.handle_collisions(walls, old_position)
        
        # Update animation
        self.update_animation(dt)
        
        # Reset acceleration
        self.acceleration = pygame.math.Vector2(0, 0)
        
        # Update noise level based on movement
        self.update_noise_level()
    
    def handle_collisions(self, walls, old_position):
        """Handle collisions with walls."""
        # Check for collisions
        collisions = pygame.sprite.spritecollide(self, walls, False, 
                                               pygame.sprite.collide_rect_ratio(0.8))
        
        if collisions:
            # Move back to old position
            self.position = old_position
            self.rect.center = (int(self.position.x), int(self.position.y))
            self.collision_rect.center = self.rect.center
            self.velocity = pygame.math.Vector2(0, 0)
    
    def move(self, direction_x, direction_y):
        """Apply movement in the given direction."""
        # Determine current speed based on state
        if self.is_crouching:
            self.current_speed = self.crouch_speed
            self.state = PlayerState.CROUCHING
        elif self.is_running:
            self.current_speed = self.run_speed
            self.state = PlayerState.RUNNING
        else:
            self.current_speed = self.walk_speed
            self.state = PlayerState.WALKING
        
        # Apply acceleration in the given direction
        self.acceleration.x = direction_x * self.current_speed * 0.1
        self.acceleration.y = direction_y * self.current_speed * 0.1
        
        # Update direction based on movement
        if direction_x > 0:
            self.direction = Direction.RIGHT
        elif direction_x < 0:
            self.direction = Direction.LEFT
        elif direction_y > 0:
            self.direction = Direction.DOWN
        elif direction_y < 0:
            self.direction = Direction.UP
        
        # If not moving, set to idle
        if direction_x == 0 and direction_y == 0:
            self.state = PlayerState.IDLE
    
    def toggle_crouch(self):
        """Toggle crouching state."""
        self.is_crouching = not self.is_crouching
        if self.is_crouching:
            self.is_running = False  # Can't run while crouching
    
    def toggle_run(self):
        """Toggle running state."""
        self.is_running = not self.is_running
        if self.is_running:
            self.is_crouching = False  # Can't crouch while running
    
    def start_looting(self):
        """Start looting animation."""
        self.is_looting = True
        self.state = PlayerState.LOOTING
        self.velocity = pygame.math.Vector2(0, 0)  # Stop movement while looting
    
    def stop_looting(self):
        """Stop looting animation."""
        self.is_looting = False
        self.state = PlayerState.IDLE
    
    def add_loot(self, value=1):
        """Add loot to player's count."""
        self.loot_count += value
        return self.loot_count
    
    def add_to_inventory(self, item):
        """Add item to inventory if there's space."""
        if len(self.inventory) < self.max_inventory:
            self.inventory.append(item)
            return True
        return False
    
    def use_item(self, item_index):
        """Use item from inventory."""
        if 0 <= item_index < len(self.inventory):
            item = self.inventory.pop(item_index)
            # Item use logic would go here
            return item
        return None
    
    def update_noise_level(self):
        """Update player's noise level based on movement and state."""
        # Base noise on velocity and state
        speed = self.velocity.length()
        
        if self.is_looting:
            self.noise_level = 10  # Base looting noise
        elif self.is_crouching:
            self.noise_level = speed * 5  # Quieter when crouching
        elif self.is_running:
            self.noise_level = speed * 20  # Louder when running
        else:
            self.noise_level = speed * 10  # Normal walking noise
        
        # Clamp noise level
        self.noise_level = max(0, min(100, self.noise_level))
        
        return self.noise_level
    
    def get_detection_radius(self):
        """Get the radius at which guards can detect the player."""
        # Base detection on noise level and visibility
        return 50 + (self.noise_level * 2) + (self.visibility * 1.5)
