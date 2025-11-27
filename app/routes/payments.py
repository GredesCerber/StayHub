from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.models.payment import Payment
from app.models.booking import Booking
from app.schemas.payment import PaymentCreate, PaymentUpdate, Payment as PaymentSchema

router = APIRouter(prefix="/payments", tags=["payments"])
templates = Jinja2Templates(directory="app/templates")


# API Routes
@router.get("/api", response_model=List[PaymentSchema])
def get_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    payments = db.query(Payment).offset(skip).limit(limit).all()
    return payments


@router.get("/api/{payment_id}", response_model=PaymentSchema)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.post("/api", response_model=PaymentSchema)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    # Verify booking exists
    booking = db.query(Booking).filter(Booking.id == payment.booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db_payment = Payment(**payment.model_dump())
    db_payment.payment_date = date.today()
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.put("/api/{payment_id}", response_model=PaymentSchema)
def update_payment(payment_id: int, payment: PaymentUpdate, db: Session = Depends(get_db)):
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    update_data = payment.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_payment, key, value)
    
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.delete("/api/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    db.delete(db_payment)
    db.commit()
    return {"message": "Payment deleted successfully"}


# Web Routes
@router.get("/", response_class=HTMLResponse)
def payments_list(request: Request, db: Session = Depends(get_db)):
    payments = db.query(Payment).all()
    return templates.TemplateResponse("payments/list.html", {"request": request, "payments": payments})


@router.get("/new", response_class=HTMLResponse)
def new_payment_form(request: Request, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.status.in_(["pending", "confirmed"])).all()
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
    db: Session = Depends(get_db)
):
    payment = Payment(
        booking_id=booking_id,
        amount=amount,
        payment_date=date.today(),
        payment_method=payment_method,
        status=status
    )
    db.add(payment)
    db.commit()
    return RedirectResponse(url="/payments", status_code=303)


@router.get("/{payment_id}/edit", response_class=HTMLResponse)
def edit_payment_form(request: Request, payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    bookings = db.query(Booking).all()
    return templates.TemplateResponse("payments/form.html", {
        "request": request, 
        "payment": payment, 
        "bookings": bookings
    })


@router.post("/{payment_id}/edit")
def update_payment_form(
    payment_id: int,
    booking_id: int = Form(...),
    amount: float = Form(...),
    payment_method: str = Form(...),
    status: str = Form("completed"),
    db: Session = Depends(get_db)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment.booking_id = booking_id
    payment.amount = amount
    payment.payment_method = payment_method
    payment.status = status
    
    db.commit()
    return RedirectResponse(url="/payments", status_code=303)


@router.get("/{payment_id}/delete")
def delete_payment_web(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    db.delete(payment)
    db.commit()
    return RedirectResponse(url="/payments", status_code=303)
