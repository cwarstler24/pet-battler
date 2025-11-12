"""
API routes for creature management.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from ..models.creature import Creature, CreatureType, CREATURE_STAT_BIASES

router = APIRouter(prefix="/creatures", tags=["creatures"])


class CreateCreatureRequest(BaseModel):
    """Request model for creating a new creature."""
    name: str = Field(min_length=1, max_length=50)
    creature_type: CreatureType
    stat_allocations: Optional[Dict[str, int]] = None


class CreatureResponse(BaseModel):
    """Response model for creature data."""
    id: str
    name: str
    creature_type: CreatureType
    stats: Dict[str, int]
    current_hp: int
    max_hp: int
    defend_uses: int
    special_uses: int


class CreatureTypeInfo(BaseModel):
    """Information about a creature type."""
    type: CreatureType
    stat_biases: Dict[str, int]
    description: str


# In-memory storage (replace with database in production)
creatures_db: Dict[str, Creature] = {}


@router.get("/types", response_model=List[CreatureTypeInfo])
async def get_creature_types():
    """Get all available creature types with their stat biases."""
    
    descriptions = {
        CreatureType.DRAGON: "High health and strength, but slower. Breathes fire!",
        CreatureType.OWLBEAR: "Strong and defensive, balanced fighter.",
        CreatureType.GNOME: "Lucky and fast, but physically weak.",
        CreatureType.KRAKEN: "High health and strength, controls the seas.",
        CreatureType.CTHULU: "Extremely lucky with cosmic powers.",
        CreatureType.MINOTAUR: "Pure strength, charges into battle.",
        CreatureType.CERBERUS: "Fast with good defense, triple threat.",
        CreatureType.MEDUSA: "Lucky with stone gaze, moderate stats.",
        CreatureType.ROBOT: "Heavily armored but predictable.",
        CreatureType.PYTHON: "Fast and lucky, constricts enemies.",
        CreatureType.JACOB: "Mysterious and balanced.",
        CreatureType.BEYBLADE: "Extremely fast but fragile, let it rip!",
    }
    
    return [
        CreatureTypeInfo(
            type=creature_type,
            stat_biases=CREATURE_STAT_BIASES.get(creature_type, {}),
            description=descriptions.get(creature_type, "A mysterious creature.")
        )
        for creature_type in CreatureType
    ]


@router.post("", response_model=CreatureResponse, status_code=201)
async def create_creature(request: CreateCreatureRequest):
    """Create a new creature with custom stats."""
    
    try:
        # Validate stat allocations
        if request.stat_allocations:
            total_points = sum(request.stat_allocations.values())
            if total_points > 6:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot allocate more than 6 stat points (you used {total_points})"
                )
        
        # Create creature
        creature = Creature.create_with_biases(
            name=request.name,
            creature_type=request.creature_type,
            stat_allocations=request.stat_allocations,
            is_ai=False
        )
        
        # Generate ID and store
        import uuid
        creature.id = str(uuid.uuid4())
        creatures_db[creature.id] = creature
        
        return CreatureResponse(
            id=creature.id,
            name=creature.name,
            creature_type=creature.creature_type,
            stats={
                "speed": creature.base_stats.speed,
                "health": creature.base_stats.health,
                "defense": creature.base_stats.defense,
                "strength": creature.base_stats.strength,
                "luck": creature.base_stats.luck,
            },
            current_hp=creature.current_hp,
            max_hp=creature.max_hp,
            defend_uses=creature.defend_uses_remaining,
            special_uses=creature.special_uses_remaining,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{creature_id}", response_model=CreatureResponse)
async def get_creature(creature_id: str):
    """Get a specific creature by ID."""
    
    if creature_id not in creatures_db:
        raise HTTPException(status_code=404, detail="Creature not found")
    
    creature = creatures_db[creature_id]
    
    return CreatureResponse(
        id=creature.id,
        name=creature.name,
        creature_type=creature.creature_type,
        stats={
            "speed": creature.base_stats.speed,
            "health": creature.base_stats.health,
            "defense": creature.base_stats.defense,
            "strength": creature.base_stats.strength,
            "luck": creature.base_stats.luck,
        },
        current_hp=creature.current_hp,
        max_hp=creature.max_hp,
        defend_uses=creature.defend_uses_remaining,
        special_uses=creature.special_uses_remaining,
    )


@router.get("", response_model=List[CreatureResponse])
async def list_creatures():
    """List all created creatures."""
    
    return [
        CreatureResponse(
            id=creature.id,
            name=creature.name,
            creature_type=creature.creature_type,
            stats={
                "speed": creature.base_stats.speed,
                "health": creature.base_stats.health,
                "defense": creature.base_stats.defense,
                "strength": creature.base_stats.strength,
                "luck": creature.base_stats.luck,
            },
            current_hp=creature.current_hp,
            max_hp=creature.max_hp,
            defend_uses=creature.defend_uses_remaining,
            special_uses=creature.special_uses_remaining,
        )
        for creature in creatures_db.values()
    ]
