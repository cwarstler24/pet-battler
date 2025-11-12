# Pet Battler - Project Outline & Task Distribution

## Project Overview
A turn-based creature battle game with tournament-style gameplay, player customization, and AI opponents.

---

## 1. Data Models & Core Classes

### Task 1.1: Creature/Player Model
**Owner:** _[Assign]_
- [ ] Define `Creature` class with attributes:
  - Base stats (Speed, Health, Defense, Strength, Luck) - range 1-20
  - Creature type (Dragon, Owlbear, Gnome, Kraken, etc.)
  - Current HP vs Max HP
  - Name (custom player input)
  - Stat biases per creature type
- [ ] Implement stat point allocation system (6 points max)
- [ ] Create creature type configurations with stat biases
  - Dragon: +Health, -Speed
  - Owlbear, Gnome, Kraken, Cthulu, Minotaur, Cerberus, Medusa, Robot, Python-python, Jacob, Beyblade

### Task 1.2: Move/Action System
**Owner:** _[Assign]_
- [ ] Define `Move` base class/interface
- [ ] Implement move types:
  - `Attack` - standard damage based on Strength
  - `Defend` - damage reduction (3 uses per round max)
  - `SpecialAbility` - unique per creature type (1 use per round max)
- [ ] Track move usage counters per round

### Task 1.3: Game State Management
**Owner:** _[Assign]_
- [ ] Define `GameState` class:
  - Tournament bracket structure
  - Current round/match
  - Player creatures
  - AI-generated creatures
  - Match history
- [ ] Implement tournament bracket generator
- [ ] Track player progress through tournament

---

## 2. Game Logic (Backend Core)

### Task 2.1: Combat System
**Owner:** _[Assign]_
- [ ] Implement damage calculation:
  - Base damage from attacker's Strength
  - Apply defender's Defense percentage
  - Apply defender's Speed for dodge chance
  - Calculate critical hits using Luck stat (1.5x multiplier)
- [ ] Implement move execution logic
- [ ] Handle turn resolution (both players select, then execute)

### Task 2.2: AI Opponent Generator
**Owner:** _[Assign]_
- [ ] Create random creature generator for AI opponents
- [ ] Implement AI move selection algorithm
- [ ] Balance AI difficulty/randomness

### Task 2.3: Match & Round Logic
**Owner:** _[Assign]_
- [ ] Implement round system
- [ ] Track HP changes during battle
- [ ] Determine match winner (HP reaches 0)
- [ ] Advance winner to next bracket position
- [ ] Reset round-specific resources (defend/special uses)

---

## 3. Backend API (FastAPI/Flask)

### Task 3.1: API Setup & Configuration
**Owner:** _[Assign]_
- [ ] Set up FastAPI/Flask project structure
- [ ] Configure CORS if needed
- [ ] Set up basic error handling
- [ ] Add rate limiting middleware

### Task 3.2: Creature Management Endpoints
**Owner:** _[Assign]_
- [ ] `POST /creatures` - Create new creature
  - Accept: creature type, name, stat allocations
  - Validate: stat point limits, valid creature type
  - Return: created creature with final stats
- [ ] `GET /creatures` - Get available creature types
  - Return: list of creature types with base stat biases
- [ ] `GET /creatures/{id}` - Get specific creature details

### Task 3.3: Game Flow Endpoints
**Owner:** _[Assign]_
- [ ] `POST /game/start` - Initialize new game
  - Accept: number of players (1-2), player creatures
  - Return: tournament bracket, game ID
- [ ] `POST /game/{game_id}/move` - Submit player move
  - Accept: player ID, move type
  - Return: current game state or match result
- [ ] `GET /game/{game_id}/state` - Get current game state

### Task 3.4: Input Validation & Security
**Owner:** _[Assign]_
- [ ] Validate all user inputs (stat ranges, move types, etc.)
- [ ] Implement rate limiting per endpoint
- [ ] Sanitize text inputs (creature names)
- [ ] Add request size limits

---

## 4. Frontend (HTML/CLI Interface)

### Task 4.1: Game Setup Interface
**Owner:** _[Assign]_
- [ ] Player count selection (1-2 players)
- [ ] Creature selection screen
  - Display available creatures with stat biases
- [ ] Creature naming input
- [ ] Stat allocation interface (6 points to distribute)

### Task 4.2: Battle Display
**Owner:** _[Assign]_
- [ ] Display current match state:
  - Player creature stats (HP, current stats)
  - Opponent creature stats
  - Current round number
- [ ] Show available moves with usage counts
- [ ] Display tournament bracket progress

### Task 4.3: ASCII Animations
**Owner:** _[Assign]_
- [ ] Create ASCII art for each creature type (12 total)
- [ ] Implement simple animations for:
  - Attack actions
  - Defend actions
  - Special ability actions
  - Damage taken / HP changes
- [ ] Victory/defeat animations

### Task 4.4: User Input & Controls
**Owner:** _[Assign]_
- [ ] Implement move selection interface
- [ ] Add confirmation prompts
- [ ] Handle invalid input gracefully
- [ ] Create navigation between screens

---

## 5. Integration & Testing

### Task 5.1: API Integration
**Owner:** _[Assign]_
- [ ] Connect frontend to backend endpoints
- [ ] Handle API errors and timeouts
- [ ] Implement loading states

### Task 5.2: Game Flow Testing
**Owner:** _[Assign]_
- [ ] Test full game loop (setup → battles → tournament completion)
- [ ] Test edge cases:
  - Equal HP creatures
  - Max stat allocations
  - Resource limits (defend/special uses)
- [ ] Test 1-player and 2-player modes

### Task 5.3: Balance Testing
**Owner:** _[Assign]_
- [ ] Test creature type balance
- [ ] Verify stat calculations
- [ ] Adjust AI difficulty if needed

---

## 6. Documentation & AI Process

### Task 6.1: Technical Documentation
**Owner:** _[Assign]_
- [ ] Document API endpoints (OpenAPI/Swagger)
- [ ] Create setup/installation guide
- [ ] Document game mechanics and formulas

### Task 6.2: AI Usage Documentation
**Owner:** _[Assign]_
- [ ] Document how AI tools were used throughout development:
  - Code generation
  - Debugging assistance
  - Design decisions
  - Testing strategies
- [ ] Record prompts and outcomes
- [ ] Reflect on AI effectiveness in different tasks

---

## Creature Types Reference

| Creature | Stat Bias | Special Ability Ideas |
|----------|-----------|----------------------|
| Dragon | +Health, -Speed | Fire Breath |
| Owlbear | +Strength, +Defense | Bear Hug |
| Gnome | +Luck, +Speed | Illusion |
| Kraken | +Health, +Strength | Tentacle Slam |
| Cthulu | +Luck, -Speed | Madness |
| Minotaur | +Strength, -Luck | Charge |
| Cerberus | +Speed, +Defense | Triple Bite |
| Medusa | +Luck, -Strength | Stone Gaze |
| Robot | +Defense, -Luck | Laser Beam |
| Python-python | +Speed, +Luck | Constrict |
| Jacob | TBD | TBD |
| Beyblade | +Speed, -Defense | Let It Rip! |

---

## Dependencies & Setup

### Backend Requirements
- FastAPI or Flask
- Pydantic (for data validation)
- uvicorn (if using FastAPI)
- Rate limiting library (slowapi, flask-limiter)

### Frontend Requirements
- Basic HTML/CSS/JavaScript
- Fetch API for backend communication
- Optional: Simple CLI library for enhanced display

---

## Timeline Suggestions

1. **Week 1**: Data models, core game logic, API setup
2. **Week 2**: Combat system, AI generation, basic endpoints
3. **Week 3**: Frontend interfaces, ASCII art, integration
4. **Week 4**: Testing, balance adjustments, documentation

---

## Notes
- Focus on getting a minimal working version first (1-2 creatures, basic moves)
- Iterate and add complexity (more creatures, special abilities)
- Keep AI usage documentation updated throughout process
- Regular team sync-ups to ensure components integrate smoothly
