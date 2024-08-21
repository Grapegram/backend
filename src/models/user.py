from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .types import timestamp, uuidpk


class User(Base):
    __tablename__ = "User"

    id: Mapped[uuidpk]
    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    joined_data: Mapped[timestamp]
    last_update_date: Mapped[timestamp]
