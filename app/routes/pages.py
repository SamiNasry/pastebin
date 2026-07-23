from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.highlight import stylesheet
from app.services import pastes as paste_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/static/highlight.css", response_class=PlainTextResponse)
async def highlight_css() -> PlainTextResponse:
    return PlainTextResponse(
        content=stylesheet(),
        media_type="text/css",
        headers={"Cache-Control": "public, max-age=86400"},
    )

@router.get("/{paste_id}", response_class=HTMLResponse)
async def view_paste(
    paste_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    paste = await paste_service.get_paste(db, paste_id)

    if paste is None:
        raise HTTPException(status_code=404, detail="not found")

    return templates.TemplateResponse(
        request=request,
        name="paste.html",
        context={"paste": paste},
        headers={"Cache-Control" : "no-store"},
    )