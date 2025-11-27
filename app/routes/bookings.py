from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.dependencies import get_db
from app.services.booking_service import BookingService
from app.services.room_service import RoomService
from app.services.guest_service import GuestService
from app.schemas.booking import (
    BookingCreate, BookingUpdate, Booking as BookingSchema,
    AvailabilityResponse, CostBreakdown
)

router = APIRouter(prefix="/bookings", tags=["bookings"])
templates = Jinja2Templates(directory="app/templates")


def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    """Dependency for BookingService."""
    return BookingService(db)


def get_room_service(db: Session = Depends(get_db)) -> RoomService:
    """Dependency for RoomService."""
    return RoomService(db)


def get_guest_service(db: Session = Depends(get_db)) -> GuestService:
    """Dependency for GuestService."""
    return GuestService(db)


# API Routes
@router.get("/api", response_model=List[BookingSchema])
def get_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    guest_id: Optional[int] = None,
    room_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    service: BookingService = Depends(get_booking_service)
):
    """Get all bookings with optional filtering."""
    if any([guest_id, room_id, status, start_date, end_date]):
        return service.search_bookings(
            guest_id=guest_id,
            room_id=room_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
    return service.get_all_bookings(skip, limit)


@router.get("/api/availability", response_model=AvailabilityResponse)
def check_availability(
    room_id: int,
    check_in: date,
    check_out: date,
    service: BookingService = Depends(get_booking_service)
):
    """Check if a room is available for the specified dates."""
    is_available = service.check_room_availability(room_id, check_in, check_out)
    return AvailabilityResponse(
        room_id=room_id, 
        available=is_available, 
        check_in=check_in, 
        check_out=check_out
    )


@router.get("/api/available-rooms")
def get_available_rooms_for_dates(
    check_in: date,
    check_out: date,
    room_type: Optional[str] = None,
    min_capacity: Optional[int] = None,
    service: BookingService = Depends(get_booking_service)
):
    """Get all rooms available for given date range."""
    rooms = service.get_available_rooms_for_dates(
        check_in, check_out, room_type, min_capacity
    )
    return rooms


@router.get("/api/{booking_id}", response_model=BookingSchema)
def get_booking(booking_id: int, service: BookingService = Depends(get_booking_service)):
    """Get booking by ID."""
    return service.get_booking(booking_id)


@router.get("/api/{booking_id}/cost")
def get_booking_cost(booking_id: int, service: BookingService = Depends(get_booking_service)):
    """Calculate and return detailed cost breakdown for a booking."""
    booking = service.get_booking(booking_id)
    breakdown = service.calculate_cost_breakdown(booking)
    return {
        "booking_id": booking_id,
        "room_cost": breakdown.room_cost,
        "nights": breakdown.nights,
        "price_per_night": breakdown.price_per_night,
        "services": breakdown.services,
        "services_total": breakdown.services_total,
        "total_cost": breakdown.total_cost
    }


@router.post("/api", response_model=BookingSchema, status_code=201)
def create_booking(
    booking: BookingCreate, 
    service: BookingService = Depends(get_booking_service)
):
    """Create a new booking."""
    return service.create_booking(booking.model_dump())


@router.put("/api/{booking_id}", response_model=BookingSchema)
def update_booking(
    booking_id: int, 
    booking: BookingUpdate, 
    service: BookingService = Depends(get_booking_service)
):
    """Update a booking."""
    return service.update_booking(booking_id, booking.model_dump(exclude_unset=True))


@router.delete("/api/{booking_id}")
def delete_booking(booking_id: int, service: BookingService = Depends(get_booking_service)):
    """Delete a booking."""
    service.delete_booking(booking_id)
    return {"message": "Booking deleted successfully"}


@router.post("/api/{booking_id}/status")
def update_booking_status(
    booking_id: int,
    status: str,
    service: BookingService = Depends(get_booking_service)
):
    """Update booking status."""
    return service.update_status(booking_id, status)


@router.post("/api/{booking_id}/recalculate")
def recalculate_cost(booking_id: int, service: BookingService = Depends(get_booking_service)):
    """Recalculate booking cost."""
    booking = service.recalculate_cost(booking_id)
    return {"booking_id": booking_id, "total_cost": booking.total_cost}


# Web Routes
@router.get("/", response_class=HTMLResponse)
def bookings_list(
    request: Request,
    status: Optional[str] = None,
    guest_id: Optional[int] = None,
    room_id: Optional[int] = None,
    service: BookingService = Depends(get_booking_service)
):
    """Bookings list page with filtering."""
    if any([status, guest_id, room_id]):
        bookings = service.search_bookings(
            status=status, 
            guest_id=guest_id, 
            room_id=room_id
        )
    else:
        bookings = service.get_all_bookings()
    
    return templates.TemplateResponse("bookings/list.html", {
        "request": request, 
        "bookings": bookings,
        "filter_status": status,
        "filter_guest_id": guest_id,
        "filter_room_id": room_id
    })


@router.get("/new", response_class=HTMLResponse)
def new_booking_form(
    request: Request,
    room_service: RoomService = Depends(get_room_service),
    guest_service: GuestService = Depends(get_guest_service)
):
    """New booking form page."""
    rooms = room_service.get_available_rooms()
    guests = guest_service.get_all_guests()
    return templates.TemplateResponse("bookings/form.html", {
        "request": request, 
        "booking": None, 
        "rooms": rooms, 
        "guests": guests
    })


@router.post("/new")
def create_booking_form(
    request: Request,
    guest_id: int = Form(...),
    room_id: int = Form(...),
    check_in_date: date = Form(...),
    check_out_date: date = Form(...),
    status: str = Form("pending"),
    booking_service: BookingService = Depends(get_booking_service),
    room_service: RoomService = Depends(get_room_service),
    guest_service: GuestService = Depends(get_guest_service)
):
    """Create booking from form."""
    try:
        booking_service.create_booking({
            "guest_id": guest_id,
            "room_id": room_id,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "status": status
        })
        return RedirectResponse(url="/bookings", status_code=303)
    except Exception as e:
        rooms = room_service.get_available_rooms()
        guests = guest_service.get_all_guests()
        return templates.TemplateResponse("bookings/form.html", {
            "request": request, 
            "booking": None, 
            "rooms": rooms, 
            "guests": guests,
            "error": str(e)
        })


@router.get("/{booking_id}/edit", response_class=HTMLResponse)
def edit_booking_form(
    request: Request, 
    booking_id: int,
    booking_service: BookingService = Depends(get_booking_service),
    room_service: RoomService = Depends(get_room_service),
    guest_service: GuestService = Depends(get_guest_service)
):
    """Edit booking form page."""
    booking = booking_service.get_booking(booking_id)
    rooms = room_service.get_all_rooms()
    guests = guest_service.get_all_guests()
    return templates.TemplateResponse("bookings/form.html", {
        "request": request, 
        "booking": booking, 
        "rooms": rooms, 
        "guests": guests
    })


@router.post("/{booking_id}/edit")
def update_booking_form(
    booking_id: int,
    request: Request,
    guest_id: int = Form(...),
    room_id: int = Form(...),
    check_in_date: date = Form(...),
    check_out_date: date = Form(...),
    status: str = Form("pending"),
    booking_service: BookingService = Depends(get_booking_service),
    room_service: RoomService = Depends(get_room_service),
    guest_service: GuestService = Depends(get_guest_service)
):
    """Update booking from form."""
    try:
        booking_service.update_booking(booking_id, {
            "guest_id": guest_id,
            "room_id": room_id,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "status": status
        })
        return RedirectResponse(url="/bookings", status_code=303)
    except Exception as e:
        booking = booking_service.get_booking(booking_id)
        rooms = room_service.get_all_rooms()
        guests = guest_service.get_all_guests()
        return templates.TemplateResponse("bookings/form.html", {
            "request": request, 
            "booking": booking, 
            "rooms": rooms, 
            "guests": guests,
            "error": str(e)
        })


@router.get("/{booking_id}/delete")
def delete_booking_web(
    booking_id: int, 
    service: BookingService = Depends(get_booking_service)
):
    """Delete booking from web interface."""
    service.delete_booking(booking_id)
    return RedirectResponse(url="/bookings", status_code=303)


@router.post("/{booking_id}/recalculate")
def recalculate_booking_cost(
    booking_id: int, 
    service: BookingService = Depends(get_booking_service)
):
    """Recalculate and update the total cost for a booking."""
    service.recalculate_cost(booking_id)
    return RedirectResponse(url="/bookings", status_code=303)
