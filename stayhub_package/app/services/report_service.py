"""Report service for generating reports and statistics."""
from typing import Dict, List, Any, Optional
from datetime import date, timedelta
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.repositories.room_repository import RoomRepository
from app.repositories.guest_repository import GuestRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.booking_service_repository import BookingServiceRepository
from app.repositories.service_repository import ServiceRepository
from app.models.booking import Booking
from app.models.payment import Payment


@dataclass
class DashboardStats:
    """Dashboard statistics."""
    total_rooms: int
    available_rooms: int
    total_guests: int
    total_bookings: int
    active_bookings: int
    total_revenue: float
    todays_checkins: int
    todays_checkouts: int
    pending_payments: int


@dataclass
class OccupancyReport:
    """Room occupancy report."""
    total_rooms: int
    occupied_rooms: int
    available_rooms: int
    occupancy_rate: float
    room_details: List[Dict[str, Any]]


@dataclass
class RevenueReport:
    """Revenue report."""
    total_revenue: float
    revenue_by_method: Dict[str, float]
    recent_payments: List[Any]
    payment_count: int
    monthly_revenue: Dict[str, float]


@dataclass
class ServiceUsageReport:
    """Service usage report."""
    most_used_services: List[Dict[str, Any]]
    total_service_revenue: float


class ReportService:
    """Service for generating reports and statistics."""
    
    def __init__(self, db: Session):
        self.db = db
        self.room_repository = RoomRepository(db)
        self.guest_repository = GuestRepository(db)
        self.booking_repository = BookingRepository(db)
        self.payment_repository = PaymentRepository(db)
        self.booking_service_repository = BookingServiceRepository(db)
        self.service_repository = ServiceRepository(db)
    
    def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics."""
        return DashboardStats(
            total_rooms=self.room_repository.count(),
            available_rooms=len(self.room_repository.get_available_rooms()),
            total_guests=self.guest_repository.count(),
            total_bookings=self.booking_repository.count(),
            active_bookings=len(self.booking_repository.get_active_bookings()),
            total_revenue=self.payment_repository.get_total_revenue(),
            todays_checkins=len(self.booking_repository.get_todays_checkins()),
            todays_checkouts=len(self.booking_repository.get_todays_checkouts()),
            pending_payments=len(self.payment_repository.get_by_status("pending"))
        )
    
    def get_occupancy_report(self, target_date: Optional[date] = None) -> OccupancyReport:
        """Get room occupancy report for a specific date."""
        if target_date is None:
            target_date = date.today()
        
        rooms = self.room_repository.get_all()
        room_details = []
        occupied_count = 0
        
        for room in rooms:
            # Check if room has active booking for target date
            bookings = self.db.query(Booking).filter(
                Booking.room_id == room.id,
                Booking.check_in_date <= target_date,
                Booking.check_out_date > target_date,
                Booking.status.in_(["pending", "confirmed"])
            ).all()
            
            is_occupied = len(bookings) > 0
            if is_occupied:
                occupied_count += 1
            
            current_booking = bookings[0] if bookings else None
            room_details.append({
                "room": room,
                "is_occupied": is_occupied,
                "current_booking": current_booking,
                "guest": current_booking.guest if current_booking else None
            })
        
        total_rooms = len(rooms)
        occupancy_rate = (occupied_count / total_rooms * 100) if total_rooms > 0 else 0
        
        return OccupancyReport(
            total_rooms=total_rooms,
            occupied_rooms=occupied_count,
            available_rooms=total_rooms - occupied_count,
            occupancy_rate=round(occupancy_rate, 2),
            room_details=room_details
        )
    
    def get_occupancy_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Get occupancy data for a date range."""
        occupancy_data = []
        current_date = start_date
        
        while current_date <= end_date:
            report = self.get_occupancy_report(current_date)
            occupancy_data.append({
                "date": current_date,
                "occupancy_rate": report.occupancy_rate,
                "occupied_rooms": report.occupied_rooms,
                "available_rooms": report.available_rooms
            })
            current_date += timedelta(days=1)
        
        return occupancy_data
    
    def get_revenue_report(
        self, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> RevenueReport:
        """Get revenue report."""
        # Get all completed payments
        if start_date and end_date:
            payments = self.payment_repository.get_by_date_range(start_date, end_date)
            payments = [p for p in payments if p.status == "completed"]
        else:
            payments = self.payment_repository.get_by_status("completed")
        
        total_revenue = sum(p.amount for p in payments)
        
        # Revenue by method
        revenue_by_method = {}
        for payment in payments:
            method = payment.payment_method
            if method not in revenue_by_method:
                revenue_by_method[method] = 0
            revenue_by_method[method] += payment.amount
        
        # Monthly revenue
        monthly_revenue = {}
        for payment in payments:
            month_key = payment.payment_date.strftime("%Y-%m")
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = 0
            monthly_revenue[month_key] += payment.amount
        
        # Sort monthly revenue by month
        monthly_revenue = dict(sorted(monthly_revenue.items()))
        
        return RevenueReport(
            total_revenue=total_revenue,
            revenue_by_method=revenue_by_method,
            recent_payments=self.payment_repository.get_recent_payments(10),
            payment_count=len(payments),
            monthly_revenue=monthly_revenue
        )
    
    def get_service_usage_report(self) -> ServiceUsageReport:
        """Get service usage report."""
        most_used = self.booking_service_repository.get_most_used_services(10)
        
        service_details = []
        total_revenue = 0
        
        for service_id, usage_count, revenue in most_used:
            service = self.service_repository.get_by_id(service_id)
            if service:
                service_details.append({
                    "service": service,
                    "usage_count": usage_count,
                    "total_revenue": revenue or 0
                })
                total_revenue += revenue or 0
        
        return ServiceUsageReport(
            most_used_services=service_details,
            total_service_revenue=total_revenue
        )
    
    def get_booking_statistics(self) -> Dict[str, Any]:
        """Get booking statistics."""
        return {
            "total": self.booking_repository.count(),
            "pending": len(self.booking_repository.get_by_status("pending")),
            "confirmed": len(self.booking_repository.get_by_status("confirmed")),
            "cancelled": len(self.booking_repository.get_by_status("cancelled")),
            "completed": len(self.booking_repository.get_by_status("completed")),
            "upcoming": self.booking_repository.get_upcoming_bookings(10),
            "todays_checkins": self.booking_repository.get_todays_checkins(),
            "todays_checkouts": self.booking_repository.get_todays_checkouts()
        }
