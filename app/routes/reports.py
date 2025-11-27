from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.database import get_db
from app.models.booking import Booking
from app.models.room import Room
from app.models.guest import Guest
from app.models.service import Service
from app.models.payment import Payment
from app.models.booking_service import BookingService

router = APIRouter(prefix="/reports", tags=["reports"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def reports_dashboard(request: Request, db: Session = Depends(get_db)):
    """Main reports dashboard."""
    # Summary statistics
    total_rooms = db.query(Room).count()
    available_rooms = db.query(Room).filter(Room.is_available == True).count()
    total_guests = db.query(Guest).count()
    total_bookings = db.query(Booking).count()
    active_bookings = db.query(Booking).filter(Booking.status.in_(["pending", "confirmed"])).count()
    
    # Revenue statistics
    total_revenue = db.query(func.sum(Payment.amount)).filter(Payment.status == "completed").scalar() or 0
    
    # Today's check-ins and check-outs
    today = date.today()
    todays_checkins = db.query(Booking).filter(Booking.check_in_date == today).count()
    todays_checkouts = db.query(Booking).filter(Booking.check_out_date == today).count()
    
    return templates.TemplateResponse("reports/dashboard.html", {
        "request": request,
        "total_rooms": total_rooms,
        "available_rooms": available_rooms,
        "total_guests": total_guests,
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "total_revenue": total_revenue,
        "todays_checkins": todays_checkins,
        "todays_checkouts": todays_checkouts
    })


@router.get("/occupancy", response_class=HTMLResponse)
def occupancy_report(request: Request, db: Session = Depends(get_db)):
    """Room occupancy report."""
    rooms = db.query(Room).all()
    today = date.today()
    
    room_status = []
    for room in rooms:
        # Check if room has active booking
        active_booking = db.query(Booking).filter(
            Booking.room_id == room.id,
            Booking.check_in_date <= today,
            Booking.check_out_date > today,
            Booking.status.in_(["pending", "confirmed"])
        ).first()
        
        room_status.append({
            "room": room,
            "is_occupied": active_booking is not None,
            "current_booking": active_booking
        })
    
    occupied_count = sum(1 for rs in room_status if rs["is_occupied"])
    occupancy_rate = (occupied_count / len(rooms) * 100) if rooms else 0
    
    return templates.TemplateResponse("reports/occupancy.html", {
        "request": request,
        "room_status": room_status,
        "occupancy_rate": occupancy_rate,
        "occupied_count": occupied_count,
        "total_rooms": len(rooms)
    })


@router.get("/revenue", response_class=HTMLResponse)
def revenue_report(request: Request, db: Session = Depends(get_db)):
    """Revenue report."""
    # Get all completed payments
    payments = db.query(Payment).filter(Payment.status == "completed").all()
    
    total_revenue = sum(p.amount for p in payments)
    
    # Group by payment method
    revenue_by_method = {}
    for payment in payments:
        method = payment.payment_method
        if method not in revenue_by_method:
            revenue_by_method[method] = 0
        revenue_by_method[method] += payment.amount
    
    # Recent payments
    recent_payments = db.query(Payment).order_by(Payment.payment_date.desc()).limit(10).all()
    
    return templates.TemplateResponse("reports/revenue.html", {
        "request": request,
        "total_revenue": total_revenue,
        "revenue_by_method": revenue_by_method,
        "recent_payments": recent_payments,
        "payment_count": len(payments)
    })


@router.get("/bookings", response_class=HTMLResponse)
def bookings_report(request: Request, db: Session = Depends(get_db)):
    """Bookings report."""
    # Booking status breakdown
    pending = db.query(Booking).filter(Booking.status == "pending").count()
    confirmed = db.query(Booking).filter(Booking.status == "confirmed").count()
    cancelled = db.query(Booking).filter(Booking.status == "cancelled").count()
    completed = db.query(Booking).filter(Booking.status == "completed").count()
    
    # Upcoming bookings
    today = date.today()
    upcoming_bookings = db.query(Booking).filter(
        Booking.check_in_date >= today,
        Booking.status.in_(["pending", "confirmed"])
    ).order_by(Booking.check_in_date).limit(10).all()
    
    return templates.TemplateResponse("reports/bookings.html", {
        "request": request,
        "pending": pending,
        "confirmed": confirmed,
        "cancelled": cancelled,
        "completed": completed,
        "upcoming_bookings": upcoming_bookings,
        "total_bookings": pending + confirmed + cancelled + completed
    })


# API endpoints for reports
@router.get("/api/summary")
def get_summary_report(db: Session = Depends(get_db)):
    """Get summary report data as JSON."""
    total_rooms = db.query(Room).count()
    available_rooms = db.query(Room).filter(Room.is_available == True).count()
    total_guests = db.query(Guest).count()
    total_bookings = db.query(Booking).count()
    active_bookings = db.query(Booking).filter(Booking.status.in_(["pending", "confirmed"])).count()
    total_revenue = db.query(func.sum(Payment.amount)).filter(Payment.status == "completed").scalar() or 0
    
    today = date.today()
    todays_checkins = db.query(Booking).filter(Booking.check_in_date == today).count()
    todays_checkouts = db.query(Booking).filter(Booking.check_out_date == today).count()
    
    return {
        "total_rooms": total_rooms,
        "available_rooms": available_rooms,
        "total_guests": total_guests,
        "total_bookings": total_bookings,
        "active_bookings": active_bookings,
        "total_revenue": total_revenue,
        "todays_checkins": todays_checkins,
        "todays_checkouts": todays_checkouts
    }


@router.get("/api/occupancy")
def get_occupancy_report(db: Session = Depends(get_db)):
    """Get occupancy report data as JSON."""
    rooms = db.query(Room).all()
    today = date.today()
    
    occupied_count = 0
    for room in rooms:
        active_booking = db.query(Booking).filter(
            Booking.room_id == room.id,
            Booking.check_in_date <= today,
            Booking.check_out_date > today,
            Booking.status.in_(["pending", "confirmed"])
        ).first()
        if active_booking:
            occupied_count += 1
    
    total_rooms = len(rooms)
    occupancy_rate = (occupied_count / total_rooms * 100) if total_rooms > 0 else 0
    
    return {
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_count,
        "available_rooms": total_rooms - occupied_count,
        "occupancy_rate": round(occupancy_rate, 2)
    }
