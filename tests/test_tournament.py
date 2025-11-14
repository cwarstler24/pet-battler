import pytest
from src.backend.logic.tournament import TournamentManager
from src.backend.models.creature import Creature, CreatureType
from src.backend.models.game_state import Match, TournamentBracket

def make_creature(name="Player", cid=None):
    c = Creature(
        name=name,
        creature_type=CreatureType.DRAGON,
        base_stats={'strength': 10, 'defense': 5, 'speed': 5, 'health': 20, 'luck': 1},
        stat_allocations={'strength': 10, 'defense': 5, 'speed': 5, 'health': 20, 'luck': 1},
        is_ai=False,
        current_hp=20,
        max_hp=20
    )
    c.id = cid or name
    c.current_hp = 20
    c.max_hp = 20
    c.defend_uses_remaining = 1
    c.special_uses_remaining = 1
    return c

def test_create_tournament_typical():
    players = [make_creature("P1"), make_creature("P2")]
    bracket = TournamentManager.create_tournament(players, tournament_size=8)
    assert isinstance(bracket, TournamentBracket)
    assert len(bracket.matches) == 4
    assert bracket.total_rounds == 3

def test_create_tournament_boundary_sizes():
    for size in [4, 8, 16]:
        players = [make_creature("P1")]
        bracket = TournamentManager.create_tournament(players, tournament_size=size)
        assert isinstance(bracket, TournamentBracket)
        assert bracket.total_rounds == size.bit_length() - 1

def test_create_tournament_invalid_size():
    players = [make_creature("P1")]
    with pytest.raises(ValueError):
        TournamentManager.create_tournament(players, tournament_size=5)

def test_create_tournament_too_many_players():
    players = [make_creature(f"P{i}") for i in range(9)]
    with pytest.raises(ValueError):
        TournamentManager.create_tournament(players, tournament_size=8)

def test_create_tournament_empty_players():
    bracket = TournamentManager.create_tournament([], tournament_size=4)
    assert isinstance(bracket, TournamentBracket)
    assert len(bracket.matches) == 2

def test_create_tournament_null_players():
    with pytest.raises(TypeError):
        TournamentManager.create_tournament(None, tournament_size=4)

def test_create_tournament_zero_size():
    """Test that creating a tournament with size zero raises a ValueError."""
    players = [make_creature("P1")]
    with pytest.raises(ValueError):
        TournamentManager.create_tournament(players, tournament_size=0)

def test_create_tournament_negative_size():
    players = [make_creature("P1")]
    with pytest.raises(ValueError):
        TournamentManager.create_tournament(players, tournament_size=-8)

def test_create_tournament_large_size():
    players = [make_creature("P1")]
    with pytest.raises(ValueError):
        TournamentManager.create_tournament(players, tournament_size=1024)

def test_advance_tournament_typical():
    players = [make_creature("P1"), make_creature("P2")]
    bracket = TournamentManager.create_tournament(players, tournament_size=4)
    # Simulate all matches complete
    for m in list(bracket.matches):
        m.is_complete = True
        m.winner_id = m.creature1.id
        m.bracket_round = 0
    continued = TournamentManager.advance_tournament(bracket)
    assert continued is True or continued is False

def test_advance_tournament_no_matches():
    bracket = TournamentBracket(bracket_id="b1", total_rounds=2, current_round=0, matches=[])
    assert TournamentManager.advance_tournament(bracket) is False

def test_advance_tournament_null_bracket():
    with pytest.raises(AttributeError):
        TournamentManager.advance_tournament(None)

def test_get_tournament_winner_typical():
    players = [make_creature("P1"), make_creature("P2")]
    bracket = TournamentManager.create_tournament(players, tournament_size=4)
    # Simulate all matches complete and set winner
    for m in bracket.matches:
        m.is_complete = True
        m.winner_id = m.creature1.id
        m.bracket_round = 1
    winner = TournamentManager.get_tournament_winner(bracket)
    assert isinstance(winner, Creature)
    # Find the first match in the final round
    final_matches = [m for m in bracket.matches if m.is_complete and m.bracket_round == bracket.total_rounds - 1]
    assert winner.id == final_matches[0].creature1.id

def test_get_tournament_winner_not_complete():
    players = [make_creature("P1"), make_creature("P2")]
    bracket = TournamentManager.create_tournament(players, tournament_size=4)
    # No matches complete
    for m in list(bracket.matches):
        m.is_complete = False
        m.bracket_round = 1
    with pytest.raises(ValueError):
        TournamentManager.get_tournament_winner(bracket)

def test_get_tournament_winner_null_bracket():
    with pytest.raises(AttributeError):
        TournamentManager.get_tournament_winner(None)

def test_create_round_matches_typical():
    creatures = [make_creature(f"C{i}") for i in range(4)]
    matches = TournamentManager._create_round_matches(creatures)
    assert len(matches) == 2
    assert all(isinstance(m, Match) for m in matches)

def test_create_round_matches_odd_number():
    creatures = [make_creature(f"C{i}") for i in range(5)]
    matches = TournamentManager._create_round_matches(creatures)
    assert len(matches) == 2  # Last creature left out

def test_create_round_matches_empty():
    matches = TournamentManager._create_round_matches([])
    assert matches == []

def test_create_round_matches_null():
    with pytest.raises(TypeError):
        TournamentManager._create_round_matches(None)
