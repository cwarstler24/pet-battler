"""
Tournament bracket management and progression.
"""

import uuid
from typing import List
from ..models.creature import Creature
from ..models.game_state import Match, TournamentBracket
from .ai_opponent import AIOpponentGenerator


class TournamentManager:
    """Manages tournament bracket creation and progression."""
    
    @staticmethod
    def create_tournament(
        player_creatures: List[Creature],
        tournament_size: int = 8
    ) -> TournamentBracket:
        """
        Create a tournament bracket with player creatures and AI opponents.
        
        Args:
            player_creatures: List of player-controlled creatures (1-2)
            tournament_size: Total number of creatures in tournament (must be power of 2)
        """
        if tournament_size not in [4, 8, 16]:
            raise ValueError("Tournament size must be 4, 8, or 16")
        
        if len(player_creatures) > tournament_size:
            raise ValueError("Too many player creatures for tournament size")
        
        # Calculate number of AI opponents needed
        num_ai = tournament_size - len(player_creatures)
        
        # Generate AI opponents
        ai_creatures = []
        for i in range(num_ai):
            difficulty = 1 if i < num_ai // 2 else 2  # Mix of easy and medium
            ai_creature = AIOpponentGenerator.generate_ai_creature(difficulty_level=difficulty)
            ai_creatures.append(ai_creature)
        
        # Combine and shuffle all creatures
        all_creatures = player_creatures + ai_creatures
        
        # Create initial round matches
        matches = TournamentManager._create_round_matches(all_creatures)
        
        # Calculate total rounds needed (log2 of tournament size)
        total_rounds = tournament_size.bit_length() - 1
        
        bracket = TournamentBracket(
            bracket_id=str(uuid.uuid4()),
            total_rounds=total_rounds,
            current_round=0,
            matches=matches
        )
        
        return bracket
    
    @staticmethod
    def _create_round_matches(creatures: List[Creature]) -> List[Match]:
        """Create matches by pairing creatures sequentially."""
        matches = []
        
        for i in range(0, len(creatures), 2):
            if i + 1 < len(creatures):
                match = Match(
                    match_id=str(uuid.uuid4()),
                    creature1=creatures[i],
                    creature2=creatures[i + 1]
                )
                matches.append(match)
        
        return matches
    
    @staticmethod
    def advance_tournament(bracket: TournamentBracket) -> bool:
        """
        Advance the tournament to the next round.
        
        Returns:
            True if tournament continues, False if tournament is complete
        """
        # Check if current round is complete
        current_round_matches = [
            m for m in bracket.matches 
            if not m.is_complete and m.current_round == bracket.current_round
        ]
        
        if current_round_matches:
            return True  # Round still in progress
        
        # Get winners from completed round
        completed_matches = [
            m for m in bracket.matches 
            if m.is_complete and m.current_round == bracket.current_round
        ]
        
        if not completed_matches:
            return False  # Tournament complete
        
        winners = []
        for match in completed_matches:
            if match.winner_id == match.creature1.id:
                winner = match.creature1
            else:
                winner = match.creature2
            
            # Reset winner's resources for next round
            winner.reset_round_resources()
            winner.current_hp = winner.max_hp  # Full heal between rounds
            winners.append(winner)
        
        if len(winners) == 1:
            # Tournament complete - we have a champion
            return False
        
        # Create next round matches
        next_round_matches = TournamentManager._create_round_matches(winners)
        bracket.current_round += 1
        
        for match in next_round_matches:
            match.current_round = bracket.current_round
        
        bracket.matches.extend(next_round_matches)
        
        return True
    
    @staticmethod
    def get_tournament_winner(bracket: TournamentBracket) -> Creature:
        """Get the tournament champion."""
        # Find the final match
        final_matches = [
            m for m in bracket.matches 
            if m.is_complete and m.current_round == bracket.total_rounds - 1
        ]
        
        if not final_matches:
            raise ValueError("Tournament not complete")
        
        final_match = final_matches[0]
        
        if final_match.winner_id == final_match.creature1.id:
            return final_match.creature1
        else:
            return final_match.creature2
