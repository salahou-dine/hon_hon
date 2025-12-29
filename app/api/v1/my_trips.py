from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.booking import Booking
from app.schemas.timeline import TimelineResponse
from app.services.timeline_service import build_timeline


router = APIRouter(prefix="/my-trips", tags=["my-trips"])


def pick_active_or_next_booking(db: Session, owner_id: str, today: date) -> Booking | None:
    # 1) Prochain voyage (depart >= today) le plus proche
    next_b = (
        db.query(Booking)
        .filter(Booking.owner_id == owner_id, Booking.depart_date >= today)
        .order_by(Booking.depart_date.asc())
        .first()
    )
    if next_b:
        return next_b

    # 2) Sinon, dernier voyage passé (le plus récent)
    last_b = (
        db.query(Booking)
        .filter(Booking.owner_id == owner_id)
        .order_by(Booking.depart_date.desc())
        .first()
    )
    return last_b


@router.get("/timeline", response_model=TimelineResponse)
def timeline_current_or_next(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    booking = pick_active_or_next_booking(db=db, owner_id=user["id"], today=today)

    if not booking:
        raise HTTPException(status_code=404, detail="No bookings found for this user")

    return build_timeline(booking=booking, today=today)


@router.get("/{booking_id}/timeline", response_model=TimelineResponse)
def timeline_for_booking(
    booking_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.owner_id != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return build_timeline(booking=booking, today=date.today())
