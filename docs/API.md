# 📡 Pet Battler API Documentation

Complete API reference for the Pet Battler backend.

## Base Configuration

- **Base URL**: `http://localhost:8000`
- **Rate Limit**: 60 requests per minute per IP
- **Content-Type**: `application/json`
- **CORS**: Enabled for all origins (configure for production)

## Authentication

Currently no authentication required. In production, consider implementing:
- JWT tokens
- API keys
- OAuth2

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200 OK` - Successful GET request
- `201 Created` - Successful POST creating new resource
- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Endpoints Reference

### Health Check

#### GET /health

Check if the API is running.

**Response** `200 OK`
```json
{
  "status": "healthy",
  "service": "pet-battler-api"
}
```

---

## Creature Endpoints

### Get Creature Types

#### GET /creatures/types

Retrieve all available creature types with their stat biases and descriptions.

**Response** `200 OK`
```json
[
  {
    "type": "dragon",
    "stat_biases": {
      "health": 5,
      "speed": -3,
      "strength": 2
    },
    "description": "High health and strength, but slower. Breathes fire!"
  },
  {
    "type": "gnome",
    "stat_biases": {
      "luck": 4,
      "speed": 3,
      "strength": -3
    },
    "description": "Lucky and fast, but physically weak."
  }
]
```

**Creature Types Available**:
- dragon, owlbear, gnome, kraken, cthulu, minotaur
- cerberus, medusa, robot, python-python, jacob, beyblade

---

### Create Creature

#### POST /creatures

Create a new creature with custom name and stat allocations.

**Request Body**
```json
{
  "name": "Flamezord",
  "creature_type": "dragon",
  "stat_allocations": {
    "strength": 3,
    "health": 2,
    "speed": 1
  }
}
```

**Parameters**:
- `name` (string, required): 1-50 characters
- `creature_type` (string, required): One of the available creature types
- `stat_allocations` (object, optional): Stat point distribution
  - Total points cannot exceed 6
  - Valid stats: speed, health, defense, strength, luck
  - Each stat allocation must be non-negative

**Response** `201 Created`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Flamezord",
  "creature_type": "dragon",
  "stats": {
    "speed": 8,
    "health": 17,
    "defense": 10,
    "strength": 15,
    "luck": 10
  },
  "current_hp": 17,
  "max_hp": 17,
  "defend_uses": 3,
  "special_uses": 1
}
```

**Errors**:
- `400 Bad Request` - Stat allocations exceed 6 points
- `400 Bad Request` - Invalid creature type
- `400 Bad Request` - Invalid stat name

---

### Get Creature by ID

#### GET /creatures/{creature_id}

Retrieve details of a specific creature.

**Path Parameters**:
- `creature_id` (string, required): UUID of the creature

**Response** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Flamezord",
  "creature_type": "dragon",
  "stats": {
    "speed": 8,
    "health": 17,
    "defense": 10,
    "strength": 15,
    "luck": 10
  },
  "current_hp": 17,
  "max_hp": 17,
  "defend_uses": 3,
  "special_uses": 1
}
```

**Errors**:
- `404 Not Found` - Creature ID does not exist

---

### List All Creatures

#### GET /creatures

Get all created creatures.

**Response** `200 OK`
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Flamezord",
    "creature_type": "dragon",
    "stats": { ... },
    "current_hp": 17,
    "max_hp": 17,
    "defend_uses": 3,
    "special_uses": 1
  }
]
```

---

## Game Endpoints

### Start New Game

#### POST /game/start

Initialize a new tournament game.

**Request Body**
```json
{
  "num_players": 1,
  "creature_ids": ["550e8400-e29b-41d4-a716-446655440000"],
  "tournament_size": 8
}
```

**Parameters**:
- `num_players` (integer, required): 1 or 2
- `creature_ids` (array, required): Array of creature UUIDs
- `tournament_size` (integer, required): 4, 8, or 16

**Response** `200 OK`
```json
{
  "game_id": "123e4567-e89b-12d3-a456-426614174000",
  "current_match": {
    "match_id": "match-uuid",
    "creature1_id": "creature-1-uuid",
    "creature1_name": "Flamezord",
    "creature1_type": "dragon",
    "creature1_hp": 17,
    "creature1_max_hp": 17,
    "creature2_id": "creature-2-uuid",
    "creature2_name": "Bolt777",
    "creature2_type": "robot",
    "creature2_hp": 12,
    "creature2_max_hp": 12,
    "current_round": 0,
    "is_complete": false
  },
  "tournament_complete": false
}
```

**Errors**:
- `404 Not Found` - Creature ID not found
- `400 Bad Request` - Invalid tournament size
- `400 Bad Request` - Too many player creatures for tournament size

---

### Submit Move

#### POST /game/{game_id}/move

Submit a move for a creature in the current match.

**Path Parameters**:
- `game_id` (string, required): UUID of the game

**Request Body**
```json
{
  "creature_id": "550e8400-e29b-41d4-a716-446655440000",
  "move_type": "attack"
}
```

**Parameters**:
- `creature_id` (string, required): UUID of creature making the move
- `move_type` (string, required): "attack", "defend", or "special"

**Response** `200 OK`

*If move is pending (waiting for opponent)*:
```json
{
  "game_id": "game-uuid",
  "current_match": {
    "match_id": "match-uuid",
    "creature1_id": "creature-1-uuid",
    "creature1_name": "Flamezord",
    "creature1_hp": 17,
    "creature1_max_hp": 17,
    "creature2_id": "creature-2-uuid",
    "creature2_name": "Bolt777",
    "creature2_hp": 12,
    "creature2_max_hp": 12,
    "current_round": 1,
    "is_complete": false,
    "latest_results": []
  },
  "tournament_complete": false,
  "player_won_match": false,
  "stat_points_available": 0,
  "match_just_completed": false
}
```

*If both moves submitted (round executed)*:
```json
{
  "game_id": "game-uuid",
  "current_match": {
    "match_id": "match-uuid",
    "creature1_id": "creature-1-uuid",
    "creature1_name": "Flamezord",
    "creature1_hp": 14,
    "creature1_max_hp": 17,
    "creature2_id": "creature-2-uuid",
    "creature2_name": "Bolt777",
    "creature2_hp": 3,
    "creature2_max_hp": 12,
    "current_round": 2,
    "is_complete": false,
    "latest_results": [
      "Flamezord attacks Bolt777 for 8 damage!",
      "Bolt777 attacks Flamezord for 3 damage!"
    ]
  },
  "tournament_complete": false,
  "player_won_match": false,
  "stat_points_available": 0,
  "match_just_completed": false
}
```

*If match completed*:
```json
{
  "game_id": "game-uuid",
  "current_match": {
    "match_id": "match-uuid",
    "creature1_id": "creature-1-uuid",
    "creature1_name": "Flamezord",
    "creature1_hp": 14,
    "creature1_max_hp": 17,
    "creature2_id": "creature-2-uuid",
    "creature2_name": "Bolt777",
    "creature2_hp": 0,
    "creature2_max_hp": 12,
    "current_round": 3,
    "is_complete": true,
    "winner_name": "Flamezord",
    "latest_results": [
      "Flamezord uses special ability on Bolt777 for 9 damage!",
      "Bolt777 was defeated before acting!",
      "Flamezord wins the match!"
    ]
  },
  "tournament_complete": false,
  "player_won_match": true,
  "stat_points_available": 3,
  "match_just_completed": true,
  "current_stats": {
    "speed": 8,
    "health": 17,
    "defense": 10,
    "strength": 15,
    "luck": 10
  }
}
```

**Errors**:
- `404 Not Found` - Game ID not found
- `400 Bad Request` - No active match
- `400 Bad Request` - Match already complete
- `400 Bad Request` - Creature not in current match
- `400 Bad Request` - Invalid move type

**Notes**:
- If opponent is AI, their move is automatically submitted
- Combat executes when both moves are received
- Turn order determined by Speed stat
- Match ends when a creature reaches 0 HP

---

### Get Game State

#### GET /game/{game_id}/state

Retrieve current state of an active game.

**Path Parameters**:
- `game_id` (string, required): UUID of the game

**Response** `200 OK`
```json
{
  "game_id": "game-uuid",
  "current_match": {
    "match_id": "match-uuid",
    "creature1_id": "creature-1-uuid",
    "creature1_name": "Flamezord",
    "creature1_type": "dragon",
    "creature1_hp": 14,
    "creature1_max_hp": 17,
    "creature2_id": "creature-2-uuid",
    "creature2_name": "Bolt777",
    "creature2_type": "robot",
    "creature2_hp": 8,
    "creature2_max_hp": 12,
    "current_round": 2,
    "is_complete": false,
    "winner_name": null
  },
  "tournament_complete": false,
  "champion_name": null
}
```

**Errors**:
- `404 Not Found` - Game ID not found

---

### Allocate Stat Points

#### POST /game/{game_id}/allocate-stats

Allocate earned stat points after winning a match.

**Path Parameters**:
- `game_id` (string, required): UUID of the game

**Request Body**
```json
{
  "creature_id": "550e8400-e29b-41d4-a716-446655440000",
  "stat_allocations": {
    "strength": 2,
    "speed": 1
  }
}
```

**Parameters**:
- `creature_id` (string, required): UUID of creature to upgrade
- `stat_allocations` (object, required): Must total exactly 3 points
  - Valid stats: speed, health, defense, strength, luck
  - All values must be non-negative

**Response** `200 OK`
```json
{
  "success": true,
  "creature_id": "550e8400-e29b-41d4-a716-446655440000",
  "updated_stats": {
    "speed": 9,
    "health": 17,
    "defense": 10,
    "strength": 17,
    "luck": 10
  }
}
```

**Errors**:
- `404 Not Found` - Game or creature not found
- `400 Bad Request` - Not a player's creature
- `400 Bad Request` - Must allocate exactly 3 points
- `400 Bad Request` - Invalid stat name
- `400 Bad Request` - Negative stat allocation

**Notes**:
- Increasing health also increases max HP and current HP
- Only available after winning a match
- Must be done before starting next match
 - Not available after the final championship match (when `tournament_complete` becomes true, this endpoint will return an error if attempted)

---

## Data Models

### Creature Object

```typescript
{
  id: string;                    // UUID
  name: string;                  // 1-50 characters
  creature_type: string;         // Creature type enum
  stats: {
    speed: number;               // 1-20
    health: number;              // 1-20 (also max HP)
    defense: number;             // 1-20
    strength: number;            // 1-20
    luck: number;                // 1-20
  };
  current_hp: number;            // 0 to max_hp
  max_hp: number;                // Equals health stat
  defend_uses: number;           // 0-3 per round
  special_uses: number;          // 0-1 per round
}
```

### Match Object

```typescript
{
  match_id: string;
  creature1_id: string;
  creature1_name: string;
  creature1_type: string;
  creature1_hp: number;
  creature1_max_hp: number;
  creature2_id: string;
  creature2_name: string;
  creature2_type: string;
  creature2_hp: number;
  creature2_max_hp: number;
  current_round: number;
  is_complete: boolean;
  winner_name?: string;          // Present if match complete
  latest_results?: string[];     // Present after move execution
}
```

## Rate Limiting

The API implements per-IP rate limiting:

- **Limit**: 60 requests per minute
- **Window**: Rolling 60-second window
- **Response**: 429 Too Many Requests
- **Headers**: No rate limit headers currently exposed

## CORS Policy

Current CORS configuration:
- **Origins**: All (`*`) - Configure for production
- **Methods**: All
- **Headers**: All
- **Credentials**: Enabled

## Best Practices

### Request Guidelines

1. **Validate Input**: Client-side validation reduces errors
2. **Handle Errors**: Always check response status codes
3. **Respect Rate Limits**: Implement exponential backoff
4. **Use HTTPS**: In production environments
5. **Store IDs**: Save game_id and creature_id for session management

### Example Client Flow

```javascript
// 1. Load creature types
const types = await fetch('/creatures/types').then(r => r.json());

// 2. Create creature
const creature = await fetch('/creatures', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Flamezord',
    creature_type: 'dragon',
    stat_allocations: { strength: 3, health: 3 }
  })
}).then(r => r.json());

// 3. Start game
const game = await fetch('/game/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    num_players: 1,
    creature_ids: [creature.id],
    tournament_size: 8
  })
}).then(r => r.json());

// 4. Submit moves
const result = await fetch(`/game/${game.game_id}/move`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    creature_id: creature.id,
    move_type: 'attack'
  })
}).then(r => r.json());

// 5. Allocate stats after victory
if (result.player_won_match) {
  await fetch(`/game/${game.game_id}/allocate-stats`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      creature_id: creature.id,
      stat_allocations: { strength: 2, speed: 1 }
    })
  }).then(r => r.json());
}
```

## Interactive Documentation

Visit http://localhost:8000/docs for:
- Swagger UI with live API testing
- Request/response examples
- Schema documentation
- Try-it-out functionality
