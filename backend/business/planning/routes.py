# Planning Service Routes
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import Event, EventUpdate
from database import get_collection

router = APIRouter(prefix="/api/planning", tags=["Planning"])

# ---------- Utils ----------
async def _find_one_by_field(col, field: str, value: str) -> Optional[Dict[str, Any]]:
    docs = await col.find({})
    for d in docs:
        if d.get(field) == value:
            return d
    return None

# ---------- Endpoints ----------
@router.get("/status")
async def status():
    col = await get_collection("events")
    docs = await col.find({})
    return {
        "status": "operational", 
        "service": "Planning", 
        "counts": {"events": len(docs)}
    }

@router.post("/event", response_model=Event)
async def create_event(event: Event):
    col = await get_collection("events")
    await col.insert_one(event.model_dump())
    return event

@router.get("/events", response_model=List[Event])
async def list_events(
    assigned_to: Optional[str] = Query(None, description="Filtre par personne assignée"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200)
):
    col = await get_collection("events")
    docs = await col.find({})
    if assigned_to:
        s = assigned_to.strip().lower()
        docs = [d for d in docs if (d.get("assigned_to") or "").lower() == s]
    start = (page - 1) * page_size
    end = start + page_size
    sliced = docs[start:end]
    return [Event(**d) for d in sliced]

@router.get("/event/{event_id}", response_model=Event)
async def get_event(event_id: str):
    col = await get_collection("events")
    doc = await _find_one_by_field(col, "event_id", event_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Event not found")
    return Event(**doc)

@router.put("/event/{event_id}")
async def update_event(event_id: str, payload: EventUpdate):
    col = await get_collection("events")
    doc = await _find_one_by_field(col, "event_id", event_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Event not found")
    update_fields = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if not update_fields:
        return {"matched": 1, "modified": 0}
    update_fields["updated_at"] = datetime.utcnow().isoformat()
    res = await col.update_one({"_id": doc["_id"]}, {"$set": update_fields})
    return {"matched": res.get("matched_count", 0), "modified": res.get("modified_count", 0)}

@router.delete("/event/{event_id}")
async def delete_event(event_id: str):
    col = await get_collection("events")
    doc = await _find_one_by_field(col, "event_id", event_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Event not found")
    res = await col.delete_one({"_id": doc["_id"]})
    return {"deleted": res.get("deleted_count", 0)}

@router.get("/events/calendar")
async def get_calendar_events(
    month: Optional[int] = Query(None, description="Mois (1-12)"),
    year: Optional[int] = Query(None, description="Année")
):
    """Get events formatted for calendar view"""
    col = await get_collection("events")
    docs = await col.find({})
    
    # Filter by month/year if provided
    if month and year:
        filtered_docs = []
        for doc in docs:
            try:
                event_date = datetime.fromisoformat(doc.get("start", ""))
                if event_date.month == month and event_date.year == year:
                    filtered_docs.append(doc)
            except:
                continue
        docs = filtered_docs
    
    # Format for calendar
    calendar_events = []
    for doc in docs:
        calendar_events.append({
            "id": doc.get("event_id"),
            "title": doc.get("title"),
            "start": doc.get("start"),
            "end": doc.get("end"),
            "assigned_to": doc.get("assigned_to"),
            "tags": doc.get("tags", [])
        })
    
    return {"events": calendar_events, "total": len(calendar_events)}