from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class UserDTO:
    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class CreateUserDTO:
    email: str
    password: str
    full_name: str


@dataclass(frozen=True, slots=True)
class UpdateUserDTO:
    full_name: str | None = None
    is_active: bool | None = None


@dataclass(frozen=True, slots=True)
class LoginDTO:
    email: str
    password: str
