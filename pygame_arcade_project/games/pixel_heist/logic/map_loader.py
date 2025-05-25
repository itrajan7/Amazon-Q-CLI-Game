"""
Map loader module for Pixel Heist game.
Handles loading and rendering game maps from JSON files.
"""

import pygame
import json
import os

class Tile(pygame.sprite.Sprite):
    """A single tile in the game map."""
    
    def __init__(self, x, y, image, tile_type="wall", properties=None):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tile_type = tile_type
        self.properties = properties or {}

class MapLoader:
    """Loads and manages game maps."""
    
    def __init__(self, tile_size=16):
        self.tile_size = tile_size
        self.tileset = {}
        self.map_data = None
        self.width = 0
        self.height = 0
        
        # Sprite groups
        self.wall_sprites = pygame.sprite.Group()
        self.floor_sprites = pygame.sprite.Group()
        self.object_sprites = pygame.sprite.Group()
        self.loot_sprites = pygame.sprite.Group()
        self.door_sprites = pygame.sprite.Group()
        self.vent_sprites = pygame.sprite.Group()
        self.security_sprites = pygame.sprite.Group()
        
        # Placeholder tiles
        self.placeholder_tiles = {
            "wall": self._create_placeholder_tile((100, 100, 100)),
            "floor": self._create_placeholder_tile((50, 50, 50)),
            "door": self._create_placeholder_tile((150, 75, 0)),
            "vent": self._create_placeholder_tile((70, 70, 70)),
            "loot": self._create_placeholder_tile((255, 215, 0)),
            "security": self._create_placeholder_tile((255, 0, 0))
        }
    
    def _create_placeholder_tile(self, color):
        """Create a placeholder tile with the given color."""
        surf = pygame.Surface((self.tile_size, self.tile_size))
        surf.fill(color)
        return surf
    
    def load_tileset(self, tileset_path):
        """Load tileset images from a directory."""
        if not os.path.exists(tileset_path):
            print(f"Tileset path not found: {tileset_path}")
            return False
            
        for filename in os.listdir(tileset_path):
            if filename.endswith(('.png', '.jpg', '.bmp')):
                tile_name = os.path.splitext(filename)[0]
                try:
                    tile_image = pygame.image.load(
                        os.path.join(tileset_path, filename)
                    ).convert_alpha()
                    
                    # Resize if needed
                    if tile_image.get_width() != self.tile_size or \
                       tile_image.get_height() != self.tile_size:
                        tile_image = pygame.transform.scale(
                            tile_image, 
                            (self.tile_size, self.tile_size)
                        )
                    
                    self.tileset[tile_name] = tile_image
                except pygame.error as e:
                    print(f"Error loading tile {filename}: {e}")
        
        return len(self.tileset) > 0
    
    def load_map(self, map_path):
        """Load a map from a JSON file."""
        try:
            with open(map_path, 'r') as f:
                self.map_data = json.load(f)
            
            self.width = self.map_data.get('width', 0)
            self.height = self.map_data.get('height', 0)
            
            # Clear existing sprite groups
            self.wall_sprites.empty()
            self.floor_sprites.empty()
            self.object_sprites.empty()
            self.loot_sprites.empty()
            self.door_sprites.empty()
            self.vent_sprites.empty()
            self.security_sprites.empty()
            
            # Create tiles based on map data
            self._create_tiles()
            
            return True
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading map {map_path}: {e}")
            return False
    
    def _create_tiles(self):
        """Create tile sprites from map data."""
        if not self.map_data:
            return
            
        layers = self.map_data.get('layers', [])
        
        for layer in layers:
            layer_name = layer.get('name', '')
            layer_data = layer.get('data', [])
            
            for y in range(self.height):
                for x in range(self.width):
                    idx = y * self.width + x
                    if idx >= len(layer_data):
                        continue
                        
                    tile_id = layer_data[idx]
                    if tile_id == 0:  # Empty tile
                        continue
                    
                    # Get tile properties from map data
                    tile_info = self._get_tile_info(tile_id)
                    tile_type = tile_info.get('type', 'wall')
                    tile_name = tile_info.get('name', f'tile_{tile_id}')
                    
                    # Get tile image
                    tile_image = self.tileset.get(tile_name)
                    if not tile_image:
                        tile_image = self.placeholder_tiles.get(
                            tile_type, 
                            self.placeholder_tiles['wall']
                        )
                    
                    # Create tile sprite
                    tile = Tile(
                        x * self.tile_size,
                        y * self.tile_size,
                        tile_image,
                        tile_type,
                        tile_info.get('properties', {})
                    )
                    
                    # Add to appropriate sprite group
                    if tile_type == 'wall':
                        self.wall_sprites.add(tile)
                    elif tile_type == 'floor':
                        self.floor_sprites.add(tile)
                    elif tile_type == 'door':
                        self.door_sprites.add(tile)
                    elif tile_type == 'vent':
                        self.vent_sprites.add(tile)
                    elif tile_type == 'loot':
                        self.loot_sprites.add(tile)
                    elif tile_type == 'security':
                        self.security_sprites.add(tile)
                    else:
                        self.object_sprites.add(tile)
    
    def _get_tile_info(self, tile_id):
        """Get tile information from the map data."""
        if not self.map_data:
            return {}
            
        tilesets = self.map_data.get('tilesets', [])
        for tileset in tilesets:
            first_gid = tileset.get('firstgid', 1)
            tiles = tileset.get('tiles', [])
            
            if first_gid <= tile_id < first_gid + len(tiles):
                return tiles[tile_id - first_gid]
        
        return {}
    
    def get_guard_spawn_points(self):
        """Get guard spawn points from the map."""
        if not self.map_data:
            return []
            
        spawn_points = []
        objects = self.map_data.get('objects', [])
        
        for obj in objects:
            if obj.get('type') == 'guard_spawn':
                x = obj.get('x', 0)
                y = obj.get('y', 0)
                
                # Convert to tile coordinates
                tile_x = x // self.tile_size
                tile_y = y // self.tile_size
                
                # Get patrol points if available
                patrol_points = []
                for point in obj.get('patrol_points', []):
                    px = point.get('x', 0)
                    py = point.get('y', 0)
                    patrol_points.append((px, py))
                
                spawn_points.append({
                    'position': (tile_x * self.tile_size, tile_y * self.tile_size),
                    'patrol_points': patrol_points
                })
        
        return spawn_points
    
    def get_player_spawn_point(self):
        """Get player spawn point from the map."""
        if not self.map_data:
            return (0, 0)
            
        objects = self.map_data.get('objects', [])
        
        for obj in objects:
            if obj.get('type') == 'player_spawn':
                x = obj.get('x', 0)
                y = obj.get('y', 0)
                
                # Convert to tile coordinates
                tile_x = x // self.tile_size
                tile_y = y // self.tile_size
                
                return (tile_x * self.tile_size, tile_y * self.tile_size)
        
        return (0, 0)
    
    def get_extraction_point(self):
        """Get extraction point from the map."""
        if not self.map_data:
            return (0, 0)
            
        objects = self.map_data.get('objects', [])
        
        for obj in objects:
            if obj.get('type') == 'extraction':
                x = obj.get('x', 0)
                y = obj.get('y', 0)
                
                # Convert to tile coordinates
                tile_x = x // self.tile_size
                tile_y = y // self.tile_size
                
                return (tile_x * self.tile_size, tile_y * self.tile_size)
        
        return (0, 0)
    
    def draw(self, surface, camera_offset=(0, 0)):
        """Draw the map to the surface."""
        # Draw layers in order: floor, objects, walls
        for sprite in self.floor_sprites:
            surface.blit(sprite.image, 
                       (sprite.rect.x - camera_offset[0], 
                        sprite.rect.y - camera_offset[1]))
        
        for sprite in self.object_sprites:
            surface.blit(sprite.image, 
                       (sprite.rect.x - camera_offset[0], 
                        sprite.rect.y - camera_offset[1]))
        
        for sprite in self.loot_sprites:
            surface.blit(sprite.image, 
                       (sprite.rect.x - camera_offset[0], 
                        sprite.rect.y - camera_offset[1]))
        
        for sprite in self.door_sprites:
            surface.blit(sprite.image, 
                       (sprite.rect.x - camera_offset[0], 
                        sprite.rect.y - camera_offset[1]))
        
        for sprite in self.vent_sprites:
            surface.blit(sprite.image, 
                       (sprite.rect.x - camera_offset[0], 
                        sprite.rect.y - camera_offset[1]))
        
        for sprite in self.wall_sprites:
            surface.blit(sprite.image, 
                       (sprite.rect.x - camera_offset[0], 
                        sprite.rect.y - camera_offset[1]))
        
        for sprite in self.security_sprites:
            surface.blit(sprite.image, 
                       (sprite.rect.x - camera_offset[0], 
                        sprite.rect.y - camera_offset[1]))
