"""Сервис управления типами номеров."""
from typing import List
from sqlalchemy.orm import Session
from app.repositories.room_repository import RoomRepository
from app.repositories.room_type_repository import RoomTypeRepository
from app.core.exceptions import DuplicateException, NotFoundException, ValidationException
from app.models.room_type import RoomType


class RoomTypeService:
    """Бизнес-логика для справочника типов номеров."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = RoomTypeRepository(db)
        self.room_repository = RoomRepository(db)

    def list_types(self) -> List[RoomType]:
        return self.repository.list_sorted()

    def get_type(self, type_id: int) -> RoomType:
        room_type = self.repository.get_by_id(type_id)
        if not room_type:
            raise NotFoundException("Тип номера", type_id)
        return room_type

    def create_type(self, data: dict) -> RoomType:
        code = data.get("code", "").strip().upper()
        if not code:
            raise ValidationException("Код типа обязателен")

        if self.repository.get_by_code(code):
            raise DuplicateException("Тип номера", "code", code)

        name = data.get("name", "").strip()
        if not name:
            raise ValidationException("Название типа обязано быть заполнено")

        if self.repository.get_by_name(name) is not None:
            raise DuplicateException("Тип номера", "name", name)

        data["code"] = code
        data["name"] = name

        if "description" in data and data.get("description") is not None:
            description = data["description"].strip()
            data["description"] = description or None

        if data.get("default_capacity") is not None and data["default_capacity"] <= 0:
            raise ValidationException("Рекомендуемая вместимость должна быть больше нуля")

        if data.get("default_price") is not None and data["default_price"] <= 0:
            raise ValidationException("Базовая цена должна быть больше нуля")
        return self.repository.create(data)

    def update_type(self, type_id: int, data: dict) -> RoomType:
        room_type = self.get_type(type_id)
        if "code" in data:
            raise ValidationException("Код типа нельзя менять после создания")

        if "name" in data and data.get("name"):
            name = data["name"].strip()
            existing = self.repository.get_by_name(name)
            if existing and existing.id != type_id:
                raise DuplicateException("Тип номера", "name", name)
            data["name"] = name

        if "description" in data and data.get("description") is not None:
            description = data["description"].strip()
            data["description"] = description or None

        if data.get("default_capacity") is not None and data["default_capacity"] <= 0:
            raise ValidationException("Рекомендуемая вместимость должна быть больше нуля")

        if data.get("default_price") is not None and data["default_price"] <= 0:
            raise ValidationException("Базовая цена должна быть больше нуля")
        return self.repository.update(room_type, data)

    def delete_type(self, type_id: int) -> None:
        room_type = self.get_type(type_id)
        if self.room_repository.get_by_type(room_type.name):
            raise ValidationException("Нельзя удалить тип, пока есть номера этого типа")
        self.repository.delete(room_type)
