"""BookingService repository for database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.base_repository import BaseRepository
from app.models.booking_service import BookingService


class BookingServiceRepository(BaseRepository[BookingService]):
    """Repository for BookingService model operations."""
    
    def __init__(self, db: Session):
        super().__init__(BookingService, db)
    
    def get_by_booking(self, booking_id: int) -> List[BookingService]:
        """Get all services for a booking."""
        return self.db.query(BookingService).filter(
            BookingService.booking_id == booking_id
        ).all()
    
    def get_by_service(self, service_id: int) -> List[BookingService]:
        """Get all booking services by service."""
        return self.db.query(BookingService).filter(
            BookingService.service_id == service_id
        ).all()
    
    def get_total_for_booking(self, booking_id: int) -> float:
        """Get total service cost for a booking."""
        result = self.db.query(func.sum(BookingService.subtotal)).filter(
            BookingService.booking_id == booking_id
        ).scalar()
        return result or 0.0
    
    def get_most_used_services(self, limit: int = 5) -> List[tuple]:
        """Get most frequently used services."""
        return self.db.query(
            BookingService.service_id,
            func.count(BookingService.id).label('usage_count'),
            func.sum(BookingService.subtotal).label('total_revenue')
        ).group_by(
            BookingService.service_id
        ).order_by(
            func.count(BookingService.id).desc()
        ).limit(limit).all()
    
    def delete_by_booking(self, booking_id: int) -> int:
        """Delete all services for a booking."""
        count = self.db.query(BookingService).filter(
            BookingService.booking_id == booking_id
        ).delete()
        self.db.commit()
        return count
