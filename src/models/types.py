from datetime import datetime
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.orm import mapped_column

timestamp = Annotated[
    datetime,
    mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP()),
]

uuidpk = Annotated[
    UUID,
    mapped_column(primary_key=True, default_factory=uuid4),
]