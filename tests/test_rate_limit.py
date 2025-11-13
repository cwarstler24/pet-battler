import pytest
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.backend.middleware.rate_limit import RateLimitMiddleware

class DummyApp:
    async def __call__(self, scope, receive, send):
        pass

class DummyRequest:
    def __init__(self, host):
        self.client = type('client', (), {'host': host})

@pytest.mark.asyncio
async def test_rate_limit_typical():
    app = DummyApp()
    middleware = RateLimitMiddleware(app, requests_per_minute=2)
    request = DummyRequest("127.0.0.1")
    async def call_next(req):
        return "ok"
    # First request
    response = await middleware.dispatch(request, call_next)
    assert response == "ok"
    # Second request
    response = await middleware.dispatch(request, call_next)
    assert response == "ok"

@pytest.mark.asyncio
async def test_rate_limit_exceeded():
    app = DummyApp()
    middleware = RateLimitMiddleware(app, requests_per_minute=1)
    request = DummyRequest("127.0.0.1")
    async def call_next(req):
        return "ok"
    await middleware.dispatch(request, call_next)
    with pytest.raises(Exception):
        await middleware.dispatch(request, call_next)

@pytest.mark.asyncio
async def test_rate_limit_different_ips():
    app = DummyApp()
    middleware = RateLimitMiddleware(app, requests_per_minute=1)
    request1 = DummyRequest("127.0.0.1")
    request2 = DummyRequest("192.168.1.1")
    async def call_next(req):
        return "ok"
    await middleware.dispatch(request1, call_next)
    await middleware.dispatch(request2, call_next)

@pytest.mark.asyncio
async def test_rate_limit_null_ip():
    app = DummyApp()
    middleware = RateLimitMiddleware(app, requests_per_minute=1)
    request = DummyRequest(None)
    async def call_next(req):
        return "ok"
    response = await middleware.dispatch(request, call_next)
    assert response == "ok"

@pytest.mark.asyncio
async def test_rate_limit_zero_limit():
    app = DummyApp()
    middleware = RateLimitMiddleware(app, requests_per_minute=0)
    request = DummyRequest("127.0.0.1")
    async def call_next(req):
        return "ok"
    with pytest.raises(Exception):
        await middleware.dispatch(request, call_next)
