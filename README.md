# Space Shooter Game

A classic arcade-style space shooter game built with Python and Pygame.

## Features

- Progressive difficulty system with increasingly challenging enemies
- Three types of enemies with unique designs and behaviors:
  - Basic Enemies (Levels 1-3)
  - Advanced Enemies (Levels 4-6)
  - Elite Enemies (Level 7+)
- Boss battles with complex movement and attack patterns
- Power-up system including:
  - Shields
  - Double lasers
  - Score multipliers
- Dynamic scoring system
- Retro-style graphics and effects

## Requirements

- Python 3.x
- Pygame

## Installation

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/space-shooter.git
cd space-shooter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## How to Play

Run the game:
```bash
python game.py
```

### Controls
- Arrow keys to move
- Space to shoot
- ESC to pause
- Enter to start game/continue

### Game Rules
- Defeat enemies to progress through levels
- Collect power-ups to enhance your ship
- Boss appears after clearing regular enemies
- Game ends when you run out of lives

## Development

The game features a modular design with separate classes for:
- Player ship
- Different enemy types
- Boss mechanics
- Power-up system
- Particle effects

## License

This project is licensed under the MIT License - see the LICENSE file for details.
