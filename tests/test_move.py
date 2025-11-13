import pytest
from src.backend.models.move import MoveType, Move, AttackMove, DefendMove, SpecialMove, MoveResult

def test_move_typical():
    m = Move(move_type=MoveType.ATTACK, user_id="c1", target_id="c2")
    assert m.move_type == MoveType.ATTACK
    assert m.user_id == "c1"
    assert m.target_id == "c2"

def test_move_null_user_id():
    with pytest.raises(Exception):
        Move(move_type=MoveType.ATTACK, user_id=None)

def test_move_empty_user_id():
    m = Move(move_type=MoveType.DEFEND, user_id="")
    assert m.user_id == ""

def test_move_invalid_type():
    with pytest.raises(Exception):
        Move(move_type="invalid", user_id="c1")

def test_attack_move_typical():
    m = AttackMove(user_id="c1", target_id="c2")
    assert m.move_type == MoveType.ATTACK
    assert m.user_id == "c1"
    assert m.target_id == "c2"

def test_defend_move_typical():
    m = DefendMove(user_id="c1")
    assert m.move_type == MoveType.DEFEND
    assert m.user_id == "c1"

def test_special_move_typical():
    m = SpecialMove(user_id="c1")
    assert m.move_type == MoveType.SPECIAL
    assert m.user_id == "c1"

def test_move_result_typical():
    m = Move(move_type=MoveType.ATTACK, user_id="c1")
    r = MoveResult(move=m, success=True, damage_dealt=10, was_critical=True, was_dodged=False, was_defended=False, message="Hit!")
    assert r.success
    assert r.damage_dealt == 10
    assert r.was_critical
    assert r.message == "Hit!"

def test_move_result_zero_damage():
    m = Move(move_type=MoveType.ATTACK, user_id="c1")
    r = MoveResult(move=m, success=True, damage_dealt=0, message="Miss!")
    assert r.damage_dealt == 0
    assert r.message == "Miss!"

def test_move_result_negative_damage():
    m = Move(move_type=MoveType.ATTACK, user_id="c1")
    r = MoveResult(move=m, success=True, damage_dealt=-5, message="Error!")
    assert r.damage_dealt == -5
    assert r.message == "Error!"

def test_move_result_large_damage():
    m = Move(move_type=MoveType.ATTACK, user_id="c1")
    r = MoveResult(move=m, success=True, damage_dealt=10**6, message="Big hit!")
    assert r.damage_dealt == 10**6
    assert r.message == "Big hit!"

def test_move_result_invalid_types():
    with pytest.raises(Exception):
        MoveResult(move=None, success=True)
    with pytest.raises(Exception):
        MoveResult(move="not a move", success=True)
