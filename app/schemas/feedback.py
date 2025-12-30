from pydantic import BaseModel, Field
from typing import Literal

class FeedbackCreate(BaseModel):
    item_id: str | None = Field(None, min_length=3)
    category: Literal["hotel", "restaurant", "activity", "transport"]
    city: str | None = Field(None, min_length=2)
    booking_id: str | None = None
    action: Literal["like", "dislike", "clicked"]

class FeedbackOut(BaseModel):
    user_id: str
    item_id: str
    category: str
    city: str
    action: str
