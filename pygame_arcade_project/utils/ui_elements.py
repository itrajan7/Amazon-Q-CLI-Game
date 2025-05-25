"""UI elements for the arcade games."""

import pygame
import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FONTS_DIR, WHITE, BLACK, GRAY, BLUE

class Button:
    """A simple button class for UI interactions."""
    
    def __init__(self, x, y, width, height, text, font_size=32, 
                 text_color=WHITE, bg_color=BLUE, hover_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color or tuple(max(0, c - 30) for c in bg_color)
        self.is_hovered = False
        
        # Try to load a default font
        try:
            font_path = os.path.join(FONTS_DIR, "default.ttf")
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, font_size)
            else:
                self.font = pygame.font.SysFont("Arial", font_size)
        except:
            self.font = pygame.font.SysFont("Arial", font_size)
    
    def draw(self, surface):
        """Draw the button on the given surface."""
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Border
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, mouse_pos):
        """Check if mouse is hovering over the button."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
    
    def is_clicked(self, mouse_pos, mouse_click):
        """Check if button is clicked."""
        return self.rect.collidepoint(mouse_pos) and mouse_click


class Menu:
    """A simple menu class for UI interactions."""
    
    def __init__(self, title, width, height, bg_color=GRAY):
        self.title = title
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.buttons = []
        
        # Try to load a default font
        try:
            font_path = os.path.join(FONTS_DIR, "default.ttf")
            if os.path.exists(font_path):
                self.title_font = pygame.font.Font(font_path, 48)
            else:
                self.title_font = pygame.font.SysFont("Arial", 48)
        except:
            self.title_font = pygame.font.SysFont("Arial", 48)
    
    def add_button(self, button):
        """Add a button to the menu."""
        self.buttons.append(button)
    
    def draw(self, surface):
        """Draw the menu on the given surface."""
        # Draw background
        menu_rect = pygame.Rect(
            (surface.get_width() - self.width) // 2,
            (surface.get_height() - self.height) // 2,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, self.bg_color, menu_rect)
        pygame.draw.rect(surface, BLACK, menu_rect, 3)  # Border
        
        # Draw title
        title_surf = self.title_font.render(self.title, True, WHITE)
        title_rect = title_surf.get_rect(
            center=(surface.get_width() // 2, 
                   (surface.get_height() - self.height) // 2 + 50)
        )
        surface.blit(title_surf, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface)
    
    def handle_event(self, event):
        """Handle events for the menu."""
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons:
                button.check_hover(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button.is_clicked(event.pos, True):
                    return button.text
        
        return None
