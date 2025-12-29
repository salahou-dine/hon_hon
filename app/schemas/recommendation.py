from pydantic import BaseModel


class CTA(BaseModel):
    label: str
    action: str


class RecommendationCard(BaseModel):
    id: str
    type: str
    title: str
    subtitle: str
    why: str
    tags: list[str]
    confidence: float
    cta: CTA


class PostBookingSummary(BaseModel):
    trip_type: str
    churn_risk: str
    motive_prob: dict


class PostBookingRecoResponse(BaseModel):
    booking_id: str
    summary: PostBookingSummary
    cards: list[RecommendationCard]
