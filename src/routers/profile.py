from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import User
from ..models.auth import Auth
from ..schemas.user import UserUpdate, UserProfile, UserInDB
from .auth import get_current_user

router = APIRouter()

@router.put("/profile", response_model=UserInDB)
async def update_profile(
    profile: UserProfile,
    request: Request,
    db: Session = Depends(get_db)
):
    """Обновить профиль пользователя"""
    try:
        current_user = await get_current_user(request, db)
        
        # Обновляем только разрешенные поля
        for field, value in profile.model_dump(exclude_unset=True).items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        
        return current_user
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/profile", response_model=UserInDB)
async def get_profile(request: Request, db: Session = Depends(get_db)):
    """Получить профиль пользователя"""
    try:
        current_user = await get_current_user(request, db)
        return current_user
    except Exception as e:
        print(f"Error getting profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 