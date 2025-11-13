import pytest
from datetime import datetime
from src.backend.models.game_state import Match, TournamentBracket, GameState
from src.backend.models.creature import Creature, CreatureType
from src.backend.models.move import Move, MoveType, MoveResult

def make_creature(name="Test", cid=None):
    c = Creature(
        name=name,
        creature_type=CreatureType.DRAGON,
        base_stats={'strength': 10, 'defense': 5, 'speed': 5, 'health': 100, 'luck': 1},
        stat_allocations={'strength': 10, 'defense': 5, 'speed': 5, 'health': 100, 'luck': 1},
        is_ai=False
    )
    c.id = cid or name
    c.current_hp = 100
    c.max_hp = 100
    c.defend_uses_remaining = 1
    c.special_uses_remaining = 1
    return c

def make_match(cid1="A", cid2="B", complete=False, winner=None, round_num=0):
    c1 = make_creature("A", cid1)
    c2 = make_creature("B", cid2)
    m = Match(
        match_id=f"match_{cid1}_{cid2}",
        creature1=c1,
        creature2=c2,
        turn_number=0,
        bracket_round=round_num,
        winner_id=winner,
        is_complete=complete
    )
    return m

def test_add_move_and_both_moves_submitted():
    m = make_match()
    move1 = Move(move_type=MoveType.ATTACK, user_id=m.creature1.id)
    move2 = Move(move_type=MoveType.DEFEND, user_id=m.creature2.id)
    m.add_move(m.creature1.id, move1)
    assert not m.both_moves_submitted()
    m.add_move(m.creature2.id, move2)
    assert m.both_moves_submitted()

def test_clear_pending_moves():
    m = make_match()
    move1 = Move(move_type=MoveType.ATTACK, user_id=m.creature1.id)
    m.add_move(m.creature1.id, move1)
    m.clear_pending_moves()
    assert m.pending_moves == {}

def test_set_winner():
    m = make_match()
    m.set_winner(m.creature1.id)
    assert m.winner_id == m.creature1.id
    assert m.is_complete

def test_tournament_bracket_get_current_match():
    m1 = make_match(complete=True)
    m2 = make_match(complete=False)
    bracket = TournamentBracket(bracket_id="b1", total_rounds=2, current_round=0, matches=[m1, m2])
    current = bracket.get_current_match()
    assert current == m2

def test_tournament_bracket_advance_round():
    bracket = TournamentBracket(bracket_id="b1", total_rounds=2, current_round=0, matches=[])
    bracket.advance_bracket_round()
    assert bracket.current_round == 1

def test_game_state_get_current_match_typical():
    m1 = make_match(complete=True)
    m2 = make_match(complete=False)
    bracket = TournamentBracket(bracket_id="b1", total_rounds=2, current_round=0, matches=[m1, m2])
    gs = GameState(game_id="g1", num_players=1, player_creatures=[make_creature("A")], tournament=bracket)
    current = gs.get_current_match()
    assert current == m2

def test_game_state_get_current_match_no_tournament():
    gs = GameState(game_id="g1", num_players=1, player_creatures=[make_creature("A")], tournament=None)
    assert gs.get_current_match() is None

def test_game_state_is_tournament_complete_true():
    m1 = make_match(complete=True)
    m2 = make_match(complete=True)
    bracket = TournamentBracket(bracket_id="b1", total_rounds=2, current_round=0, matches=[m1, m2])
    gs = GameState(game_id="g1", num_players=1, player_creatures=[make_creature("A")], tournament=bracket)
    assert gs.is_tournament_complete()

def test_game_state_is_tournament_complete_false():
    m1 = make_match(complete=True)
    m2 = make_match(complete=False)
    bracket = TournamentBracket(bracket_id="b1", total_rounds=2, current_round=0, matches=[m1, m2])
    gs = GameState(game_id="g1", num_players=1, player_creatures=[make_creature("A")], tournament=bracket)
    assert not gs.is_tournament_complete()

def test_game_state_set_champion():
    gs = GameState(game_id="g1", num_players=1, player_creatures=[make_creature("A")], tournament=None)
    gs.set_champion("champion_id")
    assert gs.champion_id == "champion_id"
    assert gs.is_complete

def test_game_state_invalid_num_players():
    with pytest.raises(Exception):
        GameState(game_id="g1", num_players=0, player_creatures=[], tournament=None)
    with pytest.raises(Exception):
        GameState(game_id="g1", num_players=3, player_creatures=[], tournament=None)

def test_match_invalid_types():
    with pytest.raises(Exception):
        Match(match_id=None, creature1=None, creature2=None)

def test_tournament_bracket_invalid_types():
    with pytest.raises(Exception):
        TournamentBracket(bracket_id=None, total_rounds=None)

def test_game_state_invalid_types():
    with pytest.raises(Exception):
        GameState(game_id=None, num_players=None)

def test_match_negative_turn_number():
    m = make_match()
    m.turn_number = -1
    assert m.turn_number == -1

def test_match_large_turn_number():
    m = make_match()
    m.turn_number = 10**6
    assert m.turn_number == 10**6

def test_tournament_bracket_empty_matches():
    bracket = TournamentBracket(bracket_id="b1", total_rounds=2, current_round=0, matches=[])
    assert bracket.get_current_match() is None

def test_game_state_empty_player_creatures():
    gs = GameState(game_id="g1", num_players=1, player_creatures=[], tournament=None)
    assert gs.player_creatures == []
