from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from src.config import get_settings
from src.database import engine, get_db
from src.models.models import Base, User, Courier  # Обновляем импорт
from src.models.auth import Auth
from src.routers import auth, onboarding, profile, warehouse
from src.routers.auth import get_current_user, oauth2_scheme
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

settings = get_settings()
app = FastAPI(title="MyCourier API")

# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Инициализируем шаблоны
templates = Jinja2Templates(directory="frontend/templates")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Импортируем и подключаем роутеры API
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["onboarding"])
app.include_router(profile.router, prefix="/api/auth", tags=["auth"])
app.include_router(warehouse.router, prefix="/api/warehouse", tags=["warehouse"])

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        )
        return response

app.add_middleware(CSPMiddleware)

async def get_user_or_redirect(request: Request, db: Session):
    try:
        # Проверяем токен в cookie
        token = request.cookies.get('access_token')
        if not token:
            # Проверяем токен в заголовке
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
            else:
                return RedirectResponse(url="/login", status_code=302)
        
        # Убираем префикс Bearer если он есть
        if token.startswith("Bearer "):
            token = token[7:]
            
        user = await get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        return user
    except Exception as e:
        print(f"Error in get_user_or_redirect: {str(e)}")
        return RedirectResponse(url="/login", status_code=302)

# Маршруты для веб-интерфейса
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    try:
        # Проверяем наличие токена в куках
        token = request.cookies.get("access_token")
        if not token:
            return RedirectResponse(url="/login")
            
        if token.startswith("Bearer "):
            token = token[7:]
            
        # Проверяем токен и получаем пользователя
        try:
            current_user = await get_current_user(request, db)
            
            # Перенаправляем на соответствующую страницу в зависимости от роли
            if current_user.role == "onboarding":
                return RedirectResponse(url="/onboarding")
            elif current_user.role == "warehouse":
                return RedirectResponse(url="/warehouse")
                
            # Если роль не определена, показываем главную страницу
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "current_user": current_user}
            )
            
        except Exception as e:
            print(f"Error verifying token: {str(e)}")
            return RedirectResponse(url="/login")
            
    except Exception as e:
        print(f"Error in home route: {str(e)}")
        return RedirectResponse(url="/login")

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "current_user": None}
    )

@app.get("/onboarding")
async def onboarding_page(request: Request, db: Session = Depends(get_db)):
    try:
        # Получаем токен из разных источников
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
        else:
            token = request.cookies.get("access_token")
            if token and token.startswith("Bearer "):
                token = token[7:]

        if not token:
            print("No token found")
            return RedirectResponse(url="/login", status_code=302)

        try:
            # Пытаемся получить пользователя
            current_user = await get_current_user(request, db)
            print(f"Current user: {current_user.username}, role: {current_user.role}")
            
            return templates.TemplateResponse(
                "onboarding.html",
                {"request": request, "current_user": current_user}
            )
        except Exception as e:
            print(f"Error getting current user: {str(e)}")
            return RedirectResponse(url="/login", status_code=302)

    except Exception as e:
        print(f"Error in onboarding page: {str(e)}")
        return RedirectResponse(url="/login", status_code=302)

@app.get("/onboarding/stats")
async def onboarding_stats_page(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = await get_user_or_redirect(request, db)
        if isinstance(current_user, RedirectResponse):
            return current_user

        if current_user.role != "onboarding":
            return RedirectResponse(url="/", status_code=302)

        return templates.TemplateResponse(
            "onboarding/stats.html", 
            {
                "request": request, 
                "current_user": current_user,
                "page_title": "Статистика"
            }
        )
    except Exception as e:
        print(f"Error in stats page: {str(e)}")
        return RedirectResponse(url="/login", status_code=302)

@app.get("/warehouse")
async def warehouse_page(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = await get_user_or_redirect(request, db)
        if isinstance(current_user, RedirectResponse):
            return current_user
        
        if current_user.role != "warehouse":
            return RedirectResponse(url="/", status_code=302)
            
        return templates.TemplateResponse(
            "warehouse.html", 
            {"request": request, "current_user": current_user}
        )
    except Exception as e:
        print(f"Error in warehouse page: {str(e)}")
        return RedirectResponse(url="/login", status_code=302)