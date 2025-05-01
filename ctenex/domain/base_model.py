from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class BaseDomainModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default=datetime.now(UTC))
    updated_at: datetime = Field(default=datetime.now(UTC))
    deleted_at: datetime | None = Field(default=None)
    is_deleted: bool = Field(default=False)
    is_active: bool = Field(default=True)
