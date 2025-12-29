from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.booking import Booking
from app.schemas.recommendation import PostBookingRecoResponse
from app.services.scoring import compute_scores
from app.services.recommender import build_post_booking_cards

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/post-booking", response_model=PostBookingRecoResponse)
def post_booking_recommendations(
    booking_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.owner_id != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    # MVP: age_bucket et loyalty non stockés pour l’instant => None
    scores = compute_scores(
        depart_date=booking.depart_date,
        return_date=booking.return_date,
        cabin=booking.cabin,
        age_bucket=None,
        loyalty=None,
    )

    cards = build_post_booking_cards(scores=scores, cabin=booking.cabin)

    return {
        "booking_id": booking.id,
        "summary": {
            "trip_type": scores.trip_type,
            "churn_risk": scores.churn_risk,
            "motive_prob": scores.motive_prob,
        },
        "cards": cards,
    }
