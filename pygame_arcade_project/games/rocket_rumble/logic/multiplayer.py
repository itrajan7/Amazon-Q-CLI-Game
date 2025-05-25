"""
Multiplayer support for Rocket Rumble.
Handles local multiplayer functionality.
"""

import pygame
from enum import Enum

class PlayerID(Enum):
    """Player identification for multiplayer."""
    PLAYER1 = 1
    PLAYER2 = 2
    PLAYER3 = 3
    PLAYER4 = 4

class MultiplayerManager:
    """Manages multiplayer functionality."""
    
    def __init__(self, max_players=4):
        self.max_players = max_players
        self.active_players = 1  # Default to 1 player
        
        # Player controls
        self.controls = {
            PlayerID.PLAYER1: {
                'up': pygame.K_w,
                'down': pygame.K_s,
                'left': pygame.K_a,
                'right': pygame.K_d,
                'fire': pygame.K_SPACE,
                'missile': pygame.K_q,
                'shield': pygame.K_e,
                'emp': pygame.K_r,
                'boost': pygame.K_LSHIFT
            },
            PlayerID.PLAYER2: {
                'up': pygame.K_UP,
                'down': pygame.K_DOWN,
                'left': pygame.K_LEFT,
                'right': pygame.K_RIGHT,
                'fire': pygame.K_RCTRL,
                'missile': pygame.K_PERIOD,
                'shield': pygame.K_SLASH,
                'emp': pygame.K_RSHIFT,
                'boost': pygame.K_RETURN
            },
            PlayerID.PLAYER3: {
                'up': pygame.K_t,
                'down': pygame.K_g,
                'left': pygame.K_f,
                'right': pygame.K_h,
                'fire': pygame.K_y,
                'missile': pygame.K_u,
                'shield': pygame.K_i,
                'emp': pygame.K_o,
                'boost': pygame.K_p
            },
            PlayerID.PLAYER4: {
                'up': pygame.K_KP8,
                'down': pygame.K_KP5,
                'left': pygame.K_KP4,
                'right': pygame.K_KP6,
                'fire': pygame.K_KP0,
                'missile': pygame.K_KP_PLUS,
                'shield': pygame.K_KP_MINUS,
                'emp': pygame.K_KP_MULTIPLY,
                'boost': pygame.K_KP_ENTER
            }
        }
        
        # Player ships
        self.player_ships = {}
    
    def set_active_players(self, count):
        """Set the number of active players."""
        self.active_players = max(1, min(self.max_players, count))
    
    def register_player_ship(self, player_id, ship):
        """Register a ship for a player."""
        if player_id in PlayerID and player_id.value <= self.active_players:
            self.player_ships[player_id] = ship
    
    def handle_input(self, keys, game_manager):
        """Handle input for all active players."""
        for player_id, ship in self.player_ships.items():
            if not ship or not ship.alive():
                continue
                
            controls = self.controls[player_id]
            
            # Rotation
            if keys[controls['left']]:
                ship.rotate(1)  # Rotate left
            if keys[controls['right']]:
                ship.rotate(-1)  # Rotate right
            
            # Thrust
            if keys[controls['up']]:
                ship.thrust(1)
            elif keys[controls['down']]:
                ship.thrust(-0.5)  # Reverse thrust
            
            # Boost
            if keys[controls['boost']]:
                ship.boost()
            
            # Weapons
            if keys[controls['fire']]:
                game_manager.fire_weapon(ship)
            
            # Special abilities
            if keys[controls['missile']]:
                # Find nearest enemy
                nearest = None
                min_dist = float('inf')
                
                for other_id, other_ship in self.player_ships.items():
                    if other_id != player_id and other_ship and other_ship.alive():
                        dist = (other_ship.position - ship.position).length()
                        if dist < min_dist:
                            min_dist = dist
                            nearest = other_ship
                
                # If no player target, find an AI enemy
                if not nearest and game_manager.enemy_ships:
                    for enemy in game_manager.enemy_ships:
                        if enemy.alive():
                            dist = (enemy.position - ship.position).length()
                            if dist < min_dist:
                                min_dist = dist
                                nearest = enemy
                
                if nearest and ship.fire_missile():
                    game_manager.fire_missile(ship, nearest)
            
            if keys[controls['shield']]:
                ship.activate_shield()
            
            if keys[controls['emp']]:
                if ship.fire_emp():
                    game_manager.fire_emp(ship)
    
    def get_split_screen_rects(self):
        """Get screen rectangles for split screen mode."""
        if self.active_players == 1:
            return [pygame.Rect(0, 0, pygame.display.get_surface().get_width(), 
                              pygame.display.get_surface().get_height())]
        
        elif self.active_players == 2:
            width = pygame.display.get_surface().get_width()
            height = pygame.display.get_surface().get_height()
            return [
                pygame.Rect(0, 0, width, height // 2),
                pygame.Rect(0, height // 2, width, height // 2)
            ]
        
        elif self.active_players == 3 or self.active_players == 4:
            width = pygame.display.get_surface().get_width()
            height = pygame.display.get_surface().get_height()
            half_width = width // 2
            half_height = height // 2
            
            rects = [
                pygame.Rect(0, 0, half_width, half_height),
                pygame.Rect(half_width, 0, half_width, half_height),
                pygame.Rect(0, half_height, half_width, half_height)
            ]
            
            if self.active_players == 4:
                rects.append(pygame.Rect(half_width, half_height, half_width, half_height))
            
            return rects
        
        return []
