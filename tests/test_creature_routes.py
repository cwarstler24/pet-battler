import pytest
from fastapi.testclient import TestClient
from src.backend.app import app

client = TestClient(app)

def test_get_creature_types():
    resp = client.get("/creatures/types")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert any("type" in t for t in resp.json())

def test_create_creature_typical():
    resp = client.post("/creatures", json={
        "name": "TestCreature",
        "creature_type": "DRAGON",
        "stat_allocations": {"speed": 1, "health": 2, "defense": 1, "strength": 2, "luck": 0}
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["name"] == "TestCreature"
    assert data["creature_type"] == "DRAGON"
    assert data["current_hp"] == data["max_hp"]

def test_create_creature_invalid_points():
    resp = client.post("/creatures", json={
        "name": "TestCreature",
        "creature_type": "DRAGON",
        "stat_allocations": {"speed": 10, "health": 10, "defense": 10, "strength": 10, "luck": 10}
    })
    assert resp.status_code == 400

def test_get_creature_not_found():
    resp = client.get("/creatures/invalid_id")
    assert resp.status_code == 404

def test_list_creatures():
    resp = client.get("/creatures")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
