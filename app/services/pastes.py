from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.ids import generate_delete_token, generate_id
from app.models import Paste
from app.schemas import PasteCreate


MAX_ID_ATTEMPTS = 5

async def create_paste(db: AsyncSession, data : PasteCreate) -> Paste:
    expires_at = None
    if data.expires_in_minutes is not None:
        expires_at = datetime.now(UTC) + timedelta(minutes=data.expires_in_minutes)

    delete_token = generate_delete_token()
    for _ in range(MAX_ID_ATTEMPTS):
        paste = Paste(
            id=generate_id(),
            content=data.content,
            language=data.language,
            expires_at=expires_at,
            burn_after_read=data.burn_after_read,
            delete_token=delete_token,
        )
        db.add(paste)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            continue
        await db.refresh(paste)
        return paste

    raise RuntimeError("could not generate a unique paste id")

async def get_paste(db: AsyncSession, paste_id: str) -> Paste | None:
    result = await db.execute(select(Paste).where(Paste.id == paste_id))
    paste = result.scalar_one_or_none()

    if paste is None:
        return None

    if paste.expires_at is not None and paste.expires_at <= datetime.now(UTC):
        return None

    return paste