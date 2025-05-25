"""
Direct launcher for Pixel Heist game.
Ensures proper pygame initialization.
"""

import pygame
import sys
import os

def main():
    """Run the Pixel Heist game."""
    # Initialize pygame
    pygame.init()
    
    # Import the game module
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from games.pixel_heist.main import run_game
    
    # Run the game
    run_game()
    
    # Clean up pygame
    pygame.quit()

if __name__ == "__main__":
    main()
