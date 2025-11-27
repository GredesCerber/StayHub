from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.models.booking import Booking
from app.models.room import Room
from app.models.guest import Guest
from app.models.booking_service import BookingService
from app.schemas.booking import BookingCreate, BookingUpdate, Booking as BookingSchema

router = APIRouter(prefix="/bookings", tags=["bookings"])
templates = Jinja2Templates(directory="app/templates")


def calculate_booking_cost(db: Session, booking: Booking) -> float:
    """Calculate total cost for a booking including room and services."""
    if not booking.check_in_date or not booking.check_out_date:
        return 0.0
    
    # Calculate number of nights
    nights = (booking.check_out_date - booking.check_in_date).days
    if nights <= 0:
        nights = 1
    
    # Get room price
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    room_cost = room.price_per_night * nights if room else 0.0
    
    # Get services cost
    booking_services = db.query(BookingService).filter(BookingService.booking_id == booking.id).all()
    services_cost = sum(bs.subtotal or 0 for bs in booking_services)
    
    return room_cost + services_cost


def check_room_availability(db: Session, room_id: int, check_in: date, check_out: date, exclude_booking_id: int = None) -> bool:
    """Check if a room is available for the given date range."""
    query = db.query(Booking).filter(
        Booking.room_id == room_id,
        Booking.status.notin_(["cancelled"]),
        Booking.check_in_date < check_out,
        Booking.check_out_date > check_in
    )
    
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    
    conflicting_booking = query.first()
    return conflicting_booking is None


# API Routes
@router.get("/api", response_model=List[BookingSchema])
def get_bookings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    bookings = db.query(Booking).offset(skip).limit(limit).all()
    return bookings


@router.get("/api/availability")
def check_availability(
    room_id: int,
    check_in: date,
    check_out: date,
    db: Session = Depends(get_db)
):
    """Check if a room is available for the specified dates."""
    is_available = check_room_availability(db, room_id, check_in, check_out)
    return {"room_id": room_id, "available": is_available, "check_in": check_in, "check_out": check_out}


@router.get("/api/{booking_id}", response_model=BookingSchema)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.get("/api/{booking_id}/cost")
def get_booking_cost(booking_id: int, db: Session = Depends(get_db)):
    """Calculate and return the total cost for a booking."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    total_cost = calculate_booking_cost(db, booking)
    return {"booking_id": booking_id, "total_cost": total_cost}


@router.post("/api", response_model=BookingSchema)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    # Check room availability
    if not check_room_availability(db, booking.room_id, booking.check_in_date, booking.check_out_date):
        raise HTTPException(status_code=400, detail="Room is not available for the selected dates")
    
    db_booking = Booking(**booking.model_dump())
    db.add(db_booking)
    db.commit()
    
    # Calculate initial cost
    db_booking.total_cost = calculate_booking_cost(db, db_booking)
    db.commit()
    db.refresh(db_booking)
    
    return db_booking


@router.put("/api/{booking_id}", response_model=BookingSchema)
def update_booking(booking_id: int, booking: BookingUpdate, db: Session = Depends(get_db)):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    update_data = booking.model_dump(exclude_unset=True)
    
    # Check availability if dates or room are being changed
    new_room_id = update_data.get("room_id", db_booking.room_id)
    new_check_in = update_data.get("check_in_date", db_booking.check_in_date)
    new_check_out = update_data.get("check_out_date", db_booking.check_out_date)
    
    if not check_room_availability(db, new_room_id, new_check_in, new_check_out, booking_id):
        raise HTTPException(status_code=400, detail="Room is not available for the selected dates")
    
    for key, value in update_data.items():
        setattr(db_booking, key, value)
    
    # Recalculate cost
    db_booking.total_cost = calculate_booking_cost(db, db_booking)
    
    db.commit()
    db.refresh(db_booking)
    return db_booking


@router.delete("/api/{booking_id}")
def delete_booking(booking_id: int, db: Session = Depends(get_db)):
    db_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(db_booking)
    db.commit()
    return {"message": "Booking deleted successfully"}


# Web Routes
@router.get("/", response_class=HTMLResponse)
def bookings_list(request: Request, db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    return templates.TemplateResponse("bookings/list.html", {"request": request, "bookings": bookings})


@router.get("/new", response_class=HTMLResponse)
def new_booking_form(request: Request, db: Session = Depends(get_db)):
    rooms = db.query(Room).filter(Room.is_available == True).all()
    guests = db.query(Guest).all()
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
    db: Session = Depends(get_db)
):
    # Check room availability
    if not check_room_availability(db, room_id, check_in_date, check_out_date):
        rooms = db.query(Room).filter(Room.is_available == True).all()
        guests = db.query(Guest).all()
        return templates.TemplateResponse("bookings/form.html", {
            "request": request, 
            "booking": None, 
            "rooms": rooms, 
            "guests": guests,
            "error": "Room is not available for the selected dates"
        })
    
    booking = Booking(
        guest_id=guest_id,
        room_id=room_id,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        status=status
    )
    db.add(booking)
    db.commit()
    
    # Calculate cost
    booking.total_cost = calculate_booking_cost(db, booking)
    db.commit()
    
    return RedirectResponse(url="/bookings", status_code=303)


@router.get("/{booking_id}/edit", response_class=HTMLResponse)
def edit_booking_form(request: Request, booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    rooms = db.query(Room).all()
    guests = db.query(Guest).all()
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
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Check room availability
    if not check_room_availability(db, room_id, check_in_date, check_out_date, booking_id):
        rooms = db.query(Room).all()
        guests = db.query(Guest).all()
        return templates.TemplateResponse("bookings/form.html", {
            "request": request, 
            "booking": booking, 
            "rooms": rooms, 
            "guests": guests,
            "error": "Room is not available for the selected dates"
        })
    
    booking.guest_id = guest_id
    booking.room_id = room_id
    booking.check_in_date = check_in_date
    booking.check_out_date = check_out_date
    booking.status = status
    booking.total_cost = calculate_booking_cost(db, booking)
    
    db.commit()
    return RedirectResponse(url="/bookings", status_code=303)


@router.get("/{booking_id}/delete")
def delete_booking_web(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(booking)
    db.commit()
    return RedirectResponse(url="/bookings", status_code=303)


@router.post("/{booking_id}/recalculate")
def recalculate_booking_cost(booking_id: int, db: Session = Depends(get_db)):
    """Recalculate and update the total cost for a booking."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.total_cost = calculate_booking_cost(db, booking)
    db.commit()
    
    return RedirectResponse(url="/bookings", status_code=303)
