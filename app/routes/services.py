from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate, Service as ServiceSchema

router = APIRouter(prefix="/services", tags=["services"])
templates = Jinja2Templates(directory="app/templates")


# API Routes
@router.get("/api", response_model=List[ServiceSchema])
def get_services(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    services = db.query(Service).offset(skip).limit(limit).all()
    return services


@router.get("/api/{service_id}", response_model=ServiceSchema)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/api", response_model=ServiceSchema)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    db_service = Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@router.put("/api/{service_id}", response_model=ServiceSchema)
def update_service(service_id: int, service: ServiceUpdate, db: Session = Depends(get_db)):
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    
    update_data = service.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_service, key, value)
    
    db.commit()
    db.refresh(db_service)
    return db_service


@router.delete("/api/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    
    db.delete(db_service)
    db.commit()
    return {"message": "Service deleted successfully"}


# Web Routes
@router.get("/", response_class=HTMLResponse)
def services_list(request: Request, db: Session = Depends(get_db)):
    services = db.query(Service).all()
    return templates.TemplateResponse("services/list.html", {"request": request, "services": services})


@router.get("/new", response_class=HTMLResponse)
def new_service_form(request: Request):
    return templates.TemplateResponse("services/form.html", {"request": request, "service": None})


@router.post("/new")
def create_service_form(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    is_active: bool = Form(True),
    db: Session = Depends(get_db)
):
    service = Service(
        name=name,
        description=description,
        price=price,
        is_active=is_active
    )
    db.add(service)
    db.commit()
    return RedirectResponse(url="/services", status_code=303)


@router.get("/{service_id}/edit", response_class=HTMLResponse)
def edit_service_form(request: Request, service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return templates.TemplateResponse("services/form.html", {"request": request, "service": service})


@router.post("/{service_id}/edit")
def update_service_form(
    service_id: int,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    is_active: bool = Form(True),
    db: Session = Depends(get_db)
):
    service = db.query(Service).filter(Service.id == service_id).first()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    
    service.name = name
    service.description = description
    service.price = price
    service.is_active = is_active
    
    db.commit()
    return RedirectResponse(url="/services", status_code=303)


@router.get("/{service_id}/delete")
def delete_service_web(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == service_id).first()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    
    db.delete(service)
    db.commit()
    return RedirectResponse(url="/services", status_code=303)
