import secrets
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import TokenResponse, MeResponse, RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

def ensure_user_table(db: Session) -> None:
    bind = db.get_bind()
    if not inspect(bind).has_table(User.__tablename__):
        User.__table__.create(bind=bind, checkfirst=True)


@router.post("/guest", response_model=TokenResponse)
def create_guest_token():
    """
    Crée un token guest.
    Utilise un identifiant aléatoire pour distinguer les sessions.
    """
    guest_id = f"guest:{secrets.token_urlsafe(12)}"
    token = create_access_token(subject=guest_id, payload={"role": "guest"})
    return TokenResponse(access_token=token)

@router.post("/register", response_model=TokenResponse)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    ensure_user_table(db)
    email = payload.email.strip().lower()

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user_id = f"user:{uuid4()}"
    user = User(
        id=user_id,
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        email=email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()

    token = create_access_token(
        subject=user.id,
        payload={
            "role": "user",
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    )
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    ensure_user_table(db)
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(
        subject=user.id,
        payload={
            "role": "user",
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(user: dict = Depends(get_current_user)):
    """
    Test endpoint: renvoie qui tu es (guest ou user).
    """
    claims = user.get("claims", {})
    return MeResponse(
        id=user["id"],
        type=user["type"],
        email=claims.get("email"),
        first_name=claims.get("first_name"),
        last_name=claims.get("last_name"),
    )
