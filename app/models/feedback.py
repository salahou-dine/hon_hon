from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, Index
from datetime import datetime
from app.core.database import Base  # adapte si ton Base est ailleurs

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)

    item_id = Column(String, index=True, nullable=False)     # ex: restaurant_paris_snack_express
    category = Column(String, index=True, nullable=False)    # hotel/restaurant/activity/transport
    city = Column(String, index=True, nullable=False)        # paris
    action = Column(String, nullable=False)                  # like/dislike

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "item_id", name="uq_feedback_user_item"),
        Index("ix_feedback_user_city_cat", "user_id", "city", "category"),
    )
