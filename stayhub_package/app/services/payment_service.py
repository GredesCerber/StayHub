"""Сервис работы с платежами."""
from typing import List, Optional, Dict
from datetime import date
from sqlalchemy.orm import Session
from app.repositories.payment_repository import PaymentRepository
from app.repositories.booking_repository import BookingRepository
from app.models.payment import Payment
from app.core.exceptions import NotFoundException, ValidationException
from app.core.validators import PAYMENT_METHODS, PAYMENT_STATUSES


class PaymentService:
    """Сервисный слой для операций с платежами."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = PaymentRepository(db)
        self.booking_repository = BookingRepository(db)
    
    def get_payment(self, payment_id: int) -> Payment:
        """Получить платеж по идентификатору с проверками."""
        payment = self.repository.get_by_id(payment_id)
        if not payment:
            raise NotFoundException("Платёж", payment_id)
        return payment
    
    def get_all_payments(self, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Получить список платежей с пагинацией."""
        return self.repository.get_all(skip, limit)
    
    def get_payments_for_booking(self, booking_id: int) -> List[Payment]:
        """Получить платежи по конкретной брони."""
        return self.repository.get_by_booking(booking_id)
    
    def search_payments(
        self,
        booking_id: Optional[int] = None,
        status: Optional[str] = None,
        payment_method: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Payment]:
        """Найти платежи по фильтрам."""
        return self.repository.search(
            booking_id=booking_id,
            status=status,
            payment_method=payment_method,
            start_date=start_date,
            end_date=end_date
        )
    
    def create_payment(self, payment_data: dict) -> Payment:
        """Создать платеж с проверкой данных."""
        booking_id = payment_data.get("booking_id")
        
        # Validate booking exists
        booking = self.booking_repository.get_by_id(booking_id)
        if not booking:
            raise NotFoundException("Бронирование", booking_id)
        
        # Validate amount
        if payment_data.get("amount", 0) <= 0:
            raise ValidationException("Сумма платежа должна быть положительной")
        
        # Validate payment method
        method = payment_data.get("payment_method", "")
        if method not in PAYMENT_METHODS:
            raise ValidationException(
                "Недопустимый способ оплаты. Используйте один из: " + ", ".join(PAYMENT_METHODS)
            )
        
        # Set payment date if not provided
        if not payment_data.get("payment_date"):
            payment_data["payment_date"] = date.today()
        
        return self.repository.create(payment_data)
    
    def update_payment(self, payment_id: int, payment_data: dict) -> Payment:
        """Обновить платеж с проверками."""
        payment = self.get_payment(payment_id)
        
        # Validate amount if provided
        if payment_data.get("amount") is not None and payment_data["amount"] <= 0:
            raise ValidationException("Сумма платежа должна быть положительной")
        
        # Validate payment method if provided
        method = payment_data.get("payment_method")
        if method and method not in PAYMENT_METHODS:
            raise ValidationException(
                "Недопустимый способ оплаты. Используйте один из: " + ", ".join(PAYMENT_METHODS)
            )
        
        return self.repository.update(payment, payment_data)
    
    def delete_payment(self, payment_id: int) -> None:
        """Удалить платеж."""
        payment = self.get_payment(payment_id)
        self.repository.delete(payment)
    
    def update_status(self, payment_id: int, status: str) -> Payment:
        """Обновить статус платежа."""
        if status not in PAYMENT_STATUSES:
            raise ValidationException(
                "Недопустимый статус. Используйте один из: " + ", ".join(PAYMENT_STATUSES)
            )

        payment = self.get_payment(payment_id)
        update_payload: Dict[str, object] = {"status": status}
        if status == "completed" and not payment.payment_date:
            update_payload["payment_date"] = date.today()
        return self.repository.update(payment, update_payload)
    
    def get_total_revenue(self) -> float:
        """Получить суммарный доход по завершённым платежам."""
        return self.repository.get_total_revenue()
    
    def get_revenue_by_method(self) -> Dict[str, float]:
        """Получить доход в разрезе способов оплаты."""
        return self.repository.get_revenue_by_method()
    
    def get_recent_payments(self, limit: int = 10) -> List[Payment]:
        """Получить последние платежи."""
        return self.repository.get_recent_payments(limit)
    
    def count_payments(self) -> int:
        """Посчитать количество платежей."""
        return self.repository.count()
    
    def count_by_status(self, status: str) -> int:
        """Посчитать число платежей по статусу."""
        return len(self.repository.get_by_status(status))
