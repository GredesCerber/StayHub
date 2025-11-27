"""Booking repository for database operations."""
from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.repositories.base_repository import BaseRepository
from app.models.booking import Booking


class BookingRepository(BaseRepository[Booking]):
    """Repository for Booking model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Booking, db)
    
    def get_by_guest(self, guest_id: int) -> List[Booking]:
        """Get all bookings for a guest."""
        return self.db.query(Booking).filter(Booking.guest_id == guest_id).all()
    
    def get_by_room(self, room_id: int) -> List[Booking]:
        """Get all bookings for a room."""
        return self.db.query(Booking).filter(Booking.room_id == room_id).all()
    
    def get_by_status(self, status: str) -> List[Booking]:
        """Get bookings by status."""
        return self.db.query(Booking).filter(Booking.status == status).all()
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Booking]:
        """Get bookings within date range."""
        return self.db.query(Booking).filter(
            and_(
                Booking.check_in_date >= start_date,
                Booking.check_out_date <= end_date
            )
        ).all()
    
    def get_active_bookings(self) -> List[Booking]:
        """Get active (pending/confirmed) bookings."""
        return self.db.query(Booking).filter(
            Booking.status.in_(["pending", "confirmed"])
        ).all()
    
    def get_conflicting_bookings(
        self, 
        room_id: int, 
        check_in: date, 
        check_out: date,
        exclude_booking_id: Optional[int] = None,
        buffer_days: int = 0
    ) -> List[Booking]:
        """Get bookings that conflict with given date range (with optional buffer)."""
        buffer_delta = timedelta(days=buffer_days)
        window_start = check_in - buffer_delta
        window_end = check_out + buffer_delta
        query = self.db.query(Booking).filter(
            Booking.room_id == room_id,
            Booking.status.notin_(["cancelled"]),
            Booking.check_in_date < window_end,
            Booking.check_out_date > window_start
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        return query.all()
    
    def get_todays_checkins(self) -> List[Booking]:
        """Get today's check-ins."""
        today = date.today()
        return self.db.query(Booking).filter(
            Booking.check_in_date == today,
            Booking.status.in_(["pending", "confirmed"])
        ).all()
    
    def get_todays_checkouts(self) -> List[Booking]:
        """Get today's check-outs."""
        today = date.today()
        return self.db.query(Booking).filter(
            Booking.check_out_date == today,
            Booking.status.in_(["confirmed"])
        ).all()
    
    def get_upcoming_bookings(self, limit: int = 10) -> List[Booking]:
        """Get upcoming bookings."""
        today = date.today()
        return self.db.query(Booking).filter(
            Booking.check_in_date >= today,
            Booking.status.in_(["pending", "confirmed"])
        ).order_by(Booking.check_in_date).limit(limit).all()
    
    def search(
        self,
        guest_id: Optional[int] = None,
        room_id: Optional[int] = None,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Booking]:
        """Search bookings with filters."""
        query = self.db.query(Booking)
        
        if guest_id:
            query = query.filter(Booking.guest_id == guest_id)
        if room_id:
            query = query.filter(Booking.room_id == room_id)
        if status:
            query = query.filter(Booking.status == status)
        if start_date:
            query = query.filter(Booking.check_in_date >= start_date)
        if end_date:
            query = query.filter(Booking.check_out_date <= end_date)
        
        return query.order_by(Booking.check_in_date.desc()).all()
