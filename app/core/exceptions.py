"""Custom exceptions for StayHub application."""
from fastapi import HTTPException, status


class StayHubException(HTTPException):
    """Base exception for StayHub application."""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(StayHubException):
    """Resource not found exception."""
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            detail=f"{resource} with id {resource_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class RoomNotAvailableException(StayHubException):
    """Room not available for booking exception."""
    def __init__(self, room_id: int, check_in: str, check_out: str):
        super().__init__(
            detail=f"Room {room_id} is not available from {check_in} to {check_out}",
            status_code=status.HTTP_409_CONFLICT
        )


class ValidationException(StayHubException):
    """Validation error exception."""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class DuplicateException(StayHubException):
    """Duplicate resource exception."""
    def __init__(self, resource: str, field: str, value: str):
        super().__init__(
            detail=f"{resource} with {field} '{value}' already exists",
            status_code=status.HTTP_409_CONFLICT
        )
