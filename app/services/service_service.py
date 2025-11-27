"""Service service with business logic."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.service_repository import ServiceRepository
from app.models.service import Service
from app.core.exceptions import NotFoundException, DuplicateException, ValidationException


class ServiceService:
    """Service for hotel services operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = ServiceRepository(db)
    
    def get_service(self, service_id: int) -> Service:
        """Get service by ID with validation."""
        service = self.repository.get_by_id(service_id)
        if not service:
            raise NotFoundException("Service", service_id)
        return service
    
    def get_all_services(self, skip: int = 0, limit: int = 100) -> List[Service]:
        """Get all services with pagination."""
        return self.repository.get_all(skip, limit)
    
    def get_active_services(self) -> List[Service]:
        """Get active services."""
        return self.repository.get_active_services()
    
    def search_services(
        self,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Service]:
        """Search services with filters."""
        return self.repository.search(
            name=name,
            is_active=is_active,
            min_price=min_price,
            max_price=max_price
        )
    
    def create_service(self, service_data: dict) -> Service:
        """Create a new service with validation."""
        name = service_data.get("name", "")
        
        # Validate name uniqueness
        if name:
            existing = self.repository.get_by_name(name)
            if existing:
                raise DuplicateException("Service", "name", name)
        
        # Validate required fields
        if not name:
            raise ValidationException("Service name is required")
        
        # Validate price
        if service_data.get("price", 0) < 0:
            raise ValidationException("Price cannot be negative")
        
        return self.repository.create(service_data)
    
    def update_service(self, service_id: int, service_data: dict) -> Service:
        """Update service with validation."""
        service = self.get_service(service_id)
        
        # Check name uniqueness if changing
        new_name = service_data.get("name")
        if new_name and new_name != service.name:
            existing = self.repository.get_by_name(new_name)
            if existing:
                raise DuplicateException("Service", "name", new_name)
        
        # Validate price if provided
        if service_data.get("price") is not None and service_data["price"] < 0:
            raise ValidationException("Price cannot be negative")
        
        return self.repository.update(service, service_data)
    
    def delete_service(self, service_id: int) -> None:
        """Delete service."""
        service = self.get_service(service_id)
        self.repository.delete(service)
    
    def toggle_active(self, service_id: int) -> Service:
        """Toggle service active status."""
        service = self.get_service(service_id)
        return self.repository.update(service, {"is_active": not service.is_active})
    
    def count_services(self) -> int:
        """Count total services."""
        return self.repository.count()
    
    def count_active(self) -> int:
        """Count active services."""
        return len(self.repository.get_active_services())
