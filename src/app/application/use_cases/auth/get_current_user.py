from uuid import UUID

from app.application.dto.user import UserDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.mappers.user import user_to_dto
from app.domain.exceptions import UserNotFoundError


async def get_user_profile(uow: UnitOfWork, user_id: UUID) -> UserDTO:
    async with uow:
        user = await uow.users.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id=str(user_id))
        return user_to_dto(user)
