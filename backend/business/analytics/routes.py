# Analytics Service Routes
from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime, timedelta, date

from .models import Metrics, DailyPoint
from .analytics_engine import AnalyticsEngine
from database import get_collection

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

# Initialize analytics engine
analytics_engine = AnalyticsEngine()

@router.get("/status")
async def status():
    return {
        "status": "operational", 
        "service": "Analytics", 
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/metrics", response_model=Metrics)
async def get_metrics(
    from_date: Optional[str] = Query(None), 
    to_date: Optional[str] = Query(None)
):
    start = analytics_engine.parse_date(from_date)
    end = analytics_engine.parse_date(to_date)

    clients_col = await get_collection("clients")
    invoices_col = await get_collection("invoices")
    projects_col = await get_collection("projects")

    clients = await clients_col.find({})
    invoices = await invoices_col.find({})
    projects = await projects_col.find({})

    if start or end:
        clients = [c for c in clients if analytics_engine.in_range(c.get("created_at", ""), start, end)]
        projects = [p for p in projects if analytics_engine.in_range(p.get("created_at", ""), start, end)]
        invoices = [i for i in invoices if analytics_engine.in_range(i.get("created_at", ""), start, end)]

    revenue_paid = sum([inv.get("amount", 0.0) for inv in invoices if inv.get("status") == "paid"])
    revenue_total = sum([inv.get("amount", 0.0) for inv in invoices])

    return Metrics(
        timestamp=datetime.utcnow().isoformat(),
        totals={
            "clients": len(clients),
            "projects": len(projects),
            "invoices": len(invoices)
        },
        revenue={
            "paid": round(revenue_paid, 2),
            "total": round(revenue_total, 2)
        }
    )

@router.get("/metrics/daily", response_model=List[DailyPoint])
async def get_daily_metrics(
    days: int = 7, 
    from_date: Optional[str] = Query(None), 
    to_date: Optional[str] = Query(None)
):
    """Returns daily metrics for the last N days or a given interval."""
    invoices_col = await get_collection("invoices")
    invoices = await invoices_col.find({})

    start = analytics_engine.parse_date(from_date)
    end = analytics_engine.parse_date(to_date)

    if start and not end:
        end = datetime.utcnow().date()
    if not start and end:
        start = end - timedelta(days=days - 1)

    if not start and not end:
        end = datetime.utcnow().date()
        start = end - timedelta(days=days - 1)

    results: List[DailyPoint] = []
    cur = start
    while cur <= end:
        iso_prefix = cur.isoformat()
        day_invoices = [inv for inv in invoices if str(inv.get("created_at", "")).startswith(iso_prefix)]
        total = sum([inv.get("amount", 0.0) for inv in day_invoices])
        paid = sum([inv.get("amount", 0.0) for inv in day_invoices if inv.get("status") == "paid"])
        results.append(DailyPoint(
            date=iso_prefix, 
            invoices=len(day_invoices), 
            revenue_total=round(total, 2), 
            revenue_paid=round(paid, 2)
        ))
        cur = cur + timedelta(days=1)

    return results