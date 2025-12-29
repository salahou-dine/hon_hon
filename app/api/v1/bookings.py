import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingOut

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validation simple: si oneway => return_date doit être None
    if payload.trip_type == "oneway" and payload.return_date is not None:
        raise HTTPException(status_code=422, detail="return_date must be null for oneway trips")

    booking = Booking(
        id=str(uuid.uuid4()),
        owner_id=user["id"],
        origin=payload.origin,
        destination=payload.destination,
        trip_type=payload.trip_type,
        cabin=payload.cabin,
        depart_date=payload.depart_date,
        return_date=payload.return_date,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Sécurité: un guest ne peut lire que ses bookings
    if booking.owner_id != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return booking
