from sqlalchemy import func, case
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.models import Courier, User, OnboardingStatus

async def get_onboarding_metrics(db: Session, filters=None):
    """Получение основных метрик онбординга"""
    query = db.query(Courier)
    
    if filters:
        for key, value in filters.items():
            if key == 'region_id':
                query = query.join(User).filter(User.region_id == value)
            elif key == 'created_at__gte':
                query = query.filter(Courier.created_at >= value)
            elif key == 'created_at__lte':
                query = query.filter(Courier.created_at <= value)
            elif key == 'onboarder_id':
                query = query.filter(Courier.created_by_id == value)

    total = query.count()
    verified = query.filter(Courier.onboarding_status == OnboardingStatus.VERIFIED).count()
    will_be_verified = query.filter(Courier.onboarding_status == OnboardingStatus.WILL_BE_VERIFIED).count()
    rejected_by_hub = query.filter(Courier.onboarding_status == OnboardingStatus.REJECTED_BY_HUB).count()
    rejected_by_courier = query.filter(Courier.onboarding_status == OnboardingStatus.REJECTED_BY_COURIER).count()

    return {
        "total": total,
        "verified": verified,
        "will_be_verified": will_be_verified,
        "rejected_by_hub": rejected_by_hub,
        "rejected_by_courier": rejected_by_courier
    }

async def get_employees_statistics(db: Session, filters=None):
    """Получение статистики по сотрудникам"""
    query = db.query(
        User.id,
        User.username,
        func.count(Courier.id).label('total'),
        func.sum(case([(Courier.onboarding_status == OnboardingStatus.VERIFIED, 1)], else_=0)).label('verified'),
        func.sum(case([(Courier.onboarding_status == OnboardingStatus.WILL_BE_VERIFIED, 1)], else_=0)).label('will_be_verified'),
        func.sum(case([(Courier.onboarding_status == OnboardingStatus.REJECTED_BY_HUB, 1)], else_=0)).label('rejected_by_hub'),
        func.sum(case([(Courier.onboarding_status == OnboardingStatus.REJECTED_BY_COURIER, 1)], else_=0)).label('rejected_by_courier')
    ).join(Courier, User.id == Courier.created_by_id)

    if filters:
        if 'region_id' in filters:
            query = query.filter(User.region_id == filters['region_id'])
        if 'created_at__gte' in filters:
            query = query.filter(Courier.created_at >= filters['created_at__gte'])
        if 'created_at__lte' in filters:
            query = query.filter(Courier.created_at <= filters['created_at__lte'])

    query = query.group_by(User.id, User.username)

    results = query.all()
    return [
        {
            "id": r.id,
            "name": r.username,
            "total": r.total,
            "verified": r.verified,
            "will_be_verified": r.will_be_verified,
            "rejected_by_hub": r.rejected_by_hub,
            "rejected_by_courier": r.rejected_by_courier
        }
        for r in results
    ]

async def get_onboarding_chart_data(db: Session, filters=None):
    """Получение данных для графика"""
    query = db.query(
        func.date(Courier.created_at).label('date'),
        func.count(Courier.id).label('total'),
        func.sum(case([(Courier.onboarding_status == OnboardingStatus.VERIFIED, 1)], else_=0)).label('verified'),
        func.sum(case([(Courier.onboarding_status == OnboardingStatus.WILL_BE_VERIFIED, 1)], else_=0)).label('will_be_verified'),
        func.sum(case([(Courier.onboarding_status == OnboardingStatus.REJECTED_BY_HUB, 1)], else_=0)).label('rejected_by_hub'),
        func.sum(case([(Courier.onboarding_status == OnboardingStatus.REJECTED_BY_COURIER, 1)], else_=0)).label('rejected_by_courier')
    )

    if filters:
        for key, value in filters.items():
            if key == 'region_id':
                query = query.join(User).filter(User.region_id == value)
            elif key == 'created_at__gte':
                query = query.filter(Courier.created_at >= value)
            elif key == 'created_at__lte':
                query = query.filter(Courier.created_at <= value)
            elif key == 'onboarder_id':
                query = query.filter(Courier.created_by_id == value)

    query = query.group_by(func.date(Courier.created_at))
    query = query.order_by(func.date(Courier.created_at))

    results = query.all()
    return {
        "labels": [r.date.strftime('%Y-%m-%d') for r in results],
        "datasets": [
            {
                "label": "Всего",
                "data": [r.total for r in results]
            },
            {
                "label": "Оформлены",
                "data": [r.verified for r in results]
            },
            {
                "label": "Оформятся",
                "data": [r.will_be_verified for r in results]
            },
            {
                "label": "Отказ хаба",
                "data": [r.rejected_by_hub for r in results]
            },
            {
                "label": "Отказ курьера",
                "data": [r.rejected_by_courier for r in results]
            }
        ]
    } 