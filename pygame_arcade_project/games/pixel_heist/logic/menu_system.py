"""
Menu system for Pixel Heist game with retro terminal aesthetic.
"""

import pygame
import math
import random
import time

class RetroTerminal:
    """A class for creating retro terminal-style UI elements."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont("Courier New", 24)
        self.small_font = pygame.font.SysFont("Courier New", 16)
        
        # Terminal colors
        self.bg_color = (0, 0, 0)
        self.text_color = (0, 255, 0)  # Green text
        self.highlight_color = (0, 200, 0)
        self.dim_color = (0, 100, 0)
        self.alert_color = (255, 50, 50)
        
        # Glitch effect parameters
        self.glitch_lines = []
        self.glitch_timer = 0
        self.glitch_interval = random.uniform(1.0, 3.0)
        
        # CRT effect parameters
        self.scan_line_height = 4
        self.scan_line_opacity = 20
        
        # Create surfaces
        self.surface = pygame.Surface((width, height))
        self.scan_lines = self._create_scan_lines()
        self.static_overlay = self._create_static_overlay()
    
    def _create_scan_lines(self):
        """Create scan line overlay for CRT effect."""
        scan_lines = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(0, self.height, self.scan_line_height * 2):
            pygame.draw.rect(
                scan_lines, 
                (0, 0, 0, self.scan_line_opacity),
                (0, y, self.width, self.scan_line_height)
            )
        return scan_lines
    
    def _create_static_overlay(self):
        """Create static noise overlay."""
        static = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        static_pixels = pygame.PixelArray(static)
        
        for x in range(0, self.width, 2):
            for y in range(0, self.height, 2):
                if random.random() < 0.05:  # 5% of pixels get static
                    alpha = random.randint(5, 20)
                    static_pixels[x, y] = (255, 255, 255, alpha)
        
        static_pixels.close()
        return static
    
    def update(self, dt):
        """Update terminal effects."""
        # Update glitch effect
        self.glitch_timer += dt
        if self.glitch_timer >= self.glitch_interval:
            self.glitch_timer = 0
            self.glitch_interval = random.uniform(1.0, 3.0)
            self._generate_glitch_lines()
    
    def _generate_glitch_lines(self):
        """Generate random glitch lines."""
        self.glitch_lines = []
        if random.random() < 0.3:  # 30% chance of glitch
            num_lines = random.randint(1, 5)
            for _ in range(num_lines):
                y = random.randint(0, self.height)
                width = random.randint(20, self.width // 2)
                offset = random.randint(-10, 10)
                duration = random.uniform(0.05, 0.2)
                self.glitch_lines.append({
                    'y': y,
                    'width': width,
                    'offset': offset,
                    'duration': duration,
                    'timer': 0
                })
    
    def render_text(self, text, x, y, color=None, typewriter=False, delay=0.05):
        """Render text with optional typewriter effect."""
        if color is None:
            color = self.text_color
            
        if typewriter:
            for i in range(len(text) + 1):
                self.surface.fill(self.bg_color)
                text_surf = self.font.render(text[:i], True, color)
                self.surface.blit(text_surf, (x, y))
                yield self.surface
                time.sleep(delay)
        else:
            text_surf = self.font.render(text, True, color)
            self.surface.blit(text_surf, (x, y))
    
    def render_menu(self, title, options, selected_index):
        """Render a menu with title and options."""
        self.surface.fill(self.bg_color)
        
        # Draw title
        title_surf = self.font.render(f"[ {title} ]", True, self.text_color)
        title_rect = title_surf.get_rect(centerx=self.width // 2, y=30)
        self.surface.blit(title_surf, title_rect)
        
        # Draw separator
        pygame.draw.line(
            self.surface,
            self.text_color,
            (50, 70),
            (self.width - 50, 70),
            1
        )
        
        # Draw options
        y_pos = 100
        for i, option in enumerate(options):
            prefix = "> " if i == selected_index else "  "
            color = self.highlight_color if i == selected_index else self.text_color
            text_surf = self.font.render(f"{prefix}{option}", True, color)
            self.surface.blit(text_surf, (80, y_pos))
            y_pos += 40
        
        # Draw footer
        footer_text = "[ UP/DOWN: Navigate | ENTER: Select | ESC: Back ]"
        footer_surf = self.small_font.render(footer_text, True, self.dim_color)
        footer_rect = footer_surf.get_rect(centerx=self.width // 2, bottom=self.height - 20)
        self.surface.blit(footer_surf, footer_rect)
        
        # Apply effects
        self._apply_effects()
        
        return self.surface
    
    def render_dialog(self, title, message, options=None):
        """Render a dialog box with message and options."""
        self.surface.fill(self.bg_color)
        
        # Draw border
        border_rect = pygame.Rect(50, 50, self.width - 100, self.height - 100)
        pygame.draw.rect(self.surface, self.text_color, border_rect, 2)
        
        # Draw title
        title_surf = self.font.render(title, True, self.text_color)
        title_rect = title_surf.get_rect(centerx=self.width // 2, y=70)
        self.surface.blit(title_surf, title_rect)
        
        # Draw separator
        pygame.draw.line(
            self.surface,
            self.text_color,
            (70, 100),
            (self.width - 70, 100),
            1
        )
        
        # Draw message (with word wrap)
        words = message.split(' ')
        lines = []
        line = []
        for word in words:
            test_line = ' '.join(line + [word])
            test_surf = self.font.render(test_line, True, self.text_color)
            if test_surf.get_width() > self.width - 140:
                lines.append(' '.join(line))
                line = [word]
            else:
                line.append(word)
        if line:
            lines.append(' '.join(line))
        
        y_pos = 130
        for line in lines:
            text_surf = self.font.render(line, True, self.text_color)
            self.surface.blit(text_surf, (70, y_pos))
            y_pos += 30
        
        # Draw options if provided
        if options:
            option_y = self.height - 150
            for i, option in enumerate(options):
                text_surf = self.font.render(f"{i+1}. {option}", True, self.text_color)
                self.surface.blit(text_surf, (100, option_y))
                option_y += 30
        
        # Apply effects
        self._apply_effects()
        
        return self.surface
    
    def render_loading(self, progress, message="LOADING"):
        """Render a loading screen with progress bar."""
        self.surface.fill(self.bg_color)
        
        # Draw message
        text_surf = self.font.render(message, True, self.text_color)
        text_rect = text_surf.get_rect(centerx=self.width // 2, centery=self.height // 2 - 40)
        self.surface.blit(text_surf, text_rect)
        
        # Draw progress bar
        bar_width = 400
        bar_height = 20
        bar_rect = pygame.Rect(
            (self.width - bar_width) // 2,
            self.height // 2,
            bar_width,
            bar_height
        )
        pygame.draw.rect(self.surface, self.dim_color, bar_rect)
        
        # Draw progress
        progress_width = int(bar_width * progress)
        progress_rect = pygame.Rect(
            (self.width - bar_width) // 2,
            self.height // 2,
            progress_width,
            bar_height
        )
        pygame.draw.rect(self.surface, self.text_color, progress_rect)
        
        # Draw percentage
        percent_text = f"{int(progress * 100)}%"
        percent_surf = self.font.render(percent_text, True, self.text_color)
        percent_rect = percent_surf.get_rect(
            centerx=self.width // 2,
            centery=self.height // 2 + 40
        )
        self.surface.blit(percent_surf, percent_rect)
        
        # Apply effects
        self._apply_effects()
        
        return self.surface
    
    def _apply_effects(self):
        """Apply visual effects to the terminal surface."""
        # Apply glitch effect
        for glitch in self.glitch_lines:
            glitch_rect = pygame.Rect(
                glitch['offset'],
                glitch['y'],
                glitch['width'],
                2
            )
            line_data = pygame.Surface((glitch['width'], 2))
            line_data.blit(self.surface, (0, 0), 
                         (max(0, -glitch['offset']), glitch['y'], glitch['width'], 2))
            self.surface.blit(line_data, (max(0, glitch['offset']), glitch['y']))
        
        # Apply scan lines
        self.surface.blit(self.scan_lines, (0, 0))
        
        # Apply static
        if random.random() < 0.2:  # Only show static occasionally
            self.surface.blit(self.static_overlay, (0, 0))
        
        # Add screen flicker
        if random.random() < 0.01:  # 1% chance of screen flicker
            flicker = pygame.Surface((self.width, self.height))
            flicker.fill((255, 255, 255))
            flicker.set_alpha(random.randint(10, 30))
            self.surface.blit(flicker, (0, 0))


class GameMenu:
    """Game menu system with retro terminal aesthetic."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.terminal = RetroTerminal(screen_width, screen_height)
        
        # Menu state
        self.current_menu = "main"
        self.selected_index = 0
        self.menu_stack = []
        
        # Define menus
        self.menus = {
            "main": {
                "title": "PIXEL HEIST",
                "options": ["START GAME", "OPTIONS", "LEADERBOARD", "EXIT"]
            },
            "options": {
                "title": "OPTIONS",
                "options": ["SOUND: ON", "MUSIC: ON", "DIFFICULTY: NORMAL", "BACK"]
            },
            "difficulty": {
                "title": "SELECT DIFFICULTY",
                "options": ["EASY", "NORMAL", "HARD", "BACK"]
            },
            "pause": {
                "title": "GAME PAUSED",
                "options": ["RESUME", "OPTIONS", "QUIT TO MENU"]
            }
        }
        
        # Background animation
        self.bg_timer = 0
        self.bg_frame = 0
        self.bg_frames = []  # Would contain CCTV footage frames
        
        # Sound effects
        self.sounds = {
            "select": None,
            "navigate": None,
            "back": None,
            "error": None
        }
    
    def load_assets(self):
        """Load menu assets like background animations and sounds."""
        # This would load actual assets in a complete implementation
        pass
    
    def update(self, dt):
        """Update menu state and animations."""
        self.terminal.update(dt)
        
        # Update background animation
        self.bg_timer += dt
        if self.bg_timer >= 0.2:  # 5 FPS for background
            self.bg_timer = 0
            self.bg_frame = (self.bg_frame + 1) % max(1, len(self.bg_frames))
    
    def handle_input(self, event):
        """Handle menu input events."""
        if event.type == pygame.KEYDOWN:
            current_options = self.menus[self.current_menu]["options"]
            
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_index = (self.selected_index - 1) % len(current_options)
                # Play navigate sound
                return "navigate"
                
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_index = (self.selected_index + 1) % len(current_options)
                # Play navigate sound
                return "navigate"
                
            elif event.key == pygame.K_RETURN:
                selected_option = current_options[self.selected_index]
                # Play select sound
                return self._handle_selection(selected_option)
                
            elif event.key == pygame.K_ESCAPE:
                if self.menu_stack:
                    # Go back to previous menu
                    prev_menu = self.menu_stack.pop()
                    self.current_menu = prev_menu["menu"]
                    self.selected_index = prev_menu["index"]
                    # Play back sound
                    return "back"
        
        return None
    
    def _handle_selection(self, option):
        """Handle menu option selection."""
        if self.current_menu == "main":
            if option == "START GAME":
                return "start_game"
            elif option == "OPTIONS":
                self._push_menu("options")
            elif option == "LEADERBOARD":
                return "leaderboard"
            elif option == "EXIT":
                return "exit"
                
        elif self.current_menu == "options":
            if option == "BACK":
                self._pop_menu()
            elif option == "DIFFICULTY: NORMAL":
                self._push_menu("difficulty")
            elif option.startswith("SOUND:"):
                # Toggle sound
                new_state = "OFF" if "ON" in option else "ON"
                self.menus["options"]["options"][0] = f"SOUND: {new_state}"
                return "toggle_sound"
            elif option.startswith("MUSIC:"):
                # Toggle music
                new_state = "OFF" if "ON" in option else "ON"
                self.menus["options"]["options"][1] = f"MUSIC: {new_state}"
                return "toggle_music"
                
        elif self.current_menu == "difficulty":
            if option == "BACK":
                self._pop_menu()
            else:
                # Set difficulty
                self.menus["options"]["options"][2] = f"DIFFICULTY: {option}"
                self._pop_menu()
                return f"set_difficulty_{option.lower()}"
                
        elif self.current_menu == "pause":
            if option == "RESUME":
                return "resume_game"
            elif option == "OPTIONS":
                self._push_menu("options")
            elif option == "QUIT TO MENU":
                return "quit_to_menu"
                
        elif self.current_menu == "game_over":
            if option == "RETRY":
                return "retry"
            elif option == "QUIT TO MENU":
                return "quit_to_menu"
                
        elif self.current_menu == "victory":
            if option == "NEXT LEVEL":
                return "next_level"
            elif option == "QUIT TO MENU":
                return "quit_to_menu"
        
        return None
    
    def _push_menu(self, menu_name):
        """Push current menu to stack and switch to new menu."""
        self.menu_stack.append({
            "menu": self.current_menu,
            "index": self.selected_index
        })
        self.current_menu = menu_name
        self.selected_index = 0
    
    def _pop_menu(self):
        """Pop menu from stack and return to previous menu."""
        if self.menu_stack:
            prev_menu = self.menu_stack.pop()
            self.current_menu = prev_menu["menu"]
            self.selected_index = prev_menu["index"]
    
    def draw(self, surface):
        """Draw the current menu to the surface."""
        # Get current menu data
        menu_data = self.menus[self.current_menu]
        
        # Render menu
        menu_surface = self.terminal.render_menu(
            menu_data["title"],
            menu_data["options"],
            self.selected_index
        )
        
        # Draw to main surface
        surface.blit(menu_surface, (0, 0))
    
    def show_dialog(self, surface, title, message, options=None):
        """Show a dialog box with message and options."""
        dialog_surface = self.terminal.render_dialog(title, message, options)
        surface.blit(dialog_surface, (0, 0))
    
    def show_loading(self, surface, progress, message="LOADING"):
        """Show a loading screen with progress bar."""
        loading_surface = self.terminal.render_loading(progress, message)
        surface.blit(loading_surface, (0, 0))
