# Asteroids
A Python implementation of the classic Asteroids vector game.

## License
Copyright © 2025 Arne Damvin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

## Description
This project is a recreation of the classic Asteroids game for educational purposes.
This game is a clone of the original Atari Asteroids arcade game from 1979. 

It features:

- Vector-style graphics
- Inertia-based movement for the spaceship
- Asteroid splitting mechanics
- Flying saucers (UFOs) that shoot at the player
- Hyperspace functionality

## Controls

- Left/Right Arrow Keys: Rotate the ship
- Up Arrow Key: Thrust
- Space: Fire
- H: Hyperspace (teleport to a random location)
- Esc: Quit the game

## Installation

### Clone the repository

```bash
git clone https://github.com/arndam/asteroids.git
cd asteroids
```

### Setting up a Virtual Environment

#### On Windows:
```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### Install dependencies
Once your virtual environment is activated, install the required packages:

```bash
pip install -r requirements.txt
```

### Generate Sound Files
The game requires sound files to be created:

```bash
python create_sounds.py
```

### Run the game
```bash
python asteroids.py
```

## Requirements

- Python 3.6+
- Pygame 2.0+

