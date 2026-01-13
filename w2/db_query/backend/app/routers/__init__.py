"""API routers."""

from fastapi import APIRouter

from app.routers import databases

api_router = APIRouter()

# Include all routers
api_router.include_router(databases.router, prefix="/dbs", tags=["databases"])
