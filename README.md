# StayHub

Hotel/Hostel management system for automating booking, guests, rooms, services and payments. Built with FastAPI, SQLAlchemy, SQLite and Bootstrap. Educational project for database automation.

## Features

- **Rooms Management**: Create, update, delete rooms with pricing and availability tracking
- **Guests Management**: Register and manage guest information
- **Bookings**: Create reservations with room availability checking and automatic cost calculation
- **Services**: Configure additional hotel services (breakfast, laundry, spa, etc.)
- **Booking Services**: Add services to bookings with quantity tracking
- **Payments**: Record and track payments with multiple payment methods
- **Reports**: Dashboard with occupancy rates, revenue reports, and booking statistics

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: Jinja2 templates with Bootstrap 5
- **Icons**: Bootstrap Icons

## Project Structure

```
StayHub/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Database configuration
│   ├── models/              # SQLAlchemy models
│   │   ├── room.py
│   │   ├── guest.py
│   │   ├── service.py
│   │   ├── booking.py
│   │   ├── booking_service.py
│   │   └── payment.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── room.py
│   │   ├── guest.py
│   │   ├── service.py
│   │   ├── booking.py
│   │   ├── booking_service.py
│   │   └── payment.py
│   ├── routes/              # API and web routes
│   │   ├── rooms.py
│   │   ├── guests.py
│   │   ├── services.py
│   │   ├── bookings.py
│   │   ├── booking_services.py
│   │   ├── payments.py
│   │   └── reports.py
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base/
│   │   ├── rooms/
│   │   ├── guests/
│   │   ├── bookings/
│   │   ├── services/
│   │   ├── payments/
│   │   └── reports/
│   └── static/              # Static files (CSS)
├── seed_data.py             # Database seed script
├── requirements.txt         # Python dependencies
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/GredesCerber/StayHub.git
cd StayHub
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Seed the database with sample data (optional):
```bash
python seed_data.py
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

6. Open your browser and navigate to:
   - Web UI: http://localhost:8000
   - API docs: http://localhost:8000/docs

## API Endpoints

### Rooms
- `GET /rooms/api` - List all rooms
- `GET /rooms/api/{room_id}` - Get room by ID
- `POST /rooms/api` - Create new room
- `PUT /rooms/api/{room_id}` - Update room
- `DELETE /rooms/api/{room_id}` - Delete room

### Guests
- `GET /guests/api` - List all guests
- `GET /guests/api/{guest_id}` - Get guest by ID
- `POST /guests/api` - Create new guest
- `PUT /guests/api/{guest_id}` - Update guest
- `DELETE /guests/api/{guest_id}` - Delete guest

### Bookings
- `GET /bookings/api` - List all bookings
- `GET /bookings/api/{booking_id}` - Get booking by ID
- `GET /bookings/api/availability` - Check room availability
- `GET /bookings/api/{booking_id}/cost` - Calculate booking cost
- `POST /bookings/api` - Create new booking
- `PUT /bookings/api/{booking_id}` - Update booking
- `DELETE /bookings/api/{booking_id}` - Delete booking

### Services
- `GET /services/api` - List all services
- `GET /services/api/{service_id}` - Get service by ID
- `POST /services/api` - Create new service
- `PUT /services/api/{service_id}` - Update service
- `DELETE /services/api/{service_id}` - Delete service

### Payments
- `GET /payments/api` - List all payments
- `GET /payments/api/{payment_id}` - Get payment by ID
- `POST /payments/api` - Create new payment
- `PUT /payments/api/{payment_id}` - Update payment
- `DELETE /payments/api/{payment_id}` - Delete payment

### Reports
- `GET /reports/api/summary` - Get summary statistics
- `GET /reports/api/occupancy` - Get occupancy report

## Database Models

### Room
- `id`: Primary key
- `room_number`: Unique room identifier
- `room_type`: Type of room (single, double, suite)
- `capacity`: Maximum number of guests
- `price_per_night`: Nightly rate
- `is_available`: Availability status
- `description`: Room description

### Guest
- `id`: Primary key
- `first_name`: Guest's first name
- `last_name`: Guest's last name
- `email`: Email address (unique)
- `phone`: Phone number
- `address`: Address
- `id_document`: ID document number

### Booking
- `id`: Primary key
- `guest_id`: Foreign key to Guest
- `room_id`: Foreign key to Room
- `check_in_date`: Check-in date
- `check_out_date`: Check-out date
- `total_cost`: Calculated total cost
- `status`: Booking status (pending, confirmed, cancelled, completed)

### Service
- `id`: Primary key
- `name`: Service name
- `description`: Service description
- `price`: Service price
- `is_active`: Active status

### BookingService
- `id`: Primary key
- `booking_id`: Foreign key to Booking
- `service_id`: Foreign key to Service
- `quantity`: Quantity ordered
- `subtotal`: Calculated subtotal

### Payment
- `id`: Primary key
- `booking_id`: Foreign key to Booking
- `amount`: Payment amount
- `payment_date`: Date of payment
- `payment_method`: Payment method (cash, card, transfer)
- `status`: Payment status (pending, completed, refunded)

## License

This project is for educational purposes.
