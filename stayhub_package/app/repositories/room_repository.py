"""Room repository for database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.room import Room


class RoomRepository(BaseRepository[Room]):
    """Repository for Room model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Room, db)
    
    def get_by_room_number(self, room_number: str) -> Optional[Room]:
        """Get room by room number."""
        return self.db.query(Room).filter(Room.room_number == room_number).first()
    
    def get_available_rooms(self) -> List[Room]:
        """Get all available rooms."""
        return self.db.query(Room).filter(Room.is_available == True).all()
    
    def get_by_type(self, room_type: str) -> List[Room]:
        """Get rooms by type."""
        return self.db.query(Room).filter(Room.room_type == room_type).all()
    
    def get_by_capacity(self, min_capacity: int) -> List[Room]:
        """Get rooms with minimum capacity."""
        return self.db.query(Room).filter(Room.capacity >= min_capacity).all()
    
    def get_by_price_range(self, min_price: float, max_price: float) -> List[Room]:
        """Get rooms within price range."""
        return self.db.query(Room).filter(
            Room.price_per_night >= min_price,
            Room.price_per_night <= max_price
        ).all()
    
    def search(
        self, 
        room_type: Optional[str] = None,
        min_capacity: Optional[int] = None,
        is_available: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[Room]:
        """Search rooms with filters."""
        query = self.db.query(Room)
        
        if room_type:
            query = query.filter(Room.room_type == room_type)
        if min_capacity:
            query = query.filter(Room.capacity >= min_capacity)
        if is_available is not None:
            query = query.filter(Room.is_available == is_available)
        if min_price:
            query = query.filter(Room.price_per_night >= min_price)
        if max_price:
            query = query.filter(Room.price_per_night <= max_price)
        
        return query.all()
