from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.consent import Consent
from app.schemas.privacy import ConsentUpsert, ConsentOut

router = APIRouter(prefix="/privacy", tags=["privacy"])


@router.get("/consent", response_model=ConsentOut)
def get_consent(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(Consent).filter(Consent.user_id == user["id"]).first()
    if not row:
        row = Consent(user_id=user["id"], destination_recos_enabled=True)
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


@router.post("/consent", response_model=ConsentOut)
def upsert_consent(
    payload: ConsentUpsert,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = db.query(Consent).filter(Consent.user_id == user["id"]).first()
    if not row:
        row = Consent(user_id=user["id"], destination_recos_enabled=payload.destination_recos_enabled)
        db.add(row)
    else:
        row.destination_recos_enabled = payload.destination_recos_enabled

    db.commit()
    db.refresh(row)
    return row
