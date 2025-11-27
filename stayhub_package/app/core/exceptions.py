"""Пользовательские исключения приложения StayHub."""
from fastapi import HTTPException, status


class StayHubException(HTTPException):
    """Базовый класс исключений StayHub."""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(StayHubException):
    """Исключение отсутствия ресурса."""
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            detail=f"{resource} с идентификатором {resource_id} не найден",
            status_code=status.HTTP_404_NOT_FOUND
        )


class RoomNotAvailableException(StayHubException):
    """Исключение недоступности номера для бронирования."""
    def __init__(self, room_id: int, check_in: str, check_out: str):
        super().__init__(
            detail=f"Номер {room_id} недоступен с {check_in} по {check_out}",
            status_code=status.HTTP_409_CONFLICT
        )


class ValidationException(StayHubException):
    """Исключение ошибки валидации."""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class DuplicateException(StayHubException):
    """Исключение дублирования ресурса."""
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            detail=f"{resource} с полем {field} = '{value}' уже существует",
            status_code=status.HTTP_409_CONFLICT
        )
