"""Room service with business logic."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.room_repository import RoomRepository
from app.models.room import Room
from app.repositories.room_type_repository import RoomTypeRepository
from app.core.exceptions import NotFoundException, DuplicateException, ValidationException


class RoomService:
    """Service for room operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = RoomRepository(db)
        self.room_type_repository = RoomTypeRepository(db)

    def get_room_type_options(self):
        """Return available room types ordered by name."""
        return self.room_type_repository.list_sorted()

    def _normalize_payload(self, room_data: dict) -> dict:
        """Cast primitive fields and trim whitespace from string inputs."""
        if "capacity" in room_data and isinstance(room_data.get("capacity"), str):
            capacity_raw = room_data["capacity"].strip()
            if capacity_raw:
                if not capacity_raw.isdigit():
                    raise ValidationException("Вместимость должна быть целым числом")
                room_data["capacity"] = int(capacity_raw)

        if "room_number" in room_data and room_data.get("room_number") is not None:
            room_data["room_number"] = str(room_data["room_number"]).strip()

        if "price_per_night" in room_data and isinstance(room_data.get("price_per_night"), str):
            price_raw = room_data["price_per_night"].strip().replace(",", ".")
            if price_raw:
                try:
                    room_data["price_per_night"] = float(price_raw)
                except ValueError as exc:
                    raise ValidationException("Цена должна быть числом") from exc

        if "is_available" in room_data and isinstance(room_data.get("is_available"), str):
            room_data["is_available"] = room_data["is_available"].lower() in {"true", "1", "on", "yes"}

        return room_data

    def _apply_room_type_defaults(self, room_data: dict, current_type: Optional[str] = None) -> dict:
        """Normalize room type field and apply defaults when possible."""
        provided_value = ""
        if "room_type" in room_data and room_data.get("room_type") is not None:
            provided_value = str(room_data.get("room_type")).strip()

        identifier_source = provided_value if provided_value else (current_type or "")
        identifier = (identifier_source or "").strip()

        if not identifier:
            raise ValidationException("Не выбран тип номера")

        room_type_ref = self.room_type_repository.find_by_identifier(identifier)

        room_type_key_present = "room_type" in room_data

        if room_type_ref:
            if provided_value or room_type_key_present:
                room_data["room_type"] = room_type_ref.name

            should_apply_defaults = bool(provided_value) or current_type is None

            if should_apply_defaults:
                capacity_value = room_data.get("capacity")
                if (
                    capacity_value in (None, "", 0)
                    and room_type_ref.default_capacity is not None
                ):
                    room_data["capacity"] = room_type_ref.default_capacity

                price_value = room_data.get("price_per_night")
                if (
                    price_value in (None, "", 0)
                    and room_type_ref.default_price is not None
                ):
                    room_data["price_per_night"] = room_type_ref.default_price
        else:
            if provided_value or room_type_key_present:
                room_data["room_type"] = identifier

        return room_data
    
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
            room_type=room_type.strip() if room_type else None,
            min_capacity=min_capacity,
            is_available=is_available,
            min_price=min_price,
            max_price=max_price
        )
    
    def create_room(self, room_data: dict) -> Room:
        """Create a new room with validation."""
        room_data = self._normalize_payload(room_data)

        # Normalize type and auto-fill defaults
        room_data = self._apply_room_type_defaults(room_data)

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
        
        room_data = self._normalize_payload(room_data)

        # Normalize type and auto-fill defaults when updating
        room_data = self._apply_room_type_defaults(room_data, current_type=room.room_type if room else None)

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
