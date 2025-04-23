from fastapi import APIRouter
from .healthcheck import router as healthcheck_router
from .slack import router as slack_router
from .genie import router as genie_router

router = APIRouter()
router.include_router(healthcheck_router)
router.include_router(slack_router)
router.include_router(genie_router)
