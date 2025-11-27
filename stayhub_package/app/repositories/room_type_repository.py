"""Repository для управления типами номеров."""
from typing import Optional, List
from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.room_type import RoomType


class RoomTypeRepository(BaseRepository[RoomType]):
    """Операции с типами номеров."""

    def __init__(self, db: Session):
        super().__init__(RoomType, db)

    def get_by_code(self, code: str) -> Optional[RoomType]:
        normalized = (code or "").strip().upper()
        if not normalized:
            return None
        return self.db.query(RoomType).filter(RoomType.code == normalized).first()

    def get_by_name(self, name: str) -> Optional[RoomType]:
        normalized = (name or "").strip()
        if not normalized:
            return None
        return self.db.query(RoomType).filter(func.lower(RoomType.name) == normalized.lower()).first()

    def find_by_identifier(self, identifier: str) -> Optional[RoomType]:
        normalized = (identifier or "").strip()
        if not normalized:
            return None
        upper_code = normalized.upper()
        return (
            self.db.query(RoomType)
            .filter(
                or_(
                    RoomType.code == upper_code,
                    func.lower(RoomType.name) == normalized.lower(),
                )
            )
            .first()
        )

    def list_sorted(self) -> List[RoomType]:
        return self.db.query(RoomType).order_by(RoomType.name.asc()).all()
