from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.highlight import stylesheet
from app.services import pastes as paste_service

from app.security import verify_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/static/highlight.css", response_class=PlainTextResponse)
async def highlight_css() -> PlainTextResponse:
    return PlainTextResponse(
        content=stylesheet(),
        media_type="text/css",
        headers={"Cache-Control": "public, max-age=86400"},
    )

@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html")

@router.get("/{paste_id}", response_class=HTMLResponse)
async def view_paste(
    paste_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    paste = await paste_service.get_paste(db, paste_id)

    if paste is None:
        raise HTTPException(status_code=404, detail="not found")

    if paste.password_hash is not None:
        return templates.TemplateResponse(
            request = request,
            name="unlock.html",
            context = {"paste_id": paste_id, "error": None},
            headers={"Cache-Control": "no-store"},
        )
    return await _render_paste(request, db, paste, paste_id)    





@router.post("/{paste_id}", response_class=HTMLResponse)
async def unlock_paste(
    paste_id: str,
    request: Request,
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    paste = await paste_service.get_paste(db, paste_id)

    if paste is None or paste.password_hash is None:
        raise HTTPException(status_code=404, detail="not found")

    if not verify_password(password, paste.password_hash):
        raise HTTPException(status_code=404, detail="not found")

    return await _render_paste(request, db, paste, paste_id)

async def _render_paste(
    request: Request,
    db: AsyncSession,
    paste,
    paste_id: str,
) -> HTMLResponse:
    burned = False
    if paste.burn_after_read:
        paste = await paste_service.burn_paste(db, paste_id)
        if paste is None:
            raise HTTPException(status_code=404, detail="not found")
        burned = True

    return templates.TemplateResponse(
        request=request,
        name="paste.html",
        context={"paste": paste, "burned": burned},
        headers={"Cache-Control": "no-store"},
    )