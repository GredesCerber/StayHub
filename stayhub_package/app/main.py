from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.database import engine, Base
from app.routes import rooms, guests, services, bookings, payments, booking_services, reports, room_types

# Import all models to ensure they are registered
from app.models.room import Room
from app.models.guest import Guest
from app.models.service import Service
from app.models.booking import Booking
from app.models.booking_service import BookingService
from app.models.payment import Payment
from app.models.room_type import RoomType

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StayHub",
    description="Hotel/Hostel management system for automating booking, guests, rooms, services and payments.",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(rooms.router)
app.include_router(guests.router)
app.include_router(services.router)
app.include_router(bookings.router)
app.include_router(payments.router)
app.include_router(booking_services.router)
app.include_router(reports.router)
app.include_router(room_types.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with navigation to all modules."""
    return templates.TemplateResponse("base/home.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": "StayHub"}
