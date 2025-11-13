"""
API routes for game flow and tournament management.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from ..logic.narrator import NarratorAgent
from pydantic import BaseModel
from ..models.game_state import GameState, TournamentBracket
from ..models.move import Move, MoveType
from ..logic.tournament import TournamentManager
from ..logic.combat import CombatEngine
from ..logic.ai_opponent import AIOpponentGenerator

router = APIRouter(prefix="/game", tags=["game"])

games_db = {}


class StartGameRequest(BaseModel):
    """Request model for starting a new game."""

    num_players: int = 1
    creature_ids: List[str]
    tournament_size: int = 8


class SubmitMoveRequest(BaseModel):
    """Request model for submitting a move."""

    creature_id: str
    move_type: str


class AllocateStatsRequest(BaseModel):
    """Request model for allocating stat points after winning a match."""

    creature_id: str
    stat_allocations: dict  # e.g., {"speed": 1, "strength": 2}


def auto_complete_ai_matches(tournament: TournamentBracket, current_round: int):
    """Auto-complete all AI-only matches in the current round."""
    ai_matches = [
        m for m in tournament.matches
        if not m.is_complete
        and m.bracket_round == current_round
        and m.creature1.is_ai
        and m.creature2.is_ai
    ]

    for match in ai_matches:
        # Simulate the match - just pick a random winner for simplicity
        import random
        winner = random.choice([match.creature1, match.creature2])
        loser = match.creature2 if winner == match.creature1 else match.creature1

        # Set loser HP to 0
        loser.current_hp = 0
        if winner.id:
            match.set_winner(winner.id)


@router.post("/start")
async def start_game(request: StartGameRequest):
    """Start a new game with the specified creatures and tournament size."""
    from .creature_routes import creatures_db
    player_creatures = []
    for creature_id in request.creature_ids:
        if creature_id not in creatures_db:
            raise HTTPException(status_code=404, detail=f"Creature {creature_id} not found")
        player_creatures.append(creatures_db[creature_id])

    try:
        tournament = TournamentManager.create_tournament(
            player_creatures=player_creatures,
            tournament_size=request.tournament_size
        )

        import uuid
        game = GameState(
            game_id=str(uuid.uuid4()),
            num_players=request.num_players,
            player_creatures=player_creatures,
            tournament=tournament
        )

        games_db[game.game_id] = game
        current_match = game.get_current_match()
        match_state = None

        if current_match:
            match_state = {
                "match_id": current_match.match_id,
                "creature1_id": current_match.creature1.id,
                "creature1_name": current_match.creature1.name,
                "creature1_type": current_match.creature1.creature_type.value,
                "creature1_hp": current_match.creature1.current_hp,
                "creature1_max_hp": current_match.creature1.max_hp,
                "creature2_id": current_match.creature2.id,
                "creature2_name": current_match.creature2.name,
                "creature2_type": current_match.creature2.creature_type.value,
                "creature2_hp": current_match.creature2.current_hp,
                "creature2_max_hp": current_match.creature2.max_hp,
                "turn_number": current_match.turn_number,
                "bracket_round": current_match.bracket_round,
                "current_round": current_match.bracket_round,
                "is_complete": current_match.is_complete
            }

        return {
            "game_id": game.game_id,
            "current_match": match_state,
            "tournament_complete": False
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/{game_id}/move")
async def submit_move(game_id: str, request: SubmitMoveRequest):
    narrator = NarratorAgent(model="gpt-4-1106-preview")
    """Submit a move for a creature in the current match."""

    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games_db[game_id]
    current_match = game.get_current_match()

    if not current_match:
        # Added diagnostic detail to help trace post-tournament / new game issues
        print(
            f"[Move] No active match for game {game_id}. "
            f"is_complete={game.is_complete}. "
            f"Tournament present={game.tournament is not None}"
        )
        if game.tournament:
            incomplete = [
                m.match_id for m in game.tournament.matches
                if not m.is_complete
            ]
            print(f"[Move] Incomplete match IDs: {incomplete}")
            if not incomplete:
                msg = (
                    "[Move] All matches complete - client may be using "
                    "an old game_id after tournament end."
                )
                print(msg)
        detail_msg = (
            "No active match - ensure you've started a NEW game "
            "after finishing a tournament."
        )
        raise HTTPException(status_code=400, detail=detail_msg)

    if current_match.is_complete:
        raise HTTPException(status_code=400, detail="Current match is complete")

    # Validate creature is in this match
    creature_ids = [current_match.creature1.id, current_match.creature2.id]
    if request.creature_id not in creature_ids:
        error_msg = (
            f"Creature {request.creature_id} not in current match. "
            f"Match has {current_match.creature1.id} vs "
            f"{current_match.creature2.id}"
        )
        raise HTTPException(status_code=400, detail=error_msg)

    # Convert move type string to MoveType enum
    move_type_map = {
        "attack": MoveType.ATTACK,
        "defend": MoveType.DEFEND,
        "special": MoveType.SPECIAL
    }

    if request.move_type.lower() not in move_type_map:
        error_msg = f"Invalid move type: {request.move_type}"
        raise HTTPException(status_code=400, detail=error_msg)

    # Add move to pending moves
    move = Move(
        move_type=move_type_map[request.move_type.lower()],
        user_id=request.creature_id
    )
    current_match.add_move(request.creature_id, move)

    latest_results = []
    completed_match_winner = None  # Track winner before tournament advances

    # If opponent is AI, make its move automatically
    if current_match.creature2.is_ai and current_match.creature2.id not in current_match.pending_moves:
        ai_move_type = AIOpponentGenerator.decide_move(
            current_match.creature2,
            current_match.creature1,
            current_match.turn_number
        )
        ai_move = Move(move_type=ai_move_type, user_id=current_match.creature2.id)
        current_match.add_move(current_match.creature2.id, ai_move)

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

        # --- Narration Integration ---
        narration_event = {
            "round": current_match.turn_number + 1,  # since we increment after
            "creature1": creature1.name,
            "creature2": creature2.name,
            "move1": move1.move_type.name.title(),
            "move2": move2.move_type.name.title(),
            "result": f"{result1.message} {result2.message}",
            "creature1_hp": creature1.current_hp,
            "creature2_hp": creature2.current_hp
        }
        narration = narrator.generate_narration(narration_event)
        # --- End Narration Integration ---

        # Clear pending moves
        current_match.clear_pending_moves()
        current_match.turn_number += 1

        # Check for match end
        if not creature1.is_alive():
            current_match.set_winner(creature2.id)
            latest_results.append(f"{creature2.name} wins the match!")
            completed_match_winner = creature2.id
        elif not creature2.is_alive():
            current_match.set_winner(creature1.id)
            latest_results.append(f"{creature1.name} wins the match!")
            completed_match_winner = creature1.id

        # If match is complete, check tournament progression
        if current_match.is_complete:
            # Check if the player lost (their creature died)
            player_lost = False
            for player_creature in game.player_creatures:
                if player_creature.id == creature1.id and not creature1.is_alive():
                    player_lost = True
                    break

            if player_lost:
                # Player lost - they're out of the tournament
                game.is_complete = True
                latest_results.append("Game Over - You have been eliminated from the tournament!")
            else:
                # Player won - auto-complete other AI-only matches in this round
                current_round = game.tournament.current_round
                print(f"Auto-completing AI matches for bracket round {current_round}")
                auto_complete_ai_matches(game.tournament, current_round)

                # Check how many matches are still incomplete
                incomplete = [m for m in game.tournament.matches if not m.is_complete and m.bracket_round == current_round]
                print(f"Incomplete matches after auto-complete: {len(incomplete)}")
                for m in incomplete:
                    print(f"  - {m.creature1.name} vs {m.creature2.name}, AI1: {m.creature1.is_ai}, AI2: {m.creature2.is_ai}")

                # Player won this match - check if tournament continues
                tournament_continues = TournamentManager.advance_tournament(game.tournament)
                print(f"Tournament continues: {tournament_continues}, New bracket round: {game.tournament.current_round}")
                # Bracket diagnostic summary
                print("[Bracket Summary]")
                for m in game.tournament.matches:
                    print(f"  Round {m.bracket_round} | Match {m.match_id[:8]} | {m.creature1.name} vs {m.creature2.name} | complete={m.is_complete} | winner={m.winner_id}")

                if not tournament_continues:
                    # Tournament complete!
                    champion = TournamentManager.get_tournament_winner(game.tournament)
                    game.set_champion(champion.id)
                    latest_results.append(f"🏆 {champion.name} is the tournament champion! 🏆")

    # Build response
    current_match = game.get_current_match()
    match_state = None

    # Check if player won the completed match and gets stat points
    player_won_match = False
    stat_points_available = 0
    match_just_completed = False
    current_stats = None

    if completed_match_winner:
        match_just_completed = True
        # Check if player's creature won the just-completed match
        for player_creature in game.player_creatures:
            if player_creature.id == completed_match_winner:
                player_won_match = True
                # Only award points if tournament is still ongoing
                if not game.is_complete:
                    stat_points_available = 3
                    # Include current stats for display
                    current_stats = {
                        "speed": player_creature.base_stats.speed,
                        "health": player_creature.base_stats.health,
                        "defense": player_creature.base_stats.defense,
                        "strength": player_creature.base_stats.strength,
                        "luck": player_creature.base_stats.luck
                    }
                break

    if current_match:
        winner_name = None
        if current_match.is_complete:
            winner_name = (current_match.creature1.name
                          if current_match.winner_id == current_match.creature1.id
                          else current_match.creature2.name)

        match_state = {
            "match_id": current_match.match_id,
            "creature1_id": current_match.creature1.id,
            "creature1_name": current_match.creature1.name,
            "creature1_type": current_match.creature1.creature_type.value,
            "creature1_hp": current_match.creature1.current_hp,
            "creature1_max_hp": current_match.creature1.max_hp,
            "creature2_id": current_match.creature2.id,
            "creature2_name": current_match.creature2.name,
            "creature2_type": current_match.creature2.creature_type.value,
            "creature2_hp": current_match.creature2.current_hp,
            "creature2_max_hp": current_match.creature2.max_hp,
            "turn_number": current_match.turn_number,
            "bracket_round": current_match.bracket_round,
            "current_round": current_match.turn_number,
            "is_complete": current_match.is_complete,
            "winner_name": winner_name,
            "latest_results": latest_results
        }

    champion_name = None
    if game.is_complete and game.champion_id:
        for creature in [c for match in game.tournament.matches for c in [match.creature1, match.creature2]]:
            if creature.id == game.champion_id:
                champion_name = creature.name
                break

    return {
        "game_id": game.game_id,
        "current_match": match_state,
        "tournament_complete": game.is_complete,
        "champion_name": champion_name,
        "player_won_match": player_won_match,
        "stat_points_available": stat_points_available,
        "match_just_completed": match_just_completed,
        "current_stats": current_stats,
        "narration": narration if 'narration' in locals() else None
    }


@router.get("/{game_id}/state")
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

        match_state = {
            "match_id": current_match.match_id,
            "creature1_id": current_match.creature1.id,
            "creature1_name": current_match.creature1.name,
            "creature1_type": current_match.creature1.creature_type.value,
            "creature1_hp": current_match.creature1.current_hp,
            "creature1_max_hp": current_match.creature1.max_hp,
            "creature2_id": current_match.creature2.id,
            "creature2_name": current_match.creature2.name,
            "creature2_type": current_match.creature2.creature_type.value,
            "creature2_hp": current_match.creature2.current_hp,
            "creature2_max_hp": current_match.creature2.max_hp,
            "turn_number": current_match.turn_number,
            "bracket_round": current_match.bracket_round,
            "current_round": current_match.turn_number,
            "is_complete": current_match.is_complete,
            "winner_name": winner_name
        }

    champion_name = None
    if game.is_complete and game.champion_id:
        for creature in [c for match in game.tournament.matches for c in [match.creature1, match.creature2]]:
            if creature.id == game.champion_id:
                champion_name = creature.name
                break

    return {
        "game_id": game_id,
        "current_match": match_state,
        "tournament_complete": game.is_complete,
        "champion_name": champion_name
    }


@router.post("/{game_id}/allocate-stats")
async def allocate_stats(game_id: str, request: AllocateStatsRequest):
    """Allocate stat points to a creature after winning a match."""
    from .creature_routes import creatures_db

    if game_id not in games_db:
        raise HTTPException(status_code=404, detail="Game not found")

    game = games_db[game_id]

    if request.creature_id not in creatures_db:
        raise HTTPException(status_code=404, detail="Creature not found")

    creature = creatures_db[request.creature_id]

    # Verify this is a player's creature
    is_player_creature = any(pc.id == request.creature_id for pc in game.player_creatures)
    if not is_player_creature:
        raise HTTPException(status_code=400, detail="Can only allocate stats to player creatures")

    # Validate stat allocations (should total to 3 points)
    total_points = sum(request.stat_allocations.values())
    if total_points != 3:
        raise HTTPException(status_code=400, detail="Must allocate exactly 3 stat points")

    # Apply stat increases
    for stat, points in request.stat_allocations.items():
        if stat not in ["speed", "health", "defense", "strength", "luck"]:
            raise HTTPException(status_code=400, detail=f"Invalid stat: {stat}")
        if points < 0:
            raise HTTPException(status_code=400, detail="Cannot decrease stats")

        current_value = getattr(creature.base_stats, stat)
        setattr(creature.base_stats, stat, current_value + points)

        # Update max HP if health was increased
        if stat == "health":
            creature.max_hp += points
            creature.current_hp += points  # Also restore the HP gained

    return {
        "success": True,
        "creature_id": creature.id,
        "updated_stats": {
            "speed": creature.base_stats.speed,
            "health": creature.base_stats.health,
            "defense": creature.base_stats.defense,
            "strength": creature.base_stats.strength,
            "luck": creature.base_stats.luck
        }
    }
