// Pet Battler Game Logic

const API_BASE = 'http://localhost:8000';

// Game State
let gameState = {
    creatureTypes: [],
    selectedType: null,
    statAllocations: { speed: 0, health: 0, defense: 0, strength: 0, luck: 0 },
    levelupStatAllocations: { speed: 0, health: 0, defense: 0, strength: 0, luck: 0 },
    creatureId: null,
    creatureName: null,
    gameId: null,
    currentMatch: null,
    creature1Type: null,
    creature2Type: null
};

// ASCII Art for creatures
const CREATURE_ASCII = {
    dragon: `
      /\\___/\\
     ( o   o )
      >  ^  <
     /|_____| \\
    /_|     |_\\
    DRAGON
    `,
    owlbear: `
    ___,___
   (O,,,,,O)
    ( V V )
    /|   |\\
   / |   | \\
    OWLBEAR
    `,
    gnome: `
      _._
     (o.o)
    --|||--
     / | \\
    /  |  \\
     GNOME
    `,
    kraken: `
    ≈≈≈≈≈≈
   ((O  O))
    \\ == /
   ≈≈≈≈≈≈≈
    KRAKEN
    `,
    cthulu: `
    /~~~~~\\
   ( O   O )
    \\ ___ /
    |||||||
    CTHULU
    `,
    minotaur: `
     @ @ 
    (O-O)
    | ^ |
    /| |\\
   / |_| \\
   MINOTAUR
    `,
    cerberus: `
   /\\ /\\ /\\
  (oo)(oo)(oo)
   VV  VV  VV
    CERBERUS
    `,
    medusa: `
    ~~~§~~~
   ( O   O )
    \\  o  /
     |||||
     MEDUSA
    `,
    robot: `
    [■■■]
    (o o)
    |===|
    | | |
    |_|_|
     ROBOT
    `,
    "python-python": `
    ~~~~S~
   ( o   )~
    ~~~~~
    PYTHON
    `,
    jacob: `
      _
     (O)
    /|\\
    / \\
    JACOB
    `,
    beyblade: `
    ═══╬═══
   ═══╬╬╬═══
    ═══╬═══
    BEYBLADE
    `,
    default: `
    O
   /|\\
   / \\
    `
};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    await loadCreatureTypes();
    setupEventListeners();
});

// Load available creature types
async function loadCreatureTypes() {
    try {
        const response = await fetch(`${API_BASE}/creatures/types`);
        const types = await response.json();
        gameState.creatureTypes = types;
        displayCreatureTypes(types);
    } catch (error) {
        console.error('Error loading creature types:', error);
        alert('Failed to load creature types. Make sure the backend is running.');
    }
}

// Display creature type cards
function displayCreatureTypes(types) {
    const container = document.getElementById('creature-types');
    container.innerHTML = '';

    types.forEach(type => {
        const card = document.createElement('div');
        card.className = 'creature-card';
        card.dataset.type = type.type;

        const biases = Object.entries(type.stat_biases)
            .map(([stat, value]) => `${stat}: ${value > 0 ? '+' : ''}${value}`)
            .join(', ');

        card.innerHTML = `
            <h4>${type.type.toUpperCase()}</h4>
            <p>${type.description}</p>
            <p class="stat-biases">${biases}</p>
        `;

        card.addEventListener('click', () => selectCreatureType(type.type));
        container.appendChild(card);
    });
}

// Select creature type
function selectCreatureType(type) {
    gameState.selectedType = type;

    // Update UI
    document.querySelectorAll('.creature-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`[data-type="${type}"]`).classList.add('selected');

    // Show stat allocation
    document.getElementById('stat-allocation').style.display = 'block';
    updateStartButton();
}

// Setup event listeners
function setupEventListeners() {
    // Creature name input
    document.getElementById('creature-name').addEventListener('input', updateStartButton);

    // Stat allocation buttons
    document.querySelectorAll('.stat-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const stat = btn.dataset.stat;
            const change = parseInt(btn.dataset.change);
            adjustStat(stat, change);
        });
    });

    // Start game button
    document.getElementById('start-game-btn').addEventListener('click', createCreatureAndStartGame);

    // Move buttons
    document.querySelectorAll('.move-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const moveType = btn.dataset.move;
            submitMove(moveType);
        });
    });

    // Next match button
    document.getElementById('next-match-btn').addEventListener('click', loadCurrentMatch);

    // Level-up stat allocation buttons
    document.querySelectorAll('.levelup-stat-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const stat = btn.dataset.stat;
            const change = parseInt(btn.dataset.change);
            adjustLevelupStat(stat, change);
        });
    });

    // Continue tournament button
    document.getElementById('continue-tournament-btn').addEventListener('click', submitStatAllocations);

    // New game button
    document.getElementById('new-game-btn').addEventListener('click', resetGame);
}

// Adjust stat allocation
function adjustStat(stat, change) {
    const currentTotal = Object.values(gameState.statAllocations).reduce((a, b) => a + b, 0);
    const newValue = gameState.statAllocations[stat] + change;

    if (newValue < 0) return;
    if (change > 0 && currentTotal >= 6) return;

    gameState.statAllocations[stat] = newValue;
    document.getElementById(`${stat}-value`).textContent = newValue;

    const remaining = 6 - Object.values(gameState.statAllocations).reduce((a, b) => a + b, 0);
    document.getElementById('points-remaining').textContent = remaining;

    updateStartButton();
}

// Adjust level-up stat allocation
function adjustLevelupStat(stat, change) {
    const currentTotal = Object.values(gameState.levelupStatAllocations).reduce((a, b) => a + b, 0);
    const newValue = gameState.levelupStatAllocations[stat] + change;

    if (newValue < 0) return;
    if (change > 0 && currentTotal >= 3) return;

    gameState.levelupStatAllocations[stat] = newValue;
    document.getElementById(`levelup-${stat}-value`).textContent = newValue;

    const remaining = 3 - Object.values(gameState.levelupStatAllocations).reduce((a, b) => a + b, 0);
    document.getElementById('levelup-points-remaining').textContent = remaining;
    
    // Update the new total display
    const currentStatValue = parseInt(document.getElementById(`current-${stat}`).textContent);
    const newTotal = currentStatValue + newValue;
    document.getElementById(`new-${stat}-total`).textContent = newTotal;

    // Enable continue button only when all 3 points are allocated
    const btn = document.getElementById('continue-tournament-btn');
    btn.disabled = remaining !== 0;
}

// Update start button state
function updateStartButton() {
    const name = document.getElementById('creature-name').value.trim();
    const hasType = gameState.selectedType !== null;
    const btn = document.getElementById('start-game-btn');

    btn.disabled = !(name && hasType);
}

// Create creature and start game
async function createCreatureAndStartGame() {
    const name = document.getElementById('creature-name').value.trim();

    try {
        // Create creature
        const creatureResponse = await fetch(`${API_BASE}/creatures`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                creature_type: gameState.selectedType,
                stat_allocations: gameState.statAllocations
            })
        });

        if (!creatureResponse.ok) {
            throw new Error('Failed to create creature');
        }

        const creature = await creatureResponse.json();
        gameState.creatureId = creature.id;
        gameState.creatureName = name;
        gameState.creature1Type = gameState.selectedType;

        // Start game
        const gameResponse = await fetch(`${API_BASE}/game/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                num_players: 1,
                creature_ids: [creature.id],
                tournament_size: 8
            })
        });

        if (!gameResponse.ok) {
            throw new Error('Failed to start game');
        }

        const game = await gameResponse.json();
        gameState.gameId = game.game_id;
        gameState.currentMatch = game.current_match;
        
        // Set up creature tracking for first match
        if (game.current_match) {
            // Determine which creature is the player's
            if (game.current_match.creature1_name === gameState.creatureName) {
                // Player is creature1
                gameState.creatureId = game.current_match.creature1_id;
                gameState.creature1Type = game.current_match.creature1_type;
                gameState.creature2Type = game.current_match.creature2_type;
            } else {
                // Player is creature2
                gameState.creatureId = game.current_match.creature2_id;
                gameState.creature1Type = game.current_match.creature2_type;
                gameState.creature2Type = game.current_match.creature1_type;
            }
        }

        // Switch to battle screen
        switchScreen('battle-screen');
        updateBattleDisplay();

    } catch (error) {
        console.error('Error starting game:', error);
        alert('Failed to start game: ' + error.message);
    }
}

// Submit move
async function submitMove(moveType) {
    if (!gameState.gameId || !gameState.creatureId) return;

    // Disable buttons
    document.querySelectorAll('.move-btn').forEach(btn => btn.disabled = true);

    try {
        const response = await fetch(`${API_BASE}/game/${gameState.gameId}/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                creature_id: gameState.creatureId,
                move_type: moveType
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
            console.error('Move submission failed:', errorData);
            throw new Error(errorData.detail || 'Failed to submit move');
        }

        const result = await response.json();
        gameState.currentMatch = result.current_match;
        
        // Update opponent's creature type if available
        if (result.current_match) {
            gameState.creature2Type = result.current_match.creature2_type;
        }

        // Update display with results
        updateBattleDisplay(result.current_match?.latest_results);

        // Check if match is complete
        if (result.tournament_complete) {
            showVictoryScreen(result.champion_name);
        } else if (result.match_just_completed) {
            // A match just finished - check if player won or lost
            const playerWon = result.player_won_match;
            
            if (playerWon && result.stat_points_available > 0) {
                // Player won - show level-up screen
                showLevelUpScreen(result.current_stats);
            } else if (!playerWon) {
                // Player lost - return to character selection
                alert('You have been eliminated from the tournament!');
                setTimeout(() => resetGame(), 2000);
            } else {
                // No stat points (shouldn't happen, but just in case)
                document.getElementById('next-match-btn').style.display = 'block';
            }
        } else {
            // Re-enable move buttons for next round
            setTimeout(() => {
                document.querySelectorAll('.move-btn').forEach(btn => btn.disabled = false);
            }, 1000);
        }

    } catch (error) {
        console.error('Error submitting move:', error);
        alert('Failed to submit move: ' + error.message);
        document.querySelectorAll('.move-btn').forEach(btn => btn.disabled = false);
    }
}

// Update battle display
function updateBattleDisplay(messages = []) {
    const match = gameState.currentMatch;
    if (!match) return;

    // Determine if player is creature1 or creature2 and swap display accordingly
    const playerIsCreature1 = match.creature1_name === gameState.creatureName;
    
    // Player should always be shown on left (p1), opponent on right (p2)
    const playerName = playerIsCreature1 ? match.creature1_name : match.creature2_name;
    const playerHp = playerIsCreature1 ? match.creature1_hp : match.creature2_hp;
    const playerMaxHp = playerIsCreature1 ? match.creature1_max_hp : match.creature2_max_hp;
    
    const opponentName = playerIsCreature1 ? match.creature2_name : match.creature1_name;
    const opponentHp = playerIsCreature1 ? match.creature2_hp : match.creature1_hp;
    const opponentMaxHp = playerIsCreature1 ? match.creature2_max_hp : match.creature1_max_hp;

    // Update player info (always p1)
    document.getElementById('p1-name').textContent = playerName;
    document.getElementById('p1-hp').textContent = `HP: ${playerHp}/${playerMaxHp}`;
    updateHPBar('p1', playerHp, playerMaxHp);

    // Update opponent info (always p2)
    document.getElementById('p2-name').textContent = opponentName;
    document.getElementById('p2-hp').textContent = `HP: ${opponentHp}/${opponentMaxHp}`;
    updateHPBar('p2', opponentHp, opponentMaxHp);

    // Update round number
    document.getElementById('round-number').textContent = match.current_round + 1;

    // Update ASCII art using creature types (already set correctly in loadCurrentMatch)
    const p1Type = gameState.creature1Type || 'default';
    const p2Type = gameState.creature2Type || 'default';
    
    document.getElementById('p1-ascii').textContent = CREATURE_ASCII[p1Type] || CREATURE_ASCII.default;
    document.getElementById('p2-ascii').textContent = CREATURE_ASCII[p2Type] || CREATURE_ASCII.default;

    // Add messages to battle log
    if (messages && messages.length > 0) {
        const logContainer = document.getElementById('battle-messages');
        messages.forEach(msg => {
            const msgDiv = document.createElement('div');
            msgDiv.className = 'battle-message';
            msgDiv.textContent = msg;
            logContainer.appendChild(msgDiv);
        });
        logContainer.scrollTop = logContainer.scrollHeight;
    }
}

// Update HP bar
function updateHPBar(player, current, max) {
    const fill = document.getElementById(`${player}-hp-fill`);
    const percentage = (current / max) * 100;
    fill.style.width = percentage + '%';

    // Update color based on HP
    fill.classList.remove('low', 'critical');
    if (percentage <= 25) {
        fill.classList.add('critical');
    } else if (percentage <= 50) {
        fill.classList.add('low');
    }
}

// Load current match (after previous match ends)
async function loadCurrentMatch() {
    try {
        const response = await fetch(`${API_BASE}/game/${gameState.gameId}/state`);
        const result = await response.json();

        console.log('Loading match:', result.current_match);
        console.log('Player name:', gameState.creatureName);

        if (result.tournament_complete) {
            showVictoryScreen(result.champion_name);
        } else {
            gameState.currentMatch = result.current_match;
            
            // Update which creature is the player's in this match
            if (result.current_match) {
                // The player's creature might be creature1 or creature2 depending on bracket
                if (result.current_match.creature1_name === gameState.creatureName) {
                    // Player is creature1
                    console.log('Player is creature1');
                    gameState.creatureId = result.current_match.creature1_id;
                    gameState.creature1Type = result.current_match.creature1_type;
                    gameState.creature2Type = result.current_match.creature2_type;
                } else {
                    // Player is creature2 - swap for display
                    console.log('Player is creature2');
                    gameState.creatureId = result.current_match.creature2_id;
                    gameState.creature1Type = result.current_match.creature2_type;
                    gameState.creature2Type = result.current_match.creature1_type;
                }
                console.log('Player creature type:', gameState.creature1Type);
                console.log('Opponent creature type:', gameState.creature2Type);
            }
            
            document.getElementById('battle-messages').innerHTML = '';
            document.getElementById('next-match-btn').style.display = 'none';
            document.querySelectorAll('.move-btn').forEach(btn => btn.disabled = false);
            
            // Switch to battle screen
            switchScreen('battle-screen');
            updateBattleDisplay();
        }
    } catch (error) {
        console.error('Error loading match:', error);
    }
}

// Show level-up screen
function showLevelUpScreen(currentStats) {
    // Reset level-up allocations
    gameState.levelupStatAllocations = { speed: 0, health: 0, defense: 0, strength: 0, luck: 0 };
    
    // Display current stats
    if (currentStats) {
        Object.keys(currentStats).forEach(stat => {
            document.getElementById(`current-${stat}`).textContent = currentStats[stat];
            document.getElementById(`new-${stat}-total`).textContent = currentStats[stat];
        });
    }
    
    // Reset allocation values
    Object.keys(gameState.levelupStatAllocations).forEach(stat => {
        document.getElementById(`levelup-${stat}-value`).textContent = '0';
    });
    document.getElementById('levelup-points-remaining').textContent = '3';
    document.getElementById('continue-tournament-btn').disabled = true;
    
    switchScreen('levelup-screen');
}

// Submit stat allocations and continue to next match
async function submitStatAllocations() {
    try {
        const response = await fetch(`${API_BASE}/game/${gameState.gameId}/allocate-stats`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                creature_id: gameState.creatureId,
                stat_allocations: gameState.levelupStatAllocations
            })
        });

        if (!response.ok) {
            throw new Error('Failed to allocate stats');
        }

        await response.json();
        
        // Load the next match
        loadCurrentMatch();

    } catch (error) {
        console.error('Error allocating stats:', error);
        alert('Failed to allocate stats: ' + error.message);
    }
}

// Show victory screen
function showVictoryScreen(championName) {
    switchScreen('victory-screen');
    document.getElementById('champion-name').textContent = championName;
    
    // Determine if player won or lost
    const playerWon = championName === gameState.creatureName;
    const asciiType = playerWon ? gameState.creature1Type : 'default';
    document.getElementById('champion-ascii').textContent = CREATURE_ASCII[asciiType] || CREATURE_ASCII.default;
    
    // Update victory text based on result
    const victoryText = document.querySelector('.victory-text');
    if (playerWon) {
        victoryText.textContent = '🎉 YOU ARE THE CHAMPION! 🎉';
        victoryText.style.color = 'var(--success-color)';
    } else {
        victoryText.textContent = 'Better luck next time!';
        victoryText.style.color = 'var(--danger-color)';
    }
}

// Switch between screens
function switchScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

// Reset game
function resetGame() {
    gameState = {
        creatureTypes: gameState.creatureTypes,
        selectedType: null,
        statAllocations: { speed: 0, health: 0, defense: 0, strength: 0, luck: 0 },
        levelupStatAllocations: { speed: 0, health: 0, defense: 0, strength: 0, luck: 0 },
        creatureId: null,
        creatureName: null,
        gameId: null,
        currentMatch: null,
        creature1Type: null,
        creature2Type: null
    };

    // Reset UI
    document.getElementById('creature-name').value = '';
    document.querySelectorAll('.creature-card').forEach(card => card.classList.remove('selected'));
    document.getElementById('stat-allocation').style.display = 'none';
    Object.keys(gameState.statAllocations).forEach(stat => {
        document.getElementById(`${stat}-value`).textContent = '0';
    });
    document.getElementById('points-remaining').textContent = '6';
    document.getElementById('battle-messages').innerHTML = '';
    document.getElementById('next-match-btn').style.display = 'none';

    switchScreen('setup-screen');
}
