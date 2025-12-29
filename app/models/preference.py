from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Preference(Base):
    __tablename__ = "preferences"

    user_id: Mapped[str] = mapped_column(String(120), primary_key=True, index=True)

    # MVP: budget global (low/mid/high) et intérêts en CSV
    budget: Mapped[str] = mapped_column(String(10), default="mid")
    interests: Mapped[str] = mapped_column(String(300), default="")  # ex: "food,culture,nature"

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
