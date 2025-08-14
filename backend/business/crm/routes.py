# CRM Service Routes
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import Client, ClientUpdate, Project, ProjectUpdate
from database import get_collection

router = APIRouter(prefix="/api/crm", tags=["CRM"])

# ---------- Utils ----------
async def _find_one_by_field(col, field: str, value: Any) -> Optional[Dict[str, Any]]:
    docs = await col.find({})
    for d in docs:
        if d.get(field) == value:
            return d
    return None

# ---------- Endpoints ----------
@router.get("/status")
async def status():
    clients_col = await get_collection("clients")
    projects_col = await get_collection("projects")
    clients = await clients_col.find({})
    projects = await projects_col.find({})
    return {
        "status": "operational",
        "service": "CRM",
        "counts": {"clients": len(clients), "projects": len(projects)}
    }

@router.post("/client", response_model=Client)
async def create_client(client: Client):
    col = await get_collection("clients")
    await col.insert_one(client.model_dump())
    return client

@router.get("/clients", response_model=List[Client])
async def list_clients(
    search: Optional[str] = Query(None, description="Recherche par société (contient)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    col = await get_collection("clients")
    docs = await col.find({})
    if search:
        s = search.lower().strip()
        docs = [d for d in docs if s in (d.get("company", "").lower())]
    start = (page - 1) * page_size
    end = start + page_size
    sliced = docs[start:end]
    return [Client(**d) for d in sliced]

@router.get("/client/{client_id}", response_model=Client)
async def get_client(client_id: str):
    col = await get_collection("clients")
    doc = await _find_one_by_field(col, "client_id", client_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Client not found")
    return Client(**doc)

@router.put("/client/{client_id}")
async def update_client(client_id: str, payload: ClientUpdate):
    col = await get_collection("clients")
    doc = await _find_one_by_field(col, "client_id", client_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Client not found")
    update_fields = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if not update_fields:
        return {"matched": 1, "modified": 0}
    update_fields["updated_at"] = datetime.utcnow().isoformat()
    res = await col.update_one({"_id": doc["_id"]}, {"$set": update_fields})
    return {"matched": res.get("matched_count", 0), "modified": res.get("modified_count", 0)}

@router.delete("/client/{client_id}")
async def delete_client(client_id: str):
    clients_col = await get_collection("clients")
    projects_col = await get_collection("projects")
    doc = await _find_one_by_field(clients_col, "client_id", client_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Client not found")
    # Supprimer projets liés
    all_projects = await projects_col.find({})
    for p in all_projects:
        if p.get("client_id") == client_id:
            await projects_col.delete_one({"_id": p["_id"]})
    # Supprimer le client
    res = await clients_col.delete_one({"_id": doc["_id"]})
    return {"deleted": res.get("deleted_count", 0)}

@router.post("/project", response_model=Project)
async def create_project(project: Project):
    # Basic validation: client exists
    clients_col = await get_collection("clients")
    client = await _find_one_by_field(clients_col, "client_id", project.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    projects_col = await get_collection("projects")
    await projects_col.insert_one(project.model_dump())
    return project

@router.get("/projects", response_model=List[Project])
async def list_projects(
    client_id: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    col = await get_collection("projects")
    docs = await col.find({})
    if client_id:
        docs = [d for d in docs if d.get("client_id") == client_id]
    start = (page - 1) * page_size
    end = start + page_size
    sliced = docs[start:end]
    return [Project(**d) for d in sliced]

@router.get("/project/{project_id}", response_model=Project)
async def get_project(project_id: str):
    col = await get_collection("projects")
    doc = await _find_one_by_field(col, "project_id", project_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    return Project(**doc)

@router.put("/project/{project_id}")
async def update_project(project_id: str, payload: ProjectUpdate):
    col = await get_collection("projects")
    doc = await _find_one_by_field(col, "project_id", project_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    update_fields = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if not update_fields:
        return {"matched": 1, "modified": 0}
    update_fields["updated_at"] = datetime.utcnow().isoformat()
    res = await col.update_one({"_id": doc["_id"]}, {"$set": update_fields})
    return {"matched": res.get("matched_count", 0), "modified": res.get("modified_count", 0)}

@router.delete("/project/{project_id}")
async def delete_project(project_id: str):
    col = await get_collection("projects")
    doc = await _find_one_by_field(col, "project_id", project_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
    res = await col.delete_one({"_id": doc["_id"]})
    return {"deleted": res.get("deleted_count", 0)}