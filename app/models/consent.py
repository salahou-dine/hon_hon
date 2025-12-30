from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Consent(Base):
    __tablename__ = "consents"

    # 1 enregistrement par utilisateur (guest:user id)
    user_id: Mapped[str] = mapped_column(String(120), primary_key=True, index=True)

    # Opt-in pour recos destination (données externes)
    destination_recos_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
