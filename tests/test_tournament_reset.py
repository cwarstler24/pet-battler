"""Tests that starting a new tournament resets player creature state enabling moves."""

from src.backend.logic.tournament import TournamentManager
from src.backend.models.creature import Creature, CreatureType


def test_tournament_resets_player_creature_state():
    # Create a player creature and exhaust its resources / HP
    creature = Creature.create_with_biases(
        name="Hero",
        creature_type=CreatureType.DRAGON,
        is_ai=False
    )
    creature.current_hp = 0
    creature.defend_uses_remaining = 0
    creature.special_uses_remaining = 0

    # Start a new tournament (size 4) with this exhausted creature
    bracket = TournamentManager.create_tournament([creature], tournament_size=4)

    # Creature should be fully reset for the new tournament
    assert creature.current_hp == creature.max_hp, "Creature HP should be restored at tournament start"
    assert creature.defend_uses_remaining == 3, "Defend uses should reset to 3"
    assert creature.special_uses_remaining == 1, "Special uses should reset to 1"

    # Sanity: creature appears in first match
    assert bracket.matches, "Bracket should have matches"
    first_match = bracket.matches[0]
    assert first_match.creature1 == creature or first_match.creature2 == creature, "Player creature should be placed in a match"
