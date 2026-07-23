from fastapi import APIRouter, Depends, Request
from fastapi import HTTPException
from fastapi.responses import PlainTextResponse

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas import PasteCreate, PasteCreated
from app.services import pastes as paste_service

router = APIRouter(prefix="/api/pastes", tags=["pastes"])

@router.post("", response_model=PasteCreated, status_code=201)
async def create_paste(
    data: PasteCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> PasteCreated:
    paste = await paste_service.create_paste(db, data)
    base = str(request.base_url).rstrip("/")

    return PasteCreated(
        id=paste.id,
        url=f"{base}/{paste.id}",
        raw_url=f"{base}/api/pastes/{paste.id}/raw",
        delete_token=paste.delete_token,
        expires_at=paste.expires_at,
    )

@router.get("/{paste_id}/raw", response_class=PlainTextResponse)
async def read_raw(
    paste_id: str,
    db: AsyncSession = Depends(get_db),
) -> PlainTextResponse:
    paste = await paste_service.get_paste(db, paste_id)

    if paste is None:
        raise HTTPException(status_code=404, detail="not found")

    if paste.password_hash is not None:
        raise HTTPException(status_code=404, detail="not found")

    if paste.burn_after_read:
        raise HTTPException(status_code=404, detail="not found")


    return PlainTextResponse(
        content=paste.content,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )


@router.delete("/{paste_id}", status_code=204)
async def delete_paste(
    paste_id: str,
    token: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    deleted = await paste_service.delete_paste(db, paste_id, token)
    if not deleted:
        raise HTTPException(status_code = 404, detail = "not found")