# Pygame Arcade Project

A collection of modular arcade games with a central launcher interface.

## Project Structure

```
pygame_arcade_project/
│
├── launcher.py                 # Main UI to select and launch games
├── config.py                   # Global configurations
├── utils/                      # Shared utility modules
├── assets/                     # Shared assets
└── games/                      # Individual game modules
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Games

Launch the arcade launcher:
```bash
python launcher.py
```

## Adding New Games

1. Create a new game directory in `games/`:
```bash
mkdir games/your_game_name
```

2. Add required files:
   - `__init__.py`
   - `main.py` (with `run_game()` function)
   - `assets/` directory for game-specific assets
   - `logic/` directory for game-specific code

3. Update `config.py` to include your game in `GAME_MODULES`.

## Controls

- Use mouse to navigate the launcher menu
- ESC key returns to launcher from any game
- Game-specific controls are shown in each game's menu

## Development

- Each game is a self-contained module
- Shared utilities are available in the `utils/` directory
- Common assets are stored in `assets/`
- Game-specific assets should be stored in the game's own `assets/` directory

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
