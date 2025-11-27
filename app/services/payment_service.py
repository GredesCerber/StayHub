"""Payment service with business logic."""
from typing import List, Optional, Dict
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.payment_repository import PaymentRepository
from app.repositories.booking_repository import BookingRepository
from app.models.payment import Payment
from app.core.exceptions import NotFoundException, ValidationException


class PaymentService:
    """Service for payment operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = PaymentRepository(db)
        self.booking_repository = BookingRepository(db)
    
    def get_payment(self, payment_id: int) -> Payment:
        """Get payment by ID with validation."""
        payment = self.repository.get_by_id(payment_id)
        if not payment:
            raise NotFoundException("Payment", payment_id)
        return payment
    
    def get_all_payments(self, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Get all payments with pagination."""
        return self.repository.get_all(skip, limit)
    
    def get_payments_for_booking(self, booking_id: int) -> List[Payment]:
        """Get all payments for a booking."""
        return self.repository.get_by_booking(booking_id)
    
    def search_payments(
        self,
        booking_id: Optional[int] = None,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Payment]:
        """Search payments with filters."""
        return self.repository.search(
            booking_id=booking_id,
            status=status,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date
        )
    
    def create_payment(self, payment_data: dict) -> Payment:
        """Create a new payment with validation."""
        booking_id = payment_data.get("booking_id")
        
        # Validate booking exists
        booking = self.booking_repository.get_by_id(booking_id)
        if not booking:
            raise NotFoundException("Booking", booking_id)
        
        # Validate amount
        if payment_data.get("amount", 0) <= 0:
            raise ValidationException("Payment amount must be positive")
        
        # Validate payment method
        valid_methods = ["cash", "card", "transfer"]
        method = payment_data.get("payment_method", "")
        if method not in valid_methods:
            raise ValidationException(f"Invalid payment method. Must be one of: {', '.join(valid_methods)}")
        
        # Set payment date if not provided
        if not payment_data.get("payment_date"):
            payment_data["payment_date"] = date.today()
        
        return self.repository.create(payment_data)
    
    def update_payment(self, payment_id: int, payment_data: dict) -> Payment:
        """Update payment with validation."""
        payment = self.get_payment(payment_id)
        
        # Validate amount if provided
        if payment_data.get("amount") is not None and payment_data["amount"] <= 0:
            raise ValidationException("Payment amount must be positive")
        
        # Validate payment method if provided
        valid_methods = ["cash", "card", "transfer"]
        method = payment_data.get("payment_method")
        if method and method not in valid_methods:
            raise ValidationException(f"Invalid payment method. Must be one of: {', '.join(valid_methods)}")
        
        return self.repository.update(payment, payment_data)
    
    def delete_payment(self, payment_id: int) -> None:
        """Delete payment."""
        payment = self.get_payment(payment_id)
        self.repository.delete(payment)
    
    def update_status(self, payment_id: int, status: str) -> Payment:
        """Update payment status."""
        valid_statuses = ["pending", "completed", "refunded"]
        if status not in valid_statuses:
            raise ValidationException(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        payment = self.get_payment(payment_id)
        return self.repository.update(payment, {"status": status})
    
    def get_total_revenue(self) -> float:
        """Get total revenue from completed payments."""
        return self.repository.get_total_revenue()
    
    def get_revenue_by_method(self) -> Dict[str, float]:
        """Get revenue grouped by payment method."""
        return self.repository.get_revenue_by_method()
    
    def get_recent_payments(self, limit: int = 10) -> List[Payment]:
        """Get recent payments."""
        return self.repository.get_recent_payments(limit)
    
    def count_payments(self) -> int:
        """Count total payments."""
        return self.repository.count()
    
    def count_by_status(self, status: str) -> int:
        """Count payments by status."""
        return len(self.repository.get_by_status(status))
