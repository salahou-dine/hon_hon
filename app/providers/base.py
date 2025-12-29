from abc import ABC, abstractmethod
from typing import Optional

from app.schemas.destination import DestinationItem


class DestinationProvider(ABC):
    @abstractmethod
    async def search(
        self,
        city: str,
        category: str,
        budget: Optional[str] = None,  # low / mid / high
        limit: int = 10,
    ) -> list[DestinationItem]:
        raise NotImplementedError
