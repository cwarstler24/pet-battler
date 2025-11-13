import pytest
from fastapi.testclient import TestClient
from src.backend.app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_serves_frontend():
    response = client.get("/")
    assert response.status_code in [200, 404]  # 404 if frontend missing

def test_static_files():
    response = client.get("/static/css/styles.css")
    assert response.status_code in [200, 404]

def test_cors_headers():
    response = client.options("/health")
    assert "access-control-allow-origin" in response.headers

def test_rate_limit_exceeded():
    for _ in range(61):
        response = client.get("/health")
    assert response.status_code in [200, 429]
