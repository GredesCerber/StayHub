from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db
from app.repositories.booking_service_repository import BookingServiceRepository
from app.services.booking_service import BookingService as BookingServiceClass
from app.services.service_service import ServiceService
from app.models.booking_service import BookingService
from app.schemas.booking_service import BookingServiceCreate, BookingServiceUpdate, BookingService as BookingServiceSchema

router = APIRouter(prefix="/booking-services", tags=["booking-services"])
templates = Jinja2Templates(directory="app/templates")


def get_booking_service_repo(db: Session = Depends(get_db)) -> BookingServiceRepository:
    """Dependency for BookingServiceRepository."""
    return BookingServiceRepository(db)


def get_booking_service(db: Session = Depends(get_db)) -> BookingServiceClass:
    """Dependency for BookingService."""
    return BookingServiceClass(db)


def get_service_service(db: Session = Depends(get_db)) -> ServiceService:
    """Dependency for ServiceService."""
    return ServiceService(db)


# API Routes
@router.get("/api", response_model=List[BookingServiceSchema])
def get_booking_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    booking_id: int = None,
    repo: BookingServiceRepository = Depends(get_booking_service_repo)
):
    """Get all booking services with optional filtering."""
    if booking_id:
        return repo.get_by_booking(booking_id)
    return repo.get_all(skip, limit)


@router.get("/api/{booking_service_id}", response_model=BookingServiceSchema)
def get_booking_service_by_id(
    booking_service_id: int, 
    repo: BookingServiceRepository = Depends(get_booking_service_repo)
):
    """Get booking service by ID."""
    bs = repo.get_by_id(booking_service_id)
    if bs is None:
        raise HTTPException(status_code=404, detail="Услуга в бронировании не найдена")
    return bs


@router.post("/api", response_model=BookingServiceSchema, status_code=201)
def create_booking_service(
    booking_service: BookingServiceCreate, 
    repo: BookingServiceRepository = Depends(get_booking_service_repo),
    service_svc: ServiceService = Depends(get_service_service),
    booking_svc: BookingServiceClass = Depends(get_booking_service)
):
    """Create a new booking service."""
    service = service_svc.get_service(booking_service.service_id)
    subtotal = service.price * booking_service.quantity
    
    data = booking_service.model_dump()
    data["subtotal"] = subtotal
    
    created = repo.create(data)
    booking_svc.register_additional_charge(created.booking_id, subtotal)
    return created


@router.put("/api/{booking_service_id}", response_model=BookingServiceSchema)
def update_booking_service(
    booking_service_id: int, 
    booking_service: BookingServiceUpdate,
    repo: BookingServiceRepository = Depends(get_booking_service_repo),
    service_svc: ServiceService = Depends(get_service_service)
):
    """Update a booking service."""
    bs = repo.get_by_id(booking_service_id)
    if bs is None:
        raise HTTPException(status_code=404, detail="Услуга в бронировании не найдена")
    
    update_data = booking_service.model_dump(exclude_unset=True)
    
    # Recalculate subtotal if quantity or service changed
    service_id = update_data.get("service_id", bs.service_id)
    quantity = update_data.get("quantity", bs.quantity)
    service = service_svc.get_service(service_id)
    update_data["subtotal"] = service.price * quantity
    
    return repo.update(bs, update_data)


@router.delete("/api/{booking_service_id}")
def delete_booking_service(
    booking_service_id: int, 
    repo: BookingServiceRepository = Depends(get_booking_service_repo)
):
    """Delete a booking service."""
    bs = repo.get_by_id(booking_service_id)
    if bs is None:
        raise HTTPException(status_code=404, detail="Услуга в бронировании не найдена")
    
    repo.delete(bs)
    return {"message": "Услуга из брони успешно удалена"}


# Web Routes - Add service to booking
@router.get("/booking/{booking_id}/add", response_class=HTMLResponse)
def add_service_to_booking_form(
    request: Request, 
    booking_id: int,
    booking_svc: BookingServiceClass = Depends(get_booking_service),
    service_svc: ServiceService = Depends(get_service_service),
    repo: BookingServiceRepository = Depends(get_booking_service_repo)
):
    """Form to add services to a booking."""
    booking = booking_svc.get_booking(booking_id)
    services = service_svc.get_active_services()
    booking_services = repo.get_by_booking(booking_id)
    
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
    repo: BookingServiceRepository = Depends(get_booking_service_repo),
    service_svc: ServiceService = Depends(get_service_service),
    booking_svc: BookingServiceClass = Depends(get_booking_service)
):
    """Add a service to a booking."""
    service = service_svc.get_service(service_id)
    subtotal = service.price * quantity
    
    repo.create({
        "booking_id": booking_id,
        "service_id": service_id,
        "quantity": quantity,
        "subtotal": subtotal
    })

    booking_svc.register_additional_charge(booking_id, subtotal)
    
    return RedirectResponse(url=f"/booking-services/booking/{booking_id}/add", status_code=303)


@router.get("/{booking_service_id}/delete")
def delete_booking_service_web(
    booking_service_id: int, 
    repo: BookingServiceRepository = Depends(get_booking_service_repo)
):
    """Delete a booking service from web interface."""
    bs = repo.get_by_id(booking_service_id)
    if bs is None:
        raise HTTPException(status_code=404, detail="Услуга в бронировании не найдена")
    
    booking_id = bs.booking_id
    repo.delete(bs)
    
    return RedirectResponse(url=f"/booking-services/booking/{booking_id}/add", status_code=303)
