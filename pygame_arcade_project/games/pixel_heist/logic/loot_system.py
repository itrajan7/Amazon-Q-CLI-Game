"""
Loot system module for Pixel Heist game.
Handles loot items, their values, and collection mechanics.
"""

import pygame
import random
import math
from enum import Enum

class LootType(Enum):
    """Types of loot items."""
    CASH = 1
    JEWELS = 2
    ARTWORK = 3
    ARTIFACT = 4
    DOCUMENT = 5

class LootItem(pygame.sprite.Sprite):
    """A collectable loot item in the game."""
    
    def __init__(self, x, y, loot_type, value, sprite_sheet=None):
        super().__init__()
        
        self.loot_type = loot_type
        self.value = value
        self.steal_time = self._get_steal_time()  # Time needed to steal this item
        self.being_stolen = False
        self.steal_progress = 0  # 0-100%
        
        # Animation
        self.frame = 0
        self.animation_speed = 0.1
        self.animation_timer = 0
        
        # Create image
        if sprite_sheet:
            self.load_animations(sprite_sheet)
        else:
            self.image = self._create_placeholder()
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # Hover effect
        self.hover_offset = 0
        self.hover_speed = 2
        self.original_y = y
    
    def _create_placeholder(self):
        """Create a placeholder image for the loot item."""
        colors = {
            LootType.CASH: (0, 255, 0),      # Green
            LootType.JEWELS: (255, 0, 255),  # Magenta
            LootType.ARTWORK: (0, 255, 255),  # Cyan
            LootType.ARTIFACT: (255, 165, 0), # Orange
            LootType.DOCUMENT: (255, 255, 0)  # Yellow
        }
        
        surf = pygame.Surface((16, 16))
        surf.fill(colors.get(self.loot_type, (255, 255, 255)))
        return surf
    
    def load_animations(self, sprite_sheet_path):
        """Load loot animations from sprite sheet."""
        try:
            sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
            self.animations = []
            
            # Example: Load 4 frames for each loot type
            sprite_width = 16
            sprite_height = 16
            row = self.loot_type.value - 1
            
            for i in range(4):
                rect = pygame.Rect(
                    i * sprite_width,
                    row * sprite_height,
                    sprite_width,
                    sprite_height
                )
                frame = pygame.Surface((sprite_width, sprite_height), 
                                    pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), rect)
                self.animations.append(frame)
            
            self.image = self.animations[0]
            
        except Exception as e:
            print(f"Error loading loot animations: {e}")
            self.image = self._create_placeholder()
    
    def _get_steal_time(self):
        """Calculate time needed to steal this item based on type and value."""
        base_times = {
            LootType.CASH: 1.0,      # Quick to grab
            LootType.JEWELS: 2.0,    # Need to be careful
            LootType.ARTWORK: 3.0,    # Fragile items
            LootType.ARTIFACT: 4.0,   # Heavy or complex
            LootType.DOCUMENT: 1.5    # Need to find right ones
        }
        
        # Adjust time based on value
        value_factor = 1.0 + (self.value / 1000)  # Higher value = more time
        return base_times.get(self.loot_type, 2.0) * value_factor
    
    def start_stealing(self):
        """Start the stealing process for this item."""
        if not self.being_stolen:
            self.being_stolen = True
            self.steal_progress = 0
            return True
        return False
    
    def stop_stealing(self):
        """Stop the stealing process."""
        if self.being_stolen:
            self.being_stolen = False
            self.steal_progress = 0
            return True
        return False
    
    def update_stealing(self, dt):
        """Update stealing progress."""
        if self.being_stolen:
            progress_per_second = 100 / self.steal_time
            self.steal_progress += progress_per_second * dt
            
            if self.steal_progress >= 100:
                return True  # Stealing complete
        
        return False
    
    def update(self, dt):
        """Update loot animation and effects."""
        # Update hover effect
        self.hover_offset = math.sin(pygame.time.get_ticks() * 0.003) * 3
        self.rect.y = self.original_y + self.hover_offset
        
        # Update animation
        if hasattr(self, 'animations'):
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.frame = (self.frame + 1) % len(self.animations)
                self.image = self.animations[self.frame]

class LootManager:
    """Manages loot items and their collection."""
    
    def __init__(self):
        self.loot_sprites = pygame.sprite.Group()
        self.total_value = 0
        self.collected_value = 0
        
        # Loot generation settings
        self.loot_configs = {
            LootType.CASH: {
                'weight': 40,
                'value_range': (100, 500)
            },
            LootType.JEWELS: {
                'weight': 30,
                'value_range': (300, 800)
            },
            LootType.ARTWORK: {
                'weight': 15,
                'value_range': (500, 1500)
            },
            LootType.ARTIFACT: {
                'weight': 10,
                'value_range': (1000, 2000)
            },
            LootType.DOCUMENT: {
                'weight': 5,
                'value_range': (2000, 5000)
            }
        }
        
        # Create some test loot
        self.create_test_loot()
    
    def create_test_loot(self):
        """Create some test loot items."""
        # Add some test loot items
        self.generate_loot(100, 100, LootType.CASH, 200)
        self.generate_loot(200, 150, LootType.JEWELS, 500)
        self.generate_loot(300, 200, LootType.ARTWORK, 1000)
        self.generate_loot(400, 250, LootType.ARTIFACT, 1500)
        self.generate_loot(500, 300, LootType.DOCUMENT, 3000)
    
    def generate_loot(self, x, y, loot_type=None, value=None):
        """Generate a new loot item."""
        if loot_type is None:
            # Randomly select loot type based on weights
            weights = [config['weight'] for config in self.loot_configs.values()]
            loot_type = random.choices(list(LootType), weights=weights)[0]
        
        if value is None:
            # Generate random value within range for type
            value_range = self.loot_configs[loot_type]['value_range']
            value = random.randint(value_range[0], value_range[1])
        
        loot = LootItem(x, y, loot_type, value)
        self.loot_sprites.add(loot)
        self.total_value += value
        
        return loot
    
    def collect_loot(self, loot_item):
        """Collect a loot item."""
        if loot_item in self.loot_sprites:
            self.collected_value += loot_item.value
            self.loot_sprites.remove(loot_item)
            return loot_item.value
        return 0
    
    def update(self, dt):
        """Update all loot items."""
        for loot in self.loot_sprites:
            loot.update(dt)
    
    def draw(self, surface, camera_offset=(0, 0)):
        """Draw all loot items."""
        for loot in self.loot_sprites:
            surface.blit(
                loot.image,
                (loot.rect.x - camera_offset[0],
                 loot.rect.y - camera_offset[1])
            )
    
    def get_collection_progress(self):
        """Get the percentage of total loot value collected."""
        if self.total_value == 0:
            return 0
        return (self.collected_value / self.total_value) * 100
    
    def get_nearby_loot(self, position, radius):
        """Get loot items within a certain radius of a position."""
        nearby = []
        for loot in self.loot_sprites:
            dx = loot.rect.centerx - position[0]
            dy = loot.rect.centery - position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= radius:
                nearby.append(loot)
        return nearby
