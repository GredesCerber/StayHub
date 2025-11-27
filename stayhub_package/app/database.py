from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./stayhub.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def _ensure_rooms_status_column() -> None:
    """Add the status column to rooms table when upgrading existing БД."""
    with engine.begin() as connection:
        table_exists = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='rooms'")
        ).scalar()
        if not table_exists:
            return

        columns = {
            row[1] for row in connection.execute(text("PRAGMA table_info(rooms)"))
        }
        if "status" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE rooms ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'available'"
                )
            )


_ensure_rooms_status_column()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
