"""Booking service with business logic, availability checking and cost calculation."""
from typing import List, Optional, Dict, Any
from datetime import date
from dataclasses import dataclass
from sqlalchemy.orm import Session
from app.repositories.booking_repository import BookingRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.guest_repository import GuestRepository
from app.repositories.booking_service_repository import BookingServiceRepository
from app.repositories.service_repository import ServiceRepository
from app.models.booking import Booking
from app.core.exceptions import (
    NotFoundException, 
    RoomNotAvailableException, 
    ValidationException
)


@dataclass
class CostBreakdown:
    """Cost breakdown for a booking."""
    room_cost: float
    nights: int
    price_per_night: float
    services: List[Dict[str, Any]]
    services_total: float
    total_cost: float


class BookingService:
    """Service for booking operations with availability checking and cost calculation."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = BookingRepository(db)
        self.room_repository = RoomRepository(db)
        self.guest_repository = GuestRepository(db)
        self.booking_service_repository = BookingServiceRepository(db)
        self.service_repository = ServiceRepository(db)
    
    def get_booking(self, booking_id: int) -> Booking:
        """Get booking by ID with validation."""
        booking = self.repository.get_by_id(booking_id)
        if not booking:
            raise NotFoundException("Booking", booking_id)
        return booking
    
    def get_all_bookings(self, skip: int = 0, limit: int = 100) -> List[Booking]:
        """Get all bookings with pagination."""
        return self.repository.get_all(skip, limit)
    
    def search_bookings(
        self,
        guest_id: Optional[int] = None,
        room_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Booking]:
        """Search bookings with filters."""
        return self.repository.search(
            guest_id=guest_id,
            room_id=room_id,
            status=status,
            start_date=start_date,
            end_date=end_date
        )
    
    def check_room_availability(
        self,
        room_id: int,
        check_in: date,
        check_out: date,
        exclude_booking_id: Optional[int] = None
    ) -> bool:
        """Check if a room is available for the given date range."""
        # Validate dates
        if check_in >= check_out:
            raise ValidationException("Check-out date must be after check-in date")
        
        if check_in < date.today():
            raise ValidationException("Check-in date cannot be in the past")
        
        # Check room exists
        room = self.room_repository.get_by_id(room_id)
        if not room:
            raise NotFoundException("Room", room_id)
        
        # Check for conflicting bookings
        conflicts = self.repository.get_conflicting_bookings(
            room_id, check_in, check_out, exclude_booking_id
        )
        
        return len(conflicts) == 0
    
    def get_available_rooms_for_dates(
        self, 
        check_in: date, 
        check_out: date,
        room_type: Optional[str] = None,
        min_capacity: Optional[int] = None
    ) -> List[Any]:
        """Get all rooms available for given date range."""
        all_rooms = self.room_repository.search(
            room_type=room_type,
            min_capacity=min_capacity,
            is_available=True
        )
        
        available_rooms = []
        for room in all_rooms:
            if self.check_room_availability(room.id, check_in, check_out):
                available_rooms.append(room)
        
        return available_rooms
    
    def calculate_cost_breakdown(self, booking: Booking) -> CostBreakdown:
        """Calculate detailed cost breakdown for a booking."""
        if not booking.check_in_date or not booking.check_out_date:
            return CostBreakdown(
                room_cost=0.0,
                nights=0,
                price_per_night=0.0,
                services=[],
                services_total=0.0,
                total_cost=0.0
            )
        
        # Calculate nights
        nights = (booking.check_out_date - booking.check_in_date).days
        if nights <= 0:
            nights = 1
        
        # Get room price
        room = self.room_repository.get_by_id(booking.room_id)
        price_per_night = room.price_per_night if room else 0.0
        room_cost = price_per_night * nights
        
        # Get services
        booking_services = self.booking_service_repository.get_by_booking(booking.id)
        services = []
        services_total = 0.0
        
        for bs in booking_services:
            service = self.service_repository.get_by_id(bs.service_id)
            if service:
                services.append({
                    "name": service.name,
                    "quantity": bs.quantity,
                    "unit_price": service.price,
                    "subtotal": bs.subtotal or 0
                })
                services_total += bs.subtotal or 0
        
        total_cost = room_cost + services_total
        
        return CostBreakdown(
            room_cost=room_cost,
            nights=nights,
            price_per_night=price_per_night,
            services=services,
            services_total=services_total,
            total_cost=total_cost
        )
    
    def calculate_booking_cost(self, booking: Booking) -> float:
        """Calculate total cost for a booking."""
        breakdown = self.calculate_cost_breakdown(booking)
        return breakdown.total_cost
    
    def create_booking(self, booking_data: dict) -> Booking:
        """Create a new booking with availability check and cost calculation."""
        room_id = booking_data.get("room_id")
        guest_id = booking_data.get("guest_id")
        check_in = booking_data.get("check_in_date")
        check_out = booking_data.get("check_out_date")
        
        # Validate guest exists
        guest = self.guest_repository.get_by_id(guest_id)
        if not guest:
            raise NotFoundException("Guest", guest_id)
        
        # Check room availability
        if not self.check_room_availability(room_id, check_in, check_out):
            raise RoomNotAvailableException(room_id, str(check_in), str(check_out))
        
        # Create booking
        booking = self.repository.create(booking_data)
        
        # Calculate and set cost
        booking.total_cost = self.calculate_booking_cost(booking)
        self.db.commit()
        self.db.refresh(booking)
        
        return booking
    
    def update_booking(self, booking_id: int, booking_data: dict) -> Booking:
        """Update booking with availability check."""
        booking = self.get_booking(booking_id)
        
        # Get new values or use existing
        room_id = booking_data.get("room_id", booking.room_id)
        check_in = booking_data.get("check_in_date", booking.check_in_date)
        check_out = booking_data.get("check_out_date", booking.check_out_date)
        
        # Check room availability for new dates/room
        if not self.check_room_availability(room_id, check_in, check_out, booking_id):
            raise RoomNotAvailableException(room_id, str(check_in), str(check_out))
        
        # Update booking
        booking = self.repository.update(booking, booking_data)
        
        # Recalculate cost
        booking.total_cost = self.calculate_booking_cost(booking)
        self.db.commit()
        self.db.refresh(booking)
        
        return booking
    
    def delete_booking(self, booking_id: int) -> None:
        """Delete booking and associated services."""
        booking = self.get_booking(booking_id)
        self.booking_service_repository.delete_by_booking(booking_id)
        self.repository.delete(booking)
    
    def update_status(self, booking_id: int, status: str) -> Booking:
        """Update booking status."""
        valid_statuses = ["pending", "confirmed", "cancelled", "completed"]
        if status not in valid_statuses:
            raise ValidationException(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        booking = self.get_booking(booking_id)
        return self.repository.update(booking, {"status": status})
    
    def recalculate_cost(self, booking_id: int) -> Booking:
        """Recalculate and update booking cost."""
        booking = self.get_booking(booking_id)
        booking.total_cost = self.calculate_booking_cost(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking
    
    def get_todays_checkins(self) -> List[Booking]:
        """Get today's check-ins."""
        return self.repository.get_todays_checkins()
    
    def get_todays_checkouts(self) -> List[Booking]:
        """Get today's check-outs."""
        return self.repository.get_todays_checkouts()
    
    def get_upcoming_bookings(self, limit: int = 10) -> List[Booking]:
        """Get upcoming bookings."""
        return self.repository.get_upcoming_bookings(limit)
    
    def get_active_bookings(self) -> List[Booking]:
        """Get active bookings."""
        return self.repository.get_active_bookings()
    
    def count_bookings(self) -> int:
        """Count total bookings."""
        return self.repository.count()
    
    def count_by_status(self, status: str) -> int:
        """Count bookings by status."""
        return len(self.repository.get_by_status(status))
