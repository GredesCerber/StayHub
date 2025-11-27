from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomUpdate, Room as RoomSchema

router = APIRouter(prefix="/rooms", tags=["rooms"])
templates = Jinja2Templates(directory="app/templates")


# API Routes
@router.get("/api", response_model=List[RoomSchema])
def get_rooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    rooms = db.query(Room).offset(skip).limit(limit).all()
    return rooms


@router.get("/api/{room_id}", response_model=RoomSchema)
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.post("/api", response_model=RoomSchema)
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    db_room = Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


@router.put("/api/{room_id}", response_model=RoomSchema)
def update_room(room_id: int, room: RoomUpdate, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    update_data = room.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_room, key, value)
    
    db.commit()
    db.refresh(db_room)
    return db_room


@router.delete("/api/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    db_room = db.query(Room).filter(Room.id == room_id).first()
    if db_room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    db.delete(db_room)
    db.commit()
    return {"message": "Room deleted successfully"}


# Web Routes
@router.get("/", response_class=HTMLResponse)
def rooms_list(request: Request, db: Session = Depends(get_db)):
    rooms = db.query(Room).all()
    return templates.TemplateResponse("rooms/list.html", {"request": request, "rooms": rooms})


@router.get("/new", response_class=HTMLResponse)
def new_room_form(request: Request):
    return templates.TemplateResponse("rooms/form.html", {"request": request, "room": None})


@router.post("/new")
def create_room_form(
    request: Request,
    room_number: str = Form(...),
    room_type: str = Form(...),
    capacity: int = Form(...),
    price_per_night: float = Form(...),
    is_available: bool = Form(True),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    room = Room(
        room_number=room_number,
        room_type=room_type,
        capacity=capacity,
        price_per_night=price_per_night,
        is_available=is_available,
        description=description
    )
    db.add(room)
    db.commit()
    return RedirectResponse(url="/rooms", status_code=303)


@router.get("/{room_id}/edit", response_class=HTMLResponse)
def edit_room_form(request: Request, room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return templates.TemplateResponse("rooms/form.html", {"request": request, "room": room})


@router.post("/{room_id}/edit")
def update_room_form(
    room_id: int,
    room_number: str = Form(...),
    room_type: str = Form(...),
    capacity: int = Form(...),
    price_per_night: float = Form(...),
    is_available: bool = Form(False),
    description: str = Form(None),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room.room_number = room_number
    room.room_type = room_type
    room.capacity = capacity
    room.price_per_night = price_per_night
    room.is_available = is_available
    room.description = description
    
    db.commit()
    return RedirectResponse(url="/rooms", status_code=303)


@router.get("/{room_id}/delete")
def delete_room_web(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    db.delete(room)
    db.commit()
    return RedirectResponse(url="/rooms", status_code=303)
