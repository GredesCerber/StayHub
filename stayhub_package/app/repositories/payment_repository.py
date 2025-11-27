"""Payment repository for database operations."""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.base_repository import BaseRepository
from app.models.payment import Payment


class PaymentRepository(BaseRepository[Payment]):
    """Repository for Payment model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Payment, db)
    
    def get_by_booking(self, booking_id: int) -> List[Payment]:
        """Get all payments for a booking."""
        return self.db.query(Payment).filter(Payment.booking_id == booking_id).all()
    
    def get_by_status(self, status: str) -> List[Payment]:
        """Get payments by status."""
        return self.db.query(Payment).filter(Payment.status == status).all()
    
    def get_by_method(self, payment_method: str) -> List[Payment]:
        """Get payments by method."""
        return self.db.query(Payment).filter(Payment.payment_method == payment_method).all()
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Payment]:
        """Get payments within date range."""
        return self.db.query(Payment).filter(
            Payment.payment_date >= start_date,
            Payment.payment_date <= end_date
        ).all()
    
    def get_total_revenue(self, status: str = "completed") -> float:
        """Get total revenue for completed payments."""
        result = self.db.query(func.sum(Payment.amount)).filter(
            Payment.status == status
        ).scalar()
        return result or 0.0
    
    def get_revenue_by_method(self) -> dict:
        """Get revenue grouped by payment method."""
        results = self.db.query(
            Payment.payment_method,
            func.sum(Payment.amount)
        ).filter(
            Payment.status == "completed"
        ).group_by(Payment.payment_method).all()
        
        return {method: amount for method, amount in results}
    
    def get_recent_payments(self, limit: int = 10) -> List[Payment]:
        """Get recent payments."""
        return self.db.query(Payment).order_by(
            Payment.payment_date.desc()
        ).limit(limit).all()
    
    def search(
        self,
        booking_id: Optional[int] = None,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Payment]:
        """Search payments with filters."""
        query = self.db.query(Payment)
        
        if booking_id:
            query = query.filter(Payment.booking_id == booking_id)
        if status:
            query = query.filter(Payment.status == status)
        if payment_method:
            query = query.filter(Payment.payment_method == payment_method)
        if start_date:
            query = query.filter(Payment.payment_date >= start_date)
        if end_date:
            query = query.filter(Payment.payment_date <= end_date)
        
        return query.order_by(Payment.payment_date.desc()).all()
