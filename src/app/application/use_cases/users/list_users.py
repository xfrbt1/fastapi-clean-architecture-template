from app.application.dto.user import UserDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.mappers.user import user_to_dto


async def list_users(uow: UnitOfWork, *, limit: int = 50, offset: int = 0) -> list[UserDTO]:
    async with uow:
        users = await uow.users.list_users(limit=limit, offset=offset)
        return [user_to_dto(u) for u in users]
