from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from app.services.room_type_service import RoomTypeService
from app.schemas.room_type import RoomTypeCreate, RoomTypeUpdate, RoomType as RoomTypeSchema

router = APIRouter(prefix="/room-types", tags=["room-types"])
templates = Jinja2Templates(directory="app/templates")


def get_room_type_service(db: Session = Depends(get_db)) -> RoomTypeService:
    return RoomTypeService(db)


@router.get("/api", response_model=List[RoomTypeSchema])
def list_room_types(service: RoomTypeService = Depends(get_room_type_service)):
    return service.list_types()


@router.post("/api", response_model=RoomTypeSchema, status_code=201)
def create_room_type_api(
    room_type: RoomTypeCreate,
    service: RoomTypeService = Depends(get_room_type_service)
):
    return service.create_type(room_type.model_dump())


@router.put("/api/{type_id}", response_model=RoomTypeSchema)
def update_room_type_api(
    type_id: int,
    room_type: RoomTypeUpdate,
    service: RoomTypeService = Depends(get_room_type_service)
):
    return service.update_type(type_id, room_type.model_dump(exclude_unset=True))


@router.delete("/api/{type_id}")
def delete_room_type_api(type_id: int, service: RoomTypeService = Depends(get_room_type_service)):
    service.delete_type(type_id)
    return {"message": "Тип номера удалён"}


@router.get("/", response_class=HTMLResponse)
def room_type_list_page(
    request: Request,
    service: RoomTypeService = Depends(get_room_type_service),
    error: Optional[str] = None
):
    types = service.list_types()
    return templates.TemplateResponse("room_types/list.html", {
        "request": request,
        "types": types,
        "error": error
    })


@router.get("/new", response_class=HTMLResponse)
def room_type_form_page(request: Request):
    return templates.TemplateResponse("room_types/form.html", {
        "request": request,
        "room_type": None
    })


@router.post("/new")
def create_room_type_form(
    request: Request,
    code: str = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    default_capacity: str = Form(None),
    default_price: str = Form(None),
    service: RoomTypeService = Depends(get_room_type_service)
):
    try:
        capacity_value = (default_capacity or "").strip()
        price_value = (default_price or "").strip()
        data = {
            "code": code,
            "name": name,
            "description": description,
            "default_capacity": int(capacity_value) if capacity_value else None,
            "default_price": float(price_value.replace(",", ".")) if price_value else None
        }
        service.create_type(data)
        return RedirectResponse(url="/room-types", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("room_types/form.html", {
            "request": request,
            "room_type": None,
            "error": str(e)
        })


@router.get("/{type_id}/edit", response_class=HTMLResponse)
def edit_room_type_form(
    request: Request,
    type_id: int,
    service: RoomTypeService = Depends(get_room_type_service)
):
    room_type = service.get_type(type_id)
    return templates.TemplateResponse("room_types/form.html", {
        "request": request,
        "room_type": room_type
    })


@router.post("/{type_id}/edit")
def update_room_type_form(
    type_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    default_capacity: str = Form(None),
    default_price: str = Form(None),
    service: RoomTypeService = Depends(get_room_type_service)
):
    try:
        capacity_value = (default_capacity or "").strip()
        price_value = (default_price or "").strip()
        data = {
            "name": name,
            "description": description,
            "default_capacity": int(capacity_value) if capacity_value else None,
            "default_price": float(price_value.replace(",", ".")) if price_value else None
        }
        service.update_type(type_id, data)
        return RedirectResponse(url="/room-types", status_code=303)
    except Exception as e:
        room_type = service.get_type(type_id)
        return templates.TemplateResponse("room_types/form.html", {
            "request": request,
            "room_type": room_type,
            "error": str(e)
        })


@router.get("/{type_id}/delete")
def delete_room_type_form(
    request: Request,
    type_id: int,
    service: RoomTypeService = Depends(get_room_type_service)
):
    try:
        service.delete_type(type_id)
        return RedirectResponse(url="/room-types", status_code=303)
    except Exception as exc:
        types = service.list_types()
        return templates.TemplateResponse("room_types/list.html", {
            "request": request,
            "types": types,
            "error": str(exc)
        })
