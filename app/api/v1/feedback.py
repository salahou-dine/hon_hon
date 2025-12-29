from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.feedback import FeedbackCreate, FeedbackOut
from app.models.feedback import Feedback
from app.api.deps import get_current_user
from app.core.database import get_db

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("", response_model=FeedbackOut)
def upsert_feedback(
    payload: FeedbackCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    uid = user["id"]
    # Normaliser city en lowercase pour cohérence
    city_clean = payload.city.strip().lower()

    existing = (
        db.query(Feedback)
        .filter(Feedback.user_id == uid, Feedback.item_id == payload.item_id)
        .first()
    )

    if existing:
        existing.action = payload.action
        existing.category = payload.category
        existing.city = city_clean
        db.add(existing)
    else:
        fb = Feedback(
            user_id=uid,
            item_id=payload.item_id,
            category=payload.category,
            city=city_clean,
            action=payload.action,
        )
        db.add(fb)

    db.commit()

    return {
        "user_id": uid,
        "item_id": payload.item_id,
        "category": payload.category,
        "city": city_clean,
        "action": payload.action,
    }
