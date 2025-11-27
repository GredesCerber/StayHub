"""Shared validation utilities for StayHub."""
import re

# Email validation pattern
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


def validate_email(email: str) -> bool:
    """Validate email format."""
    return bool(re.match(EMAIL_PATTERN, email))


# Valid values for Literal types
ROOM_TYPES = ["single", "double", "suite"]
BOOKING_STATUSES = ["pending", "confirmed", "cancelled", "completed"]
PAYMENT_STATUSES = ["pending", "completed", "refunded"]
PAYMENT_METHODS = ["cash", "card", "transfer"]
