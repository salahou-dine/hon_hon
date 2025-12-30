import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from datetime import datetime

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.booking import Booking
from app.models.consent import Consent
from app.schemas.booking import BookingCreate, BookingOut

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validation simple: si oneway => return_date doit être None
    if payload.trip_type == "oneway" and payload.return_date is not None:
        raise HTTPException(status_code=422, detail="return_date must be null for oneway trips")

    booking = Booking(
        id=str(uuid.uuid4()),
        owner_id=user["id"],
        origin=payload.origin,
        destination=payload.destination,
        trip_type=payload.trip_type,
        cabin=payload.cabin,
        depart_date=payload.depart_date,
        return_date=payload.return_date,
        first_name=payload.first_name,
        last_name=payload.last_name,
        birth_date=payload.birth_date,
        email=payload.email,
    )

    db.add(booking)
    
    # ✅ Activation automatique du consentement pour les recommandations
    # Logique: si l'utilisateur réserve, il manifeste un intérêt pour les recommandations
    consent = db.query(Consent).filter(Consent.user_id == user["id"]).first()
    if not consent:
        # Créer le consentement avec recommandations activées par défaut
        consent = Consent(
            user_id=user["id"],
            destination_recos_enabled=True,
        )
        db.add(consent)
    elif not consent.destination_recos_enabled:
        # Activer les recommandations si elles étaient désactivées
        consent.destination_recos_enabled = True
    
    db.commit()
    db.refresh(booking)
    return booking


@router.put("/{booking_id}", response_model=BookingOut)
def update_booking_info(
    booking_id: str,
    payload: BookingCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Mise à jour des informations personnelles d'une réservation existante"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.owner_id != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Mise à jour des informations personnelles
    booking.first_name = payload.first_name
    booking.last_name = payload.last_name
    booking.birth_date = payload.birth_date
    booking.email = payload.email
    
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/{booking_id}/ticket", response_class=StreamingResponse)
def download_ticket(
    booking_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Télécharger le billet de réservation en PDF"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.owner_id != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    # Créer le PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # En-tête
    p.setFillColorRGB(0.7, 0.1, 0.1)  # Rouge RAM
    p.rect(0, height - 4*cm, width, 4*cm, fill=True)
    
    p.setFillColorRGB(1, 1, 1)  # Blanc
    p.setFont("Helvetica-Bold", 24)
    p.drawString(2*cm, height - 2.5*cm, "Royal Air Maroc")
    p.setFont("Helvetica", 14)
    p.drawString(2*cm, height - 3.2*cm, "E-Ticket / Billet Électronique")
    
    # Informations du passager
    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(2*cm, height - 6*cm, "PASSAGER / PASSENGER")
    
    p.setFont("Helvetica", 10)
    y_pos = height - 7*cm
    if booking.first_name and booking.last_name:
        p.drawString(2*cm, y_pos, f"Nom / Name: {booking.last_name.upper()} {booking.first_name}")
        y_pos -= 0.6*cm
    if booking.email:
        p.drawString(2*cm, y_pos, f"Email: {booking.email}")
        y_pos -= 0.6*cm
    if booking.birth_date:
        p.drawString(2*cm, y_pos, f"Date de naissance / Birth date: {booking.birth_date.strftime('%d/%m/%Y')}")
        y_pos -= 1*cm
    
    # Détails du vol
    p.setFont("Helvetica-Bold", 12)
    p.drawString(2*cm, y_pos, "DÉTAILS DU VOL / FLIGHT DETAILS")
    y_pos -= 0.8*cm
    
    p.setFont("Helvetica", 10)
    p.drawString(2*cm, y_pos, f"Référence: {booking.id[:8].upper()}")
    y_pos -= 0.6*cm
    p.drawString(2*cm, y_pos, f"Trajet: {booking.origin} → {booking.destination}")
    y_pos -= 0.6*cm
    p.drawString(2*cm, y_pos, f"Date de départ: {booking.depart_date.strftime('%d/%m/%Y')}")
    y_pos -= 0.6*cm
    if booking.return_date:
        p.drawString(2*cm, y_pos, f"Date de retour: {booking.return_date.strftime('%d/%m/%Y')}")
        y_pos -= 0.6*cm
    p.drawString(2*cm, y_pos, f"Classe: {booking.cabin.upper()}")
    y_pos -= 0.6*cm
    p.drawString(2*cm, y_pos, f"Type: {'Aller-Retour' if booking.trip_type == 'roundtrip' else 'Aller Simple'}")
    
    # Pied de page
    p.setFont("Helvetica-Oblique", 8)
    p.drawString(2*cm, 2*cm, f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    p.drawString(2*cm, 1.5*cm, "Veuillez présenter ce document à l'embarquement / Please present this document at boarding")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    filename = f"ticket_RAM_{booking.id[:8]}.pdf"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Sécurité: un guest ne peut lire que ses bookings
    if booking.owner_id != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return booking
