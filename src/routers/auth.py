from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional, Dict
from ..database import get_db
from ..models.models import User, UserRole
from ..models.auth import Auth
from ..schemas.auth import Token, UserAuth, UserCreate, TokenData
from ..schemas.user import UserInDB
from ..config import get_settings

settings = get_settings()
router = APIRouter()

def verify_token(token: str, db: Session) -> TokenData:
    """Проверяет JWT токен и возвращает данные пользователя"""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        exp = payload.get("exp")
        
        if username is None or exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
            
        if datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        
        user = db.query(User).filter(
            User.username == username,
            User.is_active == True
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
            
        return TokenData(user_id=user.id, username=username)
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

# Изменяем OAuth2PasswordBearer чтобы он работал с куки
class CookieOAuth2(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        token = request.cookies.get("access_token")
        if token and token.startswith("Bearer "):
            token = token[7:]
        if not token:
            token = await super().__call__(request)
        return token

oauth2_scheme = CookieOAuth2(tokenUrl="/api/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

security = HTTPBearer()

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    try:
        # Получаем токен из заголовка
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
        else:
            # Если нет в заголовке, проверяем в cookie
            token = request.cookies.get("access_token")

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

        print(f"Using token: {token[:20]}...")

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            username = payload.get("sub")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            print(f"Decoded username: {username}")
        except JWTError as e:
            print(f"JWT decode error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        return user

    except Exception as e:
        print(f"Error in get_current_user: {str(e)}")
        raise

def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
    """Аутентификация пользователя"""
    try:
        if not username or not password:
            print("Empty username or password")
            return None
            
        print(f"\nAttempting login with username: {username}")
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print("User not found")
            return None
            
        if not user.is_active:
            print("User is inactive")
            return None
            
        is_valid = Auth.verify_password(password, user.hashed_password)
        print(f"Password verification result: {is_valid}")
        
        if not is_valid:
            print("Invalid password")
            return None
            
        return user
        
    except Exception as e:
        print(f"Error in authenticate_user: {str(e)}")
        return None

@router.post("/token")
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        print(f"\nLogin attempt for user: {form_data.username}")
        user = authenticate_user(form_data.username, form_data.password, db)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверное имя пользователя или пароль"
            )
        
        print(f"User authenticated: {user.username}, {user.role}")
        
        # Создаем токен
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(hours=24)
        )

        # Устанавливаем токен в cookie без префикса Bearer
        response.set_cookie(
            key="access_token",
            value=access_token,  # Сохраняем токен без префикса Bearer
            httponly=False,
            max_age=24 * 60 * 60,
            samesite="lax",
            secure=False,
            path="/"
        )
        
        print(f"Generated token: {access_token[:20]}...")  # Логируем для отладки
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "redirect_url": "/onboarding",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active
            }
        }
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/me", response_model=UserInDB)
async def read_users_me(request: Request, db: Session = Depends(get_db)):
    """Получить информацию о текущем пользователе"""
    try:
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        if token.startswith("Bearer "):
            token = token[7:]
            
        user = await get_current_user(request, db)
        return user
    except Exception as e:
        print(f"Error in read_users_me: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

@router.post("/logout")
async def logout(response: Response):
    """Выход из системы"""
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out"}

@router.post("/register", response_model=UserInDB)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = Auth.get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Экспортируем функцию для использования в других модулях
__all__ = ["router", "get_current_user"]