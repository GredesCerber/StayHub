from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.guest import Guest
from app.schemas.guest import GuestCreate, GuestUpdate, Guest as GuestSchema

router = APIRouter(prefix="/guests", tags=["guests"])
templates = Jinja2Templates(directory="app/templates")


# API Routes
@router.get("/api", response_model=List[GuestSchema])
def get_guests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    guests = db.query(Guest).offset(skip).limit(limit).all()
    return guests


@router.get("/api/{guest_id}", response_model=GuestSchema)
def get_guest(guest_id: int, db: Session = Depends(get_db)):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if guest is None:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest


@router.post("/api", response_model=GuestSchema)
def create_guest(guest: GuestCreate, db: Session = Depends(get_db)):
    db_guest = Guest(**guest.model_dump())
    db.add(db_guest)
    db.commit()
    db.refresh(db_guest)
    return db_guest


@router.put("/api/{guest_id}", response_model=GuestSchema)
def update_guest(guest_id: int, guest: GuestUpdate, db: Session = Depends(get_db)):
    db_guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if db_guest is None:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    update_data = guest.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_guest, key, value)
    
    db.commit()
    db.refresh(db_guest)
    return db_guest


@router.delete("/api/{guest_id}")
def delete_guest(guest_id: int, db: Session = Depends(get_db)):
    db_guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if db_guest is None:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    db.delete(db_guest)
    db.commit()
    return {"message": "Guest deleted successfully"}


# Web Routes
@router.get("/", response_class=HTMLResponse)
def guests_list(request: Request, db: Session = Depends(get_db)):
    guests = db.query(Guest).all()
    return templates.TemplateResponse("guests/list.html", {"request": request, "guests": guests})


@router.get("/new", response_class=HTMLResponse)
def new_guest_form(request: Request):
    return templates.TemplateResponse("guests/form.html", {"request": request, "guest": None})


@router.post("/new")
def create_guest_form(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    address: str = Form(None),
    id_document: str = Form(None),
    db: Session = Depends(get_db)
):
    guest = Guest(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        address=address,
        id_document=id_document
    )
    db.add(guest)
    db.commit()
    return RedirectResponse(url="/guests", status_code=303)


@router.get("/{guest_id}/edit", response_class=HTMLResponse)
def edit_guest_form(request: Request, guest_id: int, db: Session = Depends(get_db)):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if guest is None:
        raise HTTPException(status_code=404, detail="Guest not found")
    return templates.TemplateResponse("guests/form.html", {"request": request, "guest": guest})


@router.post("/{guest_id}/edit")
def update_guest_form(
    guest_id: int,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    address: str = Form(None),
    id_document: str = Form(None),
    db: Session = Depends(get_db)
):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if guest is None:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    guest.first_name = first_name
    guest.last_name = last_name
    guest.email = email
    guest.phone = phone
    guest.address = address
    guest.id_document = id_document
    
    db.commit()
    return RedirectResponse(url="/guests", status_code=303)


@router.get("/{guest_id}/delete")
def delete_guest_web(guest_id: int, db: Session = Depends(get_db)):
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if guest is None:
        raise HTTPException(status_code=404, detail="Guest not found")
    
    db.delete(guest)
    db.commit()
    return RedirectResponse(url="/guests", status_code=303)
