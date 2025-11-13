"""
Game state models for managing tournament and match state.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from .creature import Creature
from .move import Move, MoveResult


class Match(BaseModel):
    """Represents a single battle match between two creatures."""
    match_id: str
    creature1: Creature
    creature2: Creature
    current_round: int = 0
    pending_moves: Dict[str, Move] = Field(default_factory=dict)  # creature_id -> move
    move_history: List[MoveResult] = Field(default_factory=list)
    winner_id: Optional[str] = None
    is_complete: bool = False
    
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True

    def add_move(self, creature_id: str, move: Move):
        """Add a pending move for a creature."""
        self.pending_moves[creature_id] = move

    def both_moves_submitted(self) -> bool:
        """Check if both creatures have submitted moves."""
        return len(self.pending_moves) == 2

    def clear_pending_moves(self):
        """Clear pending moves after execution."""
        self.pending_moves.clear()

    def set_winner(self, creature_id: str):
        """Set the match winner."""
        self.winner_id = creature_id
        self.is_complete = True


class TournamentBracket(BaseModel):
    """Manages the tournament bracket structure."""
    bracket_id: str
    total_rounds: int
    current_round: int = 0
    matches: List[Match] = Field(default_factory=list)
    
    def get_current_match(self) -> Optional[Match]:
        """Get the current active match."""
        for match in self.matches:
            if not match.is_complete:
                return match
        return None

    def advance_bracket(self):
        """Advance to the next round/match in the bracket."""
        current = self.get_current_match()
        if current and current.is_complete:
            self.current_round += 1


class GameState(BaseModel):
    """Overall game state tracking."""
    game_id: str
    num_players: int = Field(ge=1, le=2)
    player_creatures: List[Creature] = Field(default_factory=list)
    tournament: Optional[TournamentBracket] = None
    created_at: datetime = Field(default_factory=datetime.now)
    is_complete: bool = False
    champion_id: Optional[str] = None

    def get_current_match(self) -> Optional[Match]:
        """Get the current active match."""
        if self.tournament:
            return self.tournament.get_current_match()
        return None

    def is_tournament_complete(self) -> bool:
        """Check if the tournament is complete."""
        if not self.tournament:
            return False
        return all(match.is_complete for match in self.tournament.matches)

    def set_champion(self, creature_id: str):
        """Set the tournament champion."""
        self.champion_id = creature_id
        self.is_complete = True
