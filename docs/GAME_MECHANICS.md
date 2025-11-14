# 🎲 Pet Battler - Game Mechanics Guide

Complete guide to the combat system, stats, and gameplay mechanics.

## Table of Contents

- [Core Stats](#core-stats)
- [Creature Types](#creature-types)
- [Combat System](#combat-system)
- [Move Types](#move-types)
- [Damage Calculation](#damage-calculation)
- [Tournament Rules](#tournament-rules)
- [Strategy Guide](#strategy-guide)

---

## Core Stats

All creatures have five core stats ranging from 1 to 20.

### ⚡ Speed

**Primary Effect:** Turn Order  
**Secondary Effect:** Dodge Chance

- **Turn Order:** Creature with higher Speed attacks first each round
- **Dodge Calculation:** `(Speed / 20) × 0.4`
  - Speed 1 → 2% dodge chance
  - Speed 10 → 20% dodge chance
  - Speed 20 → 40% dodge chance

---

### ❤️ Health

**Primary Effect:** Maximum HP  
**Secondary Effect:** None

- **HP Formula:** Health stat = Max HP
- **Example:** Health 15 = 15 Max HP

**Special Note:** Increasing Health during level-up also increases current HP immediately.

---

### 🛡️ Defense

**Primary Effect:** Damage Reduction  
**Secondary Effect:** None

- **Reduction Calculation:** `(Defense / 20) × 0.5`
  - Defense 1 → 2.5% damage reduction
  - Defense 10 → 25% damage reduction
  - Defense 20 → 50% damage reduction

**Defend Move Bonus:** 70% total damage reduction

---

### 💪 Strength

**Primary Effect:** Damage Output  
**Secondary Effect:** None

- **Damage Modifier:** `Strength / 10`
  - Strength 1 → 0.1x damage (very weak)
  - Strength 10 → 1.0x damage (normal)
  - Strength 20 → 2.0x damage (double!)

**Example Damage:**
```
Base damage roll: 10
Strength 15: 10 × 1.5 = 15 damage
Strength 5:  10 × 0.5 = 5 damage
```

---

### 🍀 Luck

**Primary Effect:** Critical Hit Chance  
**Secondary Effect:** None

- **Crit Calculation:** `(Luck / 20) × 0.3`
  - Luck 1 → 1.5% crit chance
  - Luck 10 → 15% crit chance
  - Luck 20 → 30% crit chance

**Crit Multiplier:** 1.5x damage

**Special Ability Bonus:** 1.2x base crit chance (Luck 20 → 36%)

---

## Creature Types

Each creature type has stat biases applied to base stats (all start at 10).

### 🐉 Dragon

**Stat Biases:** +5 Health, -3 Speed, +2 Strength  
**Base Stats:** Speed 7, Health 15, Defense 10, Strength 12, Luck 10

**Strengths:** High survivability, decent damage  
**Weaknesses:** Slow, goes second often  
**Special Ability:** Fire Breath

---

### 🦉 Owlbear

**Stat Biases:** +3 Strength, +3 Defense, -2 Speed  
**Base Stats:** Speed 8, Health 10, Defense 13, Strength 13, Luck 10

**Strengths:** Good offense and defense  
**Weaknesses:** Average HP, slightly slow  
**Special Ability:** Bear Hug

---

### 🧙 Gnome

**Stat Biases:** +4 Luck, +3 Speed, -3 Strength  
**Base Stats:** Speed 13, Health 10, Defense 10, Strength 7, Luck 14
 
**Strengths:** High dodge, high crit, first strike  
**Weaknesses:** Low damage, fragile  
**Special Ability:** Illusion

---

### 🐙 Kraken

**Stat Biases:** +4 Health, +3 Strength, -2 Speed  
**Base Stats:** Speed 8, Health 14, Defense 10, Strength 13, Luck 10
 
**Strengths:** High HP and damage  
**Weaknesses:** Slow  
**Special Ability:** Tentacle Slam

---

### 👾 Cthulu

**Stat Biases:** +5 Luck, -3 Speed, +2 Defense  
**Base Stats:** Speed 7, Health 10, Defense 12, Strength 10, Luck 15
 
**Strengths:** Extremely high crit chance (22.5% base)  
**Weaknesses:** Slow, average stats otherwise  
**Special Ability:** Madness

---

### 🐂 Minotaur

**Stat Biases:** +5 Strength, -3 Luck, +2 Health  
**Base Stats:** Speed 10, Health 12, Defense 10, Strength 15, Luck 7

**Strengths:** Highest base Strength (15)  
**Weaknesses:** Low crit chance  
**Special Ability:** Charge

---

### 🐕 Cerberus

**Stat Biases:** +4 Speed, +2 Defense, -1 Luck  
**Base Stats:** Speed 14, Health 10, Defense 12, Strength 10, Luck 9

**Strengths:** High speed (first strike), good defense  
**Weaknesses:** Average damage  
**Special Ability:** Triple Bite

---

### 🐍 Medusa

**Stat Biases:** +4 Luck, -2 Strength, +2 Defense  
**Base Stats:** Speed 10, Health 10, Defense 12, Strength 8, Luck 14

**Strengths:** High crit, decent defense  
**Weaknesses:** Low damage  
**Special Ability:** Stone Gaze

---

### 🤖 Robot

**Stat Biases:** +5 Defense, -3 Luck, +2 Health  
**Base Stats:** Speed 10, Health 12, Defense 15, Strength 10, Luck 7

**Strengths:** Highest base Defense (37.5% reduction)  
**Weaknesses:** No crit chance  
**Special Ability:** Laser Beam (precise energy attack)

---

### 🐍 Python-python

**Stat Biases:** +4 Speed, +3 Luck, -2 Defense  
**Base Stats:** Speed 14, Health 10, Defense 8, Strength 10, Luck 13

**Strengths:** Fast with good crit  
**Weaknesses:** Low defense  
**Special Ability:** Constrict

---

### 👤 Jacob

**Stat Biases:** +2 All Stats  
**Base Stats:** Speed 12, Health 12, Defense 12, Strength 12, Luck 12

**Strengths:** No weaknesses, very flexible  
**Weaknesses:** No particular strength  
**Special Ability:** ??? (unknown power)

---

### 🌪️ Beyblade

**Stat Biases:** +6 Speed, -4 Defense, +2 Strength  
**Base Stats:** Speed 16, Health 10, Defense 6, Strength 12, Luck 10

**Strengths:** Fastest creature (32% dodge), strong  
**Weaknesses:** Paper-thin defense  
**Special Ability:** Let It Rip! (spinning strike)

---

## Combat System

### Battle Flow

```
1. Match Starts
   ├─ Both creatures at full HP
   ├─ 3 Defend uses available
   └─ 1 Special use available

2. Round Begins
   ├─ Player selects move
   ├─ AI selects move (automatic)
   └─ Both moves submitted

3. Moves Execute
   ├─ Turn order by Speed (higher goes first)
   ├─ First creature's move resolves
   ├─ Damage applied, HP updated
   ├─ If target still alive:
   │   └─ Second creature's move resolves
   └─ Battle log updated

4. Check Victory
   ├─ If creature HP = 0: Match Over
   └─ Else: Next round begins

5. Match Ends
   ├─ Winner determined
   ├─ Winner healed to full
   └─ Winner resources reset
```

### Turn Order

**Determination:** Compare Speed stats

```python
if creature1.speed >= creature2.speed:
    first = creature1
    second = creature2
else:
    first = creature2
    second = creature1
```

**Tied Speed:** Creature 1 goes first (player advantage if player is creature1)

**Impact:**
- First attacker can defeat enemy before they act
- Defending creature takes reduced damage
- Special abilities can be used to finish low-HP opponents

---

## Move Types

### ⚔️ Attack

**Description:** Standard damage attack  
**Uses:** Unlimited  
**Damage:** Base (5-15) × modifiers

**When to Use:**
- Default action when nothing special needed
- Chip away at enemy HP
- After using all special resources

---

### 🛡️ Defend

**Description:** Defensive stance reducing incoming damage  
**Uses:** 3 per round  
**Effect:** Take 30% damage (70% reduction)

**When to Use:**
- Low HP and need to survive
- Opponent has high Strength
- Expecting enemy Special ability
- Baiting opponent into wasting moves

**Mechanics:**
```python
if defender is defending:
    damage = damage × 0.3
else:
    damage = damage × (1 - defense_percentage)
```

**Stacking:** Defend move (70%) + Defense stat (up to 50%) is very powerful!

**Example:**
```
Attack damage: 12
Robot with 15 Defense (37.5% reduction):
  Normal: 12 × 0.625 = 7.5 damage
  Defending: 12 × 0.3 = 3.6 damage
```

---

### ✨ Special Ability

**Description:** Enhanced attack unique to creature type  
**Uses:** 1 per round  
**Damage:** Base (5-15) × Strength × 1.75

**Special Properties:**
- **Harder to Dodge:** Dodge chance × 0.7
- **Higher Crit Chance:** Crit chance × 1.2
- **Defense Less Effective:** Defense reduction × 0.7
- **Minimum Damage:** 2 (vs 1 for normal attack)

**When to Use:**
- Finish low-HP opponents (< 40% HP)
- Burst damage turn 1
- Break through high-Defense enemies
- Guarantee damage with lower dodge chance

**Damage Comparison:**
```
Creature: 15 Strength, 10 Luck
Base roll: 10

Normal Attack:
  10 × 1.5 = 15 damage
  15% crit chance → 22.5 crit damage

Special Ability:
  10 × 1.5 × 1.75 = 26.25 damage
  18% crit chance → 39.4 crit damage
```

---

## Damage Calculation

### Step-by-Step Formula

**1. Roll Base Damage**
```python
base_damage = random.randint(5, 15)
```

**2. Apply Strength Modifier**
```python
strength_modifier = attacker.strength / 10
damage = base_damage × strength_modifier
```

**3. Check for Critical Hit**
```python
crit_chance = (attacker.luck / 20) × 0.3

if random() < crit_chance:
    damage = damage × 1.5
    is_crit = True
```

**4. Check for Dodge**
```python
dodge_chance = (defender.speed / 20) × 0.4

if random() < dodge_chance:
    return "MISS"
```

**5. Apply Defense**
```python
if defender is defending:
    damage = damage × 0.3
else:
    defense_reduction = (defender.defense / 20) × 0.5
    damage = damage × (1 - defense_reduction)
```

**6. Apply Damage (Min 1)**
```python
damage = max(1, int(damage))
defender.current_hp -= damage
```

### Example Calculations

**Scenario 1: Average Attack**
```
Attacker: Dragon (Strength 15, Luck 10)
Defender: Gnome (Speed 13, Defense 10)

Base Roll: 10
× Strength: 10 × 1.5 = 15
Crit Check: 15% → Miss
Dodge Check: 26% → Miss
× Defense: 15 × 0.75 = 11.25

Final Damage: 11
```

**Scenario 2: Critical Special**
```
Attacker: Minotaur (Strength 18, Luck 7) using Special
Defender: Robot (Speed 10, Defense 15) not defending

Base Roll: 12
× Strength: 12 × 1.8 = 21.6
× Special: 21.6 × 1.75 = 37.8
Crit Check: (7/20 × 0.3 × 1.2) = 12.6% → Hit!
× Crit: 37.8 × 1.5 = 56.7
Dodge Check: (10/20 × 0.4 × 0.7) = 14% → Miss
× Defense: 56.7 × (1 - 0.375 × 0.7) = 56.7 × 0.7375 = 41.8

Final Damage: 41! (Robot's HP likely 0)
```

**Scenario 3: Defended Tank**
```
Attacker: Owlbear (Strength 13, Luck 10)
Defender: Dragon (Speed 8, Defense 10, HP 18) defending

Base Roll: 8
× Strength: 8 × 1.3 = 10.4
Crit Check: 15% → Miss
Dodge Check: 16% → Miss
× Defend: 10.4 × 0.3 = 3.12

Final Damage: 3 (Dragon barely scratched!)
```

---

## Tournament Rules

### Tournament Structure

**8-Creature Single Elimination:**
- 1 Player creature
- 7 AI creatures
- 3 rounds to victory
- Winner takes all

### Between Matches

**Winners Get:**
1. **Full HP Restore** - Healed to max HP
2. **Resource Reset** - Given 3 Defend, 1 Special
3. **3 Stat Points** - Allocate to any stats

**Losers:**
- Eliminated from tournament
- Game over!

### Stat Point Allocation

**After Each Victory:**
- Gain 3 stat points
- Allocate to any combination of stats
- No limit per stat (can do all 3 in one)
- Increases are permanent for tournament
- Health increases also add current HP immediately
