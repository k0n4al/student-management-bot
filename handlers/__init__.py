from .commands import router as commands_router
from .admin import router as admin_router
from .profile import router as profile_router

__all__ = ["commands_router", "admin_router", "profile_router"]
