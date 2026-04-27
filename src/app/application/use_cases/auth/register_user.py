from datetime import UTC, datetime
from uuid import uuid4

from app.application.dto.user import CreateUserDTO, UserDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.mappers.user import user_to_dto
from app.core.security import hash_password
from app.domain.entities.user import User
from app.domain.exceptions import UserAlreadyExistsError
from app.domain.value_objects.email import Email


async def register_user(uow: UnitOfWork, dto: CreateUserDTO) -> UserDTO:
    email = Email(dto.email)
    async with uow:
        existing = await uow.users.get_by_email(email)
        if existing is not None:
            raise UserAlreadyExistsError(email.value)
        now = datetime.now(UTC)
        user = User(
            id=uuid4(),
            email=email,
            hashed_password=hash_password(dto.password),
            full_name=dto.full_name.strip(),
            created_at=now,
            updated_at=now,
            is_active=True,
        )
        await uow.users.add(user)
        await uow.commit()
        return user_to_dto(user)
