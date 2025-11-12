"""
API routes for game flow and tournament management.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from ..models.game_state import GameState, Match
from ..models.move import MoveType
from ..logic.tournament import TournamentManager
from ..logic.combat import CombatEngine
from ..logic.ai_opponent import AIOpponentGenerator
from .creature_routes import creatures_db

router = APIRouter(prefix="/game", tags=["game"])


class StartGameRequest(BaseModel):
    """Request to start a new game."""
    num_players: int = Field(ge=1, le=2)
    creature_ids: List[str] = Field(min_length=1, max_length=2)
    tournament_size: int = Field(default=8, ge=4, le=16)


class SubmitMoveRequest(BaseModel):
    """Request to submit a move."""
    creature_id: str
    move_type: MoveType


class MatchStateResponse(BaseModel):
    """Current state of a match."""
    match_id: str
    creature1_name: str
    creature1_hp: int
    creature1_max_hp: int
    creature2_name: str
    creature2_hp: int
    creature2_max_hp: int
    current_round: int
    is_complete: bool
    winner_name: Optional[str] = None
    latest_results: List[str] = []


class GameStateResponse(BaseModel):
    """Current game state."""
    game_id: str
    current_match: Optional[MatchStateResponse] = None
    tournament_complete: bool
    champion_name: Optional[str] = None


# In-memory game storage
games_db: Dict[str, GameState] = {}


@router.post("/start", response_model=GameStateResponse, status_code=201)
async def start_game(request: StartGameRequest):
    """Start a new tournament game."""
    
    # Validate creature IDs exist
    player_creatures = []
    for creature_id in request.creature_ids:
        if creature_id not in creatures_db:
            raise HTTPException(status_code=404, detail=f"Creature {creature_id} not found")
        player_creatures.append(creatures_db[creature_id])
    
    # Validate tournament size is power of 2
    if request.tournament_size not in [4, 8, 16]:
        raise HTTPException(status_code=400, detail="Tournament size must be 4, 8, or 16")
    
    try:
        # Create tournament
        tournament = TournamentManager.create_tournament(
            player_creatures=player_creatures,
            tournament_size=request.tournament_size
        )
        
        # Create game state
        import uuid
        game = GameState(
            game_id=str(uuid.uuid4()),
            num_players=request.num_players,
            player_creatures=player_creatures,
            tournament=tournament
        )
        
        games_db[game.game_id] = game
        
        # Get current match state
        current_match = game.get_current_match()
        match_state = None
        
        if current_match:
            match_state = MatchStateResponse(
                match_id=current_match.match_id,
                creature1_name=current_match.creature1.name,
                creature1_hp=current_match.creature1.current_hp,
                creature1_max_hp=current_match.creature1.max_hp,
                creature2_name=current_match.creature2.name,
                creature2_hp=current_match.creature2.current_hp,
                creature2_max_hp=current_match.creature2.max_hp,
                current_round=current_match.current_round,
                is_complete=current_match.is_complete
            )
        
        return GameStateResponse(
            game_id=game.game_id,
            current_match=match_state,
            tournament_complete=False
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{game_id}/move", response_model=GameStateResponse)
async def submit_move(game_id: str, request: SubmitMoveRequest):
    """Submit a move for a creature in the current match."""
    
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games_db[game_id]
    current_match = game.get_current_match()
    
    if not current_match:
        raise HTTPException(status_code=400, detail="No active match")
    
    if current_match.is_complete:
        raise HTTPException(status_code=400, detail="Current match is complete")
    
    # Validate creature is in this match
    if request.creature_id not in [current_match.creature1.id, current_match.creature2.id]:
        raise HTTPException(status_code=400, detail="Creature not in current match")
    
    # Add move to pending moves
    from ..models.move import Move
    move = Move(
        move_type=request.move_type,
        user_id=request.creature_id
    )
    current_match.add_move(request.creature_id, move)
    
    latest_results = []
    
    # Check if both moves are submitted
    if current_match.both_moves_submitted():
        # Get both creatures and moves
        creature1 = current_match.creature1
        creature2 = current_match.creature2
        move1 = current_match.pending_moves[creature1.id]
        move2 = current_match.pending_moves[creature2.id]
        
        # Execute combat
        result1, result2 = CombatEngine.execute_moves(creature1, move1, creature2, move2)
        
        # Store results
        current_match.move_history.append(result1)
        current_match.move_history.append(result2)
        latest_results = [result1.message, result2.message]
        
        # Clear pending moves
        current_match.clear_pending_moves()
        current_match.current_round += 1
        
        # Check for match end
        if not creature1.is_alive():
            current_match.set_winner(creature2.id)
            latest_results.append(f"{creature2.name} wins the match!")
        elif not creature2.is_alive():
            current_match.set_winner(creature1.id)
            latest_results.append(f"{creature1.name} wins the match!")
        
        # If match is complete, check tournament progression
        if current_match.is_complete:
            tournament_continues = TournamentManager.advance_tournament(game.tournament)
            
            if not tournament_continues:
                # Tournament complete!
                champion = TournamentManager.get_tournament_winner(game.tournament)
                game.set_champion(champion.id)
                latest_results.append(f"🏆 {champion.name} is the tournament champion! 🏆")
    
    else:
        # Waiting for other player's move
        if current_match.creature2.is_ai and current_match.creature2.id not in current_match.pending_moves:
            # AI makes its move
            ai_move_type = AIOpponentGenerator.decide_move(
                current_match.creature2,
                current_match.creature1,
                current_match.current_round
            )
            ai_move = Move(move_type=ai_move_type, user_id=current_match.creature2.id)
            current_match.add_move(current_match.creature2.id, ai_move)
            
            # Now execute since both moves are ready
            creature1 = current_match.creature1
            creature2 = current_match.creature2
            move1 = current_match.pending_moves[creature1.id]
            move2 = current_match.pending_moves[creature2.id]
            
            result1, result2 = CombatEngine.execute_moves(creature1, move1, creature2, move2)
            
            current_match.move_history.append(result1)
            current_match.move_history.append(result2)
            latest_results = [result1.message, result2.message]
            
            current_match.clear_pending_moves()
            current_match.current_round += 1
            
            # Check for match end
            if not creature1.is_alive():
                current_match.set_winner(creature2.id)
                latest_results.append(f"{creature2.name} wins the match!")
            elif not creature2.is_alive():
                current_match.set_winner(creature1.id)
                latest_results.append(f"{creature1.name} wins the match!")
            
            # Tournament progression
            if current_match.is_complete:
                tournament_continues = TournamentManager.advance_tournament(game.tournament)
                
                if not tournament_continues:
                    champion = TournamentManager.get_tournament_winner(game.tournament)
                    game.set_champion(champion.id)
                    latest_results.append(f"🏆 {champion.name} is the tournament champion! 🏆")
    
    # Build response
    current_match = game.get_current_match()
    match_state = None
    
    if current_match:
        winner_name = None
        if current_match.is_complete:
            winner_name = (current_match.creature1.name 
                          if current_match.winner_id == current_match.creature1.id 
                          else current_match.creature2.name)
        
        match_state = MatchStateResponse(
            match_id=current_match.match_id,
            creature1_name=current_match.creature1.name,
            creature1_hp=current_match.creature1.current_hp,
            creature1_max_hp=current_match.creature1.max_hp,
            creature2_name=current_match.creature2.name,
            creature2_hp=current_match.creature2.current_hp,
            creature2_max_hp=current_match.creature2.max_hp,
            current_round=current_match.current_round,
            is_complete=current_match.is_complete,
            winner_name=winner_name,
            latest_results=latest_results
        )
    
    champion_name = None
    if game.is_complete and game.champion_id:
        for creature in [c for match in game.tournament.matches for c in [match.creature1, match.creature2]]:
            if creature.id == game.champion_id:
                champion_name = creature.name
                break
    
    return GameStateResponse(
        game_id=game.game_id,
        current_match=match_state,
        tournament_complete=game.is_complete,
        champion_name=champion_name
    )


@router.get("/{game_id}/state", response_model=GameStateResponse)
async def get_game_state(game_id: str):
    """Get the current state of a game."""
    
    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games_db[game_id]
    current_match = game.get_current_match()
    
    match_state = None
    if current_match:
        winner_name = None
        if current_match.is_complete:
            winner_name = (current_match.creature1.name 
                          if current_match.winner_id == current_match.creature1.id 
                          else current_match.creature2.name)
        
        match_state = MatchStateResponse(
            match_id=current_match.match_id,
            creature1_name=current_match.creature1.name,
            creature1_hp=current_match.creature1.current_hp,
            creature1_max_hp=current_match.creature1.max_hp,
            creature2_name=current_match.creature2.name,
            creature2_hp=current_match.creature2.current_hp,
            creature2_max_hp=current_match.creature2.max_hp,
            current_round=current_match.current_round,
            is_complete=current_match.is_complete,
            winner_name=winner_name
        )
    
    champion_name = None
    if game.is_complete and game.champion_id:
        for creature in [c for match in game.tournament.matches for c in [match.creature1, match.creature2]]:
            if creature.id == game.champion_id:
                champion_name = creature.name
                break
    
    return GameStateResponse(
        game_id=game.game_id,
        current_match=match_state,
        tournament_complete=game.is_complete,
        champion_name=champion_name
    )
