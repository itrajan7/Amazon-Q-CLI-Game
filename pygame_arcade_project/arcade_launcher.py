"""
Arcade Games Launcher
A modern launcher for the arcade games collection.
"""

import pygame
import sys
import os
import subprocess

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Game list
GAMES = [
    {
        "name": "Rocket Rumble",
        "description": "Space shooter with waves of enemies",
        "color": (0, 255, 255),  # Cyan
        "script": "run_rocket_rumble.py"
    },
    {
        "name": "Pixel Heist",
        "description": "Stealth-based heist game",
        "color": (0, 255, 0),  # Green
        "script": "run_pixel_heist.py"
    }
]

class Button:
    """A button class with hover effects."""
    
    def __init__(self, x, y, width, height, text, color, description=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.description = description
        self.hover = False
        self.font = pygame.font.SysFont("Arial", 24)
        self.desc_font = pygame.font.SysFont("Arial", 16)
    
    def update(self, mouse_pos):
        """Update button state."""
        self.hover = self.rect.collidepoint(mouse_pos)
        return self.hover
    
    def draw(self, surface):
        """Draw the button."""
        # Draw button background with hover effect
        color = tuple(min(c + 30, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=8)
        
        # Draw button text
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Draw description if hovering
        if self.hover and self.description:
            desc_surf = self.desc_font.render(self.description, True, (255, 255, 255))
            desc_rect = desc_surf.get_rect(midtop=(self.rect.centerx, self.rect.bottom + 5))
            surface.blit(desc_surf, desc_rect)

def main():
    """Main function to run the launcher."""
    # Create screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Arcade Games Launcher")
    clock = pygame.time.Clock()
    
    # Create buttons
    buttons = []
    y_pos = 200
    for game in GAMES:
        button = Button(
            SCREEN_WIDTH // 2 - 150,
            y_pos,
            300, 60,
            game["name"],
            game["color"],
            game["description"]
        )
        buttons.append(button)
        y_pos += 100
    
    # Add exit button
    exit_button = Button(
        SCREEN_WIDTH // 2 - 100,
        y_pos,
        200, 50,
        "EXIT",
        (255, 50, 50),
        "Quit the launcher"
    )
    buttons.append(exit_button)
    
    # Load fonts
    title_font = pygame.font.SysFont("Arial", 48)
    
    # Main loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    for i, button in enumerate(buttons):
                        if button.rect.collidepoint(mouse_pos):
                            if i == len(buttons) - 1:  # Exit button
                                running = False
                            else:
                                # Launch the selected game using subprocess
                                game = GAMES[i]
                                script_path = os.path.join(
                                    os.path.dirname(os.path.abspath(__file__)),
                                    game["script"]
                                )
                                print(f"Launching {game['name']}...")
                                
                                # Use subprocess to run the game in a separate process
                                pygame.quit()  # Quit pygame before launching
                                subprocess.call(["python3", script_path])
                                
                                # Reinitialize pygame after game exits
                                pygame.init()
                                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                                pygame.display.set_caption("Arcade Games Launcher")
        
        # Update buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.update(mouse_pos)
        
        # Draw
        screen.fill((20, 20, 40))
        
        # Draw title
        title_surf = title_font.render("ARCADE GAMES", True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surf, title_rect)
        
        # Draw buttons
        for button in buttons:
            button.draw(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
