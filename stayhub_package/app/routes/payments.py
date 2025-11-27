from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.dependencies import get_db
from app.services.payment_service import PaymentService
from app.services.booking_service import BookingService
from app.schemas.payment import PaymentCreate, PaymentUpdate, Payment as PaymentSchema

router = APIRouter(prefix="/payments", tags=["payments"])
templates = Jinja2Templates(directory="app/templates")


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    """Dependency for PaymentService."""
    return PaymentService(db)


def get_booking_service(db: Session = Depends(get_db)) -> BookingService:
    """Dependency for BookingService."""
    return BookingService(db)


# API Routes
@router.get("/api", response_model=List[PaymentSchema])
def get_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    booking_id: Optional[int] = None,
    status: Optional[str] = None,
    payment_method: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    service: PaymentService = Depends(get_payment_service)
):
    """Get all payments with optional filtering."""
    if any([booking_id, status, payment_method, start_date, end_date]):
        return service.search_payments(
            booking_id=booking_id,
            status=status,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date
        )
    return service.get_all_payments(skip, limit)


@router.get("/api/revenue")
def get_revenue(service: PaymentService = Depends(get_payment_service)):
    """Get total revenue and breakdown by method."""
    return {
        "total_revenue": service.get_total_revenue(),
        "by_method": service.get_revenue_by_method()
    }


@router.get("/api/{payment_id}", response_model=PaymentSchema)
def get_payment(payment_id: int, service: PaymentService = Depends(get_payment_service)):
    """Get payment by ID."""
    return service.get_payment(payment_id)


@router.post("/api", response_model=PaymentSchema, status_code=201)
def create_payment(
    payment: PaymentCreate, 
    service: PaymentService = Depends(get_payment_service)
):
    """Create a new payment."""
    return service.create_payment(payment.model_dump())


@router.put("/api/{payment_id}", response_model=PaymentSchema)
def update_payment(
    payment_id: int, 
    payment: PaymentUpdate, 
    service: PaymentService = Depends(get_payment_service)
):
    """Update a payment."""
    return service.update_payment(payment_id, payment.model_dump(exclude_unset=True))


@router.delete("/api/{payment_id}")
def delete_payment(payment_id: int, service: PaymentService = Depends(get_payment_service)):
    """Delete a payment."""
    service.delete_payment(payment_id)
    return {"message": "Платёж успешно удалён"}


@router.post("/api/{payment_id}/status")
def update_payment_status(
    payment_id: int,
    status: str,
    service: PaymentService = Depends(get_payment_service)
):
    """Update payment status."""
    return service.update_status(payment_id, status)


# Web Routes
@router.get("/", response_class=HTMLResponse)
def payments_list(
    request: Request,
    status: Optional[str] = None,
    payment_method: Optional[str] = None,
    service: PaymentService = Depends(get_payment_service)
):
    """Payments list page with filtering."""
    if status or payment_method:
        payments = service.search_payments(status=status, payment_method=payment_method)
    else:
        payments = service.get_all_payments()
    
    return templates.TemplateResponse("payments/list.html", {
        "request": request, 
        "payments": payments,
        "filter_status": status,
        "filter_method": payment_method
    })


@router.get("/new", response_class=HTMLResponse)
def new_payment_form(
    request: Request,
    booking_service: BookingService = Depends(get_booking_service)
):
    """New payment form page."""
    bookings = booking_service.get_active_bookings()
    return templates.TemplateResponse("payments/form.html", {
        "request": request, 
        "payment": None, 
        "bookings": bookings
    })


@router.post("/new")
def create_payment_form(
    request: Request,
    booking_id: int = Form(...),
    amount: float = Form(...),
    payment_method: str = Form(...),
    status: str = Form("completed"),
    payment_service: PaymentService = Depends(get_payment_service),
    booking_service: BookingService = Depends(get_booking_service)
):
    """Create payment from form."""
    try:
        payment_service.create_payment({
            "booking_id": booking_id,
            "amount": amount,
            "payment_method": payment_method,
            "status": status
        })
        return RedirectResponse(url="/payments", status_code=303)
    except Exception as e:
        bookings = booking_service.get_active_bookings()
        return templates.TemplateResponse("payments/form.html", {
            "request": request, 
            "payment": None, 
            "bookings": bookings,
            "error": str(e)
        })


@router.get("/{payment_id}/edit", response_class=HTMLResponse)
def edit_payment_form(
    request: Request, 
    payment_id: int,
    payment_service: PaymentService = Depends(get_payment_service),
    booking_service: BookingService = Depends(get_booking_service)
):
    """Edit payment form page."""
    payment = payment_service.get_payment(payment_id)
    bookings = booking_service.get_all_bookings()
    return templates.TemplateResponse("payments/form.html", {
        "request": request, 
        "payment": payment, 
        "bookings": bookings
    })


@router.post("/{payment_id}/edit")
def update_payment_form(
    payment_id: int,
    request: Request,
    booking_id: int = Form(...),
    amount: float = Form(...),
    payment_method: str = Form(...),
    status: str = Form("completed"),
    payment_service: PaymentService = Depends(get_payment_service),
    booking_service: BookingService = Depends(get_booking_service)
):
    """Update payment from form."""
    try:
        payment_service.update_payment(payment_id, {
            "booking_id": booking_id,
            "amount": amount,
            "payment_method": payment_method,
            "status": status
        })
        return RedirectResponse(url="/payments", status_code=303)
    except Exception as e:
        payment = payment_service.get_payment(payment_id)
        bookings = booking_service.get_all_bookings()
        return templates.TemplateResponse("payments/form.html", {
            "request": request, 
            "payment": payment, 
            "bookings": bookings,
            "error": str(e)
        })


@router.get("/{payment_id}/delete")
def delete_payment_web(
    payment_id: int, 
    service: PaymentService = Depends(get_payment_service)
):
    """Delete payment from web interface."""
    service.delete_payment(payment_id)
    return RedirectResponse(url="/payments", status_code=303)
