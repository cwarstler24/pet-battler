import pytest
from src.backend.logic.ai_opponent import AIOpponentGenerator
from src.backend.models.creature import Creature, CreatureType
from src.backend.models.move import MoveType

def make_creature(hp=100, max_hp=100, defend_uses=1, special_uses=1, strength=10):
    c = Creature(
        name="TestAI",
        creature_type=CreatureType.DRAGON,
        base_stats={'strength': strength, 'defense': 5, 'speed': 5, 'health': max_hp, 'luck': 1},
        stat_allocations={'strength': strength, 'defense': 5, 'speed': 5, 'health': max_hp, 'luck': 1},
        is_ai=True
    )
    c.current_hp = hp
    c.max_hp = max_hp
    c.defend_uses_remaining = defend_uses
    c.special_uses_remaining = special_uses
    return c

def make_opponent(hp=100, max_hp=100, strength=10):
    o = Creature(
        name="Opponent",
        creature_type=CreatureType.OWLBEAR,
        base_stats={'strength': strength, 'defense': 5, 'speed': 5, 'health': max_hp, 'luck': 1},
        stat_allocations={'strength': strength, 'defense': 5, 'speed': 5, 'health': max_hp, 'luck': 1},
        is_ai=False
    )
    o.current_hp = hp
    o.max_hp = max_hp
    return o

def test_decide_move_typical():
    ai = make_creature()
    opp = make_opponent()
    move = AIOpponentGenerator.decide_move(ai, opp, round_num=1)
    assert move in [MoveType.ATTACK, MoveType.DEFEND, MoveType.SPECIAL]

def test_decide_move_low_hp():
    ai = make_creature(hp=20, max_hp=100, defend_uses=1)
    opp = make_opponent()
    move = AIOpponentGenerator.decide_move(ai, opp, round_num=2)
    assert move in [MoveType.DEFEND, MoveType.ATTACK, MoveType.SPECIAL]

def test_decide_move_no_defend():
    ai = make_creature(defend_uses=0)
    opp = make_opponent()
    move = AIOpponentGenerator.decide_move(ai, opp, round_num=2)
    assert move in [MoveType.ATTACK, MoveType.SPECIAL]

def test_decide_move_no_special():
    ai = make_creature(special_uses=0)
    opp = make_opponent()
    move = AIOpponentGenerator.decide_move(ai, opp, round_num=2)
    assert move in [MoveType.ATTACK, MoveType.DEFEND]

def test_decide_move_opponent_low_hp():
    ai = make_creature()
    opp = make_opponent(hp=10, max_hp=100)
    move = AIOpponentGenerator.decide_move(ai, opp, round_num=2)
    assert move in [MoveType.SPECIAL, MoveType.ATTACK, MoveType.DEFEND]

def test_decide_move_zero_values():
    ai = make_creature(hp=0, max_hp=100, defend_uses=0, special_uses=0)
    opp = make_opponent(hp=0, max_hp=100)
    move = AIOpponentGenerator.decide_move(ai, opp, round_num=0)
    assert move == MoveType.ATTACK

def test_decide_move_negative_values():
    ai = make_creature(hp=-10, max_hp=100, defend_uses=-1, special_uses=-1)
    opp = make_opponent(hp=-5, max_hp=100)
    move = AIOpponentGenerator.decide_move(ai, opp, round_num=-1)
    assert move == MoveType.ATTACK

def test_decide_move_large_values():
    ai = make_creature(hp=10**6, max_hp=10**6, defend_uses=10**6, special_uses=10**6)
    opp = make_opponent(hp=10**6, max_hp=10**6)
    move = AIOpponentGenerator.decide_move(ai, opp, round_num=10**6)
    assert move in [MoveType.ATTACK, MoveType.DEFEND, MoveType.SPECIAL]

def test_generate_ai_creature_typical():
    creature = AIOpponentGenerator.generate_ai_creature(difficulty_level=2)
    assert isinstance(creature, Creature)
    assert creature.is_ai

def test_generate_ai_creature_exclude_types():
    exclude = [CreatureType.DRAGON, CreatureType.OWLBEAR]
    creature = AIOpponentGenerator.generate_ai_creature(exclude_types=exclude)
    assert creature.creature_type not in exclude

def test_generate_ai_creature_invalid_difficulty():
    creature = AIOpponentGenerator.generate_ai_creature(difficulty_level=99)
    assert isinstance(creature, Creature)

def test_decide_move_invalid_types():
    with pytest.raises(Exception):
        AIOpponentGenerator.decide_move(None, None, None)
