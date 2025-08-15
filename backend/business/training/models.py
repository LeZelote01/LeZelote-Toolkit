# Training Service Models
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class Course(BaseModel):
    course_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: Optional[str] = None
    level: str = "beginner"  # beginner, intermediate, advanced
    tags: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    tags: Optional[List[str]] = None

class CourseFilter(BaseModel):
    level: Optional[str] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None

class TrainingSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    participant_id: str
    status: str = "enrolled"  # enrolled, in_progress, completed, cancelled
    progress: float = 0.0  # 0-100
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())