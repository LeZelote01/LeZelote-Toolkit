# Training Service Routes
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import Course, CourseUpdate, TrainingSession
from database import get_collection

router = APIRouter(prefix="/api/training", tags=["Training"])

# ---------- Utils ----------
async def _find_one_by_field(col, field: str, value: str) -> Optional[Dict[str, Any]]:
    docs = await col.find({})
    for d in docs:
        if d.get(field) == value:
            return d
    return None

# ---------- Course Endpoints ----------
@router.get("/status")
async def status():
    col = await get_collection("courses")
    docs = await col.find({})
    return {
        "status": "operational", 
        "service": "Training", 
        "counts": {"courses": len(docs)}
    }

@router.post("/course", response_model=Course)
async def create_course(course: Course):
    col = await get_collection("courses")
    await col.insert_one(course.model_dump())
    return course

@router.get("/courses", response_model=List[Course])
async def list_courses(
    level: Optional[str] = Query(None, description="Filtre par niveau"),
    search: Optional[str] = Query(None, description="Recherche par titre (contient)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200)
):
    col = await get_collection("courses")
    docs = await col.find({})
    if level:
        lvl = level.strip().lower()
        docs = [d for d in docs if (d.get("level", "").lower() == lvl)]
    if search:
        s = search.strip().lower()
        docs = [d for d in docs if s in (d.get("title", "").lower())]
    start = (page - 1) * page_size
    end = start + page_size
    sliced = docs[start:end]
    return [Course(**d) for d in sliced]

@router.get("/course/{course_id}", response_model=Course)
async def get_course(course_id: str):
    col = await get_collection("courses")
    doc = await _find_one_by_field(col, "course_id", course_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Course not found")
    return Course(**doc)

@router.put("/course/{course_id}")
async def update_course(course_id: str, payload: CourseUpdate):
    col = await get_collection("courses")
    doc = await _find_one_by_field(col, "course_id", course_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Course not found")
    update_fields = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if not update_fields:
        return {"matched": 1, "modified": 0}
    update_fields["updated_at"] = datetime.utcnow().isoformat()
    res = await col.update_one({"_id": doc["_id"]}, {"$set": update_fields})
    return {"matched": res.get("matched_count", 0), "modified": res.get("modified_count", 0)}

@router.delete("/course/{course_id}")
async def delete_course(course_id: str):
    col = await get_collection("courses")
    doc = await _find_one_by_field(col, "course_id", course_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Course not found")
    res = await col.delete_one({"_id": doc["_id"]})
    return {"deleted": res.get("deleted_count", 0)}

# ---------- Training Session Endpoints ----------
@router.post("/session", response_model=TrainingSession)
async def create_training_session(session: TrainingSession):
    # Verify course exists
    courses_col = await get_collection("courses")
    course = await _find_one_by_field(courses_col, "course_id", session.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    sessions_col = await get_collection("training_sessions")
    await sessions_col.insert_one(session.model_dump())
    return session

@router.get("/sessions", response_model=List[TrainingSession])
async def list_training_sessions(
    course_id: Optional[str] = Query(None, description="Filtre par cours"),
    participant_id: Optional[str] = Query(None, description="Filtre par participant"),
    status: Optional[str] = Query(None, description="Filtre par statut")
):
    col = await get_collection("training_sessions")
    docs = await col.find({})
    
    if course_id:
        docs = [d for d in docs if d.get("course_id") == course_id]
    if participant_id:
        docs = [d for d in docs if d.get("participant_id") == participant_id]
    if status:
        docs = [d for d in docs if d.get("status") == status]
    
    return [TrainingSession(**d) for d in docs]

@router.put("/session/{session_id}/progress")
async def update_session_progress(session_id: str, progress: float):
    if not 0 <= progress <= 100:
        raise HTTPException(status_code=400, detail="Progress must be between 0 and 100")
    
    col = await get_collection("training_sessions")
    doc = await _find_one_by_field(col, "session_id", session_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Training session not found")
    
    update_fields = {
        "progress": progress,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Auto-update status based on progress
    if progress == 0:
        update_fields["status"] = "enrolled"
    elif 0 < progress < 100:
        update_fields["status"] = "in_progress"
        if not doc.get("started_at"):
            update_fields["started_at"] = datetime.utcnow().isoformat()
    elif progress == 100:
        update_fields["status"] = "completed"
        update_fields["completed_at"] = datetime.utcnow().isoformat()
    
    res = await col.update_one({"_id": doc["_id"]}, {"$set": update_fields})
    return {"matched": res.get("matched_count", 0), "modified": res.get("modified_count", 0)}