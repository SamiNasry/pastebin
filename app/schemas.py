from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.config import settings


class PasteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=settings.max_paste_bytes)
    language: str = Field(default="text", max_length=32)
    expires_in_minutes: int | None = Field(default=None, ge=1, le=60 * 24 * 365)
    burn_after_read: bool = False
    password: str | None = Field(default=None, min_length=1, max_length=128)

class PasteCreated(BaseModel):
    id: str
    url: str
    raw_url: str
    delete_token: str
    expires_at: datetime | None


class PasteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    content: str
    language: str
    created_at: datetime
    expires_at: datetime | None
    views: int