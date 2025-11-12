"""
AI opponent generation and decision-making.
"""

import random
import uuid
from typing import List
from ..models.creature import Creature, CreatureType
from ..models.move import Move, MoveType


class AIOpponentGenerator:
    """Generates AI-controlled opponents and makes decisions for them."""
    
    @staticmethod
    def generate_ai_creature(
        difficulty_level: int = 1,
        exclude_types: List[CreatureType] = None
    ) -> Creature:
        """
        Generate a random AI creature.
        
        Args:
            difficulty_level: Affects stat allocation (1-3)
            exclude_types: Creature types to exclude from selection
        """
        # Select random creature type
        available_types = [t for t in CreatureType]
        if exclude_types:
            available_types = [t for t in available_types if t not in exclude_types]
        
        creature_type = random.choice(available_types)
        
        # Generate stat allocations based on difficulty
        stat_allocations = AIOpponentGenerator._generate_stat_allocations(difficulty_level)
        
        # Generate AI name
        name = AIOpponentGenerator._generate_ai_name(creature_type)
        
        # Create creature
        creature = Creature.create_with_biases(
            name=name,
            creature_type=creature_type,
            stat_allocations=stat_allocations,
            is_ai=True
        )
        
        creature.id = str(uuid.uuid4())
        
        return creature
    
    @staticmethod
    def _generate_stat_allocations(difficulty: int) -> dict:
        """
        Generate stat point allocations for AI.
        Higher difficulty = more optimized allocations
        """
        total_points = 6
        stats = ["speed", "health", "defense", "strength", "luck"]
        
        if difficulty == 1:
            # Easy: Random allocation
            allocations = {}
            remaining = total_points
            for stat in stats[:-1]:
                points = random.randint(0, min(2, remaining))
                if points > 0:
                    allocations[stat] = points
                remaining -= points
            if remaining > 0:
                allocations[stats[-1]] = remaining
            return allocations
        
        elif difficulty == 2:
            # Medium: Focus on 2-3 stats
            focus_stats = random.sample(stats, random.randint(2, 3))
            allocations = {}
            remaining = total_points
            for stat in focus_stats:
                if stat == focus_stats[-1]:
                    allocations[stat] = remaining
                else:
                    points = random.randint(1, min(3, remaining - len(focus_stats) + 1))
                    allocations[stat] = points
                    remaining -= points
            return allocations
        
        else:  # difficulty == 3
            # Hard: Optimized allocation (focus on strength + one defensive stat)
            allocations = {
                "strength": 3,
                random.choice(["defense", "health"]): 2,
                "speed": 1
            }
            return allocations
    
    @staticmethod
    def _generate_ai_name(creature_type: CreatureType) -> str:
        """Generate a themed name for AI creature."""
        
        name_prefixes = {
            CreatureType.DRAGON: ["Flame", "Ember", "Scorch", "Inferno", "Blaze"],
            CreatureType.OWLBEAR: ["Talon", "Hoot", "Claw", "Feather", "Wing"],
            CreatureType.GNOME: ["Tink", "Gizmo", "Spark", "Widget", "Bolt"],
            CreatureType.KRAKEN: ["Tentacle", "Deep", "Squid", "Ocean", "Abyss"],
            CreatureType.CTHULU: ["Eldritch", "Void", "Cosmic", "Ancient", "Madness"],
            CreatureType.MINOTAUR: ["Bull", "Maze", "Horn", "Labyrinth", "Charge"],
            CreatureType.CERBERUS: ["Triple", "Hades", "Guard", "Snarl", "Howl"],
            CreatureType.MEDUSA: ["Stone", "Serpent", "Gaze", "Viper", "Gorgon"],
            CreatureType.ROBOT: ["Mecha", "Cyber", "Circuit", "Binary", "Steel"],
            CreatureType.PYTHON: ["Coil", "Hiss", "Scale", "Venom", "Fang"],
            CreatureType.JACOB: ["Cool", "Awesome", "Epic", "Legendary", "Supreme"],
            CreatureType.BEYBLADE: ["Spin", "Burst", "Tornado", "Vortex", "Whirl"],
        }
        
        prefixes = name_prefixes.get(creature_type, ["AI"])
        number = random.randint(1, 999)
        
        return f"{random.choice(prefixes)}{number}"
    
    @staticmethod
    def decide_move(creature: Creature, opponent: Creature, round_num: int) -> MoveType:
        """
        Decide which move the AI should use.
        
        Args:
            creature: The AI creature
            opponent: The opponent creature
            round_num: Current round number
        """
        # Calculate opponent's remaining HP percentage
        opponent_hp_percent = opponent.current_hp / opponent.max_hp
        own_hp_percent = creature.current_hp / creature.max_hp
        
        # Decision logic
        moves_available = []
        
        # Attack is always available
        moves_available.append((MoveType.ATTACK, 10))  # Base weight
        
        # Defend if low on HP and has uses
        if creature.defend_uses_remaining > 0:
            defend_weight = 0
            if own_hp_percent < 0.3:
                defend_weight = 15  # High priority when low HP
            elif own_hp_percent < 0.5:
                defend_weight = 8
            elif opponent.base_stats.strength > 15:
                defend_weight = 5  # Defend against strong opponents
            
            if defend_weight > 0:
                moves_available.append((MoveType.DEFEND, defend_weight))
        
        # Use special ability strategically
        if creature.special_uses_remaining > 0:
            special_weight = 0
            if opponent_hp_percent < 0.4:
                special_weight = 20  # Try to finish off low HP opponents
            elif round_num == 1:
                special_weight = 12  # Sometimes use special early for burst
            else:
                special_weight = 6  # Otherwise moderate priority
            
            moves_available.append((MoveType.SPECIAL, special_weight))
        
        # Weighted random selection
        total_weight = sum(weight for _, weight in moves_available)
        rand_value = random.uniform(0, total_weight)
        
        cumulative = 0
        for move_type, weight in moves_available:
            cumulative += weight
            if rand_value <= cumulative:
                return move_type
        
        # Fallback to attack
        return MoveType.ATTACK
