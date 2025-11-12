// Pet Battler Game Logic

const API_BASE = 'http://localhost:8000';

// Game State
let gameState = {
    creatureTypes: [],
    selectedType: null,
    statAllocations: { speed: 0, health: 0, defense: 0, strength: 0, luck: 0 },
    creatureId: null,
    gameId: null,
    currentMatch: null
};

// ASCII Art for creatures (simplified)
const CREATURE_ASCII = {
    dragon: `
    /\\___/\\
   ( o   o )
    >  ^  <
   /|     |\\
  (_|     |_)
    `,
    owlbear: `
    ___
   (o o)
   ( V )
   /| |\\
  / | | \\
    `,
    gnome: `
    _._
   (o.o)
    |||
   / | \\
  /  |  \\
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
            throw new Error('Failed to submit move');
        }

        const result = await response.json();
        gameState.currentMatch = result.current_match;

        // Update display with results
        updateBattleDisplay(result.current_match?.latest_results);

        // Check if match is complete
        if (result.tournament_complete) {
            showVictoryScreen(result.champion_name);
        } else if (result.current_match?.is_complete) {
            document.getElementById('next-match-btn').style.display = 'block';
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

    // Update creature info
    document.getElementById('p1-name').textContent = match.creature1_name;
    document.getElementById('p1-hp').textContent = `HP: ${match.creature1_hp}/${match.creature1_max_hp}`;
    updateHPBar('p1', match.creature1_hp, match.creature1_max_hp);

    document.getElementById('p2-name').textContent = match.creature2_name;
    document.getElementById('p2-hp').textContent = `HP: ${match.creature2_hp}/${match.creature2_max_hp}`;
    updateHPBar('p2', match.creature2_hp, match.creature2_max_hp);

    // Update round number
    document.getElementById('round-number').textContent = match.current_round + 1;

    // Update ASCII art (placeholder)
    document.getElementById('p1-ascii').textContent = CREATURE_ASCII.default;
    document.getElementById('p2-ascii').textContent = CREATURE_ASCII.default;

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

        if (result.tournament_complete) {
            showVictoryScreen(result.champion_name);
        } else {
            gameState.currentMatch = result.current_match;
            document.getElementById('battle-messages').innerHTML = '';
            document.getElementById('next-match-btn').style.display = 'none';
            document.querySelectorAll('.move-btn').forEach(btn => btn.disabled = false);
            updateBattleDisplay();
        }
    } catch (error) {
        console.error('Error loading match:', error);
    }
}

// Show victory screen
function showVictoryScreen(championName) {
    switchScreen('victory-screen');
    document.getElementById('champion-name').textContent = championName;
    document.getElementById('champion-ascii').textContent = CREATURE_ASCII.default;
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
        creatureId: null,
        gameId: null,
        currentMatch: null
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

    switchScreen('setup-screen');
}
