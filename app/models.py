from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Paste(Base):
    __tablename__ = "pastes"

    id: Mapped[str] = mapped_column(String(8), primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    rendered_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(32), nullable=False, default="text")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    burn_after_read: Mapped[bool] = mapped_column(nullable=False, default=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    delete_token: Mapped[str] = mapped_column(String(64), nullable=False)
    views: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    __table_args__ = (Index("ix_pastes_expires_at", "expires_at"),)