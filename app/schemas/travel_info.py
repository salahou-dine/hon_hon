from datetime import date
from pydantic import BaseModel


class TravelInfoItem(BaseModel):
    id: str
    title: str
    description: str
    tag: str | None = None


class TravelInfoResponse(BaseModel):
    booking_id: str | None = None
    phase: str
    title: str
    subtitle: str
    origin: str | None = None
    destination: str | None = None
    depart_date: date | None = None
    checklist: list[TravelInfoItem]
    tips: list[TravelInfoItem]
    services: list[TravelInfoItem]
