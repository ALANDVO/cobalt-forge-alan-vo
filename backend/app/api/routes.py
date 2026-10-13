from fastapi import APIRouter
from app.api.routers.auth import router as auth_router
from app.api.routers.sessions import router as sessions_router
from app.api.routers.decisions import router as decisions_router
from app.api.routers.prds import router as prds_router
from app.api.routers.issues import router as issues_router
from app.api.routers.verification import router as verification_router


router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(sessions_router)
router.include_router(decisions_router)
router.include_router(prds_router)
router.include_router(issues_router)
router.include_router(verification_router)


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cobalt-forge"}