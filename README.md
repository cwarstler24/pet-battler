# 🎮 Creature Battler - Tournament Arena

A turn-based creature battle game featuring tournament-style gameplay, AI opponents, and strategic combat mechanics. Build your ultimate creature, allocate stats wisely, and fight your way to become the tournament champion!

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Game Mechanics](#game-mechanics)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Technology Stack](#technology-stack)

## ✨ Features

- **12 Unique Creature Types** - Each with unique stat biases and characteristics
- **Strategic Stat Allocation** - Customize your creature with 6 initial stat points
- **Tournament Progression** - Battle through 8-creature tournaments to become champion
- **AI Opponents** - Smart AI opponents with difficulty scaling
- **Dynamic Combat System** - Dodge, critical hits, and defense mechanics
- **Three Move Types**: Attack, Defend (3 uses/round), and Special Ability (1 use/round)
- **Level-Up System** - Earn 3 stat points after each match victory except the final championship (no points awarded after the last win)
- **Real-time Battle Visualization** - ASCII art animations and live HP tracking
- **RESTful API** - Clean API architecture with FastAPI
- **Rate Limiting** - Built-in API protection (60 requests/minute)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (tested with Python 3.13)
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pet-battler
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   ```bash
   python -m src
   ```

4. **Open your browser**
   - Frontend: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🎯 Game Mechanics

### Creature Stats (1-20 range)

Each creature has five core stats:

- **Speed** 🏃 - Determines turn order and dodge chance (20 Speed = 40% dodge)
- **Health** ❤️ - Maximum HP for the creature
- **Defense** 🛡️ - Damage reduction percentage (20 Defense = 50% reduction)
- **Strength** 💪 - Affects damage output
- **Luck** 🍀 - Critical hit chance (20 Luck = 30% crit chance, 1.5x damage)

### Creature Types

| Creature | Stat Biases | Description |
|----------|-------------|-------------|
| 🐉 Dragon | +5 Health, -3 Speed, +2 Strength | Tank with powerful attacks |
| 🦉 Owlbear | +3 Strength, +3 Defense, -2 Speed | Balanced fighter |
| 🧙 Gnome | +4 Luck, +3 Speed, -3 Strength | Fast and lucky, weak hits |
| 🐙 Kraken | +4 Health, +3 Strength, -2 Speed | Sea monster powerhouse |
| 👾 Cthulu | +5 Luck, -3 Speed, +2 Defense | Eldritch horror with high crit |
| 🐂 Minotaur | +5 Strength, -3 Luck, +2 Health | Pure damage dealer |
| 🐕 Cerberus | +4 Speed, +2 Defense, -1 Luck | Quick three-headed guardian |
| 🐍 Medusa | +4 Luck, -2 Strength, +2 Defense | Stone gaze specialist |
| 🤖 Robot | +5 Defense, -3 Luck, +2 Health | Heavily armored |
| 🐍 Python | +4 Speed, +3 Luck, -2 Defense | Programming serpent |
| 👤 Jacob | +2 All Stats | Balanced mysterious entity |
| 🌪️ Beyblade | +6 Speed, -4 Defense, +2 Strength | Extremely fast, fragile |

### Combat Mechanics

**Turn Order**: Creatures with higher Speed move first

**Damage Calculation**:
1. Base damage: Random 5-15
2. Apply attacker's Strength modifier (Strength/10)
3. Roll for critical hit (Luck-based, 1.5x damage)
4. Apply defender's Defense reduction
5. Check if defender is using Defend move (70% damage reduction)

**Move Types**:
- **Attack** ⚔️ - Standard damage attack (always available)
- **Defend** 🛡️ - Reduces incoming damage by 70% (3 uses per round)
- **Special** ✨ - Enhanced attack (1.75x damage, 1 use per round)

**Special Abilities**: Harder to dodge, higher crit chance, but less affected by defense

### Tournament System

1. **8-Creature Bracket** - Single elimination format
2. **Player + AI Opponents** - You vs 7 AI creatures
3. **Full Heal Between Rounds** - HP restored after each victory
4. **Stat Upgrades** - Gain 3 stat points after winning each non-final match (the championship win does not grant additional points)
5. **Progressive Difficulty** - Later opponents have better stat allocations

## 📁 Project Structure

```
pet-battler/
├── src/
│   ├── __init__.py
│   ├── __main__.py              # Application entry point
│   ├── main.py
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── app.py               # FastAPI application setup
│   │   ├── models/
│   │   │   ├── creature.py      # Creature data models
│   │   │   ├── move.py          # Move/action models
│   │   │   └── game_state.py    # Game state management
│   │   ├── logic/
│   │   │   ├── combat.py        # Combat engine
│   │   │   ├── ai_opponent.py   # AI decision-making
│   │   │   └── tournament.py    # Tournament management
│   │   ├── routes/
│   │   │   ├── creature_routes.py  # Creature API endpoints
│   │   │   └── game_routes.py      # Game flow endpoints
│   │   └── middleware/
│   │       └── rate_limit.py    # Rate limiting middleware
│   └── frontend/
│       ├── index.html           # Main frontend HTML
│       └── static/
│           ├── css/
│           │   └── styles.css   # Game styling
│           └── js/
│               └── app.js       # Frontend game logic
├── tests/
│   └── test_models.py           # Unit tests
├── docs/
│   ├── project-outline.md       # Original project outline
│   └── copilotPrompts.md
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Creature Management

**GET /creatures/types**
- Get all available creature types with stat biases
- Response: Array of creature type info

**POST /creatures**
- Create a new creature
- Request Body:
  ```json
  {
    "name": "Flamezord",
    "creature_type": "dragon",
    "stat_allocations": {
      "strength": 3,
      "health": 3
    }
  }
  ```
- Returns: Creature object with ID and final stats

**GET /creatures/{creature_id}**
- Get specific creature details
- Returns: Creature object

**GET /creatures**
- List all created creatures
- Returns: Array of creatures

#### Game Flow

**POST /game/start**
- Start a new tournament
- Request Body:
  ```json
  {
    "num_players": 1,
    "creature_ids": ["creature-uuid"],
    "tournament_size": 8
  }
  ```
- Returns: Game ID and first match info

**POST /game/{game_id}/move**
- Submit a move for the current match
- Request Body:
  ```json
  {
    "creature_id": "creature-uuid",
    "move_type": "attack"  // "attack", "defend", or "special"
  }
  ```
- Returns: Updated match state with battle results

**GET /game/{game_id}/state**
- Get current game state
- Returns: Current match info, tournament status

**POST /game/{game_id}/allocate-stats**
- Allocate stat points after winning a match
- Request Body:
  ```json
  {
    "creature_id": "creature-uuid",
    "stat_allocations": {
      "strength": 2,
      "speed": 1
    }
  }
  ```
- Returns: Updated creature stats

**GET /health**
- Health check endpoint
- Returns: Service status

### Interactive API Documentation

Visit http://localhost:8000/docs for Swagger UI with interactive API testing.

## 🛠️ Development

### Running in Development Mode

The server runs with auto-reload enabled by default:

```bash
python -m src
```

### Code Structure

**Backend Architecture**:
- **Models** - Pydantic models for data validation
- **Logic** - Core game mechanics (combat, AI, tournaments)
- **Routes** - FastAPI endpoints for API
- **Middleware** - Rate limiting and request processing

**Frontend Architecture**:
- **Vanilla JavaScript** - No framework dependencies
- **Screen-based UI** - Setup, Battle, Level-up, Victory screens
- **Real-time Updates** - Fetch API for backend communication
- **ASCII Art** - Character-based creature visualization

### Key Design Patterns

1. **Pydantic Models** - Type-safe data validation
2. **Factory Pattern** - Creature creation with biases
3. **Strategy Pattern** - AI decision-making
4. **State Management** - Tournament bracket progression
5. **Middleware Chain** - CORS, rate limiting

## 🧪 Testing

### Run Tests

```bash
pytest tests/
```

### Test Coverage

Current tests cover:
- Creature creation and validation
- Stat allocation limits
- Damage calculation
- Knockout mechanics

### Adding Tests

Place test files in the `tests/` directory following the `test_*.py` naming convention.

## 🔧 Technology Stack

### Backend
- **FastAPI** 0.121.0 - Modern Python web framework
- **Uvicorn** 0.32.0 - ASGI server
- **Pydantic** 2.9.2 - Data validation
- **Starlette** 0.49.3 - ASGI toolkit

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with animations
- **Vanilla JavaScript** - Game logic
- **Fetch API** - HTTP requests

### Development Tools
- **pytest** 8.3.3 - Testing framework
- **httpx** 0.27.2 - HTTP client for tests

## 🎮 How to Play

1. **Create Your Creature**
   - Enter a name
   - Choose a creature type (consider stat biases)
   - Allocate 6 stat points strategically

2. **Battle Strategy**
   - Use **Attack** for consistent damage
   - Use **Defend** when low on HP or facing strong opponents
   - Save **Special** for finishing blows or critical moments

3. **Tournament Progression**
   - Win matches to advance through the bracket
  - Allocate 3 stat points after each non-final victory (no points after the final match)
   - Adapt your strategy as opponents get stronger

4. **Become Champion**
   - Defeat all 7 opponents
   - Claim your tournament victory!

## 🤝 Contributing

This project was developed as an educational exercise. Feel free to fork and extend!

### Future Enhancement Ideas
- Multiple tournament sizes (4, 8, 16 creatures)
- Persistent creature storage (database)
- Player vs Player multiplayer mode
- More creature types and special abilities
- Sound effects and enhanced animations
- Replay system for battles
- Leaderboard tracking

## 📄 License

This project is available for educational purposes.

## 🙏 Acknowledgments


Built with FastAPI, modern Python practices, and lots of creature-battling fun!
