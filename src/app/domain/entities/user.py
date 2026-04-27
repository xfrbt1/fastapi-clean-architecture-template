from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects.email import Email


@dataclass(slots=True)
class User:
    """Application user."""

    id: UUID
    email: Email
    hashed_password: str
    full_name: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    def rename(self, new_name: str) -> None:
        name = new_name.strip()
        if not name:
            msg = "Full name must not be empty"
            raise ValueError(msg)
        self.full_name = name
