"""
Creature model representing player and AI battle creatures.
"""

from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator

class CreatureType(str, Enum):
    """Available creature types with unique characteristics."""
    DRAGON = "dragon"
    OWLBEAR = "owlbear"
    GNOME = "gnome"
    KRAKEN = "kraken"
    CTHULU = "cthulu"
    MINOTAUR = "minotaur"
    CERBERUS = "cerberus"
    MEDUSA = "medusa"
    ROBOT = "robot"
    PYTHON = "python-python"
    JACOB = "jacob"
    BEYBLADE = "beyblade"

class CreatureStats(BaseModel):
    """Base statistics for a creature (1-20 range)."""
    speed: int = Field(gt=0, lt=21, description="Affects dodge chance")
    health: int = Field(gt=0, lt=21, description="Maximum hit points")
    defense: int = Field(gt=0, lt=21, description="Damage reduction percentage")
    strength: int = Field(gt=0, lt=21, description="Damage dealing percentage")
    luck: int = Field(gt=0, lt=21, description="Critical strike chance")

# Stat biases for each creature type (modifiers applied to base stats)
CREATURE_STAT_BIASES: Dict[CreatureType, Dict[str, int]] = {
    CreatureType.DRAGON: {"health": 5, "speed": -3, "strength": 2},
    CreatureType.OWLBEAR: {"strength": 3, "defense": 3, "speed": -2},
    CreatureType.GNOME: {"luck": 4, "speed": 3, "strength": -3},
    CreatureType.KRAKEN: {"health": 4, "strength": 3, "speed": -2},
    CreatureType.CTHULU: {"luck": 5, "speed": -3, "defense": 2},
    CreatureType.MINOTAUR: {"strength": 5, "luck": -3, "health": 2},
    CreatureType.CERBERUS: {"speed": 4, "defense": 2, "luck": -1},
    CreatureType.MEDUSA: {"luck": 4, "strength": -2, "defense": 2},
    CreatureType.ROBOT: {"defense": 5, "luck": -3, "health": 2},
    CreatureType.PYTHON: {"speed": 4, "luck": 3, "defense": -2},
    CreatureType.JACOB: {"health": 2, "strength": 2, "speed": 2},  # Balanced
    CreatureType.BEYBLADE: {"speed": 6, "defense": -4, "strength": 2},
}

class Creature(BaseModel):
    """A battle creature with stats and state."""
    id: Optional[str] = None
    name: str = Field(min_length=1, max_length=50)
    creature_type: CreatureType
    base_stats: CreatureStats
    current_hp: int = Field(ge=0)
    max_hp: int = Field(gt=0, lt=21)
    is_ai: bool = False

    # Round-specific resource tracking
    defend_uses_remaining: int = Field(default=3, gt=-1, lt=4)
    special_uses_remaining: int = Field(default=1, gt=-1, lt=2)

    @field_validator('current_hp')
    @classmethod
    def validate_current_hp(cls, v, info):
        """Ensure current HP doesn't exceed max HP."""
        if 'max_hp' in info.data and v > info.data['max_hp']:
            return info.data['max_hp']
        return v

    @classmethod
    def create_with_biases(
        cls,
        name: str,
        creature_type: CreatureType,
        stat_allocations: Optional[Dict[str, int]] = None,
        is_ai: bool = False
    ) -> "Creature":
        """
        Create a creature with type-specific stat biases and player allocations.
        
        Args:
            name: Custom name for the creature
            creature_type: Type of creature
            stat_allocations: Player-allocated stat points (max 6 total)
            is_ai: Whether this is an AI-controlled creature
        """
        # Start with base stats (20 for health, 15 for defense, 8 for strength)
        base_stats = {
            "speed": 10,
            "health": 20,
            "defense": 15,
            "strength": 8,
            "luck": 10
        }

        # Apply creature type biases
        biases = CREATURE_STAT_BIASES.get(creature_type, {})
        for stat, bias in biases.items():
            base_stats[stat] = max(1, min(20, base_stats[stat] + bias))

        # Apply player stat allocations (if provided)
        if stat_allocations:
            total_allocated = sum(stat_allocations.values())
            if total_allocated > 6:
                raise ValueError("Cannot allocate more than 6 stat points")

            for stat, points in stat_allocations.items():
                if stat in base_stats:
                    base_stats[stat] = max(1, min(20, base_stats[stat] + points))

        stats = CreatureStats(**base_stats)
        max_hp = stats.health

        return cls(
            name=name,
            creature_type=creature_type,
            base_stats=stats,
            current_hp=max_hp,
            max_hp=max_hp,
            is_ai=is_ai
        )

    def reset_round_resources(self):
        """Reset round-specific resources (defend and special uses)."""
        self.defend_uses_remaining = 3
        self.special_uses_remaining = 1

    def take_damage(self, damage: int) -> int:
        """Apply damage to creature and return actual damage taken."""
        actual_damage = min(damage, self.current_hp)
        self.current_hp -= actual_damage
        return actual_damage

    def is_alive(self) -> bool:
        """Check if creature is still alive."""
        return self.current_hp > 0

    def get_dodge_chance(self) -> float:
        """Calculate dodge chance based on speed (0-1 range)."""
        # Speed of 20 = 40% dodge chance, Speed of 1 = 2% dodge chance
        return (self.base_stats.speed / 20) * 0.4

    def get_defense_percentage(self) -> float:
        """Calculate damage reduction percentage (0-1 range)."""
        # Defense of 20 = 50% reduction, Defense of 1 = 2.5% reduction
        return (self.base_stats.defense / 20) * 0.5

    def get_crit_chance(self) -> float:
        """Calculate critical hit chance based on luck (0-1 range)."""
        # Luck of 20 = 30% crit chance, Luck of 1 = 1.5% crit chance
        return (self.base_stats.luck / 20) * 0.3
