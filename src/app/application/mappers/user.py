from app.application.dto.user import UserDTO
from app.domain.entities.user import User


def user_to_dto(entity: User) -> UserDTO:
    """Map domain User to read DTO."""
    return UserDTO(
        id=entity.id,
        email=entity.email.value,
        full_name=entity.full_name,
        is_active=entity.is_active,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
