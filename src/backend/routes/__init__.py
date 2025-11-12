"""
API routes for the Pet Battler game.
"""

from .creature_routes import router as creature_router
from .game_routes import router as game_router

__all__ = ["creature_router", "game_router"]
