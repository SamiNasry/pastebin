import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import delete

from app.db import SessionLocal
from app.models import Paste

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("cleanup")

INTERVAL_SECONDS = 60

async def delete_expired() -> int:
    async with SessionLocal() as db:
        stmt = delete(Paste).where(
            Paste.expires_at.is_not(None),
            Paste.expires_at <= datetime.now(UTC),
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount


async def main() -> None:
    logger.info("cleanup worker started, interval=%ss", INTERVAL_SECONDS)
    while True:
        try:
            count = await delete_expired()
            if count:
                logger.info("deleted %s expired pastes", count)
        except Exception:
            logger.exception("cleanup failed")
        await asyncio.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())