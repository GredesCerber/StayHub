"""Room service with business logic."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.room_repository import RoomRepository
from app.models.room import Room
from app.core.exceptions import NotFoundException, DuplicateException, ValidationException


class RoomService:
    """Service for room operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = RoomRepository(db)
    
    def get_room(self, room_id: int) -> Room:
        """Get room by ID with validation."""
        room = self.repository.get_by_id(room_id)
        if not room:
            raise NotFoundException("Room", room_id)
        return room
    
    def get_all_rooms(self, skip: int = 0, limit: int = 100) -> List[Room]:
        """Get all rooms with pagination."""
        return self.repository.get_all(skip, limit)
    
    def get_available_rooms(self) -> List[Room]:
        """Get available rooms."""
        return self.repository.get_available_rooms()
    
    def search_rooms(
        self,
        room_type: Optional[str] = None,
        min_capacity: Optional[int] = None,
        is_available: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Room]:
        """Search rooms with filters."""
        return self.repository.search(
            room_type=room_type,
            min_capacity=min_capacity,
            is_available=is_available,
            min_price=min_price,
            max_price=max_price
        )
    
    def create_room(self, room_data: dict) -> Room:
        """Create a new room with validation."""
        # Validate room number uniqueness
        existing = self.repository.get_by_room_number(room_data.get("room_number", ""))
        if existing:
            raise DuplicateException("Room", "room_number", room_data["room_number"])
        
        # Validate price
        if room_data.get("price_per_night", 0) <= 0:
            raise ValidationException("Price per night must be positive")
        
        # Validate capacity
        if room_data.get("capacity", 0) <= 0:
            raise ValidationException("Capacity must be at least 1")
        
        return self.repository.create(room_data)
    
    def update_room(self, room_id: int, room_data: dict) -> Room:
        """Update room with validation."""
        room = self.get_room(room_id)
        
        # Check room number uniqueness if changing
        new_room_number = room_data.get("room_number")
        if new_room_number and new_room_number != room.room_number:
            existing = self.repository.get_by_room_number(new_room_number)
            if existing:
                raise DuplicateException("Room", "room_number", new_room_number)
        
        # Validate price if provided
        if room_data.get("price_per_night") is not None and room_data["price_per_night"] <= 0:
            raise ValidationException("Price per night must be positive")
        
        # Validate capacity if provided
        if room_data.get("capacity") is not None and room_data["capacity"] <= 0:
            raise ValidationException("Capacity must be at least 1")
        
        return self.repository.update(room, room_data)
    
    def delete_room(self, room_id: int) -> None:
        """Delete room."""
        room = self.get_room(room_id)
        self.repository.delete(room)
    
    def toggle_availability(self, room_id: int) -> Room:
        """Toggle room availability."""
        room = self.get_room(room_id)
        return self.repository.update(room, {"is_available": not room.is_available})
    
    def count_rooms(self) -> int:
        """Count total rooms."""
        return self.repository.count()
    
    def count_available(self) -> int:
        """Count available rooms."""
        return len(self.repository.get_available_rooms())
