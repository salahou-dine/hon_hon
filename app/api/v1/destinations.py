from fastapi import APIRouter, Depends, Query
from app.api.deps import get_current_user
from app.schemas.destination import DestinationRecoResponse
from app.services.destination_service import get_destination_provider
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.consent import Consent
from fastapi import HTTPException 
from app.models.preference import Preference
from app.schemas.arrival import ArrivalResponse 
from app.models.feedback import Feedback





router = APIRouter(prefix="/destinations", tags=["destinations"])

ALLOWED_CATEGORIES = {"transport", "hotel", "restaurant", "activity"}
ALLOWED_BUDGETS = {"low", "mid", "high"}

def ensure_destination_consent(user_id: str, db: Session) -> None:
    consent = db.query(Consent).filter(Consent.user_id == user_id).first()
    if not consent:
        consent = Consent(user_id=user_id, destination_recos_enabled=True)
        db.add(consent)
        db.commit()
        db.refresh(consent)
    if not consent.destination_recos_enabled:
        raise HTTPException(
            status_code=403,
            detail="Destination recommendations disabled (consent required)",
        )

def ensure_feedback_table(db: Session) -> None:
    bind = db.get_bind()
    if not inspect(bind).has_table(Feedback.__tablename__):
        Feedback.__table__.create(bind=bind, checkfirst=True)


@router.get("/recommendations", response_model=DestinationRecoResponse)
async def destination_recommendations(
    city: str = Query(..., min_length=2),
    category: str = Query(..., description="transport/hotel/restaurant/activity"),
    budget: str | None = Query(None, description="low/mid/high"),
    limit: int = Query(10, ge=1, le=20),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    city_clean = city.strip()
    city_label = city_clean.title()
    ensure_destination_consent(user["id"], db)

    pref = db.query(Preference).filter(Preference.user_id == user["id"]).first()
    interests = []
    if pref and pref.interests:
        interests = [x.strip().lower() for x in pref.interests.split(",") if x.strip()]

    # Si le client n'envoie pas budget => on applique celui des préférences
    if budget is None and pref and pref.budget:
        budget = pref.budget

    # Sécurité/robustesse : validation simple
    category = category.lower().strip()
    if category not in ALLOWED_CATEGORIES:
        return {
            "city": city,
            "category": category,
            "budget": budget,
            "limit": limit,
            "count": 0,
            "items": [],
        }

    if budget is not None:
        budget = budget.lower().strip()
        if budget not in ALLOWED_BUDGETS:
            budget = None  # on ignore un budget invalide plutôt que casser l'expérience

    provider = get_destination_provider()
    items = await provider.search(city=city, category=category, budget=budget, limit=limit)
    
    # ✅ ÉTAPE 1 : Tri "personnalisé" léger basé sur les intérêts (MVP)
    # - food => restaurants prioritaires
    # - culture/nature => activities prioritaires
    boost_interests = False
    if category == "restaurant" and "food" in interests:
        boost_interests = True
    if category == "activity" and ("culture" in interests or "nature" in interests):
        boost_interests = True

    if boost_interests:
        items = sorted(items, key=lambda x: (-x.rating, x.distance_km))
    
    # ✅ ÉTAPE 2 : Appliquer feedback utilisateur (like/dislike) pour personnalisation fine
    uid = user["id"]
    ensure_feedback_table(db)

    feedbacks = (
        db.query(Feedback)
        .filter(
           Feedback.user_id == uid,
           Feedback.city == city_clean.lower(),
           Feedback.category == category,
       )
       .all()
   )

    fb_map = {f.item_id: f.action for f in feedbacks}

    def score(x):
        fb = fb_map.get(x.id)
        boost = 0
        if fb == "like":
            boost = 100
        elif fb == "dislike":
            boost = -100
        # base : rating haut, distance faible
        return (boost, x.rating, -x.distance_km)

    items = sorted(items, key=score, reverse=True)

    return {
        "city": city_label,
        "category": category,
        "budget": budget,
        "limit": limit,
        "count": len(items),
        "items": items
    }

@router.get("/arrival", response_model=ArrivalResponse)
async def arrival_recommendations(
    city: str = Query(..., min_length=2),
    limit_per_category: int = Query(4, ge=1, le=10),
    budget: str | None = Query(None, description="low/mid/high (optional)"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # city formatting
    city_clean = city.strip()
    city_label = city_clean.title()

    # consent required
    ensure_destination_consent(user["id"], db)

    # prefs (budget + interests)
    pref = db.query(Preference).filter(Preference.user_id == user["id"]).first()
    interests = []
    pref_budget = None
    if pref:
        pref_budget = pref.budget
        interests = [x for x in pref.interests.split(",") if x.strip()] if pref.interests else []

    if budget is None:
        budget = pref_budget

    provider = get_destination_provider()

    categories = ["hotel", "restaurant", "transport", "activity"]
    sections = {}
    ensure_feedback_table(db)

    for cat in categories:
        items = await provider.search(
            city=city_clean,
            category=cat,
            budget=budget,
            limit=limit_per_category
        )

        # Priorisation simple selon intérêts (MVP)
        if interests:
            boost = (
                (cat == "restaurant" and "food" in interests) or
                (cat == "activity" and ("culture" in interests or "nature" in interests))
            )
            if boost:
                items = sorted(items, key=lambda x: (-x.rating, x.distance_km))
                # ✅ Appliquer feedback utilisateur (like/dislike)
        uid = user["id"]
        feedbacks = (
            db.query(Feedback)
            .filter(
                Feedback.user_id == uid,
                Feedback.city == city_clean.lower(),
                Feedback.category == cat,
            )
            .all()
        )

        fb_map = {f.item_id: f.action for f in feedbacks}

        def score(x):
            fb = fb_map.get(x.id)
            boost = 0
            if fb == "like":
                boost = 100
            elif fb == "dislike":
                boost = -100
               # base : rating haut, distance faible
            return (boost, x.rating, -x.distance_km)

        items = sorted(items, key=score, reverse=True)

        sections[cat] = items

    return {
        "city": city_label,
        "budget": budget,
        "interests": interests,
        "sections": sections,
    }
