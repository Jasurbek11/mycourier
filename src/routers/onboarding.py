from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
import logging
from starlette import status
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy import or_
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm

from ..database import get_db
from ..models.models import (
    User, 
    UserRole, 
    Courier, 
    CourierStatus, 
    CourierHistory,
    DocumentStatus,
    OnboardingStatus,
    VehicleDocsStatus,
    TransportType
)
from ..schemas.courier import CourierCreate, CourierUpdate
from .auth import get_current_user
from ..services import courier_service
from ..services.statistics import get_onboarding_metrics, get_onboarding_chart_data, get_employees_statistics
from ..schemas.statistics import StatisticsResponse, StatisticsMetrics, ChartData, EmployeeStatistics
from ..config import settings

# Настройка логгера
logger = logging.getLogger(__name__)

# Инициализация роутера
router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/stats/data")
async def get_stats_data(
    request: Request,
    filter_type: str = "personal",
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Получение данных для статистики"""
    try:
        current_user = await get_current_user(request, db)
        
        # Базовый фильтр по лог-партнеру
        base_filter = (Courier.log_partner == current_user.log_partner)
        
        if filter_type == "personal":
            # Статистика текущего пользователя
            base_filter &= (Courier.created_by_id == current_user.id)
        elif filter_type == "employee" and employee_id:
            # Статистика конкретного сотрудника
            base_filter &= (Courier.created_by_id == employee_id)
        # Для department используем только фильтр по лог-партнеру
        
        stats = {
            "total_couriers": db.query(Courier).filter(base_filter).count(),
            "active_couriers": db.query(Courier).filter(
                base_filter,
                Courier.status == CourierStatus.ACTIVE
            ).count(),
            "inactive_couriers": db.query(Courier).filter(
                base_filter,
                Courier.status == CourierStatus.INACTIVE
            ).count(),
            "blocked_couriers": db.query(Courier).filter(
                base_filter,
                Courier.status == CourierStatus.BLOCKED
            ).count()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/employees")
async def get_employees(request: Request, db: Session = Depends(get_db)):
    """Получение списка сотрудников отдела"""
    try:
        current_user = await get_current_user(request, db)
        logger.info(f"Getting employees for user {current_user.username}")
        
        # Получаем всех активных сотрудников онбординга из того же лог-партнера
        employees = db.query(User).filter(
            User.log_partner == current_user.log_partner,
            User.role == UserRole.ONBOARDING,
            User.is_active == True,
            User.id != current_user.id  # Исключаем текущего пользователя
        ).all()
        
        result = [
            {
                "id": emp.id,
                "username": emp.username,
                "email": emp.email
            }
            for emp in employees
        ]
        
        logger.info(f"Found {len(result)} employees")
        return result
        
    except Exception as e:
        logger.error(f"Error getting employees: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/test")
async def test_route():
    """Тестовый маршрут для проверки работы роутера"""
    return {"message": "Onboarding router is working"}

@router.get("/couriers")
async def get_couriers(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db)
):
    try:
        print("Getting couriers, checking auth...")
        
        # Используем get_current_user вместо повторной проверки токена
        current_user = await get_current_user(request, db)
        print(f"User authenticated: {current_user.username}")

        limit = 10
        offset = (page - 1) * limit
        
        # Фильтруем курьеров по log_partner текущего пользователя
        couriers = db.query(Courier).filter(
            Courier.log_partner == current_user.log_partner
        ).offset(offset).limit(limit).all()
        
        total = db.query(Courier).filter(
            Courier.log_partner == current_user.log_partner
        ).count()
        
        courier_list = []
        for courier in couriers:
            courier_dict = {
                "id": courier.id,
                "full_name": courier.full_name,
                "phone": courier.phone,
                "status": courier.status.value if courier.status else None,
                "onboarding_status": courier.onboarding_status.value if courier.onboarding_status else None,
                "created_at": courier.created_at.isoformat() if courier.created_at else None
            }
            courier_list.append(courier_dict)
        
        return {
            "items": courier_list,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        print(f"Error in get_couriers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/couriers")
async def create_courier(
    request: Request,
    courier: CourierCreate,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user(request, db)
        
        # Проверяем существование курьера
        existing_courier = db.query(Courier).filter(
            or_(
                Courier.phone == courier.phone,
                Courier.pinfl == courier.pinfl
            )
        ).first()
        
        if existing_courier:
            if existing_courier.phone == courier.phone:
                raise HTTPException(
                    status_code=400,
                    detail="Курьер с таким номером телефона уже существует"
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Курьер с таким ПИНФЛ уже существует"
                )

        # Создаем нового курьера
        new_courier = Courier(
            full_name=courier.full_name,
            phone=courier.phone,
            pinfl=courier.pinfl,
            transport_type=courier.transport_type,
            vehicle_number=courier.vehicle_number,
            vehicle_model=courier.vehicle_model,
            status=CourierStatus.INACTIVE,
            onboarding_status=OnboardingStatus.WILL_BE_VERIFIED,
            documents_status=DocumentStatus.NOT_VERIFIED,
            created_by_id=current_user.id,
            log_partner=current_user.log_partner,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_courier)
        db.flush()  # Получаем ID без коммита
        
        # Добавляем запись в историю
        history = CourierHistory(
            courier_id=new_courier.id,
            type="onboarding",
            event="Создан новый курьер",
            status=OnboardingStatus.WILL_BE_VERIFIED,
            created_by_id=current_user.id
        )
        db.add(history)
        
        try:
            db.commit()  # Коммитим все изменения разом
            db.refresh(new_courier)
            
            # Возвращаем данные в формате, который ожидает фронтенд
            return {
                "id": new_courier.id,
                "full_name": new_courier.full_name,
                "phone": new_courier.phone,
                "pinfl": new_courier.pinfl,
                "status": new_courier.status.value,
                "onboarding_status": new_courier.onboarding_status.value,
                "transport_type": new_courier.transport_type.value,
                "vehicle_number": new_courier.vehicle_number,
                "vehicle_model": new_courier.vehicle_model,
                "created_at": new_courier.created_at.isoformat() if new_courier.created_at else None,
                "updated_at": new_courier.updated_at.isoformat() if new_courier.updated_at else None
            }

        except IntegrityError as e:
            db.rollback()
            logger.error(f"IntegrityError while creating courier: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Курьер с такими данными уже существует"
            )

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error creating courier: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании курьера"
        )

@router.get("/couriers/{courier_id}")
async def get_courier(
    courier_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user(request, db)
        
        courier = db.query(Courier).filter(
            Courier.id == courier_id,
            Courier.log_partner == current_user.log_partner
        ).first()
        
        if not courier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Курьер не найден"
            )
            
        return {
            "id": courier.id,
            "full_name": courier.full_name,
            "phone": courier.phone,
            "pinfl": courier.pinfl,
            "status": courier.status.value,
            "onboarding_status": courier.onboarding_status.value,
            "documents_status": courier.documents_status.value,
            "transport_type": courier.transport_type.value,
            "vehicle_number": courier.vehicle_number,
            "vehicle_model": courier.vehicle_model,
            "vehicle_docs_status": courier.vehicle_docs_status.value if courier.vehicle_docs_status else None,
            "created_at": courier.created_at.isoformat() if courier.created_at else None,
            "updated_at": courier.updated_at.isoformat() if courier.updated_at else None,
            "verified_at": courier.verified_at.isoformat() if courier.verified_at else None,
            "verified_by": courier.verified_by.username if courier.verified_by else None,
            "log_partner": courier.log_partner
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting courier {courier_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении данных курьера: {str(e)}"
        )

@router.put("/couriers/{courier_id}")
async def update_courier(
    courier_id: int,
    courier_update: CourierUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user(request, db)
        
        # Проверяем роль пользователя
        if current_user.role != UserRole.ONBOARDING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только сотрудники онбординга могут изменять данные курьера"
            )
        
        # Получаем курьера
        courier = db.query(Courier).filter(
            Courier.id == courier_id,
            Courier.log_partner == current_user.log_partner
        ).first()
        
        if not courier:
            raise HTTPException(status_code=404, detail="Курьер не найден")

        # Обновляем основные данные курьера
        for field, value in courier_update.dict(exclude_unset=True).items():
            if field == 'transport_type' and value:
                try:
                    courier.transport_type = TransportType[value.upper()]
                except KeyError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Неверное значение типа транспорта: {value}"
                    )
            elif field not in ['onboarding_status', 'id']:
                setattr(courier, field, value)

        # Обрабатываем изменение статуса
        if courier_update.onboarding_status:
            try:
                current_status = courier.onboarding_status
                new_status_str = courier_update.onboarding_status.upper()
                
                try:
                    new_status = OnboardingStatus[new_status_str]
                except KeyError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Неверное значение статуса: {courier_update.onboarding_status}"
                    )

                # Принудительно устанавливаем новый статус
                courier.onboarding_status = new_status
                
                # Обновляем связанные поля в зависимости от нового статуса
                if new_status == OnboardingStatus.VERIFIED:
                    courier.verified_by_id = current_user.id
                    courier.verified_at = datetime.utcnow()
                    courier.documents_status = DocumentStatus.VERIFIED
                    if courier.transport_type not in [TransportType.PEDESTRIAN, TransportType.BICYCLE]:
                        courier.vehicle_docs_status = VehicleDocsStatus.VERIFIED
                else:
                    courier.verified_by_id = None
                    courier.verified_at = None
                    courier.documents_status = DocumentStatus.NOT_VERIFIED
                    if courier.transport_type not in [TransportType.PEDESTRIAN, TransportType.BICYCLE]:
                        courier.vehicle_docs_status = VehicleDocsStatus.NOT_VERIFIED

                # Добавляем запись в историю
                history = CourierHistory(
                    courier_id=courier.id,
                    event=f"Статус изменен с '{current_status.value}' на '{new_status.value}'",
                    type="onboarding",
                    status=new_status.value,
                    created_by_id=current_user.id
                )
                db.add(history)

            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )

        courier.updated_at = datetime.utcnow()
        courier.updated_by_id = current_user.id
        
        try:
            db.commit()
            db.refresh(courier)
        except Exception as e:
            db.rollback()
            logger.error(f"Database error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при сохранении изменений"
            )
        
        return {
            "id": courier.id,
            "full_name": courier.full_name,
            "phone": courier.phone,
            "pinfl": courier.pinfl,
            "status": courier.status.value,
            "onboarding_status": courier.onboarding_status.value,
            "transport_type": courier.transport_type.value,
            "vehicle_number": courier.vehicle_number,
            "vehicle_model": courier.vehicle_model,
            "vehicle_docs_status": courier.vehicle_docs_status.value if courier.vehicle_docs_status else None,
            "updated_at": courier.updated_at.isoformat() if courier.updated_at else None
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating courier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/couriers/list")
async def get_couriers_page(request: Request, db: Session = Depends(get_db)):
    """Страница со списком курьеров"""
    try:
        current_user = await get_current_user(request, db)
        return templates.TemplateResponse(
            "onboarding/couriers.html",
            {"request": request, "current_user": current_user}
        )
    except Exception as e:
        return RedirectResponse(url="/login", status_code=302)

@router.get("/")
async def get_onboarding_page(request: Request, db: Session = Depends(get_db)):
    """Главная страница онбординга"""
    try:
        current_user = await get_current_user(request, db)
        return templates.TemplateResponse(
            "onboarding.html",
            {"request": request, "current_user": current_user}
        )
    except Exception as e:
        return RedirectResponse(url="/login", status_code=302)

@router.post("/couriers/{courier_id}/verify")
async def verify_courier(
    courier_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Подтверждение онбординга курьера"""
    try:
        current_user = await get_current_user(request, db)
        
        courier = db.query(Courier).filter(
            Courier.id == courier_id,
            Courier.log_partner == current_user.log_partner
        ).first()
        
        if not courier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Курьер не найден"
            )
            
        # Меняем статус на "Оформлен"
        courier.onboarding_status = OnboardingStatus.VERIFIED
        courier.verified_by_id = current_user.id
        courier.verified_at = datetime.utcnow()
        
        # Устанавливаем статус документов как проверенный
        courier.documents_status = DocumentStatus.VERIFIED
        if courier.transport_type not in ['pedestrian', 'bicycle']:
            courier.vehicle_docs_status = VehicleDocsStatus.VERIFIED
        
        # Добавляем запись в историю
        history = CourierHistory(
            courier_id=courier.id,
            type="onboarding",
            event="Курьер подтвержден",
            status=OnboardingStatus.VERIFIED,
            created_by_id=current_user.id
        )
        db.add(history)
        db.commit()
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error verifying courier: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/couriers/{courier_id}/history")
async def get_courier_history(
    courier_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user(request, db)
        
        # Проверяем существование курьера
        courier = db.query(Courier).filter(
            Courier.id == courier_id,
            Courier.log_partner == current_user.log_partner
        ).first()
        
        if not courier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Курьер не найден"
            )
        
        # Получаем историю с загрузкой связанных данных
        history = db.query(CourierHistory).options(
            joinedload(CourierHistory.created_by)
        ).filter(
            CourierHistory.courier_id == courier_id
        ).order_by(CourierHistory.created_at.desc()).all()
        
        return [
            {
                "created_at": record.created_at,
                "event": record.event,
                "status": record.status,
                "type": record.type,
                "user": {
                    "username": record.created_by.username if record.created_by else None
                },
                "comment": getattr(record, 'comment', None),
                "equipment_name": getattr(record, 'equipment_name', None),
                "amount": getattr(record, 'amount', None)
            }
            for record in history
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting courier history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении истории: {str(e)}"
        )

@router.get("/couriers/{courier_id}/accounting")
async def get_courier_accounting(
    courier_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user(request, db)
        
        # Здесь будет логика получения истории выплат
        # Пока возвращаем пустой список
        return []
        
    except Exception as e:
        logger.error(f"Error getting courier accounting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении истории выплат: {str(e)}"
        )

@router.get("/api/couriers")
async def get_couriers(request: Request, db: Session = Depends(get_db)):
    try:
        current_user = await get_current_user(request, db)
        couriers = db.query(Courier).filter(
            Courier.log_partner == current_user.log_partner
        ).all()
        
        return [
            {
                "id": courier.id,
                "full_name": courier.full_name,
                "phone": courier.phone,
                "onboarding_status": courier.onboarding_status,
                "created_at": courier.created_at.isoformat() if courier.created_at else None,
                "updated_at": courier.updated_at.isoformat() if courier.updated_at else None
            }
            for courier in couriers
        ]
    except Exception as e:
        logger.error(f"Error getting couriers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/api/onboarding/couriers")
async def get_couriers(
    request: Request,
    db: Session = Depends(get_db),
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    status_filter: Optional[str] = None
):
    try:
        current_user = await get_current_user(request, db)
        query = db.query(Courier).filter(
            Courier.log_partner == current_user.log_partner
        )
        
        # Применяем фильтры
        if search:
            search = f"%{search}%"
            query = query.filter(
                (Courier.full_name.ilike(search)) |
                (Courier.phone.ilike(search))
            )
            
        if status_filter:
            query = query.filter(Courier.status == status_filter)
        
        # Подсчитываем общее количество
        total = query.count()
        logger.info(f"Total couriers found: {total}")
        
        # Применяем пагинацию
        couriers = query.offset((page - 1) * limit).limit(limit).all()
        logger.info(f"Couriers after pagination: {len(couriers)}")
        
        return {
            "items": [{
                "id": c.id,
                "full_name": c.full_name,
                "phone": c.phone,
                "onboarding_status": c.onboarding_status,
                "created_at": c.created_at.isoformat() if c.created_at else None
            } for c in couriers],
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error getting couriers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/api/couriers/{courier_id}/verify")
async def verify_courier(
    courier_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user(request, db)
        courier = db.query(Courier).filter(
            Courier.id == courier_id,
            Courier.log_partner == current_user.log_partner
        ).first()
        
        if not courier:
            raise HTTPException(status_code=404, detail="Курьер не найден")
        
        # Проверяем, что статус не "Оформлен"
        if courier.onboarding_status == OnboardingStatus.VERIFIED:
            raise HTTPException(
                status_code=400,
                detail="Курьер уже оформлен"
            )
        
        # Меняем статус на "Оформлен"
        courier.onboarding_status = OnboardingStatus.VERIFIED
        courier.verified_by_id = current_user.id
        courier.verified_at = datetime.utcnow()
        
        # Добавляем запись в историю
        history = CourierHistory(
            courier_id=courier.id,
            type="onboarding",
            event="Статус изменен на 'Оформлен'",
            status=OnboardingStatus.VERIFIED,
            created_by_id=current_user.id
        )
        db.add(history)
        db.commit()
        
        return {"message": "Статус курьера успешно изменен на 'Оформлен'"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying courier: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось изменить статус курьера. Пожалуйста, попробуйте позже."
        )

@router.put("/api/couriers/{courier_id}")
async def update_courier(
    courier_id: int,
    courier_data: CourierUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        current_user = await get_current_user(request, db)
        courier = db.query(Courier).filter(
            Courier.id == courier_id,
            Courier.log_partner == current_user.log_partner
        ).first()
        
        if not courier:
            raise HTTPException(status_code=404, detail="Курьер не найден")

        # Логируем полученные данные
        logger.info(f"Updating courier {courier_id} with data: {courier_data.dict()}")
        
        # Обновляем только переданные поля
        update_data = courier_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:  # Обновляем только непустые значения
                setattr(courier, key, value)
        
        # Если статус изменился на VERIFIED, добавляем информацию о верификации
        if update_data.get('onboarding_status') == 'VERIFIED':
            courier.verified_at = datetime.utcnow()
            courier.verified_by_id = current_user.id

        db.commit()
        
        # Добавляем запись в историю
        history = CourierHistory(
            courier_id=courier.id,
            type="onboarding",
            event="Обновлены данные курьера",
            status=courier.onboarding_status,
            created_by_id=current_user.id
        )
        db.add(history)
        db.commit()

        return {"message": "Данные курьера обновлены"}
        
    except Exception as e:
        logger.error(f"Error updating courier: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при обновлении данных курьера"
        )

@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    request: Request,
    db: Session = Depends(get_db),
    region: Optional[str] = Query(None, description="Filter by region"),
    date_from: Optional[str] = Query(None, description="Start date"),
    date_to: Optional[str] = Query(None, description="End date"), 
    employee: Optional[str] = Query(None, description="Filter by employee")
):
    try:
        current_user = await get_current_user(request, db)

        filters = {}
        if region and region != 'all':
            filters['region_id'] = region
        if date_from:
            filters['created_at__gte'] = date_from
        if date_to:
            filters['created_at__lte'] = date_to
        if employee and employee != 'all':
            filters['onboarder_id'] = employee

        # Получаем статистику с учетом фильтров
        metrics = await get_onboarding_metrics(db, filters)
        chart_data = await get_onboarding_chart_data(db, filters)
        
        # Если выбраны все сотрудники, получаем их статистику
        employees_data = []
        if employee == 'all':
            employees_data = await get_employees_statistics(db, filters)

        # Возвращаем данные в формате StatisticsResponse
        return StatisticsResponse(
            metrics=metrics,
            chart_data=chart_data,
            employees=employees_data
        )

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Ошибка при получении статистики"
        )