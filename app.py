# app.py (main entrypoint)
from fastapi import FastAPI
from routes.v1.genie import router as genie_router
from routes.v1.slack import router as slack_router
from routes.v1.healthcheck import router as healthcheck_router

app = FastAPI()

app.include_router(healthcheck_router, prefix="/api/v1")
app.include_router(genie_router, prefix="/api/v1")
app.include_router(slack_router, prefix="/api/v1")

