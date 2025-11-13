import unittest
from src.backend.models.creature import Creature, CreatureType, CreatureStats

class TestCreatureModel(unittest.TestCase):
    def test_typical_creation(self):
        creature = Creature.create_with_biases(
            name="TestDragon",
            creature_type=CreatureType.DRAGON,
            stat_allocations={"strength": 3, "health": 3},
            is_ai=False
        )
        self.assertEqual(creature.name, "TestDragon")
        self.assertEqual(creature.creature_type, CreatureType.DRAGON)
        self.assertTrue(creature.is_alive())
        self.assertEqual(creature.current_hp, creature.max_hp)

    def test_stat_allocation_limit(self):
        with self.assertRaises(ValueError):
            Creature.create_with_biases(
                name="OverPowered",
                creature_type=CreatureType.GNOME,
                stat_allocations={"strength": 10},
                is_ai=False
            )

    def test_zero_and_negative_stats(self):
        creature = Creature.create_with_biases(
            name="ZeroStats",
            creature_type=CreatureType.GNOME,
            stat_allocations={"strength": -10, "health": 0},
            is_ai=False
        )
        self.assertGreaterEqual(creature.base_stats.strength, 1)
        self.assertGreaterEqual(creature.base_stats.health, 1)

    def test_maximum_stats(self):
        creature = Creature.create_with_biases(
            name="MaxStats",
            creature_type=CreatureType.DRAGON,
            stat_allocations={"strength": 20, "health": 20, "speed": 20, "defense": 20, "luck": 20},
            is_ai=False
        )
        self.assertLessEqual(creature.base_stats.strength, 20)
        self.assertLessEqual(creature.base_stats.health, 20)

    def test_invalid_creature_type(self):
        with self.assertRaises(ValueError):
            Creature.create_with_biases(
                name="BadType",
                creature_type="NOT_A_TYPE",
                stat_allocations={"strength": 3, "health": 3},
                is_ai=False
            )

    def test_incorrect_data_types(self):
        with self.assertRaises(TypeError):
            Creature.create_with_biases(
                name="BadType",
                creature_type=CreatureType.GNOME,
                stat_allocations="not_a_dict",
                is_ai=False
            )

    def test_null_and_empty_inputs(self):
        with self.assertRaises(ValueError):
            Creature.create_with_biases(
                name="",
                creature_type=CreatureType.GNOME,
                stat_allocations={"strength": 1},
                is_ai=False
            )

    def test_take_damage(self):
        creature = Creature.create_with_biases(
            name="TestCreature",
            creature_type=CreatureType.ROBOT,
            is_ai=False
        )
        initial_hp = creature.current_hp
        damage_taken = creature.take_damage(5)
        self.assertEqual(damage_taken, 5)
        self.assertEqual(creature.current_hp, initial_hp - 5)
        self.assertTrue(creature.is_alive())

    def test_take_damage_overkill(self):
        creature = Creature.create_with_biases(
            name="Weak",
            creature_type=CreatureType.GNOME,
            is_ai=False
        )
        damage_taken = creature.take_damage(creature.max_hp + 10)
        self.assertEqual(creature.current_hp, 0)
        self.assertEqual(damage_taken, creature.max_hp)
        self.assertFalse(creature.is_alive())

    def test_get_dodge_chance(self):
        creature = Creature.create_with_biases(
            name="Dodger",
            creature_type=CreatureType.PYTHON,
            stat_allocations={"speed": 20},
            is_ai=False
        )
        dodge_chance = creature.get_dodge_chance()
        self.assertGreaterEqual(dodge_chance, 0)
        self.assertLessEqual(dodge_chance, 1)

    def test_get_defense_percentage(self):
        creature = Creature.create_with_biases(
            name="Defender",
            creature_type=CreatureType.ROBOT,
            stat_allocations={"defense": 20},
            is_ai=False
        )
        defense_pct = creature.get_defense_percentage()
        self.assertGreaterEqual(defense_pct, 0)
        self.assertLessEqual(defense_pct, 1)

    def test_get_crit_chance(self):
        creature = Creature.create_with_biases(
            name="Lucky",
            creature_type=CreatureType.GNOME,
            stat_allocations={"luck": 20},
            is_ai=False
        )
        crit_chance = creature.get_crit_chance()
        self.assertGreaterEqual(crit_chance, 0)
        self.assertLessEqual(crit_chance, 1)

if __name__ == "__main__":
    unittest.main()
