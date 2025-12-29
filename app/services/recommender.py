from typing import Any
from app.services.scoring import ScoreSummary


def card(
    id: str,
    type: str,
    title: str,
    subtitle: str,
    why: str,
    tags: list[str],
    confidence: float,
    cta_label: str,
    cta_action: str,
) -> dict[str, Any]:
    return {
        "id": id,
        "type": type,
        "title": title,
        "subtitle": subtitle,
        "why": why,
        "tags": tags,
        "confidence": confidence,
        "cta": {"label": cta_label, "action": cta_action},
    }


def build_post_booking_cards(scores: ScoreSummary, cabin: str) -> list[dict]:
    cards: list[dict] = []

    # 1) Confort / siège si long + eco
    if scores.trip_type == "long" and cabin.lower() == "economy":
        cards.append(
            card(
                id="seat_plus",
                type="upsell",
                title="Siège avec plus d’espace",
                subtitle="Plus de confort sur votre vol long-courrier",
                why="Vol long + cabine économique → confort recommandé",
                tags=["Confort", "Vol long"],
                confidence=0.78,
                cta_label="Voir options",
                cta_action="OPEN_SEAT_MAP",
            )
        )

    # 2) Fast Track si churn risk medium/high (stress aéroport)
    if scores.churn_risk in ("medium", "high"):
        cards.append(
            card(
                id="fast_track",
                type="service",
                title="Accès Fast Track",
                subtitle="Réduisez l’attente aux contrôles",
                why="Risque d’insatisfaction estimé → réduire les frictions à l’aéroport",
                tags=["Aéroport", "Gain de temps"],
                confidence=0.70,
                cta_label="Ajouter",
                cta_action="ADD_FAST_TRACK",
            )
        )

    # 3) Bagage si medium/long (heuristique)
    if scores.trip_type in ("medium", "long"):
        cards.append(
            card(
                id="extra_baggage",
                type="upsell",
                title="Bagage supplémentaire",
                subtitle="Plus simple pour un séjour de plusieurs jours",
                why="Durée estimée du voyage → probabilité de besoin de bagage ↑",
                tags=["Pratique"],
                confidence=0.62,
                cta_label="Voir tarifs",
                cta_action="OPEN_BAGGAGE_OPTIONS",
            )
        )

    # 4) Lounge si motive business assez élevé
    business_p = scores.motive_prob.get("business", 0.0)
    if business_p >= 0.6:
        cards.append(
            card(
                id="lounge",
                type="service",
                title="Salon (Lounge) avant embarquement",
                subtitle="Espace calme, wifi, confort",
                why="Motif probable business → attente de confort et productivité",
                tags=["Business", "Confort"],
                confidence=business_p,
                cta_label="Découvrir",
                cta_action="OPEN_LOUNGE_INFO",
            )
        )

    # Limite UX: max 5 cartes
    return cards[:5]
