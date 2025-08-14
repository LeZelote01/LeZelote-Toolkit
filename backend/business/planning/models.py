# Planning Service Models
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    start: str
    end: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class EventUpdate(BaseModel):
    title: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    assigned_to: Optional[str] = None
    tags: Optional[List[str]] = None

class EventFilter(BaseModel):
    assigned_to: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    tags: Optional[List[str]] = None