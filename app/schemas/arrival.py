from pydantic import BaseModel
from app.schemas.destination import DestinationItem


class ArrivalResponse(BaseModel):
    city: str
    budget: str | None
    interests: list[str]
    sections: dict[str, list[DestinationItem]]
