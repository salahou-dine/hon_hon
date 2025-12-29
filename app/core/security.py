from datetime import datetime, timedelta
from typing import Any, Optional

from jose import jwt
from app.core.config import settings


def create_access_token(subject: str, payload: Optional[dict[str, Any]] = None) -> str:
    """
    Crée un JWT signé.
    - subject: identifiant principal (ex: "guest:abc123" ou "user:42")
    - payload: infos additionnelles (ex: role, scopes, etc.)
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN)

    to_encode: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    if payload:
        to_encode.update(payload)

    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGO)
    return token


def decode_token(token: str) -> dict[str, Any]:
    """
    Décode et vérifie signature + expiration.
    Lève une exception si token invalide.
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
