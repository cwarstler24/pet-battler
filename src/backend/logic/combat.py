"""
Combat engine for resolving battles between creatures.
"""

import random
from typing import Tuple
from ..models.creature import Creature
from ..models.move import Move, MoveType, MoveResult


class CombatEngine:
    """Handles combat calculations and move resolution."""
    
    CRIT_MULTIPLIER = 1.5
    BASE_DAMAGE_RANGE = (5, 15)  # Base damage before modifiers
    
    @staticmethod
    def execute_moves(
        creature1: Creature,
        move1: Move,
        creature2: Creature,
        move2: Move
    ) -> Tuple[MoveResult, MoveResult]:
        """
        Execute both creatures' moves and return results.
        Determines turn order based on speed, then resolves each move.
        """
        # Determine turn order based on speed
        if creature1.base_stats.speed >= creature2.base_stats.speed:
            first, first_move, second, second_move = creature1, move1, creature2, move2
        else:
            first, first_move, second, second_move = creature2, move2, creature1, move1
        
        # Execute first creature's move
        result1 = CombatEngine._execute_single_move(first, first_move, second, second_move)
        
        # Execute second creature's move (if still alive)
        result2 = None
        if second.is_alive():
            result2 = CombatEngine._execute_single_move(second, second_move, first, first_move)
        else:
            result2 = MoveResult(
                move=second_move,
                success=False,
                message=f"{second.name} was defeated before acting!"
            )
        
        # Return results in original order
        if creature1.base_stats.speed >= creature2.base_stats.speed:
            return result1, result2
        else:
            return result2, result1
    
    @staticmethod
    def _execute_single_move(
        attacker: Creature,
        attacker_move: Move,
        defender: Creature,
        defender_move: Move
    ) -> MoveResult:
        """Execute a single creature's move against a target."""
        
        if attacker_move.move_type == MoveType.ATTACK:
            return CombatEngine._execute_attack(attacker, defender, defender_move)
        
        elif attacker_move.move_type == MoveType.DEFEND:
            return CombatEngine._execute_defend(attacker)
        
        elif attacker_move.move_type == MoveType.SPECIAL:
            return CombatEngine._execute_special(attacker, defender, defender_move)
        
        return MoveResult(
            move=attacker_move,
            success=False,
            message="Unknown move type"
        )
    
    @staticmethod
    def _execute_attack(
        attacker: Creature,
        defender: Creature,
        defender_move: Move
    ) -> MoveResult:
        """Execute an attack move."""
        
        # Check if defender dodges
        dodge_chance = defender.get_dodge_chance()
        if random.random() < dodge_chance:
            return MoveResult(
                move=Move(move_type=MoveType.ATTACK, user_id=attacker.id or ""),
                success=True,
                was_dodged=True,
                message=f"{attacker.name}'s attack missed! {defender.name} dodged!"
            )
        
        # Calculate base damage
        base_damage = random.randint(*CombatEngine.BASE_DAMAGE_RANGE)
        
        # Apply strength modifier
        strength_modifier = attacker.base_stats.strength / 10  # 1-20 becomes 0.1-2.0
        damage = int(base_damage * strength_modifier)
        
        # Check for critical hit
        is_crit = random.random() < attacker.get_crit_chance()
        if is_crit:
            damage = int(damage * CombatEngine.CRIT_MULTIPLIER)
        
        # Apply defense reduction (unless defender is defending)
        is_defending = (defender_move.move_type == MoveType.DEFEND and 
                       defender.defend_uses_remaining > 0)
        
        if is_defending:
            # Defending provides extra damage reduction
            damage = int(damage * 0.3)  # 70% damage reduction when defending
        else:
            # Normal defense percentage
            defense_reduction = defender.get_defense_percentage()
            damage = int(damage * (1 - defense_reduction))
        
        # Apply damage
        damage = max(1, damage)  # Minimum 1 damage
        actual_damage = defender.take_damage(damage)
        
        # Build message
        crit_text = " Critical hit!" if is_crit else ""
        defend_text = " (Defended)" if is_defending else ""
        message = f"{attacker.name} attacks {defender.name} for {actual_damage} damage!{crit_text}{defend_text}"
        
        return MoveResult(
            move=Move(move_type=MoveType.ATTACK, user_id=attacker.id or ""),
            success=True,
            damage_dealt=actual_damage,
            was_critical=is_crit,
            was_defended=is_defending,
            message=message
        )
    
    @staticmethod
    def _execute_defend(attacker: Creature) -> MoveResult:
        """Execute a defend move."""
        
        if attacker.defend_uses_remaining <= 0:
            return MoveResult(
                move=Move(move_type=MoveType.DEFEND, user_id=attacker.id or ""),
                success=False,
                message=f"{attacker.name} has no defend uses remaining!"
            )
        
        attacker.defend_uses_remaining -= 1
        
        return MoveResult(
            move=Move(move_type=MoveType.DEFEND, user_id=attacker.id or ""),
            success=True,
            message=f"{attacker.name} takes a defensive stance! ({attacker.defend_uses_remaining} uses left)"
        )
    
    @staticmethod
    def _execute_special(
        attacker: Creature,
        defender: Creature,
        defender_move: Move
    ) -> MoveResult:
        """Execute a special ability move."""
        
        if attacker.special_uses_remaining <= 0:
            return MoveResult(
                move=Move(move_type=MoveType.SPECIAL, user_id=attacker.id or ""),
                success=False,
                message=f"{attacker.name} has no special uses remaining!"
            )
        
        attacker.special_uses_remaining -= 1
        
        # Special abilities are more powerful attacks (1.5x-2.0x damage)
        # Check dodge
        dodge_chance = defender.get_dodge_chance() * 0.7  # Harder to dodge specials
        if random.random() < dodge_chance:
            return MoveResult(
                move=Move(move_type=MoveType.SPECIAL, user_id=attacker.id or ""),
                success=True,
                was_dodged=True,
                message=f"{attacker.name}'s special ability missed! {defender.name} dodged!"
            )
        
        # Calculate enhanced damage
        base_damage = random.randint(*CombatEngine.BASE_DAMAGE_RANGE)
        strength_modifier = attacker.base_stats.strength / 10
        special_multiplier = 1.75  # Special abilities deal 1.75x damage
        damage = int(base_damage * strength_modifier * special_multiplier)
        
        # Check for critical
        is_crit = random.random() < (attacker.get_crit_chance() * 1.2)  # Higher crit chance
        if is_crit:
            damage = int(damage * CombatEngine.CRIT_MULTIPLIER)
        
        # Apply defense (defending doesn't help as much against specials)
        is_defending = (defender_move.move_type == MoveType.DEFEND and 
                       defender.defend_uses_remaining > 0)
        
        if is_defending:
            damage = int(damage * 0.5)  # 50% reduction when defending
        else:
            defense_reduction = defender.get_defense_percentage() * 0.7  # Defense less effective
            damage = int(damage * (1 - defense_reduction))
        
        damage = max(2, damage)  # Minimum 2 damage for specials
        actual_damage = defender.take_damage(damage)
        
        crit_text = " Critical hit!" if is_crit else ""
        defend_text = " (Defended)" if is_defending else ""
        message = f"{attacker.name} uses special ability on {defender.name} for {actual_damage} damage!{crit_text}{defend_text}"
        
        return MoveResult(
            move=Move(move_type=MoveType.SPECIAL, user_id=attacker.id or ""),
            success=True,
            damage_dealt=actual_damage,
            was_critical=is_crit,
            was_defended=is_defending,
            message=message
        )
