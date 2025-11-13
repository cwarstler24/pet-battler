"""
Move/Action models for battle system.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel

class MoveType(str, Enum):
    """Types of moves available in battle."""
    ATTACK = "attack"
    DEFEND = "defend"
    SPECIAL = "special"

class Move(BaseModel):
    """Base move/action in battle."""
    move_type: MoveType
    user_id: str  # ID of the creature using the move
    target_id: Optional[str] = None  # ID of the target creature (if applicable)

class AttackMove(Move):
    """Standard attack move."""
    move_type: MoveType = MoveType.ATTACK

    def __init__(self, **data):
        super().__init__(move_type=MoveType.ATTACK, **data)

class DefendMove(Move):
    """Defensive move that reduces incoming damage (3 uses per round)."""
    move_type: MoveType = MoveType.DEFEND

    def __init__(self, **data):
        super().__init__(move_type=MoveType.DEFEND, **data)

class SpecialMove(Move):
    """Special ability unique to each creature type (1 use per round)."""
    move_type: MoveType = MoveType.SPECIAL

    def __init__(self, **data):
        super().__init__(move_type=MoveType.SPECIAL, **data)

class MoveResult(BaseModel):
    """Result of executing a move."""
    move: Move
    success: bool
    damage_dealt: int = 0
    was_critical: bool = False
    was_dodged: bool = False
    was_defended: bool = False
    message: str
