# CRM Service Models
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class Client(BaseModel):
    client_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company: str
    contacts: List[Dict[str, Any]] = []
    projects: List[str] = []
    billing_info: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ClientUpdate(BaseModel):
    company: Optional[str] = None
    contacts: Optional[List[Dict[str, Any]]] = None
    billing_info: Optional[Dict[str, Any]] = None

class Project(BaseModel):
    project_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    services: List[str] = []
    timeline: Optional[Dict[str, Any]] = None
    budget: Optional[float] = None
    status: str = "planned"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ProjectUpdate(BaseModel):
    services: Optional[List[str]] = None
    timeline: Optional[Dict[str, Any]] = None
    budget: Optional[float] = None
    status: Optional[str] = None