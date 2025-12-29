from pydantic import BaseModel, Field
from typing import Literal

class FeedbackCreate(BaseModel):
    item_id: str = Field(..., min_length=3)
    category: Literal["hotel", "restaurant", "activity", "transport"]
    city: str = Field(..., min_length=2)
    action: Literal["like", "dislike"]

class FeedbackOut(BaseModel):
    user_id: str
    item_id: str
    category: str
    city: str
    action: str
