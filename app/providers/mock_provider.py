import random
from typing import Optional
from app.providers.base import DestinationProvider
from app.schemas.destination import DestinationItem

# Quelques templates de données réalistes (MVP) — enrichi
MOCK_DB = {
    "hotel": [
        # € (low) — plusieurs options pour éviter listes vides
        ("Budget Inn", "22 Rue Éco", "€"),
        ("Eco Lodge", "9 Rue Simple", "€"),
        ("City Hostel", "3 Rue Centrale", "€"),
        ("Cheap Stay", "14 Avenue Populaire", "€"),
        ("Simple Rooms", "18 Bd Urbain", "€"),

        # €€ (mid)
        ("Hôtel Central", "12 Rue du Centre", "€€"),
        ("Riad Atlas", "4 Derb Tradition", "€€"),
        ("Comfort Hotel", "6 Avenue Calme", "€€"),
        ("Medina Stay", "11 Rue Kasbah", "€€"),

        # €€€ (high)
        ("Skyline Hotel", "8 Avenue Panorama", "€€€"),
        ("Business Suites", "1 Bd Affaires", "€€€"),
        ("Grand Palace", "2 Avenue Prestige", "€€€"),
    ],

    "restaurant": [
        # € (low)
        ("Street Bites", "2 Place Populaire", "€"),
        ("Snack Express", "7 Rue Marché", "€"),
        ("Souk Grill", "1 Rue Souk", "€"),
        ("Pasta Corner", "13 Rue Étudiante", "€"),

        # €€ (mid)
        ("Café Medina", "17 Rue Ancienne", "€€"),
        ("Sea & Spice", "10 Avenue du Port", "€€"),
        ("Vegan Corner", "19 Rue Verte", "€€"),
        ("Brasserie du Centre", "4 Bd Central", "€€"),

        # €€€ (high)
        ("Le Gourmet", "5 Rue des Saveurs", "€€€"),
        ("Chef’s Table", "8 Avenue Luxe", "€€€"),
    ],

    "activity": [
        # € (low)
        ("Musée National", "3 Avenue Culture", "€"),
        ("City Walk (Free Tour)", "Point de départ Centre", "€"),
        ("Parc & Jardin", "Boulevard Verdure", "€"),

        # €€ (mid)
        ("Tour City View", "1 Place Horizon", "€€"),
        ("Atelier Cuisine", "6 Rue Atelier", "€€"),
        ("Excursion Nature", "Route des Montagnes", "€€"),
        ("Croisière Sunset", "Quai Principal", "€€"),

        # €€€ (high)
        ("Spectacle Soirée", "12 Avenue Arts", "€€€"),
        ("Experience VIP", "Avenue Prestige", "€€€"),
    ],

    "transport": [
        # € (low)
        ("Navette Aéroport", "Terminal Arrivées", "€"),
        ("Métro / Tram", "Station Centrale", "€"),
        ("Bus Urbain", "Arrêt Principal", "€"),

        # €€ (mid)
        ("Taxi Officiel", "Zone taxis", "€€"),
        ("VTC", "Point de prise", "€€"),
        ("Transfert Privé", "Réservation en ligne", "€€"),

        # €€€ (high)
        ("Location Voiture", "Agence Centre", "€€€"),
        ("Chauffeur Premium", "Service sur demande", "€€€"),
    ],
}

# Mapping budget — plus réaliste et plus agréable en UX
BUDGET_MAP = {
    "low": {"€"},
    "mid": {"€", "€€"},
    "high": {"€€", "€€€"},
}



class MockDestinationProvider(DestinationProvider):
    async def search(
        self,
        city: str,
        category: str,
        budget: Optional[str] = None,
        limit: int = 10,
    ) -> list[DestinationItem]:
        category = category.lower().strip()

        if category not in MOCK_DB:
            return []

        candidates = MOCK_DB[category]

        # Filtre budget
        if budget:
            budget = budget.lower().strip()
            allowed = BUDGET_MAP.get(budget)
            if allowed:
                candidates = [c for c in candidates if c[2] in allowed]

        # Génération d'items "uniques" et réalistes
        items: list[DestinationItem] = []
        random.shuffle(candidates)

        for i, (name, address, price) in enumerate(candidates):

            rating = round(random.uniform(3.6, 4.9), 1)
            distance_km = round(random.uniform(0.3, 6.5), 1)

            items.append(
                DestinationItem(
                    id=f"{category}_{city.lower().replace(' ', '_')}_{name.lower().replace(' ', '_')}",
                    category=category,
                    name=f"{name} — {city}",
                    rating=rating,
                    price_level=price,
                    distance_km=distance_km,
                    address=f"{address}, {city}",
                    image_url=(
                        f"https://picsum.photos/seed/"
                        f"{category}_{city.lower().replace(' ', '_')}_"
                        f"{name.lower().replace(' ', '_')}/400/250"
                    ),
                    source="mock",
                    link=None,
                )
            )

        # Tri utile UX: proches d'abord, puis meilleure note
        items.sort(key=lambda x: (x.distance_km, -x.rating))
        return items[:limit]
