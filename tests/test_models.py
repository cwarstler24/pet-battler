"""
Basic tests for Pet Battler models.
"""

import pytest
from src.backend.models.creature import Creature, CreatureType, CreatureStats


def test_creature_creation():
    """Test basic creature creation."""
    creature = Creature.create_with_biases(
        name="TestDragon",
        creature_type=CreatureType.DRAGON,
        stat_allocations={"strength": 3, "health": 3},
        is_ai=False
    )
    
    assert creature.name == "TestDragon"
    assert creature.creature_type == CreatureType.DRAGON
    assert creature.is_alive()
    assert creature.current_hp == creature.max_hp


def test_stat_allocation_limit():
    """Test that stat allocation is limited to 6 points."""
    with pytest.raises(ValueError):
        Creature.create_with_biases(
            name="OverPowered",
            creature_type=CreatureType.GNOME,
            stat_allocations={"strength": 10},  # Too many points
            is_ai=False
        )


def test_creature_damage():
    """Test creature taking damage."""
    creature = Creature.create_with_biases(
        name="TestCreature",
        creature_type=CreatureType.ROBOT,
        is_ai=False
    )
    
    initial_hp = creature.current_hp
    damage_taken = creature.take_damage(5)
    
    assert damage_taken == 5
    assert creature.current_hp == initial_hp - 5
    assert creature.is_alive()


def test_creature_knockout():
    """Test creature being knocked out."""
    creature = Creature.create_with_biases(
        name="Weak",
        creature_type=CreatureType.GNOME,
        is_ai=False
    )
    
    creature.take_damage(creature.max_hp)
    
    assert creature.current_hp == 0
    assert not creature.is_alive()
