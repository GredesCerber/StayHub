from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.booking_service import BookingService
from app.models.booking import Booking
from app.models.service import Service
from app.schemas.booking_service import BookingServiceCreate, BookingServiceUpdate, BookingService as BookingServiceSchema

router = APIRouter(prefix="/booking-services", tags=["booking-services"])
templates = Jinja2Templates(directory="app/templates")


def calculate_subtotal(db: Session, service_id: int, quantity: int) -> float:
    """Calculate subtotal for a booking service."""
    service = db.query(Service).filter(Service.id == service_id).first()
    if service:
        return service.price * quantity
    return 0.0


# API Routes
@router.get("/api", response_model=List[BookingServiceSchema])
def get_booking_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    booking_services = db.query(BookingService).offset(skip).limit(limit).all()
    return booking_services


@router.get("/api/{booking_service_id}", response_model=BookingServiceSchema)
def get_booking_service(booking_service_id: int, db: Session = Depends(get_db)):
    booking_service = db.query(BookingService).filter(BookingService.id == booking_service_id).first()
    if booking_service is None:
        raise HTTPException(status_code=404, detail="Booking service not found")
    return booking_service


@router.post("/api", response_model=BookingServiceSchema)
def create_booking_service(booking_service: BookingServiceCreate, db: Session = Depends(get_db)):
    db_booking_service = BookingService(**booking_service.model_dump())
    db_booking_service.subtotal = calculate_subtotal(db, booking_service.service_id, booking_service.quantity)
    db.add(db_booking_service)
    db.commit()
    db.refresh(db_booking_service)
    return db_booking_service


@router.put("/api/{booking_service_id}", response_model=BookingServiceSchema)
def update_booking_service(booking_service_id: int, booking_service: BookingServiceUpdate, db: Session = Depends(get_db)):
    db_booking_service = db.query(BookingService).filter(BookingService.id == booking_service_id).first()
    if db_booking_service is None:
        raise HTTPException(status_code=404, detail="Booking service not found")
    
    update_data = booking_service.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_booking_service, key, value)
    
    # Recalculate subtotal
    db_booking_service.subtotal = calculate_subtotal(db, db_booking_service.service_id, db_booking_service.quantity)
    
    db.commit()
    db.refresh(db_booking_service)
    return db_booking_service


@router.delete("/api/{booking_service_id}")
def delete_booking_service(booking_service_id: int, db: Session = Depends(get_db)):
    db_booking_service = db.query(BookingService).filter(BookingService.id == booking_service_id).first()
    if db_booking_service is None:
        raise HTTPException(status_code=404, detail="Booking service not found")
    
    db.delete(db_booking_service)
    db.commit()
    return {"message": "Booking service deleted successfully"}


# Web Routes - Add service to booking
@router.get("/booking/{booking_id}/add", response_class=HTMLResponse)
def add_service_to_booking_form(request: Request, booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    services = db.query(Service).filter(Service.is_active == True).all()
    booking_services = db.query(BookingService).filter(BookingService.booking_id == booking_id).all()
    
    return templates.TemplateResponse("bookings/services.html", {
        "request": request, 
        "booking": booking,
        "services": services,
        "booking_services": booking_services
    })


@router.post("/booking/{booking_id}/add")
def add_service_to_booking(
    booking_id: int,
    service_id: int = Form(...),
    quantity: int = Form(1),
    db: Session = Depends(get_db)
):
    booking_service = BookingService(
        booking_id=booking_id,
        service_id=service_id,
        quantity=quantity
    )
    booking_service.subtotal = calculate_subtotal(db, service_id, quantity)
    db.add(booking_service)
    db.commit()
    
    return RedirectResponse(url=f"/booking-services/booking/{booking_id}/add", status_code=303)


@router.get("/{booking_service_id}/delete")
def delete_booking_service_web(booking_service_id: int, db: Session = Depends(get_db)):
    booking_service = db.query(BookingService).filter(BookingService.id == booking_service_id).first()
    if booking_service is None:
        raise HTTPException(status_code=404, detail="Booking service not found")
    
    booking_id = booking_service.booking_id
    db.delete(booking_service)
    db.commit()
    
    return RedirectResponse(url=f"/booking-services/booking/{booking_id}/add", status_code=303)
