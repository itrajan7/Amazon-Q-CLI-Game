"""
Arcade Games Launcher
Main entry point for the arcade games collection.
"""

import pygame
import sys
import os
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BLACK, WHITE, BLUE, GRAY, GAME_MODULES
from utils.ui_elements import Button, Menu
from utils.audio_manager import AudioManager
from utils.helper import create_screen, load_game_module

class GameLauncher:
    """Main launcher for the arcade games."""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Arcade Games Launcher")
        
        # Create screen and clock
        self.screen = create_screen()
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize audio
        self.audio = AudioManager()
        
        # Create main menu
        self.create_main_menu()
    
    def create_main_menu(self):
        """Create the main menu with game buttons."""
        self.main_menu = Menu("ARCADE GAMES", 600, 500)
        
        # Add game buttons
        y_pos = 150
        for game_title, game_module in GAME_MODULES.items():
            button = Button(
                (SCREEN_WIDTH - 300) // 2,
                y_pos,
                300, 60,
                game_title,
                bg_color=BLUE
            )
            self.main_menu.add_button(button)
            y_pos += 80
        
        # Add quit button
        quit_button = Button(
            (SCREEN_WIDTH - 300) // 2,
            y_pos,
            300, 60,
            "Quit",
            bg_color=(200, 50, 50)
        )
        self.main_menu.add_button(quit_button)
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle menu events
            action = self.main_menu.handle_event(event)
            if action:
                if action == "Quit":
                    self.running = False
                elif action in GAME_MODULES.keys():
                    self.launch_game(GAME_MODULES[action])
    
    def update(self):
        """Update game state."""
        pass
    
    def draw(self):
        """Draw the launcher interface."""
        self.screen.fill(BLACK)
        self.main_menu.draw(self.screen)
        pygame.display.flip()
    
    def launch_game(self, game_module_name):
        """Launch the selected game."""
        print(f"Launching game: {game_module_name}")
        
        # Load and run the game module
        game_module = load_game_module(game_module_name)
        if game_module and hasattr(game_module, "run_game"):
            try:
                # Run the game
                game_module.run_game()
                
                # Reset display for launcher
                self.screen = create_screen()
                pygame.display.set_caption("Arcade Games Launcher")
                
            except Exception as e:
                print(f"Error running game {game_module_name}: {e}")
        else:
            print(f"Game module {game_module_name} not found or missing run_game function")

if __name__ == "__main__":
    launcher = GameLauncher()
    launcher.run()
