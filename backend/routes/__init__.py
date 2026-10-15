"""
Routes package for FastAPI backend.
"""

from backend.routes.assistant import router as assistant_router
from backend.routes.memories import router as memories_router
from backend.routes.memory_ops import router as memory_ops_router
from backend.routes.system import router as system_router

__all__ = [
    "memories_router",
    "memory_ops_router",
    "assistant_router",
    "system_router",
]
