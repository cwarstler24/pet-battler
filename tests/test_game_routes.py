import pytest
from fastapi.testclient import TestClient
from src.backend.app import app

client = TestClient(app)

def test_game_start_typical():
    # Create a creature first
    create_resp = client.post("/creatures", json={
        "name": "TestCreature",
        "creature_type": "DRAGON",
        "stat_allocations": {"speed": 1, "health": 2, "defense": 1, "strength": 2, "luck": 0}
    })
    assert create_resp.status_code == 201
    creature_id = create_resp.json()["id"]
    # Start game
    start_resp = client.post("/game/start", json={
        "num_players": 1,
        "creature_ids": [creature_id],
        "tournament_size": 4
    })
    assert start_resp.status_code == 200
    assert "game_id" in start_resp.json()

def test_game_start_invalid_creature():
    resp = client.post("/game/start", json={
        "num_players": 1,
        "creature_ids": ["invalid_id"],
        "tournament_size": 4
    })
    assert resp.status_code == 404

def test_game_start_invalid_size():
    # Create a creature first
    create_resp = client.post("/creatures", json={
        "name": "TestCreature2",
        "creature_type": "DRAGON",
        "stat_allocations": {"speed": 1, "health": 2, "defense": 1, "strength": 2, "luck": 0}
    })
    creature_id = create_resp.json()["id"]
    resp = client.post("/game/start", json={
        "num_players": 1,
        "creature_ids": [creature_id],
        "tournament_size": 5
    })
    assert resp.status_code == 400

def test_game_state_not_found():
    resp = client.get("/game/invalid_id/state")
    assert resp.status_code == 404

def test_allocate_stats_invalid_points():
    # Create a creature first
    create_resp = client.post("/creatures", json={
        "name": "TestCreature3",
        "creature_type": "DRAGON",
        "stat_allocations": {"speed": 1, "health": 2, "defense": 1, "strength": 2, "luck": 0}
    })
    creature_id = create_resp.json()["id"]
    # Start game
    start_resp = client.post("/game/start", json={
        "num_players": 1,
        "creature_ids": [creature_id],
        "tournament_size": 4
    })
    game_id = start_resp.json()["game_id"]
    resp = client.post(f"/game/{game_id}/allocate-stats", json={
        "creature_id": creature_id,
        "stat_allocations": {"speed": 3, "health": 1}  # 4 points
    })
    assert resp.status_code == 400
