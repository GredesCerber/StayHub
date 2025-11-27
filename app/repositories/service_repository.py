"""Service repository for database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.service import Service


class ServiceRepository(BaseRepository[Service]):
    """Repository for Service model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Service, db)
    
    def get_by_name(self, name: str) -> Optional[Service]:
        """Get service by name."""
        return self.db.query(Service).filter(Service.name == name).first()
    
    def get_active_services(self) -> List[Service]:
        """Get all active services."""
        return self.db.query(Service).filter(Service.is_active == True).all()
    
    def get_by_price_range(self, min_price: float, max_price: float) -> List[Service]:
        """Get services within price range."""
        return self.db.query(Service).filter(
            Service.price >= min_price,
            Service.price <= max_price
        ).all()
    
    def search(
        self,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Service]:
        """Search services with filters."""
        query = self.db.query(Service)
        
        if name:
            query = query.filter(Service.name.ilike(f"%{name}%"))
        if is_active is not None:
            query = query.filter(Service.is_active == is_active)
        if min_price:
            query = query.filter(Service.price >= min_price)
        if max_price:
            query = query.filter(Service.price <= max_price)
        
        return query.all()
