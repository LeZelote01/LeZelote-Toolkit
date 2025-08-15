# Analytics Service Models
from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import date

class Metrics(BaseModel):
    timestamp: str
    totals: Dict[str, int]
    revenue: Dict[str, float]

class DailyPoint(BaseModel):
    date: str
    invoices: int
    revenue_total: float
    revenue_paid: float

class DateRange(BaseModel):
    from_date: Optional[str] = None
    to_date: Optional[str] = None

class MetricsRequest(BaseModel):
    date_range: Optional[DateRange] = None
    days: int = 7