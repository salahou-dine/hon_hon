import secrets
from fastapi import APIRouter, Depends

from app.core.security import create_access_token
from app.api.deps import get_current_user
from app.schemas.auth import TokenResponse, MeResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/guest", response_model=TokenResponse)
def create_guest_token():
    """
    Crée un token guest.
    Utilise un identifiant aléatoire pour distinguer les sessions.
    """
    guest_id = f"guest:{secrets.token_urlsafe(12)}"
    token = create_access_token(subject=guest_id, payload={"role": "guest"})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(user: dict = Depends(get_current_user)):
    """
    Test endpoint: renvoie qui tu es (guest ou user).
    """
    return MeResponse(id=user["id"], type=user["type"])
