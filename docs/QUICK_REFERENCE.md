# 📖 Pet Battler - Quick Reference

Quick reference for common information and formulas.

## Quick Links

- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **GitHub**: [Repository URL]

---

## Stat Formulas

### Dodge Chance
```
dodge_chance = (Speed / 20) × 0.4

Examples:
Speed 10 → 20% dodge
Speed 20 → 40% dodge
```

### Defense Reduction
```
defense_reduction = (Defense / 20) × 0.5

Examples:
Defense 10 → 25% damage reduction
Defense 20 → 50% damage reduction
```

### Critical Hit Chance
```
crit_chance = (Luck / 20) × 0.3

Examples:
Luck 10 → 15% crit
Luck 20 → 30% crit

Special Ability: crit_chance × 1.2
```

### Strength Multiplier
```
damage_multiplier = Strength / 10

Examples:
Strength 10 → 1.0x damage
Strength 15 → 1.5x damage
Strength 20 → 2.0x damage
```

---

## Damage Calculation

### Normal Attack
```
1. base = random(5, 15)
2. damage = base × (Strength / 10)
3. if crit: damage × 1.5
4. if dodge: return 0
5. if defending: damage × 0.3
   else: damage × (1 - Defense%)
6. return max(1, damage)
```

### Special Ability
```
1. base = random(5, 15)
2. damage = base × (Strength / 10) × 1.75
3. if crit (Luck × 1.2): damage × 1.5
4. if dodge (Speed × 0.7): return 0
5. if defending: damage × 0.5
   else: damage × (1 - Defense% × 0.7)
6. return max(2, damage)
```

### Defend Move
```
Effect: Take 30% damage (70% reduction)
Uses: 3 per round
Stacks with Defense stat for massive mitigation
```

---

## Creature Type Quick Stats

| Type | Speed | Health | Defense | Strength | Luck | Build |
|------|-------|--------|---------|----------|------|-------|
| 🐉 Dragon | 7 | **15** | 10 | **12** | 10 | Tank/Bruiser |
| 🦉 Owlbear | 8 | 10 | **13** | **13** | 10 | Balanced |
| 🧙 Gnome | **13** | 10 | 10 | 7 | **14** | Dodge/Crit |
| 🐙 Kraken | 8 | **14** | 10 | **13** | 10 | Tank/Damage |
| 👾 Cthulu | 7 | 10 | **12** | 10 | **15** | Crit Machine |
| 🐂 Minotaur | 10 | **12** | 10 | **15** | 7 | Glass Cannon |
| 🐕 Cerberus | **14** | 10 | **12** | 10 | 9 | Speed/Defense |
| 🐍 Medusa | 10 | 10 | **12** | 8 | **14** | Crit/Defense |
| 🤖 Robot | 10 | **12** | **15** | 10 | 7 | Fortress |
| 🐍 Python | **14** | 10 | 8 | 10 | **13** | Speed/Crit |
| 👤 Jacob | **12** | **12** | 12 | **12** | 12 | Balanced |
| 🌪️ Beyblade | **16** | 10 | 6 | **12** | 10 | Speed Demon |

**Bold** = Above average (12+)

---

## API Endpoints Cheat Sheet

### Creatures
```http
GET    /creatures/types          # List creature types
POST   /creatures                # Create creature
GET    /creatures/{id}           # Get creature
GET    /creatures                # List all
```

### Game
```http
POST   /game/start               # Start tournament
POST   /game/{id}/move           # Submit move
GET    /game/{id}/state          # Get state
POST   /game/{id}/allocate-stats # Level up
```

### System
```http
GET    /health                   # Health check
GET    /docs                     # API docs
```

---

## Request Examples

### Create Creature
```bash
curl -X POST http://localhost:8000/creatures \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Flamezord",
    "creature_type": "dragon",
    "stat_allocations": {
      "strength": 3,
      "health": 3
    }
  }'
```

### Start Game
```bash
curl -X POST http://localhost:8000/game/start \
  -H "Content-Type: application/json" \
  -d '{
    "num_players": 1,
    "creature_ids": ["<creature-uuid>"],
    "tournament_size": 8
  }'
```

### Submit Move
```bash
curl -X POST http://localhost:8000/game/<game-id>/move \
  -H "Content-Type: application/json" \
  -d '{
    "creature_id": "<creature-uuid>",
    "move_type": "attack"
  }'
```

---

## Common Error Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| 400 | Bad Request | Invalid stat allocation, wrong move type |
| 404 | Not Found | Creature/Game ID doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded (60/min) |
| 500 | Server Error | Backend bug, check logs |

---

## File Locations

### Backend
```
src/backend/
├── app.py                  # Main application
├── models/
│   ├── creature.py        # Creature types & stats
│   ├── move.py            # Move types
│   └── game_state.py      # Game state
├── logic/
│   ├── combat.py          # Damage calculations
│   ├── ai_opponent.py     # AI decisions
│   └── tournament.py      # Bracket management
├── routes/
│   ├── creature_routes.py # Creature API
│   └── game_routes.py     # Game API
└── middleware/
    └── rate_limit.py      # Rate limiting
```

### Frontend
```
src/frontend/
├── index.html             # Main HTML
└── static/
    ├── css/
    │   └── styles.css     # All styling
    └── js/
        └── app.js         # Game logic
```

---

## Environment Variables (Future)

```bash
# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@localhost/petbattler

# Security
SECRET_KEY=your-secret-key
CORS_ORIGINS=https://yourdomain.com

# Features
RATE_LIMIT=60
TOURNAMENT_SIZES=4,8,16
```

---

## Dependencies

### Required
```
fastapi==0.121.0           # Web framework
uvicorn[standard]==0.32.0  # ASGI server
pydantic==2.9.2            # Data validation
```

### Development
```
pytest==8.3.3              # Testing
httpx==0.27.2              # HTTP client for tests
```

### Optional (Future)
```
sqlalchemy                 # Database ORM
redis                      # Caching
websockets                 # Real-time updates
```

---

## Troubleshooting Quick Fixes

### Server won't start
```bash
# Check port 8000 is free
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend blank
```bash
# Check server is running
curl http://localhost:8000/health

# Check browser console (F12)
```

### Tests failing
```bash
# Clear cache
pytest --cache-clear

# Reinstall
pip install -e .
```

---

## Resources

### Documentation
- README.md - Project overview
- API.md - Complete API reference
- ARCHITECTURE.md - System design
- GAME_MECHANICS.md - Combat formulas
- DEVELOPMENT.md - Dev guide

## License

This project is available for educational purposes.

---

**Last Updated:** 2025-11-13
