from pydantic import BaseModel


class ConsentUpsert(BaseModel):
    destination_recos_enabled: bool


class ConsentOut(BaseModel):
    user_id: str
    destination_recos_enabled: bool

    class Config:
        from_attributes = True
