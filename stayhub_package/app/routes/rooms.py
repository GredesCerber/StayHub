from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from app.services.room_service import RoomService
from app.schemas.room import RoomCreate, RoomUpdate, Room as RoomSchema

router = APIRouter(prefix="/rooms", tags=["rooms"])
templates = Jinja2Templates(directory="app/templates")


def get_room_service(db: Session = Depends(get_db)) -> RoomService:
    """Dependency for RoomService."""
    return RoomService(db)


# API Routes
@router.get("/api", response_model=List[RoomSchema])
def get_rooms(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    room_type: Optional[str] = None,
    min_capacity: Optional[int] = None,
    is_available: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    service: RoomService = Depends(get_room_service)
):
    """Get all rooms with optional filtering."""
    if any([room_type, min_capacity, is_available is not None, min_price, max_price]):
        return service.search_rooms(
            room_type=room_type,
            min_capacity=min_capacity,
            is_available=is_available,
            min_price=min_price,
            max_price=max_price
        )
    return service.get_all_rooms(skip, limit)


@router.get("/api/available", response_model=List[RoomSchema])
def get_available_rooms(service: RoomService = Depends(get_room_service)):
    """Get all available rooms."""
    return service.get_available_rooms()


@router.get("/api/{room_id}", response_model=RoomSchema)
def get_room(room_id: int, service: RoomService = Depends(get_room_service)):
    """Get room by ID."""
    return service.get_room(room_id)


@router.post("/api", response_model=RoomSchema, status_code=201)
def create_room(room: RoomCreate, service: RoomService = Depends(get_room_service)):
    """Create a new room."""
    return service.create_room(room.model_dump())


@router.put("/api/{room_id}", response_model=RoomSchema)
def update_room(
    room_id: int, 
    room: RoomUpdate, 
    service: RoomService = Depends(get_room_service)
):
    """Update a room."""
    return service.update_room(room_id, room.model_dump(exclude_unset=True))


@router.delete("/api/{room_id}")
def delete_room(room_id: int, service: RoomService = Depends(get_room_service)):
    """Delete a room."""
    service.delete_room(room_id)
    return {"message": "Номер успешно удалён"}


@router.post("/api/{room_id}/toggle-availability", response_model=RoomSchema)
def toggle_availability(room_id: int, service: RoomService = Depends(get_room_service)):
    """Toggle room availability."""
    return service.toggle_availability(room_id)


# Web Routes
@router.get("/", response_class=HTMLResponse)
def rooms_list(
    request: Request,
    room_type: Optional[str] = None,
    is_available: Optional[str] = None,
    service: RoomService = Depends(get_room_service)
):
    """Rooms list page with filtering."""
    is_avail = None
    if is_available == "true":
        is_avail = True
    elif is_available == "false":
        is_avail = False

    normalized_room_type = room_type.strip() if room_type else None
    
    if normalized_room_type or is_avail is not None:
        rooms = service.search_rooms(room_type=normalized_room_type, is_available=is_avail)
    else:
        rooms = service.get_all_rooms()

    room_type_options = service.get_room_type_options()
    room_type_map = {}
    for room_type in room_type_options:
        if room_type.name:
            room_type_map[room_type.name.lower()] = room_type
        if getattr(room_type, "code", None):
            room_type_map[room_type.code.lower()] = room_type

    return templates.TemplateResponse("rooms/list.html", {
        "request": request,
        "rooms": rooms,
        "filter_room_type": normalized_room_type,
        "filter_is_available": is_available,
        "room_types": room_type_options,
        "room_type_map": room_type_map
    })


@router.get("/new", response_class=HTMLResponse)
def new_room_form(request: Request, service: RoomService = Depends(get_room_service)):
    """New room form page."""
    room_type_options = service.get_room_type_options()
    return templates.TemplateResponse("rooms/form.html", {
        "request": request,
        "room": None,
        "room_types": room_type_options
    })


@router.post("/new")
def create_room_form(
    request: Request,
    room_number: str = Form(...),
    room_type: str = Form(...),
    capacity: int = Form(...),
    price_per_night: float = Form(...),
    is_available: bool = Form(True),
    description: str = Form(None),
    service: RoomService = Depends(get_room_service)
):
    """Create room from form."""
    try:
        service.create_room({
            "room_number": room_number,
            "room_type": room_type,
            "capacity": capacity,
            "price_per_night": price_per_night,
            "is_available": is_available,
            "description": description
        })
        return RedirectResponse(url="/rooms", status_code=303)
    except Exception as e:
        room_type_options = service.get_room_type_options()
        return templates.TemplateResponse("rooms/form.html", {
            "request": request,
            "room": None,
            "room_types": room_type_options,
            "error": str(e)
        })


@router.get("/{room_id}/edit", response_class=HTMLResponse)
def edit_room_form(
    request: Request, 
    room_id: int, 
    service: RoomService = Depends(get_room_service)
):
    """Edit room form page."""
    room = service.get_room(room_id)
    room_type_options = service.get_room_type_options()
    return templates.TemplateResponse("rooms/form.html", {
        "request": request,
        "room": room,
        "room_types": room_type_options
    })


@router.post("/{room_id}/edit")
def update_room_form(
    room_id: int,
    request: Request,
    room_number: str = Form(...),
    room_type: str = Form(...),
    capacity: int = Form(...),
    price_per_night: float = Form(...),
    is_available: bool = Form(True),
    description: str = Form(None),
    service: RoomService = Depends(get_room_service)
):
    """Update room from form."""
    try:
        service.update_room(room_id, {
            "room_number": room_number,
            "room_type": room_type,
            "capacity": capacity,
            "price_per_night": price_per_night,
            "is_available": is_available,
            "description": description
        })
        return RedirectResponse(url="/rooms", status_code=303)
    except Exception as e:
        room = service.get_room(room_id)
        room_type_options = service.get_room_type_options()
        return templates.TemplateResponse("rooms/form.html", {
            "request": request,
            "room": room,
            "room_types": room_type_options,
            "error": str(e)
        })


@router.get("/{room_id}/delete")
def delete_room_web(room_id: int, service: RoomService = Depends(get_room_service)):
    """Delete room from web interface."""
    service.delete_room(room_id)
    return RedirectResponse(url="/rooms", status_code=303)
