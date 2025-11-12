# Virtual Pet Battler Tournament Game

## ✅ **Core Game Loop**

*   **User Authentication**
    *   JWT-based login
    *   Basic profile management
*   **Pet Creation**
    *   Choose pet type (dog, cat, dragon, etc.)
    *   Assign base stats: `strength`, `agility`, `intelligence`
*   **Training Phase**
    *   Limited moves (e.g., 10 per round)
    *   Each move increases a stat
    *   Timer countdown (e.g., 5 minutes per round)
*   **Tournament Phase**
    *   After timer ends, pets enter a **bracket-style tournament**
    *   Randomized opponents from other players or AI-generated pets
    *   Battles calculated based on stats + randomness
    *   *Optional:* LLM generates battle commentary or strategy tips
*   **Leaderboard**
    *   Track wins/losses and tournament rankings

***

## ✅ **Architecture**

*   **Backend:** FastAPI (REST API)
*   **Frontend:** Start with minimal HTML or CLI → Expand to React
*   **State Management:** In-memory (Python dictionaries/classes)
*   **Testing:** `pytest` for game logic and API endpoints
*   **Security:** JWT auth, input validation, rate limiting
*   **Optional LLM:** Commentary & strategy suggestions via OpenAI API

***

## ✅ **Data Models**

```python
class User(BaseModel):
    id: int
    username: str
    hashed_password: str

class Pet(BaseModel):
    id: int
    owner_id: int
    name: str
    type: str
    strength: int
    agility: int
    intelligence: int
    level: int
    moves_left: int

class Tournament(BaseModel):
    id: int
    pets: List[int]  # Pet IDs
    bracket: Dict[str, List[int]]  # Round structure
    winner_id: int
```

***

## ✅ **Key Endpoints**

*   `POST /join` → Create user session
*   `POST /pet` → Create pet
*   `PUT /train` → Train pet (validate moves)
*   `POST /tournament/start` → Start tournament
*   `GET /tournament/{id}` → View bracket & results
*   `GET /leaderboard` → Rankings
*   `GET /status` → Show user’s pets and moves left

***

## ✅ **Tournament Logic**

*   **Bracket Generation:** Randomize pet matchups
*   **Battle Calculation:** Weighted by stats + randomness  
    Formula example:
        score = strength * 1.5 + agility * 1.2 + intelligence * 1.0 + random_factor
*   **Rounds:** Continue until one winner remains
*   *Optional:* LLM generates dynamic battle narration

***

## ✅ **Example In-Memory Data Structures**

```python
users = {
    "alice": {
        "moves_left": 10,
        "pets": [
            {"name": "Fluffy", "strength": 5, "agility": 3, "intelligence": 2}
        ]
    }
}

battle_results = []
```

***

## ✅ **Next Steps**

Do you want me to:

1.  **Write a full FastAPI skeleton** with these endpoints and in-memory logic?
2.  **Add the battle algorithm and training mechanics in detail?**
3.  **Include optional LLM integration for commentary?**
4.  Or start with a **minimal MVP code snippet for the core game loop**?

***

👉 Which one should I start with?
