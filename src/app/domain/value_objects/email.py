import re
from dataclasses import dataclass

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True, slots=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if not normalized or not _EMAIL_RE.match(normalized):
            msg = f"Invalid email format: {self.value!r}"
            raise ValueError(msg)
        object.__setattr__(self, "value", normalized)
