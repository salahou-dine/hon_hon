from datetime import date
from pydantic import BaseModel, Field, EmailStr


class BookingCreate(BaseModel):
    destination: str = Field(..., examples=["Paris"])
    depart_date: date
    return_date: date | None = None

    origin: str = "CMN"
    trip_type: str = "roundtrip"  # roundtrip/oneway
    cabin: str = "economy"        # economy/business

    # Informations personnelles (optionnelles pour la première étape)
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    email: EmailStr | None = None


class BookingOut(BaseModel):
    id: str
    owner_id: str
    origin: str
    destination: str
    trip_type: str
    cabin: str
    depart_date: date
    return_date: date | None

    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    email: str | None = None

    class Config:
        from_attributes = True
