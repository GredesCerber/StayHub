from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependencies import get_db
from app.services.service_service import ServiceService
from app.schemas.service import ServiceCreate, ServiceUpdate, Service as ServiceSchema

router = APIRouter(prefix="/services", tags=["services"])
templates = Jinja2Templates(directory="app/templates")


def get_service_service(db: Session = Depends(get_db)) -> ServiceService:
    """Dependency for ServiceService."""
    return ServiceService(db)


# API Routes
@router.get("/api", response_model=List[ServiceSchema])
def get_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    service: ServiceService = Depends(get_service_service)
):
    """Get all services with optional filtering."""
    if any([name, is_active is not None, min_price, max_price]):
        return service.search_services(
            name=name,
            is_active=is_active,
            min_price=min_price,
            max_price=max_price
        )
    return service.get_all_services(skip, limit)


@router.get("/api/active", response_model=List[ServiceSchema])
def get_active_services(service: ServiceService = Depends(get_service_service)):
    """Get all active services."""
    return service.get_active_services()


@router.get("/api/{service_id}", response_model=ServiceSchema)
def get_service(service_id: int, service: ServiceService = Depends(get_service_service)):
    """Get service by ID."""
    return service.get_service(service_id)


@router.post("/api", response_model=ServiceSchema, status_code=201)
def create_service(
    svc: ServiceCreate, 
    service: ServiceService = Depends(get_service_service)
):
    """Create a new service."""
    return service.create_service(svc.model_dump())


@router.put("/api/{service_id}", response_model=ServiceSchema)
def update_service(
    service_id: int, 
    svc: ServiceUpdate, 
    service: ServiceService = Depends(get_service_service)
):
    """Update a service."""
    return service.update_service(service_id, svc.model_dump(exclude_unset=True))


@router.delete("/api/{service_id}")
def delete_service(service_id: int, service: ServiceService = Depends(get_service_service)):
    """Delete a service."""
    service.delete_service(service_id)
    return {"message": "Service deleted successfully"}


@router.post("/api/{service_id}/toggle-active", response_model=ServiceSchema)
def toggle_active(service_id: int, service: ServiceService = Depends(get_service_service)):
    """Toggle service active status."""
    return service.toggle_active(service_id)


# Web Routes
@router.get("/", response_class=HTMLResponse)
def services_list(
    request: Request,
    name: Optional[str] = None,
    is_active: Optional[str] = None,
    service: ServiceService = Depends(get_service_service)
):
    """Services list page with filtering."""
    active = None
    if is_active == "true":
        active = True
    elif is_active == "false":
        active = False
    
    if name or active is not None:
        services = service.search_services(name=name, is_active=active)
    else:
        services = service.get_all_services()
    
    return templates.TemplateResponse("services/list.html", {
        "request": request, 
        "services": services,
        "filter_name": name,
        "filter_is_active": is_active
    })


@router.get("/new", response_class=HTMLResponse)
def new_service_form(request: Request):
    """New service form page."""
    return templates.TemplateResponse("services/form.html", {"request": request, "service": None})


@router.post("/new")
def create_service_form(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    is_active: bool = Form(True),
    service: ServiceService = Depends(get_service_service)
):
    """Create service from form."""
    try:
        service.create_service({
            "name": name,
            "description": description,
            "price": price,
            "is_active": is_active
        })
        return RedirectResponse(url="/services", status_code=303)
    except Exception as e:
        return templates.TemplateResponse("services/form.html", {
            "request": request, 
            "service": None,
            "error": str(e)
        })


@router.get("/{service_id}/edit", response_class=HTMLResponse)
def edit_service_form(
    request: Request, 
    service_id: int, 
    service: ServiceService = Depends(get_service_service)
):
    """Edit service form page."""
    svc = service.get_service(service_id)
    return templates.TemplateResponse("services/form.html", {"request": request, "service": svc})


@router.post("/{service_id}/edit")
def update_service_form(
    service_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    is_active: bool = Form(True),
    service: ServiceService = Depends(get_service_service)
):
    """Update service from form."""
    try:
        service.update_service(service_id, {
            "name": name,
            "description": description,
            "price": price,
            "is_active": is_active
        })
        return RedirectResponse(url="/services", status_code=303)
    except Exception as e:
        svc = service.get_service(service_id)
        return templates.TemplateResponse("services/form.html", {
            "request": request, 
            "service": svc,
            "error": str(e)
        })


@router.get("/{service_id}/delete")
def delete_service_web(service_id: int, service: ServiceService = Depends(get_service_service)):
    """Delete service from web interface."""
    service.delete_service(service_id)
    return RedirectResponse(url="/services", status_code=303)
