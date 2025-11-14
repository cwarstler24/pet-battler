# 🏗️ Pet Battler - Architecture Documentation

This document provides a comprehensive overview of the Pet Battler application architecture, design patterns, and technical implementation details.

## Table of Contents

- [System Overview](#system-overview)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Combat System](#combat-system)
- [AI System](#ai-system)
- [Tournament System](#tournament-system)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (Browser)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  index.html  │  │  styles.css  │  │    app.js    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/JSON
                      │ (Fetch API)
┌─────────────────────▼───────────────────────────────────┐
│                  FastAPI Backend (Python)               │
│  ┌─────────────────────────────────────────────────┐    │
│  │            Middleware Layer                     │    │
│  │  - CORS Handler                                 │    │
│  │  - Rate Limiter (60 req/min)                    │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │            Route Layer                          │    │
│  │  - Creature Routes    - Game Routes             │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │            Business Logic Layer                 │    │
│  │  - Combat Engine      - AI Opponent             │    │
│  │  - Tournament Manager                           │    │
│  └─────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────┐    │
│  │            Data Model Layer                     │    │
│  │  - Creature          - Game State               │    │
│  │  - Move              - Match                    │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI (Web Framework)
- Pydantic (Data Validation)
- Uvicorn (ASGI Server)
- Python 3.8+

**Frontend:**
- Vanilla JavaScript (ES6+)
- HTML5
- CSS3
- Fetch API

**Storage:**
- In-memory dictionaries

---

## Backend Architecture

### Application Structure

```
src/backend/
├── app.py                   # FastAPI application entry point
├── models/                  # Pydantic data models
│   ├── creature.py          # Creature, CreatureType, CreatureStats
│   ├── move.py              # Move types and results
│   └── game_state.py        # GameState, Match, Tournament
├── logic/                   # Business logic
│   ├── combat.py            # CombatEngine (battle mechanics)
│   ├── ai_opponent.py       # AIOpponentGenerator
│   └── tournament.py        # TournamentManager
├── routes/                  # API endpoints
│   ├── creature_routes.py   # Creature CRUD operations
│   └── game_routes.py       # Game flow management
└── middleware/              # Request processing
    └── rate_limit.py        # Rate limiting
```

### Layer Responsibilities

#### 1. Application Layer (`app.py`)

```python
# Responsibilities:
- FastAPI app initialization
- Middleware registration (CORS, rate limiting)
- Router inclusion
- Static file serving
- Frontend routing
```

**Key Features:**
- CORS configuration for cross-origin requests
- Static file mounting for frontend assets
- Health check endpoint
- API documentation auto-generation

#### 2. Model Layer (`models/`)

**Pydantic Models** provide:
- Type validation
- Data serialization/deserialization
- Schema generation for API docs
- Immutable defaults

**Key Models:**

```python
# creature.py
class Creature(BaseModel):
    - Stat management (speed, health, defense, strength, luck)
    - HP tracking (current_hp, max_hp)
    - Resource management (defend/special uses)
    - Factory method: create_with_biases()
    - Methods: take_damage(), reset_round_resources()

# move.py
class Move(BaseModel):
    - Move type (attack, defend, special)
    - User and target references
    
class MoveResult(BaseModel):
    - Execution results (damage, crits, dodges)
    - Combat messages

# game_state.py
class Match(BaseModel):
    - Two-creature battle state
    - Pending move collection
    - Move history tracking
    
class TournamentBracket(BaseModel):
    - Bracket structure
    - Match progression
    - Round management
    
class GameState(BaseModel):
    - Overall game tracking
    - Player creatures
    - Tournament instance
    - Champion determination
```

#### 3. Logic Layer (`logic/`)

**CombatEngine** (`combat.py`)
```python
Responsibilities:
- Turn order determination (speed-based)
- Damage calculation with modifiers
- Dodge/crit/defense mechanics
- Move execution (attack, defend, special)
- Result generation

Key Methods:
- execute_moves(): Main combat resolution
- _execute_attack(): Standard attack damage
- _execute_defend(): Defensive stance
- _execute_special(): Enhanced ability damage
```

**AIOpponentGenerator** (`ai_opponent.py`)
```python
Responsibilities:
- Random AI creature generation
- Difficulty-based stat allocation
- Move decision-making
- Named AI opponent creation

Key Methods:
- generate_ai_creature(): Create AI opponent
- decide_move(): Strategic move selection
- _generate_stat_allocations(): Difficulty-scaled stats
```

**TournamentManager** (`tournament.py`)
```python
Responsibilities:
- Tournament bracket creation
- Match pairing
- Bracket progression
- Winner advancement
- HP/resource reset between rounds

Key Methods:
- create_tournament(): Initialize bracket
- advance_tournament(): Progress to next round
- get_tournament_winner(): Final champion
```

#### 4. Route Layer (`routes/`)

**RESTful API Design:**

```
Creature Routes:
GET    /creatures/types      - List creature types
POST   /creatures            - Create creature
GET    /creatures/{id}       - Get creature
GET    /creatures            - List all creatures

Game Routes:
POST   /game/start           - Start tournament
POST   /game/{id}/move       - Submit move
GET    /game/{id}/state      - Get game state
POST   /game/{id}/allocate-stats - Upgrade creature
```

**Route Responsibilities:**
- Request validation
- Business logic delegation
- Response formatting
- Error handling

#### 5. Middleware Layer (`middleware/`)

**Rate Limiter:**
```python
- Per-IP request tracking
- Rolling 60-second window
- 60 requests per minute limit
- 429 response on exceed
```

---

## Frontend Architecture

### Component Structure

```
frontend/
├── index.html               # Main HTML structure
├── static/
    ├── css/
    │   └── styles.css      # All styling
    └── js/
        └── app.js          # Game logic and API calls
```

### Screen-Based UI Flow

```
Setup Screen
    ↓
Battle Screen ←─┐
    ↓           │
Level-Up Screen │ (if won)
    ↓           │
Victory Screen  │ (if tournament complete)
    or          │
Continue ───────┘ (next match)
```

### JavaScript Architecture

**State Management:**
```javascript
gameState = {
    creatureTypes: [],           // Available types from API
    selectedType: null,          // User selection
    statAllocations: {},         // Initial stats
    levelupStatAllocations: {},  // Mid-tournament upgrades
    creatureId: null,            // Created creature ID
    gameId: null,                // Active game ID
    currentMatch: null,          // Match state
    creature1Type: null,         // For ASCII art
    creature2Type: null          // For ASCII art
}
```

**Key Functions:**

```javascript
// Initialization
loadCreatureTypes()         // Fetch creature types
setupEventListeners()       // Attach UI handlers

// Setup Flow
selectCreatureType()        // Handle type selection
adjustStat()                // Stat allocation
createCreatureAndStartGame() // API calls to create & start

// Battle Flow
submitMove()                // Send move to backend
updateBattleDisplay()       // Render match state
showLevelUpScreen()         // Post-victory upgrades

// Utility
getCreatureASCII()          // ASCII art lookup
updateHPBar()               // Visual HP representation
addBattleMessage()          // Battle log updates
```

### UI/UX Patterns

**Screen Transitions:**
```javascript
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => 
        s.classList.remove('active')
    );
    document.getElementById(screenId).classList.add('active');
}
```

**Progressive Enhancement:**
- Disable buttons until valid input
- Real-time stat allocation feedback
- Animated HP bars
- Battle log with scrolling

---

## Data Flow

### 1. Game Initialization Flow

```
User Input (Frontend)
    ↓
[1] Load Creature Types
    GET /creatures/types
    ↓
[2] Select Type + Allocate Stats
    ↓
[3] Create Creature
    POST /creatures
    {name, type, stats}
    ↓
[4] Start Tournament
    POST /game/start
    {creature_ids, size}
    ↓
Backend generates AI opponents
    ↓
Tournament bracket created
    ↓
First match initialized
    ↓
Match state returned to frontend
```

### 2. Battle Round Flow

```
Frontend: User selects move
    ↓
POST /game/{id}/move
{creature_id, move_type}
    ↓
Backend: Store pending move
    ↓
If opponent is AI:
    AI decides move automatically
    ↓
Both moves submitted?
    ↓
YES → Execute Combat
    ↓
[CombatEngine]
1. Determine turn order (speed)
2. First creature acts
   - Calculate damage
   - Apply modifiers
   - Update HP
3. Second creature acts (if alive)
4. Generate results
    ↓
Update match state
    ↓
Check for match end
    ↓
Return results to frontend
    ↓
Frontend updates UI
- HP bars
- Battle log
- Victory/defeat screen
```

### 3. Tournament Progression Flow

```
Match Complete
    ↓
Player creature alive?
    ↓
NO → Tournament Over (Elimination)
    ↓
YES → Award 3 stat points
    ↓
Player allocates stats
    POST /game/{id}/allocate-stats
    ↓
Advance tournament bracket
    ↓
Heal winners to full HP
    ↓
Reset resources (defend/special)
    ↓
Create next round matches
    ↓
More matches remaining?
    ↓
YES → Load next match
NO  → Declare champion
```

---

## Design Patterns

### 1. Factory Pattern

**Creature Creation:**
```python
class Creature:
    @classmethod
    def create_with_biases(cls, name, creature_type, 
                          stat_allocations, is_ai):
        """
        Factory method that:
        1. Sets base stats (all 10)
        2. Applies creature type biases
        3. Applies player allocations
        4. Validates ranges (1-20)
        5. Returns configured creature
        """
```

**Benefits:**
- Encapsulated creation logic
- Type-specific stat modifications
- Validation in one place
- Consistent object initialization

### 2. Strategy Pattern

**AI Decision Making:**
```python
class AIOpponentGenerator:
    @staticmethod
    def decide_move(creature, opponent, round_num):
        """
        Selects move based on:
        - Current HP percentages
        - Opponent stats
        - Round number
        - Resource availability
        
        Weighted random selection:
        - Attack (always available)
        - Defend (if low HP or vs strong opponent)
        - Special (to finish low HP opponents)
        """
```

**Benefits:**
- Flexible AI behavior
- Easy difficulty tuning
- Predictable yet varied gameplay

### 3. State Pattern

**Game State Management:**
```python
class GameState:
    - tracks tournament progress
    - manages current match
    - determines game completion
    
class Match:
    - tracks battle state
    - collects pending moves
    - determines match winner
```

**Benefits:**
- Clear state transitions
- Centralized state logic
- Easy to query game status

### 4. Command Pattern

**Move System:**
```python
class Move(BaseModel):
    move_type: MoveType
    user_id: str
    target_id: Optional[str]

# Moves are queued, then executed together
match.add_move(creature_id, move)
if match.both_moves_submitted():
    result1, result2 = CombatEngine.execute_moves(...)
```

**Benefits:**
- Decoupled move submission from execution
- Both moves execute simultaneously
- Move history tracking

### 5. Repository Pattern (Simplified)

**In-Memory Storage:**
```python
# creature_routes.py
creatures_db: Dict[str, Creature] = {}

# game_routes.py
games_db: Dict[str, GameState] = {}
```

**Future Enhancement:**
```python
class CreatureRepository:
    async def create(creature: Creature) -> Creature
    async def get(id: str) -> Creature
    async def list() -> List[Creature]
    async def update(creature: Creature) -> Creature
```

---

## Combat System

### Damage Calculation Pipeline

```
1. Base Damage
   └─ Random 5-15

2. Strength Modifier
   └─ damage *= (attacker.strength / 10)
      Example: 15 strength → 1.5x multiplier

3. Critical Hit Check
   └─ if random() < attacker.get_crit_chance():
         damage *= 1.5
      Luck 20 → 30% crit chance

4. Dodge Check
   └─ if random() < defender.get_dodge_chance():
         return "MISS"
      Speed 20 → 40% dodge chance

5. Defense Reduction
   └─ if defender defending:
         damage *= 0.3  (70% reduction)
      else:
         damage *= (1 - defender.get_defense_percentage())
      Defense 20 → 50% reduction

6. Apply Damage
   └─ defender.take_damage(max(1, damage))
```

### Special Ability Mechanics

**Enhanced Damage:**
```python
special_multiplier = 1.75
damage = base * strength_modifier * special_multiplier
```

**Modified Chances:**
```python
dodge_chance *= 0.7      # Harder to dodge
crit_chance *= 1.2       # Higher crit rate
defense *= 0.7           # Defense less effective
```

**Resource Cost:**
- 1 use per round
- Resets after round completion

### Turn Order Resolution

```python
# Speed determines who goes first
if creature1.base_stats.speed >= creature2.base_stats.speed:
    first, second = creature1, creature2
else:
    first, second = creature2, creature1

# First creature acts
result1 = execute_move(first, ...)

# Second creature acts (if alive)
if second.is_alive():
    result2 = execute_move(second, ...)
```

---

## AI System

### Difficulty Levels

**Level 1 (Easy):**
```python
# Random stat allocation
- Distribute 6 points randomly
- No strategic focus
```

**Level 2 (Medium):**
```python
# Focus on 2-3 stats
- Select 2-3 random stats
- Distribute points among them
- Some synergy
```

**Level 3 (Hard):**
```python
# Optimized allocation
- 3 points to Strength
- 2 points to Defense or Health
- 1 point to Speed
- Maximizes damage output
```

### Move Selection Algorithm

```python
def decide_move(creature, opponent, round_num):
    weights = []
    
    # Attack (always available)
    weights.append((ATTACK, 10))
    
    # Defend (conditional)
    if creature.defend_uses_remaining > 0:
        weight = 0
        if own_hp < 30%: weight = 15
        elif own_hp < 50%: weight = 8
        elif opponent.strength > 15: weight = 5
        
        if weight > 0:
            weights.append((DEFEND, weight))
    
    # Special (strategic)
    if creature.special_uses_remaining > 0:
        weight = 0
        if opponent_hp < 40%: weight = 20  # Finish them!
        elif round_num == 1: weight = 12   # Early burst
        else: weight = 6
        
        weights.append((SPECIAL, weight))
    
    # Weighted random selection
    return random.choices(weights)
```

---

## Tournament System

### Bracket Structure

```
8-Creature Single Elimination:

Round 1 (4 matches):
    [C1] vs [C2]  →  Winner1
    [C3] vs [C4]  →  Winner2
    [C5] vs [C6]  →  Winner3
    [C7] vs [C8]  →  Winner4

Round 2 (2 matches):
    [Winner1] vs [Winner2]  →  Finalist1
    [Winner3] vs [Winner4]  →  Finalist2

Round 3 (1 match):
    [Finalist1] vs [Finalist2]  →  Champion
```

### Match Progression

```python
class TournamentManager:
    @staticmethod
    def advance_tournament(bracket):
        # 1. Check current round complete
        # 2. Collect winners
        # 3. Heal winners (HP + resources)
        # 4. Create next round matches
        # 5. Update bracket state
        
        if len(winners) == 1:
            return False  # Tournament complete
        
        return True  # Tournament continues
```

### State Persistence

```python
GameState:
    game_id: str
    player_creatures: List[Creature]
    tournament: TournamentBracket
        current_round: int
        matches: List[Match]
            match_id: str
            creature1, creature2: Creature
            pending_moves: Dict
            is_complete: bool
            winner_id: str
```

---

## Error Handling

### Backend Error Strategy

```python
# Validation Errors (400)
- Pydantic model validation
- Stat allocation limits
- Invalid move types

# Not Found (404)
- Creature ID doesn't exist
- Game ID doesn't exist

# Rate Limit (429)
- Middleware rejection

# Server Errors (500)
- Unhandled exceptions
- FastAPI automatic logging
```

### Frontend Error Handling

```javascript
async function apiCall(url, options) {
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        alert(`Error: ${error.message}`);
        throw error;
    }
}
```

---

## Performance Considerations

### Current Limitations

**In-Memory Storage:**
- Data lost on server restart
- No persistence
- Single-server only

**No Caching:**
- Creature types fetched every time
- No response caching

**Synchronous Combat:**
- Blocking move execution
- No parallelization

### Future Optimizations

1. **Database Integration:**
   - PostgreSQL for relational data
   - Redis for session state
   
2. **Caching Layer:**
   - Cache creature types
   - Cache game states
   
3. **WebSocket Support:**
   - Real-time battle updates
   - Live opponent moves
   
4. **Horizontal Scaling:**
   - Stateless API design
   - External session storage

---

## Security Considerations

### Current Implementation

**Rate Limiting:**
- 60 requests/minute per IP
- Basic DoS protection

**Input Validation:**
- Pydantic model validation
- Stat range checks
- String length limits

### Production Requirements

1. **Authentication:**
   - JWT tokens
   - User accounts
   - Session management

2. **Authorization:**
   - Creature ownership verification
   - Game access control

3. **HTTPS:**
   - SSL/TLS encryption
   - Secure cookie flags

4. **Input Sanitization:**
   - SQL injection prevention (when DB added)
   - XSS protection
   - CSRF tokens

5. **CORS Configuration:**
   - Specific origin whitelist
   - Credential handling

---

## Testing Strategy

### Current Tests

```python
# test_models.py
- Creature creation
- Stat allocation validation
- Damage mechanics
- Knockout detection
```

### Recommended Test Coverage

**Unit Tests:**
```python
# Combat System
- Damage calculations
- Crit/dodge/defense mechanics
- Turn order determination
- Move resource tracking

# AI System
- Stat allocation by difficulty
- Move decision logic
- Creature generation

# Tournament System
- Bracket creation
- Match progression
- Winner advancement
```

**Integration Tests:**
```python
# API Endpoints
- Creature CRUD operations
- Game flow (start → moves → completion)
- Stat allocation

# Full Game Flow
- Create creature → tournament → victory
- Error handling paths
```

**Load Tests:**
```python
# Rate limiting
# Concurrent game sessions
# Battle execution performance
```

---

## Deployment Guide

### Development

```bash
# Run with auto-reload
python -m src

# Uvicorn directly
uvicorn src.backend.app:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
# With Gunicorn + Uvicorn workers
gunicorn src.backend.app:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000

# Docker
docker build -t pet-battler .
docker run -p 8000:8000 pet-battler
```

### Environment Variables

```bash
# Future configuration
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
CORS_ORIGINS=https://petbattler.com
RATE_LIMIT=60
```

---

## Future Architecture Enhancements

### 1. Microservices Architecture

```
┌──────────────┐
│   Frontend   │
└──────┬───────┘
       │
┌──────▼───────┐
│  API Gateway │
└──────┬───────┘
       │
       ├────► Creature Service (CRUD)
       ├────► Battle Service (Combat)
       ├────► Tournament Service (Bracket)
       └────► User Service (Auth)
```

### 2. Event-Driven Architecture

```python
# Event Bus
- CreatureCreated
- MatchStarted
- MoveSubmitted
- MatchCompleted
- TournamentFinished

# Subscribers
- Notification Service
- Statistics Service
- Leaderboard Service
```

### 3. Real-Time Updates

```
WebSocket Connections:
- Live battle updates
- Opponent move notifications
- Tournament bracket changes
```

---

This architecture provides a solid foundation for the Pet Battler game with clear separation of concerns, extensibility, and maintainability.
