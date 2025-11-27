"""Guest repository for database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.guest import Guest


class GuestRepository(BaseRepository[Guest]):
    """Repository for Guest model operations."""
    
    def __init__(self, db: Session):
        super().__init__(Guest, db)
    
    def get_by_email(self, email: str) -> Optional[Guest]:
        """Get guest by email."""
        return self.db.query(Guest).filter(Guest.email == email).first()
    
    def get_by_id_document(self, id_document: str) -> Optional[Guest]:
        """Get guest by ID document."""
        return self.db.query(Guest).filter(Guest.id_document == id_document).first()
    
    def search_by_name(self, name: str) -> List[Guest]:
        """Search guests by name (first or last)."""
        search_term = f"%{name}%"
        return self.db.query(Guest).filter(
            (Guest.first_name.ilike(search_term)) | 
            (Guest.last_name.ilike(search_term))
        ).all()
    
    def search(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> List[Guest]:
        """Search guests with filters."""
        query = self.db.query(Guest)
        
        if name:
            search_term = f"%{name}%"
            query = query.filter(
                (Guest.first_name.ilike(search_term)) | 
                (Guest.last_name.ilike(search_term))
            )
        if email:
            query = query.filter(Guest.email.ilike(f"%{email}%"))
        if phone:
            query = query.filter(Guest.phone.ilike(f"%{phone}%"))
        
        return query.all()
