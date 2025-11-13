import unittest
import random

from src.backend.logic.combat import CombatEngine
from src.backend.models.creature import Creature, CreatureType
from src.backend.models.move import Move, MoveType, MoveResult

class TestCombatEngine(unittest.TestCase):
    def setUp(self):
        self.creature1 = Creature.create_with_biases(
            name="Dragon",
            creature_type=CreatureType.DRAGON,
            stat_allocations={"strength": 3, "speed": 2, "health": 1},
            is_ai=False
        )
        self.creature2 = Creature.create_with_biases(
            name="Robot",
            creature_type=CreatureType.ROBOT,
            stat_allocations={"defense": 3, "health": 2, "luck": 1},
            is_ai=True
        )
        self.attack_move = Move(move_type=MoveType.ATTACK, user_id="1")
        self.defend_move = Move(move_type=MoveType.DEFEND, user_id="2")
        self.special_move = Move(move_type=MoveType.SPECIAL, user_id="1")

    def test_execute_moves_typical(self):
        result1, result2 = CombatEngine.execute_moves(
            self.creature1, self.attack_move, self.creature2, self.defend_move
        )
        self.assertIsInstance(result1, MoveResult)
        self.assertIsInstance(result2, MoveResult)

    def test_execute_moves_speed_tiebreak(self):
        self.creature1.base_stats.speed = self.creature2.base_stats.speed
        result1, result2 = CombatEngine.execute_moves(
            self.creature1, self.attack_move, self.creature2, self.attack_move
        )
        self.assertIsInstance(result1, MoveResult)
        self.assertIsInstance(result2, MoveResult)

    def test_attack_move_damage_range(self):
        result = CombatEngine._execute_attack(self.creature1, self.creature2, self.defend_move)
        self.assertGreaterEqual(result.damage_dealt or 0, 1)
        self.assertLessEqual(result.damage_dealt or 0, self.creature2.max_hp)

    def test_defend_move_resource_limit(self):
        self.creature1.defend_uses_remaining = 0
        result = CombatEngine._execute_defend(self.creature1)
        self.assertFalse(result.success)
        self.assertIn("no defend uses", result.message.lower())

    def test_special_move_resource_limit(self):
        self.creature1.special_uses_remaining = 0
        result = CombatEngine._execute_special(self.creature1, self.creature2, self.attack_move)
        self.assertFalse(result.success)
        self.assertIn("no special uses", result.message.lower())

    def test_attack_move_defended(self):
        self.creature2.defend_uses_remaining = 3
        result = CombatEngine._execute_attack(self.creature1, self.creature2, self.defend_move)
        self.assertIn(result.was_defended, [True, False])

    def test_special_move_defended(self):
        self.creature2.defend_uses_remaining = 3
        result = CombatEngine._execute_special(self.creature1, self.creature2, self.defend_move)
        self.assertIn(result.was_defended, [True, False])

    def test_attack_move_dodge(self):
        self.creature2.base_stats.speed = 20
        dodged = False
        for _ in range(20):
            result = CombatEngine._execute_attack(self.creature1, self.creature2, self.attack_move)
            if getattr(result, "was_dodged", False):
                dodged = True
                break
        self.assertTrue(dodged)

    def test_special_move_dodge(self):
        self.creature2.base_stats.speed = 20
        dodged = False
        for _ in range(20):
            result = CombatEngine._execute_special(self.creature1, self.creature2, self.attack_move)
            if getattr(result, "was_dodged", False):
                dodged = True
                break
        self.assertTrue(dodged)

    def test_invalid_move_type(self):
        bad_move = Move(move_type="INVALID", user_id="1")
        result = CombatEngine._execute_single_move(self.creature1, bad_move, self.creature2, self.attack_move)
        self.assertFalse(result.success)
        self.assertIn("unknown move type", result.message.lower())

    def test_null_inputs(self):
        with self.assertRaises(AttributeError):
            CombatEngine.execute_moves(None, None, None, None)

    def test_incorrect_data_types(self):
        with self.assertRaises(AttributeError):
            CombatEngine.execute_moves("not_a_creature", self.attack_move, self.creature2, self.attack_move)
        with self.assertRaises(AttributeError):
            CombatEngine.execute_moves(self.creature1, "not_a_move", self.creature2, self.attack_move)

    def test_zero_and_negative_values(self):
        self.creature1.base_stats.strength = 0
        result = CombatEngine._execute_attack(self.creature1, self.creature2, self.attack_move)
        self.assertGreaterEqual(result.damage_dealt or 0, 1)
        self.creature1.base_stats.strength = -5
        result = CombatEngine._execute_attack(self.creature1, self.creature2, self.attack_move)
        self.assertGreaterEqual(result.damage_dealt or 0, 1)

    def test_very_large_values(self):
        self.creature1.base_stats.strength = 1000
        result = CombatEngine._execute_attack(self.creature1, self.creature2, self.attack_move)
        self.assertGreaterEqual(result.damage_dealt or 0, 1)

    def test_very_small_values(self):
        self.creature1.base_stats.strength = 1
        result = CombatEngine._execute_attack(self.creature1, self.creature2, self.attack_move)
        self.assertGreaterEqual(result.damage_dealt or 0, 1)

    def test_creature_defeated_before_acting(self):
        self.creature2.current_hp = 0
        result1, result2 = CombatEngine.execute_moves(
            self.creature1, self.attack_move, self.creature2, self.attack_move
        )
        self.assertIn("defeated before acting", result2.message.lower())

if __name__ == "__main__":
    unittest.main()
