from pydantic import BaseModel, Field


class PreferenceUpsert(BaseModel):
    budget: str = Field(default="mid", description="low/mid/high")
    interests: list[str] = Field(default_factory=list, description="ex: ['food','culture']")


class PreferenceOut(BaseModel):
    user_id: str
    budget: str
    interests: list[str]

    class Config:
        from_attributes = True
