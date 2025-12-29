from app.core.config import settings
from app.providers.mock_provider import MockDestinationProvider
from app.providers.base import DestinationProvider


def get_destination_provider() -> DestinationProvider:
    """
    MVP: provider choisi via .env (DEST_PROVIDER=mock).
    Plus tard: places/amadeus/etc.
    """
    if settings.DEST_PROVIDER == "mock":
        return MockDestinationProvider()

    # fallback sécurisé
    return MockDestinationProvider()
