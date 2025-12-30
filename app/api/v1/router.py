from fastapi import APIRouter
from app.core.config import settings
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.destinations import router as destinations_router
from app.api.v1.privacy import router as privacy_router
from app.api.v1.preferences import router as preferences_router
from app.api.v1.my_trips import router as my_trips_router
from app.api.v1.travel_info import router as travel_info_router

from app.api.v1.auth import router as auth_router
from app.api.v1.bookings import router as bookings_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(bookings_router)
router.include_router(recommendations_router)
router.include_router(destinations_router)
router.include_router(privacy_router)
router.include_router(preferences_router)
router.include_router(my_trips_router)
router.include_router(travel_info_router)



@router.get("/health", tags=["health"])
def health():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENV}
