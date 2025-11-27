"""Guest service with business logic."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.guest_repository import GuestRepository
from app.models.guest import Guest
from app.core.exceptions import NotFoundException, DuplicateException, ValidationException


class GuestService:
    """Service for guest operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.repository = GuestRepository(db)
    
    def get_guest(self, guest_id: int) -> Guest:
        """Get guest by ID with validation."""
        guest = self.repository.get_by_id(guest_id)
        if not guest:
            raise NotFoundException("Guest", guest_id)
        return guest
    
    def get_all_guests(self, skip: int = 0, limit: int = 100) -> List[Guest]:
        """Get all guests with pagination."""
        return self.repository.get_all(skip, limit)

    def list_guests(
        self,
        search: Optional[str] = None,
        sort_field: str = "name",
        sort_direction: str = "asc"
    ) -> List[Guest]:
        """Return guests with optional search and sorting."""
        return self.repository.list_with_filters(search=search, sort_field=sort_field, sort_direction=sort_direction)
    
    def search_guests(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> List[Guest]:
        """Search guests with filters."""
        return self.repository.search(name=name, email=email, phone=phone)
    
    def create_guest(self, guest_data: dict) -> Guest:
        """Create a new guest with validation."""
        # Validate email uniqueness
        email = guest_data.get("email", "")
        if email:
            existing = self.repository.get_by_email(email)
            if existing:
                raise DuplicateException("Guest", "email", email)
        
        # Validate required fields
        if not guest_data.get("first_name"):
            raise ValidationException("First name is required")
        if not guest_data.get("last_name"):
            raise ValidationException("Last name is required")
        if not email:
            raise ValidationException("Email is required")
        
        return self.repository.create(guest_data)
    
    def update_guest(self, guest_id: int, guest_data: dict) -> Guest:
        """Update guest with validation."""
        guest = self.get_guest(guest_id)
        
        # Check email uniqueness if changing
        new_email = guest_data.get("email")
        if new_email and new_email != guest.email:
            existing = self.repository.get_by_email(new_email)
            if existing:
                raise DuplicateException("Guest", "email", new_email)
        
        return self.repository.update(guest, guest_data)
    
    def delete_guest(self, guest_id: int) -> None:
        """Delete guest."""
        guest = self.get_guest(guest_id)
        self.repository.delete(guest)
    
    def count_guests(self) -> int:
        """Count total guests."""
        return self.repository.count()
