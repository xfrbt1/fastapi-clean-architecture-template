from app.application.dto.user import LoginDTO, UserDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.mappers.user import user_to_dto
from app.core.security import verify_password
from app.domain.exceptions import InvalidCredentialsError
from app.domain.value_objects.email import Email


async def login_user(uow: UnitOfWork, dto: LoginDTO) -> UserDTO:
    email = Email(dto.email)
    async with uow:
        user = await uow.users.get_by_email(email)
        if user is None or not verify_password(dto.password, user.hashed_password):
            raise InvalidCredentialsError()
        return user_to_dto(user)
