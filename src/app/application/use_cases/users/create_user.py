from app.application.dto.user import CreateUserDTO, UserDTO
from app.application.interfaces.unit_of_work import UnitOfWork
from app.application.use_cases.auth.register_user import register_user


async def create_user(uow: UnitOfWork, dto: CreateUserDTO) -> UserDTO:
    return await register_user(uow, dto)
