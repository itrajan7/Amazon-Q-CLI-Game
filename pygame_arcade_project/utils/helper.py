"""Helper functions for the arcade games."""

import pygame
import os
import sys
import importlib

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SCREEN_WIDTH, SCREEN_HEIGHT

def create_screen(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, fullscreen=False):
    """Create a pygame display surface."""
    flags = pygame.FULLSCREEN if fullscreen else 0
    return pygame.display.set_mode((width, height), flags)

def load_image(file_path, scale=None, alpha=False):
    """Load an image from file path."""
    try:
        if alpha:
            image = pygame.image.load(file_path).convert_alpha()
        else:
            image = pygame.image.load(file_path).convert()
        
        if scale:
            if isinstance(scale, tuple):
                image = pygame.transform.scale(image, scale)
            else:
                # Assume scale is a float representing a multiplier
                size = image.get_size()
                image = pygame.transform.scale(
                    image, 
                    (int(size[0] * scale), int(size[1] * scale))
                )
        return image
    except Exception as e:
        print(f"Error loading image {file_path}: {e}")
        # Return a small surface with error color
        surf = pygame.Surface((32, 32))
        surf.fill((255, 0, 255))  # Magenta for error
        return surf

def load_game_module(game_name):
    """Dynamically load a game module."""
    try:
        # Import the game's main module
        module_path = f"games.{game_name}.main"
        game_module = importlib.import_module(module_path, package="pygame_arcade_project")
        return game_module
    except ImportError as e:
        print(f"Error importing game {game_name}: {e}")
        return None

def center_rect(width, height, screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT):
    """Return a centered rectangle."""
    return pygame.Rect(
        (screen_width - width) // 2,
        (screen_height - height) // 2,
        width, 
        height
    )

def draw_text(surface, text, font, color, x, y, align="center"):
    """Draw text on a surface with alignment options."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    
    if align == "center":
        text_rect.center = (x, y)
    elif align == "topleft":
        text_rect.topleft = (x, y)
    elif align == "topright":
        text_rect.topright = (x, y)
    elif align == "bottomleft":
        text_rect.bottomleft = (x, y)
    elif align == "bottomright":
        text_rect.bottomright = (x, y)
    
    surface.blit(text_surface, text_rect)
    return text_rect
