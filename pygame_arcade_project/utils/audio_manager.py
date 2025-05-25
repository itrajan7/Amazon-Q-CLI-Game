"""Audio manager for the arcade games."""

import pygame
import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import SOUNDS_DIR

class AudioManager:
    """Manages audio playback for the games."""
    
    def __init__(self):
        self.sounds = {}
        self.music_file = None
        self.volume = 0.5
        pygame.mixer.init()
    
    def load_sound(self, name, file_path):
        """Load a sound effect."""
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(self.volume)
            self.sounds[name] = sound
            return True
        except Exception as e:
            print(f"Error loading sound {name}: {e}")
            return False
    
    def load_sounds_from_directory(self, directory=SOUNDS_DIR):
        """Load all sound files from a directory."""
        if not os.path.exists(directory):
            print(f"Sound directory not found: {directory}")
            return
            
        for filename in os.listdir(directory):
            if filename.endswith(('.wav', '.mp3', '.ogg')):
                name = os.path.splitext(filename)[0]
                file_path = os.path.join(directory, filename)
                self.load_sound(name, file_path)
    
    def play_sound(self, name):
        """Play a sound effect."""
        if name in self.sounds:
            self.sounds[name].play()
            return True
        return False
    
    def play_music(self, file_path, loops=-1):
        """Play background music."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(loops)
            self.music_file = file_path
            return True
        except Exception as e:
            print(f"Error playing music: {e}")
            return False
    
    def stop_music(self):
        """Stop the currently playing music."""
        pygame.mixer.music.stop()
        self.music_file = None
    
    def pause_music(self):
        """Pause the currently playing music."""
        pygame.mixer.music.pause()
    
    def unpause_music(self):
        """Unpause the currently playing music."""
        pygame.mixer.music.unpause()
    
    def set_volume(self, volume):
        """Set the volume for all sounds and music."""
        self.volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.volume)
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
