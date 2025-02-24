from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .auth import get_current_user
from ..models.models import UserRole

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница - редирект на логин или панель в зависимости от авторизации"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница логина"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/onboarding", response_class=HTMLResponse)
async def onboarding_page(request: Request):
    """Страница онбординга"""
    try:
        user = await get_current_user(request)
        if user.role != UserRole.ONBOARDING:
            return templates.TemplateResponse("login.html", {"request": request})
        return templates.TemplateResponse("onboarding.html", {"request": request})
    except:
        return templates.TemplateResponse("login.html", {"request": request})

@router.get("/onboarding/stats", response_class=HTMLResponse)
async def onboarding_stats_page(request: Request):
    """Страница статистики онбординга"""
    try:
        user = await get_current_user(request)
        if user.role != UserRole.ONBOARDING:
            return templates.TemplateResponse("login.html", {"request": request})
        return templates.TemplateResponse("onboarding_stats.html", {"request": request})
    except:
        return templates.TemplateResponse("login.html", {"request": request}) 