from fastapi import APIRouter
from datetime import datetime, timezone
from typing import Dict

router = APIRouter()

@router.get("/healthcheck")
async def healthcheck() -> Dict[str, str]:
    return {"status": "OK", "timestamp": datetime.now(timezone.utc).isoformat()}

