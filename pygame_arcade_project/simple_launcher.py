"""
Simple Arcade Games Launcher
A basic launcher for the arcade games collection.
"""

import pygame
import sys
import os
import importlib

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

# Game modules to load
GAMES = {
    "Rocket Rumble": {
        "module": "games.rocket_rumble.main",
        "function": "run_game",
        "color": (0, 255, 255)  # Cyan
    },
    "Pixel Heist": {
        "module": "games.pixel_heist.main",
        "function": "run_game",
        "color": (0, 255, 0)  # Green
    }
}

class Button:
    """A simple button class."""
    
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
        self.font = pygame.font.SysFont("Arial", 24)
    
    def update(self, mouse_pos):
        """Update button state."""
        self.hover = self.rect.collidepoint(mouse_pos)
        return self.hover
    
    def draw(self, surface):
        """Draw the button."""
        # Draw button background
        color = tuple(min(c + 30, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=8)
        
        # Draw button text
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class SimpleLauncher:
    """Simple launcher for the arcade games."""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Arcade Games Launcher")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create buttons
        self.buttons = []
        y_pos = 200
        for game_name, game_info in GAMES.items():
            button = Button(
                SCREEN_WIDTH // 2 - 150,
                y_pos,
                300, 60,
                game_name,
                game_info["color"]
            )
            self.buttons.append(button)
            y_pos += 100
        
        # Add exit button
        exit_button = Button(
            SCREEN_WIDTH // 2 - 100,
            y_pos,
            200, 50,
            "EXIT",
            (255, 50, 50)
        )
        self.buttons.append(exit_button)
        
        # Load fonts
        self.title_font = pygame.font.SysFont("Arial", 48)
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    for i, button in enumerate(self.buttons):
                        if button.rect.collidepoint(mouse_pos):
                            if i == len(self.buttons) - 1:  # Exit button
                                self.running = False
                            else:
                                # Launch the selected game
                                game_name = button.text
                                self.launch_game(game_name)
    
    def update(self):
        """Update launcher state."""
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
    
    def draw(self):
        """Draw the launcher interface."""
        # Fill background
        self.screen.fill((20, 20, 40))
        
        # Draw title
        title_surf = self.title_font.render("ARCADE GAMES", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_surf, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        pygame.display.flip()
    
    def launch_game(self, game_name):
        """Launch the selected game."""
        if game_name in GAMES:
            game_info = GAMES[game_name]
            
            try:
                # Import the game module
                game_module = importlib.import_module(game_info["module"])
                
                # Get the run function
                run_func = getattr(game_module, game_info["function"])
                
                # Run the game
                run_func()
                
                # Reset display for launcher
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                pygame.display.set_caption("Arcade Games Launcher")
                
            except Exception as e:
                print(f"Error launching game {game_name}: {e}")
    
    def run(self):
        """Main launcher loop."""
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Arcade Games Launcher")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    launcher = SimpleLauncher()
    launcher.run()
