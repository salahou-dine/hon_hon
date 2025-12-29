from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.preference import Preference
from app.schemas.preference import PreferenceUpsert, PreferenceOut

router = APIRouter(prefix="/preferences", tags=["preferences"])

ALLOWED_BUDGETS = {"low", "mid", "high"}


@router.get("", response_model=PreferenceOut)
def get_preferences(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(Preference).filter(Preference.user_id == user["id"]).first()
    if not row:
        row = Preference(user_id=user["id"], budget="mid", interests="")
        db.add(row)
        db.commit()
        db.refresh(row)

    interests_list = [x for x in row.interests.split(",") if x.strip()] if row.interests else []
    return {"user_id": row.user_id, "budget": row.budget, "interests": interests_list}


@router.post("", response_model=PreferenceOut)
def upsert_preferences(
    payload: PreferenceUpsert,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    budget = payload.budget.lower().strip()
    if budget not in ALLOWED_BUDGETS:
        budget = "mid"

    interests_clean = [i.lower().strip() for i in payload.interests if i.strip()]
    interests_csv = ",".join(sorted(set(interests_clean)))

    row = db.query(Preference).filter(Preference.user_id == user["id"]).first()
    if not row:
        row = Preference(user_id=user["id"], budget=budget, interests=interests_csv)
        db.add(row)
    else:
        row.budget = budget
        row.interests = interests_csv

    db.commit()
    db.refresh(row)

    return {"user_id": row.user_id, "budget": row.budget, "interests": interests_clean}
