from datetime import date
from dataclasses import dataclass


@dataclass
class ScoreSummary:
    trip_type: str  # short / medium / long
    churn_risk: str  # low / medium / high
    motive_prob: dict  # {"leisure": 0.7, "business": 0.3}


def days_between(d1: date, d2: date) -> int:
    return abs((d2 - d1).days)


def infer_trip_type(depart: date, ret: date | None) -> str:
    # Heuristique MVP : si pas de retour -> "medium" par défaut
    if ret is None:
        return "medium"

    duration = days_between(depart, ret)
    if duration <= 3:
        return "short"
    if duration <= 10:
        return "medium"
    return "long"


def infer_motive_prob(age_bucket: str | None) -> dict:
    """
    MVP: on ne veut pas stocker l'âge exact.
    age_bucket: "under_30" / "30_60" / "over_60" / None
    """
    # Par défaut : loisir dominant
    if age_bucket is None:
        return {"leisure": 0.65, "business": 0.35}

    if age_bucket == "30_60":
        return {"leisure": 0.35, "business": 0.65}

    return {"leisure": 0.75, "business": 0.25}


def infer_churn_risk(cabin: str, trip_type: str, loyalty: str | None) -> str:
    """
    Heuristique MVP inspirée de ton analyse:
    - Eco + long => inconfort => risque ↑
    - Disloyal => risque ↑
    """
    score = 0
    if cabin.lower() == "economy":
        score += 2
    if trip_type == "long":
        score += 1
    if loyalty == "disloyal":
        score += 2

    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def compute_scores(
    depart_date: date,
    return_date: date | None,
    cabin: str,
    age_bucket: str | None = None,
    loyalty: str | None = None,
) -> ScoreSummary:
    trip_type = infer_trip_type(depart_date, return_date)
    motive_prob = infer_motive_prob(age_bucket)
    churn_risk = infer_churn_risk(cabin=cabin, trip_type=trip_type, loyalty=loyalty)
    return ScoreSummary(trip_type=trip_type, churn_risk=churn_risk, motive_prob=motive_prob)
