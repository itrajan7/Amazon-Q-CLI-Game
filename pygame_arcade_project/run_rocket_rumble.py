"""
Direct launcher for Rocket Rumble game.
Ensures proper pygame initialization.
"""

import pygame
import sys
import os

def main():
    """Run the Rocket Rumble game."""
    # Initialize pygame
    pygame.init()
    
    # Import the game module
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from games.rocket_rumble.main import run_game
    
    # Run the game
    run_game()
    
    # Clean up pygame
    pygame.quit()

if __name__ == "__main__":
    main()
