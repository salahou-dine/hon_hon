from datetime import date
from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    destination: str = Field(..., examples=["Paris"])
    depart_date: date
    return_date: date | None = None

    origin: str = "CMN"
    trip_type: str = "roundtrip"  # roundtrip/oneway
    cabin: str = "economy"        # economy/business


class BookingOut(BaseModel):
    id: str
    owner_id: str
    origin: str
    destination: str
    trip_type: str
    cabin: str
    depart_date: date
    return_date: date | None

    class Config:
        from_attributes = True
