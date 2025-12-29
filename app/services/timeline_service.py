from datetime import date, timedelta
from app.models.booking import Booking


def compute_phase(today: date, depart: date, ret: date | None) -> str:
    # repères
    d_minus_7 = depart - timedelta(days=7)
    d_minus_1 = depart - timedelta(days=1)

    if today < d_minus_7:
        return "pre_departure"
    if d_minus_7 <= today <= d_minus_1:
        return "check_in"
    if today == depart:
        return "departure_day"

    # Si one-way (pas de return_date)
    if ret is None:
        # après départ, on considère arrivée puis séjour quelques jours
        if depart < today <= depart + timedelta(days=1):
            return "arrival"
        if today <= depart + timedelta(days=5):
            return "stay"
        return "post_trip"

    # roundtrip
    if depart < today <= depart + timedelta(days=1):
        return "arrival"
    if depart + timedelta(days=2) <= today <= ret:
        return "stay"
    if today > ret:
        return "post_trip"

    # fallback
    return "pre_departure"


def build_steps(current: str) -> list[dict]:
    # mapping des phases -> contenu UI
    steps = [
        {
            "phase": "pre_departure",
            "title": "Pré-départ",
            "description": "Préparez votre voyage : documents, bagages, options de confort.",
            "actions": ["OPEN_POST_BOOKING_RECO", "OPEN_BAGGAGE_OPTIONS", "OPEN_SEAT_MAP"],
        },
        {
            "phase": "check_in",
            "title": "Check-in",
            "description": "Finalisez avant le départ : check-in, infos aéroport, fast track.",
            "actions": ["OPEN_CHECKIN_INFO", "ADD_FAST_TRACK", "OPEN_AIRPORT_TIPS"],
        },
        {
            "phase": "departure_day",
            "title": "Jour du départ",
            "description": "Derniers rappels : porte d’embarquement, temps d’attente, services.",
            "actions": ["OPEN_AIRPORT_TIPS", "ADD_FAST_TRACK", "OPEN_LOUNGE_INFO"],
        },
        {
            "phase": "arrival",
            "title": "Arrivée",
            "description": "À votre arrivée : transport, hôtel, restaurants, activités.",
            "actions": ["OPEN_ARRIVAL_RECO"],  # => /destinations/arrival
        },
        {
            "phase": "stay",
            "title": "Séjour",
            "description": "Profitez : activités, restaurants, retours pour améliorer vos recommandations.",
            "actions": ["OPEN_ARRIVAL_RECO", "OPEN_FEEDBACK"],
        },
        {
            "phase": "post_trip",
            "title": "Après le voyage",
            "description": "Aidez-nous à améliorer : feedback global, préférences, récapitulatif.",
            "actions": ["OPEN_FEEDBACK", "OPEN_PREFERENCES"],
        },
    ]

    for s in steps:
        s["active"] = (s["phase"] == current)

    return steps


def build_timeline(booking: Booking, today: date) -> dict:
    current = compute_phase(today=today, depart=booking.depart_date, ret=booking.return_date)
    steps = build_steps(current)

    return {
        "booking_id": booking.id,
        "destination": booking.destination,
        "origin": booking.origin,
        "trip_type": booking.trip_type,
        "cabin": booking.cabin,
        "status": current,
        "dates": {
            "depart_date": booking.depart_date,
            "return_date": booking.return_date,
        },
        "steps": steps,
    }
