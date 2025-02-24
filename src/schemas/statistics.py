from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class StatisticsMetrics(BaseModel):
    total: int
    verified: int
    will_be_verified: int
    rejected_by_hub: int
    rejected_by_courier: int

class ChartDataset(BaseModel):
    label: str
    data: List[int]

class ChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]  # Оставляем Any для гибкости с данными графика

class EmployeeStatistics(BaseModel):
    id: int
    name: str
    total: int
    verified: int
    will_be_verified: int
    rejected_by_hub: int
    rejected_by_courier: int

class StatisticsResponse(BaseModel):
    metrics: StatisticsMetrics
    chart_data: ChartData
    employees: List[EmployeeStatistics]

    class Config:
        from_attributes = True  # Для поддержки атрибутов SQLAlchemy 