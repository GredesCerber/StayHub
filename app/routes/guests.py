from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from app.services.guest_service import GuestService
from app.schemas.guest import GuestCreate, GuestUpdate, Guest as GuestSchema

router = APIRouter(prefix="/guests", tags=["guests"])
templates = Jinja2Templates(directory="app/templates")


def get_guest_service(db: Session = Depends(get_db)) -> GuestService:
    """Dependency for GuestService."""
    return GuestService(db)


# API Routes
@router.get("/api", response_model=List[GuestSchema])
def get_guests(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    service: GuestService = Depends(get_guest_service)
):
    """Get all guests with optional filtering."""
    if any([name, email, phone]):
        return service.search_guests(name=name, email=email, phone=phone)
    return service.get_all_guests(skip, limit)


@router.get("/api/{guest_id}", response_model=GuestSchema)
def get_guest(guest_id: int, service: GuestService = Depends(get_guest_service)):
    """Get guest by ID."""
    return service.get_guest(guest_id)


@router.post("/api", response_model=GuestSchema, status_code=201)
def create_guest(guest: GuestCreate, service: GuestService = Depends(get_guest_service)):
    """Create a new guest."""
    return service.create_guest(guest.model_dump())


@router.put("/api/{guest_id}", response_model=GuestSchema)
def update_guest(
    guest_id: int, 
    guest: GuestUpdate, 
    service: GuestService = Depends(get_guest_service)
):
    """Update a guest."""
    return service.update_guest(guest_id, guest.model_dump(exclude_unset=True))


@router.delete("/api/{guest_id}")
def delete_guest(guest_id: int, service: GuestService = Depends(get_guest_service)):
    """Delete a guest."""
    service.delete_guest(guest_id)
    return {"message": "Guest deleted successfully"}


# Web Routes
@router.get("/", response_class=HTMLResponse)
def guests_list(
    request: Request,
    name: Optional[str] = None,
    email: Optional[str] = None,
    service: GuestService = Depends(get_guest_service)
):
    """Guests list page with filtering."""
    if name or email:
        guests = service.search_guests(name=name, email=email)
    else:
        guests = service.get_all_guests()
    
    return templates.TemplateResponse("guests/list.html", {
        "request": request, 
        "guests": guests,
        "filter_name": name,
        "filter_email": email
    })


@router.get("/new", response_class=HTMLResponse)
def new_guest_form(request: Request):
    """New guest form page."""
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
    service: GuestService = Depends(get_guest_service)
):
    """Create guest from form."""
    try:
        service.create_guest({
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "address": address,
            "id_document": id_document
        })
        return RedirectResponse(url="/guests", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("guests/form.html", {
            "request": request, 
            "guest": None,
            "error": str(e)
        })


@router.get("/{guest_id}/edit", response_class=HTMLResponse)
def edit_guest_form(
    request: Request, 
    guest_id: int, 
    service: GuestService = Depends(get_guest_service)
):
    """Edit guest form page."""
    guest = service.get_guest(guest_id)
    return templates.TemplateResponse("guests/form.html", {"request": request, "guest": guest})


@router.post("/{guest_id}/edit")
def update_guest_form(
    guest_id: int,
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    address: str = Form(None),
    id_document: str = Form(None),
    service: GuestService = Depends(get_guest_service)
):
    """Update guest from form."""
    try:
        service.update_guest(guest_id, {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "address": address,
            "id_document": id_document
        })
        return RedirectResponse(url="/guests", status_code=303)
    except Exception as e:
        guest = service.get_guest(guest_id)
        return templates.TemplateResponse("guests/form.html", {
            "request": request, 
            "guest": guest,
            "error": str(e)
        })


@router.get("/{guest_id}/delete")
def delete_guest_web(guest_id: int, service: GuestService = Depends(get_guest_service)):
    """Delete guest from web interface."""
    service.delete_guest(guest_id)
    return RedirectResponse(url="/guests", status_code=303)
