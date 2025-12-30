from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.booking import Booking
from app.schemas.travel_info import TravelInfoResponse, TravelInfoItem

router = APIRouter(prefix="/travel-info", tags=["travel-info"])


def get_booking_or_none(
    booking_id: str | None,
    user_id: str,
    db: Session,
) -> Booking | None:
    if not booking_id:
        return None
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return booking


def build_check_in_response(booking: Booking | None) -> TravelInfoResponse:
    checklist = [
        TravelInfoItem(
            id="doc_id",
            title="Piece d'identite",
            description="Passeport ou CNI selon destination.",
            tag="document",
        ),
        TravelInfoItem(
            id="boarding_pass",
            title="Carte d'embarquement",
            description="Check-in en ligne recommande pour gagner du temps.",
            tag="check-in",
        ),
        TravelInfoItem(
            id="baggage",
            title="Bagages",
            description="Respecter les limites de poids et dimensions.",
            tag="bagage",
        ),
    ]
    tips = [
        TravelInfoItem(
            id="online_window",
            title="Fenetre check-in",
            description="Ouvre 24h avant le depart (selon vol).",
        ),
        TravelInfoItem(
            id="airport_time",
            title="Arriver tot",
            description="Prevoir 2h (vol national) ou 3h (international).",
        ),
    ]
    services = [
        TravelInfoItem(
            id="fast_track",
            title="Fast Track",
            description="Acces prioritaire aux controles de securite.",
            tag="service",
        ),
        TravelInfoItem(
            id="seat",
            title="Choisir mon siege",
            description="Selection de siege selon disponibilite.",
            tag="confort",
        ),
    ]

    return TravelInfoResponse(
        booking_id=booking.id if booking else None,
        phase="check_in",
        title="Check-in",
        subtitle="Finalisez avant le depart : check-in, infos aeroport, fast track.",
        origin=booking.origin if booking else None,
        destination=booking.destination if booking else None,
        depart_date=booking.depart_date if booking else None,
        checklist=checklist,
        tips=tips,
        services=services,
    )


def build_departure_day_response(booking: Booking | None) -> TravelInfoResponse:
    checklist = [
        TravelInfoItem(
            id="gate",
            title="Porte d'embarquement",
            description="Verifier l'ecran d'affichage regulierement.",
            tag="embarquement",
        ),
        TravelInfoItem(
            id="security",
            title="Controle de securite",
            description="Prevoir du temps selon l'affluence.",
            tag="aeroport",
        ),
        TravelInfoItem(
            id="boarding_time",
            title="Heure d'embarquement",
            description="Se presenter avant l'heure indiquee.",
            tag="horaires",
        ),
    ]
    tips = [
        TravelInfoItem(
            id="documents",
            title="Documents a portee",
            description="Passeport et carte d'embarquement faciles d'acces.",
        ),
        TravelInfoItem(
            id="carry_on",
            title="Bagage cabine",
            description="Objets essentiels uniquement pour accelerer le controle.",
        ),
    ]
    services = [
        TravelInfoItem(
            id="fast_track",
            title="Fast Track",
            description="Option pour reduire l'attente aux controles.",
            tag="service",
        ),
        TravelInfoItem(
            id="lounge",
            title="Acces lounge",
            description="Espace calme avec wifi et rafraichissements.",
            tag="confort",
        ),
    ]

    return TravelInfoResponse(
        booking_id=booking.id if booking else None,
        phase="departure_day",
        title="Jour du depart",
        subtitle="Derniers rappels : porte d'embarquement, attente, services.",
        origin=booking.origin if booking else None,
        destination=booking.destination if booking else None,
        depart_date=booking.depart_date if booking else None,
        checklist=checklist,
        tips=tips,
        services=services,
    )


@router.get("/check-in", response_model=TravelInfoResponse)
def check_in_info(
    booking_id: str | None = Query(None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = get_booking_or_none(booking_id, user["id"], db)
    return build_check_in_response(booking)


@router.get("/departure-day", response_model=TravelInfoResponse)
def departure_day_info(
    booking_id: str | None = Query(None),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = get_booking_or_none(booking_id, user["id"], db)
    return build_departure_day_response(booking)
