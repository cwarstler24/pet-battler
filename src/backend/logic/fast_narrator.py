"""
Fast Template-Based Narrator - instant responses with no ML overhead
Use this for ultra-low latency instead of the AI model.
"""

import random
from typing import Dict, Any


class FastNarrator:
    """Template-based narrator for instant (<0.001s) narration."""
    
    def __init__(self):
        """Initialize template library."""
        self.attack_templates = [
            "{c1} strikes {c2} with a powerful attack!",
            "{c1} launches a fierce assault on {c2}!",
            "{c1} charges forward and attacks {c2}!",
            "A devastating blow from {c1} hits {c2}!",
            "{c1}'s attack connects with {c2}!",
        ]
        
        self.defend_templates = [
            "{c1} raises their defenses!",
            "{c1} braces for impact!",
            "{c1} takes a defensive stance!",
            "{c1} fortifies their position!",
            "{c1} prepares to weather the storm!",
        ]
        
        self.special_templates = [
            "{c1} unleashes a special attack on {c2}!",
            "{c1} channels their inner power against {c2}!",
            "A spectacular special move from {c1}!",
            "{c1}'s ultimate technique strikes {c2}!",
            "{c1} goes all-out with their special ability!",
        ]
        
        self.damage_templates = [
            "{c2} takes {damage} damage!",
            "{damage} damage dealt to {c2}!",
            "{c2} reels from {damage} damage!",
            "Ouch! {c2} suffers {damage} damage!",
            "{c2} is hit for {damage} damage!",
        ]
        
        self.ko_templates = [
            "{c2} has been defeated!",
            "{c2} falls in battle!",
            "Victory for {c1}! {c2} is down!",
            "{c2} can't continue!",
            "{c1} emerges victorious as {c2} falls!",
        ]
        
        self.miss_templates = [
            "{c1}'s attack misses!",
            "{c2} dodges the attack!",
            "The attack goes wide!",
            "{c2} evades {c1}'s strike!",
            "A narrow miss!",
        ]
        
        self.critical_templates = [
            "Critical hit! {c1} deals massive damage!",
            "A devastating critical strike from {c1}!",
            "CRITICAL! {c1}'s attack finds a weak spot!",
            "{c1} lands a critical blow!",
            "It's a critical hit! {c2} is staggered!",
        ]
    
    def generate_narration(self, event: Dict[str, Any]) -> str:
        """
        Generate instant narration from templates.
        
        Args:
            event: dict with keys like 'creature1', 'creature2', 'move1', 'move2', 
                   'damage', 'is_ko', 'is_critical', 'is_miss', etc.
        
        Returns:
            Narration string
        """
        c1 = event.get("creature1", "Creature1")
        c2 = event.get("creature2", "Creature2")
        move1 = event.get("move1", "attack")
        damage = event.get("damage", 0)
        is_ko = event.get("is_ko", False)
        is_critical = event.get("is_critical", False)
        is_miss = event.get("is_miss", False)
        
        narration_parts = []
        
        # First part: the action
        if move1.lower() == "attack":
            narration_parts.append(random.choice(self.attack_templates))
        elif move1.lower() == "defend":
            narration_parts.append(random.choice(self.defend_templates))
        elif move1.lower() == "special":
            narration_parts.append(random.choice(self.special_templates))
        else:
            narration_parts.append(f"{c1} uses {move1}!")
        
        # Second part: the result
        if is_ko:
            narration_parts.append(random.choice(self.ko_templates))
        elif is_miss:
            narration_parts.append(random.choice(self.miss_templates))
        elif is_critical:
            narration_parts.append(random.choice(self.critical_templates))
        elif damage > 0:
            narration_parts.append(random.choice(self.damage_templates))
        
        # Format with actual names
        narration = " ".join(narration_parts)
        narration = narration.format(c1=c1, c2=c2, damage=damage)
        
        return narration
