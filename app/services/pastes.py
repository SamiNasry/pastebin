from datetime import UTC, datetime, timedelta


from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.ids import generate_delete_token, generate_id
from app.models import Paste
from app.schemas import PasteCreate
from app.highlight import render
from app.security import hash_password



MAX_ID_ATTEMPTS = 5

async def create_paste(db: AsyncSession, data : PasteCreate) -> Paste:
    expires_at = None
    if data.expires_in_minutes is not None:
        expires_at = datetime.now(UTC) + timedelta(minutes=data.expires_in_minutes)

    delete_token = generate_delete_token()
    rendered_html, resolved_language = render(data.content, data.language)
    for _ in range(MAX_ID_ATTEMPTS):
        paste = Paste(
            id=generate_id(),
            content=data.content,
            language=resolved_language,
            expires_at=expires_at,
            rendered_html=rendered_html,
            burn_after_read=data.burn_after_read,
            delete_token=delete_token,
            password_hash = hash_password(data.password) if data.password else None,
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


async def burn_paste(db: AsyncSession, paste_id:str) -> Paste | None:
    stmt = (
        delete(Paste)
        .where(Paste.id == paste_id)
        .where(Paste.burn_after_read.is_(True))
        .returning(Paste)
    )
    result = await db.execute(stmt)
    paste = result.scalar_one_or_none()
    await db.commit()

    if paste is None:
        return None

    if paste.expires_at is not None and paste.expires_at <= datetime.now(UTC):
        return None


    return paste



async def delete_paste(db: AsyncSession, paste_id: str, token: str) -> bool:
    stmt = (
        delete(Paste)
        .where(Paste.id == paste_id)
        .where(Paste.delete_token == token)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


