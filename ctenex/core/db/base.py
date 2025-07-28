import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TIMESTAMP, UUID, Boolean, DateTime


class Base(DeclarativeBase):
    pass


class AbstractBase(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        # type_=TIMESTAMP(timezone=True),
        type_=DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime] = mapped_column(
        type_=TIMESTAMP(timezone=True),
        nullable=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        type_=Boolean,
        default=False,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        type_=Boolean,
        default=True,
        nullable=False,
    )
