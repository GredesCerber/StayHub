"""
Seed data for StayHub application.
Run this script to populate the database with sample data.
"""
from datetime import date, timedelta
from app.database import SessionLocal, engine, Base
from app.models.room import Room
from app.models.guest import Guest
from app.models.service import Service
from app.models.booking import Booking
from app.models.booking_service import BookingService
from app.models.payment import Payment

# Create tables
Base.metadata.create_all(bind=engine)


def seed_database():
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Room).first():
            print("Database already seeded. Skipping...")
            return
        
        # Seed Rooms
        rooms = [
            Room(room_number="101", room_type="single", capacity=1, price_per_night=50.0, is_available=True, description="Cozy single room with city view"),
            Room(room_number="102", room_type="single", capacity=1, price_per_night=50.0, is_available=True, description="Single room with garden view"),
            Room(room_number="201", room_type="double", capacity=2, price_per_night=80.0, is_available=True, description="Spacious double room with balcony"),
            Room(room_number="202", room_type="double", capacity=2, price_per_night=80.0, is_available=True, description="Double room with king-size bed"),
            Room(room_number="301", room_type="suite", capacity=4, price_per_night=150.0, is_available=True, description="Luxury suite with living area"),
            Room(room_number="302", room_type="suite", capacity=4, price_per_night=150.0, is_available=True, description="Presidential suite with panoramic view"),
            Room(room_number="103", room_type="single", capacity=1, price_per_night=55.0, is_available=True, description="Single room with work desk"),
            Room(room_number="203", room_type="double", capacity=2, price_per_night=85.0, is_available=True, description="Double room with sofa"),
        ]
        db.add_all(rooms)
        db.commit()
        print("Rooms seeded successfully.")
        
        # Seed Guests
        guests = [
            Guest(first_name="John", last_name="Smith", email="john.smith@email.com", phone="+1234567890", address="123 Main St, New York", id_document="AB123456"),
            Guest(first_name="Emma", last_name="Johnson", email="emma.j@email.com", phone="+1987654321", address="456 Oak Ave, Los Angeles", id_document="CD789012"),
            Guest(first_name="Michael", last_name="Williams", email="m.williams@email.com", phone="+1555666777", address="789 Pine Rd, Chicago", id_document="EF345678"),
            Guest(first_name="Sarah", last_name="Brown", email="sarah.b@email.com", phone="+1444333222", address="321 Elm St, Houston", id_document="GH901234"),
            Guest(first_name="David", last_name="Davis", email="david.d@email.com", phone="+1222111000", address="654 Maple Dr, Phoenix", id_document="IJ567890"),
        ]
        db.add_all(guests)
        db.commit()
        print("Guests seeded successfully.")
        
        # Seed Services
        services = [
            Service(name="Breakfast", description="Continental breakfast buffet", price=15.0, is_active=True),
            Service(name="Room Service", description="24/7 in-room dining", price=25.0, is_active=True),
            Service(name="Laundry", description="Same-day laundry service", price=20.0, is_active=True),
            Service(name="Airport Transfer", description="Private car to/from airport", price=50.0, is_active=True),
            Service(name="Spa Treatment", description="1-hour relaxation massage", price=80.0, is_active=True),
            Service(name="Parking", description="Daily parking fee", price=10.0, is_active=True),
            Service(name="Mini Bar", description="In-room mini bar consumption", price=30.0, is_active=True),
            Service(name="Gym Access", description="Daily gym access", price=5.0, is_active=True),
        ]
        db.add_all(services)
        db.commit()
        print("Services seeded successfully.")
        
        # Seed Bookings
        today = date.today()
        bookings = [
            Booking(guest_id=1, room_id=1, check_in_date=today, check_out_date=today + timedelta(days=3), status="confirmed", total_cost=150.0),
            Booking(guest_id=2, room_id=3, check_in_date=today + timedelta(days=1), check_out_date=today + timedelta(days=5), status="pending", total_cost=320.0),
            Booking(guest_id=3, room_id=5, check_in_date=today - timedelta(days=2), check_out_date=today + timedelta(days=1), status="confirmed", total_cost=450.0),
            Booking(guest_id=4, room_id=2, check_in_date=today + timedelta(days=7), check_out_date=today + timedelta(days=10), status="pending", total_cost=150.0),
            Booking(guest_id=5, room_id=4, check_in_date=today - timedelta(days=5), check_out_date=today - timedelta(days=2), status="completed", total_cost=240.0),
        ]
        db.add_all(bookings)
        db.commit()
        print("Bookings seeded successfully.")
        
        # Seed Booking Services
        booking_services = [
            BookingService(booking_id=1, service_id=1, quantity=3, subtotal=45.0),  # 3 breakfasts
            BookingService(booking_id=1, service_id=6, quantity=3, subtotal=30.0),  # 3 days parking
            BookingService(booking_id=2, service_id=4, quantity=1, subtotal=50.0),  # Airport transfer
            BookingService(booking_id=3, service_id=5, quantity=1, subtotal=80.0),  # Spa treatment
            BookingService(booking_id=3, service_id=2, quantity=2, subtotal=50.0),  # 2x room service
            BookingService(booking_id=5, service_id=3, quantity=1, subtotal=20.0),  # Laundry
        ]
        db.add_all(booking_services)
        db.commit()
        print("Booking services seeded successfully.")
        
        # Seed Payments
        payments = [
            Payment(booking_id=1, amount=150.0, payment_date=today, payment_method="card", status="completed"),
            Payment(booking_id=3, amount=450.0, payment_date=today - timedelta(days=2), payment_method="cash", status="completed"),
            Payment(booking_id=5, amount=240.0, payment_date=today - timedelta(days=5), payment_method="transfer", status="completed"),
        ]
        db.add_all(payments)
        db.commit()
        print("Payments seeded successfully.")
        
        print("\n✓ Database seeded successfully with sample data!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
