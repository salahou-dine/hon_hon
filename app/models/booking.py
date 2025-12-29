from datetime import datetime, date
from sqlalchemy import String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)

    # MVP: on associe un booking à un "owner" (guest:user id)
    owner_id: Mapped[str] = mapped_column(String(120), index=True)

    origin: Mapped[str] = mapped_column(String(10), default="CMN")  # Casablanca par défaut
    destination: Mapped[str] = mapped_column(String(80), index=True)

    trip_type: Mapped[str] = mapped_column(String(20), default="roundtrip")  # roundtrip/oneway
    cabin: Mapped[str] = mapped_column(String(20), default="economy")  # economy/business

    depart_date: Mapped[date] = mapped_column(Date)
    return_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
