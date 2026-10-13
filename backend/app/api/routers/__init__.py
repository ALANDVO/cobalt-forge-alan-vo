from app.api.routers.auth import router as auth_router
from app.api.routers.sessions import router as sessions_router
from app.api.routers.decisions import router as decisions_router
from app.api.routers.prds import router as prds_router
from app.api.routers.issues import router as issues_router
from app.api.routers.verification import router as verification_router

__all__ = [
    "auth_router",
    "sessions_router",
    "decisions_router",
    "prds_router",
    "issues_router",
    "verification_router",
]