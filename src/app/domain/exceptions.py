class DomainError(Exception):
    """Base class for all domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class UserAlreadyExistsError(DomainError):
    """Raised when creating a user with an email that already exists."""

    def __init__(self, email: str) -> None:
        super().__init__(f"User with email {email!r} already exists")


class UserNotFoundError(DomainError):
    """Raised when a user cannot be found by id or email."""

    def __init__(self, *, user_id: str | None = None, email: str | None = None) -> None:
        if user_id is not None:
            super().__init__(f"User not found: id={user_id}")
        elif email is not None:
            super().__init__(f"User not found: email={email!r}")
        else:
            super().__init__("User not found")


class InvalidCredentialsError(DomainError):
    """Raised on failed login."""

    def __init__(self) -> None:
        super().__init__("Invalid email or password")
