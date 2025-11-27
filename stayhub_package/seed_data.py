"""
Заполнение базы данных StayHub демонстрационными данными.
Запустите скрипт, чтобы создать тестовые записи.
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
            print("База уже заполнена. Пропускаем...")
            return
        
        # Seed Rooms
        rooms = [
            Room(room_number="101", room_type="single", capacity=1, price_per_night=50.0, is_available=True, description="Уютный одноместный номер с видом на город"),
            Room(room_number="102", room_type="single", capacity=1, price_per_night=50.0, is_available=True, description="Одноместный номер с видом на сад"),
            Room(room_number="201", room_type="double", capacity=2, price_per_night=80.0, is_available=True, description="Просторный двухместный номер с балконом"),
            Room(room_number="202", room_type="double", capacity=2, price_per_night=80.0, is_available=True, description="Двухместный номер с кроватью king-size"),
            Room(room_number="301", room_type="suite", capacity=4, price_per_night=150.0, is_available=True, description="Люксовый номер с гостиной зоной"),
            Room(room_number="302", room_type="suite", capacity=4, price_per_night=150.0, is_available=True, description="Президентский люкс с панорамным видом"),
            Room(room_number="103", room_type="single", capacity=1, price_per_night=55.0, is_available=True, description="Одноместный номер с рабочим столом"),
            Room(room_number="203", room_type="double", capacity=2, price_per_night=85.0, is_available=True, description="Двухместный номер с диваном"),
            Room(room_number="104", room_type="single", capacity=1, price_per_night=58.0, is_available=True, description="Одноместный номер в стиле казахского модерна с видом на Байтерек"),
            Room(room_number="204", room_type="double", capacity=2, price_per_night=95.0, is_available=True, description="Двухместный номер с панорамой на реку Есиль и Expo"),
            Room(room_number="205", room_type="double", capacity=2, price_per_night=92.0, is_available=True, description="Степной интерьер с орнаментами из Кызылорды"),
            Room(room_number="206", room_type="double", capacity=3, price_per_night=105.0, is_available=True, description="Семейный номер с уголком казахских ремёсел"),
            Room(room_number="207", room_type="double", capacity=2, price_per_night=88.0, is_available=False, description="Номер, зарезервированный для делегации из Атырау"),
            Room(room_number="303", room_type="suite", capacity=4, price_per_night=170.0, is_available=True, description="Люкс 'Национальный колорит' с домброй и чайным столом"),
            Room(room_number="304", room_type="suite", capacity=4, price_per_night=175.0, is_available=True, description="Люкс 'Шымбулак' с мини-камином и зимним садом"),
            Room(room_number="305", room_type="suite", capacity=5, price_per_night=190.0, is_available=False, description="Люкс 'Визит Президента' с переговорной зоной"),
            Room(room_number="401", room_type="suite", capacity=4, price_per_night=210.0, is_available=True, description="Панорамный люкс с видом на Хан Шатыр"),
            Room(room_number="402", room_type="suite", capacity=4, price_per_night=220.0, is_available=True, description="Премиальный люкс с коллекцией чаёв из Жаркента"),
            Room(room_number="403", room_type="suite", capacity=6, price_per_night=250.0, is_available=False, description="Sky-люкс с приватной террасой над рекой Есиль"),
            Room(room_number="501", room_type="suite", capacity=6, price_per_night=260.0, is_available=True, description="Пентхаус 'Алтын адам' с частной сауной"),
        ]
        db.add_all(rooms)
        db.commit()
        print("Данные по номерам успешно загружены.")
        
        # Seed Guests
        guests = [
            Guest(first_name="Иван", last_name="Петров", email="ivan.petrov@example.com", phone="+74951234567", address="Москва, ул. Тверская, 12", id_document="45 01 123456"),
            Guest(first_name="Анна", last_name="Смирнова", email="anna.smirnova@example.com", phone="+78124567890", address="Санкт-Петербург, Невский проспект, 45", id_document="40 98 765432"),
            Guest(first_name="Михаил", last_name="Волков", email="m.volkov@example.com", phone="+73432894567", address="Екатеринбург, ул. Ленина, 8", id_document="82 34 567890"),
            Guest(first_name="Светлана", last_name="Кузнецова", email="svetlana.k@example.com", phone="+73832334455", address="Новосибирск, Красный проспект, 64", id_document="70 90 123456"),
            Guest(first_name="Дмитрий", last_name="Иванов", email="d.ivanov@example.com", phone="+78432567890", address="Казань, ул. Баумана, 7", id_document="12 34 567123"),
            Guest(first_name="Айгуль", last_name="Нурланова", email="a.nurlanova@stayhub.kz", phone="+77014567890", address="Алматы, проспект Абая, 15", id_document="900512401234"),
            Guest(first_name="Ернар", last_name="Садыков", email="ernar.sadykov@stayhub.kz", phone="+77017894561", address="Астана, проспект Кабанбай батыра, 12", id_document="920803500321"),
            Guest(first_name="Жанар", last_name="Абдрахманова", email="zhanar.abdrahmanova@stayhub.kz", phone="+77021234567", address="Актобе, ул. Сарыарка, 8", id_document="881224600987"),
            Guest(first_name="Бекзат", last_name="Уалиханов", email="bekzat.ualikhanov@stayhub.kz", phone="+77025551234", address="Кокшетау, проспект Назарбаева, 23", id_document="950101300456"),
            Guest(first_name="Алибек", last_name="Жаксылыков", email="alibek.zhaks@stayhub.kz", phone="+77029993456", address="Шымкент, ул. Байдибек би, 44", id_document="930709500214"),
            Guest(first_name="Сания", last_name="Рахимова", email="saniya.rahimova@stayhub.kz", phone="+77034561234", address="Павлодар, ул. Торайгырова, 19", id_document="940417600321"),
            Guest(first_name="Асель", last_name="Ермекова", email="assel.ermekova@stayhub.kz", phone="+77037894567", address="Костанай, ул. Абая, 65", id_document="970215400632"),
            Guest(first_name="Рустем", last_name="Каримов", email="rustem.karimov@stayhub.kz", phone="+77041230987", address="Атырау, ул. Сатпаева, 17", id_document="910430300145"),
            Guest(first_name="Алия", last_name="Мухамеджан", email="aliya.mukhamedzhan@stayhub.kz", phone="+77045556789", address="Талдыкорган, ул. Жетысу, 3", id_document="990911200758"),
            Guest(first_name="Тимур", last_name="Сеитов", email="timur.seitov@stayhub.kz", phone="+77048881234", address="Караганда, проспект Бухар жырау, 71", id_document="940321500987"),
        ]
        db.add_all(guests)
        db.commit()
        print("Данные по гостям успешно загружены.")
        
        # Seed Services
        services = [
            Service(name="Завтрак", description="Континентальный шведский стол", price=15.0, is_active=True),
            Service(name="Обслуживание в номере", description="Доставка блюд в номер 24/7", price=25.0, is_active=True),
            Service(name="Прачечная", description="Стирка и глажка в день обращения", price=20.0, is_active=True),
            Service(name="Трансфер в аэропорт", description="Индивидуальный трансфер на автомобиле", price=50.0, is_active=True),
            Service(name="SPA-процедура", description="Часовой расслабляющий массаж", price=80.0, is_active=True),
            Service(name="Парковка", description="Посуточная парковка", price=10.0, is_active=True),
            Service(name="Мини-бар", description="Расходы по мини-бару в номере", price=30.0, is_active=True),
            Service(name="Фитнес-зал", description="Посещение тренажёрного зала", price=5.0, is_active=True),
            Service(name="Экскурсия по Астане", description="Гид по Байтереку, Хан Шатыр и набережной Есиля", price=65.0, is_active=True),
            Service(name="Дегустация казахской кухни", description="Бешбармак, баурсаки и кумыс от шеф-повара", price=45.0, is_active=True),
            Service(name="Юрта-лаунж", description="Чайхана в юрте с килимами и домброй", price=35.0, is_active=True),
            Service(name="Чайная церемония Жаркент", description="Подбор и дегустация чаёв из Жаркента", price=18.0, is_active=True),
            Service(name="Прокат самокатов", description="Прогулка по набережной на брендовых самокатах", price=12.0, is_active=True),
            Service(name="Урок игры на домбре", description="Индивидуальное занятие с музыкантом-фольклористом", price=55.0, is_active=True),
        ]
        db.add_all(services)
        db.commit()
        print("Данные по услугам успешно загружены.")
        
        # Seed Bookings
        today = date.today()
        bookings = [
            Booking(guest_id=1, room_id=1, check_in_date=today, check_out_date=today + timedelta(days=3), status="confirmed", total_cost=150.0),
            Booking(guest_id=6, room_id=10, check_in_date=today + timedelta(days=1), check_out_date=today + timedelta(days=5), status="confirmed", total_cost=380.0),
            Booking(guest_id=7, room_id=17, check_in_date=today + timedelta(days=10), check_out_date=today + timedelta(days=15), status="pending", total_cost=1050.0),
            Booking(guest_id=8, room_id=11, check_in_date=today - timedelta(days=4), check_out_date=today - timedelta(days=1), status="completed", total_cost=276.0),
            Booking(guest_id=9, room_id=18, check_in_date=today + timedelta(days=3), check_out_date=today + timedelta(days=6), status="confirmed", total_cost=660.0),
            Booking(guest_id=10, room_id=12, check_in_date=today, check_out_date=today + timedelta(days=2), status="pending", total_cost=210.0),
            Booking(guest_id=11, room_id=14, check_in_date=today + timedelta(days=7), check_out_date=today + timedelta(days=11), status="confirmed", total_cost=680.0),
            Booking(guest_id=12, room_id=13, check_in_date=today - timedelta(days=10), check_out_date=today - timedelta(days=5), status="completed", total_cost=440.0),
            Booking(guest_id=13, room_id=15, check_in_date=today - timedelta(days=2), check_out_date=today + timedelta(days=2), status="confirmed", total_cost=700.0),
            Booking(guest_id=14, room_id=16, check_in_date=today + timedelta(days=2), check_out_date=today + timedelta(days=8), status="pending", total_cost=1140.0),
            Booking(guest_id=15, room_id=19, check_in_date=today + timedelta(days=1), check_out_date=today + timedelta(days=4), status="pending", total_cost=750.0),
            Booking(guest_id=2, room_id=4, check_in_date=today + timedelta(days=12), check_out_date=today + timedelta(days=14), status="cancelled", total_cost=160.0),
            Booking(guest_id=3, room_id=20, check_in_date=today + timedelta(days=20), check_out_date=today + timedelta(days=25), status="pending", total_cost=1300.0),
            Booking(guest_id=4, room_id=7, check_in_date=today - timedelta(days=3), check_out_date=today + timedelta(days=1), status="confirmed", total_cost=220.0),
            Booking(guest_id=5, room_id=8, check_in_date=today + timedelta(days=5), check_out_date=today + timedelta(days=7), status="pending", total_cost=170.0),
        ]
        db.add_all(bookings)
        db.commit()
        print("Данные по бронированиям успешно загружены.")
        
        # Seed Booking Services
        booking_services = [
            BookingService(booking_id=1, service_id=1, quantity=3, subtotal=45.0),
            BookingService(booking_id=1, service_id=6, quantity=3, subtotal=30.0),
            BookingService(booking_id=2, service_id=4, quantity=1, subtotal=50.0),
            BookingService(booking_id=2, service_id=10, quantity=1, subtotal=45.0),
            BookingService(booking_id=3, service_id=9, quantity=2, subtotal=130.0),
            BookingService(booking_id=3, service_id=12, quantity=3, subtotal=54.0),
            BookingService(booking_id=4, service_id=5, quantity=1, subtotal=80.0),
            BookingService(booking_id=4, service_id=3, quantity=1, subtotal=20.0),
            BookingService(booking_id=5, service_id=11, quantity=1, subtotal=35.0),
            BookingService(booking_id=5, service_id=7, quantity=2, subtotal=60.0),
            BookingService(booking_id=6, service_id=2, quantity=1, subtotal=25.0),
            BookingService(booking_id=6, service_id=8, quantity=2, subtotal=10.0),
            BookingService(booking_id=7, service_id=1, quantity=4, subtotal=60.0),
            BookingService(booking_id=7, service_id=14, quantity=1, subtotal=55.0),
            BookingService(booking_id=8, service_id=3, quantity=2, subtotal=40.0),
            BookingService(booking_id=8, service_id=12, quantity=2, subtotal=36.0),
            BookingService(booking_id=9, service_id=5, quantity=2, subtotal=160.0),
            BookingService(booking_id=9, service_id=10, quantity=1, subtotal=45.0),
            BookingService(booking_id=10, service_id=11, quantity=2, subtotal=70.0),
            BookingService(booking_id=10, service_id=9, quantity=1, subtotal=65.0),
            BookingService(booking_id=11, service_id=13, quantity=3, subtotal=36.0),
            BookingService(booking_id=11, service_id=7, quantity=1, subtotal=30.0),
            BookingService(booking_id=12, service_id=4, quantity=1, subtotal=50.0),
            BookingService(booking_id=13, service_id=5, quantity=1, subtotal=80.0),
            BookingService(booking_id=13, service_id=2, quantity=2, subtotal=50.0),
            BookingService(booking_id=14, service_id=1, quantity=4, subtotal=60.0),
            BookingService(booking_id=14, service_id=6, quantity=4, subtotal=40.0),
            BookingService(booking_id=15, service_id=9, quantity=1, subtotal=65.0),
            BookingService(booking_id=15, service_id=3, quantity=1, subtotal=20.0),
        ]
        db.add_all(booking_services)
        db.commit()
        print("Позиции услуг в бронированиях успешно загружены.")
        
        # Seed Payments
        payments = [
            Payment(booking_id=1, amount=150.0, payment_date=today, payment_method="card", status="completed"),
            Payment(booking_id=4, amount=276.0, payment_date=today - timedelta(days=3), payment_method="card", status="completed"),
            Payment(booking_id=8, amount=440.0, payment_date=today - timedelta(days=6), payment_method="cash", status="completed"),
            Payment(booking_id=9, amount=700.0, payment_date=today - timedelta(days=1), payment_method="transfer", status="completed"),
            Payment(booking_id=12, amount=160.0, payment_date=today + timedelta(days=5), payment_method="card", status="refunded"),
            Payment(booking_id=3, amount=525.0, payment_date=today + timedelta(days=2), payment_method="transfer", status="pending"),
            Payment(booking_id=5, amount=330.0, payment_date=today + timedelta(days=4), payment_method="card", status="pending"),
            Payment(booking_id=10, amount=570.0, payment_date=today + timedelta(days=1), payment_method="transfer", status="pending"),
            Payment(booking_id=11, amount=750.0, payment_date=today + timedelta(days=1), payment_method="card", status="pending"),
            Payment(booking_id=15, amount=170.0, payment_date=today + timedelta(days=2), payment_method="cash", status="pending"),
        ]
        db.add_all(payments)
        db.commit()
        print("Данные по платежам успешно загружены.")
        
        print("\n✓ Демонстрационные данные успешно загружены!")
        
    except Exception as e:
        print(f"Ошибка заполнения базы: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
