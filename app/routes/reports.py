from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional

from app.core.dependencies import get_db
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])
templates = Jinja2Templates(directory="app/templates")


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    """Dependency for ReportService."""
    return ReportService(db)


@router.get("/", response_class=HTMLResponse)
def reports_dashboard(
    request: Request, 
    service: ReportService = Depends(get_report_service)
):
    """Main reports dashboard."""
    stats = service.get_dashboard_stats()
    
    return templates.TemplateResponse("reports/dashboard.html", {
        "request": request,
        "total_rooms": stats.total_rooms,
        "available_rooms": stats.available_rooms,
        "total_guests": stats.total_guests,
        "total_bookings": stats.total_bookings,
        "active_bookings": stats.active_bookings,
        "total_revenue": stats.total_revenue,
        "todays_checkins": stats.todays_checkins,
        "todays_checkouts": stats.todays_checkouts,
        "pending_payments": stats.pending_payments
    })


@router.get("/occupancy", response_class=HTMLResponse)
def occupancy_report(
    request: Request,
    target_date: Optional[date] = None,
    service: ReportService = Depends(get_report_service)
):
    """Room occupancy report."""
    report = service.get_occupancy_report(target_date)
    
    return templates.TemplateResponse("reports/occupancy.html", {
        "request": request,
        "room_status": report.room_details,
        "occupancy_rate": report.occupancy_rate,
        "occupied_count": report.occupied_rooms,
        "total_rooms": report.total_rooms,
        "target_date": target_date or date.today()
    })


@router.get("/revenue", response_class=HTMLResponse)
def revenue_report(
    request: Request,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    service: ReportService = Depends(get_report_service)
):
    """Revenue report."""
    report = service.get_revenue_report(start_date, end_date)
    
    return templates.TemplateResponse("reports/revenue.html", {
        "request": request,
        "total_revenue": report.total_revenue,
        "revenue_by_method": report.revenue_by_method,
        "recent_payments": report.recent_payments,
        "payment_count": report.payment_count,
        "monthly_revenue": report.monthly_revenue,
        "start_date": start_date,
        "end_date": end_date
    })


@router.get("/bookings", response_class=HTMLResponse)
def bookings_report(
    request: Request,
    service: ReportService = Depends(get_report_service)
):
    """Bookings report."""
    stats = service.get_booking_statistics()
    
    return templates.TemplateResponse("reports/bookings.html", {
        "request": request,
        "pending": stats["pending"],
        "confirmed": stats["confirmed"],
        "cancelled": stats["cancelled"],
        "completed": stats["completed"],
        "upcoming_bookings": stats["upcoming"],
        "total_bookings": stats["total"],
        "todays_checkins": stats["todays_checkins"],
        "todays_checkouts": stats["todays_checkouts"]
    })


@router.get("/services", response_class=HTMLResponse)
def services_report(
    request: Request,
    service: ReportService = Depends(get_report_service)
):
    """Service usage report."""
    report = service.get_service_usage_report()
    
    return templates.TemplateResponse("reports/services.html", {
        "request": request,
        "most_used_services": report.most_used_services,
        "total_service_revenue": report.total_service_revenue
    })


# API endpoints for reports
@router.get("/api/summary")
def get_summary_report(service: ReportService = Depends(get_report_service)):
    """Get summary report data as JSON."""
    stats = service.get_dashboard_stats()
    return {
        "total_rooms": stats.total_rooms,
        "available_rooms": stats.available_rooms,
        "total_guests": stats.total_guests,
        "total_bookings": stats.total_bookings,
        "active_bookings": stats.active_bookings,
        "total_revenue": stats.total_revenue,
        "todays_checkins": stats.todays_checkins,
        "todays_checkouts": stats.todays_checkouts,
        "pending_payments": stats.pending_payments
    }


@router.get("/api/occupancy")
def get_occupancy_report(
    target_date: Optional[date] = None,
    service: ReportService = Depends(get_report_service)
):
    """Get occupancy report data as JSON."""
    report = service.get_occupancy_report(target_date)
    return {
        "total_rooms": report.total_rooms,
        "occupied_rooms": report.occupied_rooms,
        "available_rooms": report.available_rooms,
        "occupancy_rate": report.occupancy_rate
    }


@router.get("/api/occupancy/range")
def get_occupancy_range(
    start_date: date,
    end_date: date,
    service: ReportService = Depends(get_report_service)
):
    """Get occupancy data for a date range."""
    return service.get_occupancy_by_date_range(start_date, end_date)


@router.get("/api/revenue")
def get_revenue_report(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    service: ReportService = Depends(get_report_service)
):
    """Get revenue report data as JSON."""
    report = service.get_revenue_report(start_date, end_date)
    return {
        "total_revenue": report.total_revenue,
        "revenue_by_method": report.revenue_by_method,
        "payment_count": report.payment_count,
        "monthly_revenue": report.monthly_revenue
    }


@router.get("/api/services")
def get_service_usage(service: ReportService = Depends(get_report_service)):
    """Get service usage data as JSON."""
    report = service.get_service_usage_report()
    return {
        "most_used_services": [
            {
                "name": s["service"].name,
                "usage_count": s["usage_count"],
                "total_revenue": s["total_revenue"]
            }
            for s in report.most_used_services
        ],
        "total_service_revenue": report.total_service_revenue
    }


@router.get("/api/bookings")
def get_booking_stats(service: ReportService = Depends(get_report_service)):
    """Get booking statistics as JSON."""
    stats = service.get_booking_statistics()
    return {
        "total": stats["total"],
        "pending": stats["pending"],
        "confirmed": stats["confirmed"],
        "cancelled": stats["cancelled"],
        "completed": stats["completed"]
    }
