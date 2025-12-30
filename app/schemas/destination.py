from pydantic import BaseModel, Field


class DestinationItem(BaseModel):
    id: str
    category: str  # hotel / restaurant / activity / transport
    name: str
    rating: float = Field(ge=0, le=5)
    price_level: str  # € / €€ / €€€
    distance_km: float = Field(ge=0)
    address: str

    # ⬇️ NOUVEAUX CHAMPS
    image_url: str | None = None
    source: str = "mock"

    link: str | None = None


class DestinationRecoResponse(BaseModel):
    city: str
    category: str
    budget: str | None = None
    limit: int
    count: int
    items: list[DestinationItem]
