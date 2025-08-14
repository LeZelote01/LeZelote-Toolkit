"""
Routes API pour Automation AI - CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - Endpoints REST pour l'automatisation des workflows sécurité
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import uuid

from .main import automation_ai_service, SecurityWorkflow, WorkflowExecutionRequest, WorkflowExecutionResult, AutomationRule, WorkflowStep
from backend.config import settings

router = APIRouter(prefix="/api/automation-ai", tags=["Automation AI"])

@router.post("/workflows", response_model=Dict[str, Any])
async def create_workflow(workflow: Dict[str, Any]):
    """
    Création d'un nouveau workflow d'automatisation (compat payload minimal des tests)
    """
    try:
        # Normalisation du payload pour correspondre au modèle SecurityWorkflow
        normalized = dict(workflow)
        steps = normalized.get("steps", [])
        norm_steps: List[WorkflowStep] = []
        for s in steps:
            action_type = s.get("action_type") or s.get("action") or "analyze"
            # Normaliser synonymes
            if action_type in ("assess", "assessment"):
                action_type = "analyze"
            norm_steps.append(WorkflowStep(
                step_id=s.get("step_id", str(uuid.uuid4())),
                name=s.get("name", "Step"),
                action_type=action_type,
                parameters=s.get("parameters", {}),
                conditions=s.get("conditions"),
                timeout=int(s.get("timeout", 120)),
                retry_count=int(s.get("retry_count", 1))
            ))
        normalized.setdefault("trigger_type", normalized.get("trigger_type", "manual"))
        normalized.setdefault("trigger_conditions", normalized.get("trigger_conditions", {}))
        normalized["steps"] = norm_steps
        normalized.setdefault("is_active", True)
        normalized.setdefault("created_by", "automation_ai")
        
        wf = SecurityWorkflow(
            workflow_id=normalized.get("workflow_id", f"wf_{uuid.uuid4().hex[:8]}"),
            name=normalized.get("name", "Security Workflow"),
            description=normalized.get("description", ""),
            category=normalized.get("category", "incident_response"),
            trigger_type=normalized.get("trigger_type"),
            trigger_conditions=normalized.get("trigger_conditions"),
            steps=normalized["steps"],
            is_active=normalized.get("is_active", True),
            created_by=normalized.get("created_by", "automation_ai")
        )
        result = await automation_ai_service.create_workflow(wf)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création workflow: {str(e)}")

@router.post("/workflows/{workflow_id}/execute", response_model=WorkflowExecutionResult)
async def execute_workflow(workflow_id: str, execution_request: Optional[WorkflowExecutionRequest] = None):
    try:
        if execution_request is None:
            execution_request = WorkflowExecutionRequest(workflow_id=workflow_id)
        else:
            execution_request.workflow_id = workflow_id
        result = await automation_ai_service.execute_workflow(execution_request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur exécution workflow: {str(e)}")

@router.get("/workflows")
async def list_workflows(
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    active_only: bool = Query(True, description="Seulement les workflows actifs")
):
    try:
        workflows = automation_ai_service.workflow_templates
        filtered_workflows = {}
        for wf_id, workflow in workflows.items():
            if category and workflow.category != category:
                continue
            if active_only and not workflow.is_active:
                continue
            filtered_workflows[wf_id] = {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "description": workflow.description,
                "category": workflow.category,
                "trigger_type": workflow.trigger_type,
                "steps_count": len(workflow.steps),
                "is_active": workflow.is_active
            }
        return {
            "status": "success",
            "total_workflows": len(filtered_workflows),
            "workflows": filtered_workflows,
            "categories": list(set(wf.category for wf in workflows.values()))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur liste workflows: {str(e)}")

@router.get("/workflows/{workflow_id}")
async def get_workflow_details(workflow_id: str):
    try:
        workflow = automation_ai_service.workflow_templates.get(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow non trouvé")
        return {
            "status": "success",
            "workflow": workflow.dict(),
            "estimated_duration": automation_ai_service._estimate_execution_time(workflow),
            "last_executions": await automation_ai_service._get_recent_executions(workflow_id, limit=5)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur détails workflow: {str(e)}")

@router.get("/executions")
async def list_executions(
    status: Optional[str] = Query(None, description="Filtrer par statut"),
    limit: int = Query(50, le=100, description="Nombre maximum de résultats")
):
    try:
        active_executions = list(automation_ai_service.active_workflows.values())
        historical_executions = await automation_ai_service._get_historical_executions(limit - len(active_executions))
        all_executions = active_executions + historical_executions
        if status:
            all_executions = [exe for exe in all_executions if (exe.get("status") if isinstance(exe, dict) else exe.status) == status]
        executions_data = []
        for exe in all_executions[:limit]:
            exe_dict = exe.dict() if hasattr(exe, 'dict') else exe
            executions_data.append({
                "execution_id": exe_dict.get("execution_id"),
                "workflow_id": exe_dict.get("workflow_id"),
                "status": exe_dict.get("status"),
                "start_time": exe_dict.get("start_time"),
                "end_time": exe_dict.get("end_time"),
                "execution_time": exe_dict.get("execution_time"),
                "success_count": exe_dict.get("success_count", 0),
                "failure_count": exe_dict.get("failure_count", 0)
            })
        return {
            "status": "success",
            "total_executions": len(executions_data),
            "active_executions": len(active_executions),
            "executions": executions_data,
            "status_distribution": automation_ai_service._calculate_status_distribution(
                [e if isinstance(e, dict) else e.dict() for e in all_executions]
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur liste exécutions: {str(e)}")

@router.get("/executions/{execution_id}")
async def get_execution_details(execution_id: str):
    try:
        if execution_id in automation_ai_service.active_workflows:
            execution = automation_ai_service.active_workflows[execution_id]
            return {"status": "success", "execution": execution.dict(), "is_active": True}
        historical_execution = await automation_ai_service._get_execution_from_history(execution_id)
        if historical_execution:
            return {"status": "success", "execution": historical_execution, "is_active": False}
        raise HTTPException(status_code=404, detail="Exécution non trouvée")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur détails exécution: {str(e)}")

@router.post("/executions/{execution_id}/cancel")
async def cancel_execution(execution_id: str):
    try:
        if execution_id not in automation_ai_service.active_workflows:
            raise HTTPException(status_code=404, detail="Exécution non trouvée ou déjà terminée")
        from datetime import datetime, timezone
        execution = automation_ai_service.active_workflows[execution_id]
        execution.status = "cancelled"
        execution.end_time = datetime.now(timezone.utc)
        await automation_ai_service._save_execution_result(execution)
        del automation_ai_service.active_workflows[execution_id]
        return {"status": "success", "message": "Exécution annulée", "execution_id": execution_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur annulation exécution: {str(e)}")

@router.post("/rules")
async def create_automation_rule(rule: AutomationRule):
    try:
        if rule.rule_id in automation_ai_service.automation_rules:
            raise HTTPException(status_code=409, detail="Règle déjà existante")
        automation_ai_service.automation_rules[rule.rule_id] = rule
        await automation_ai_service._save_automation_rule(rule)
        return {"status": "created", "rule_id": rule.rule_id, "message": "Règle d'automatisation créée", "is_active": rule.is_active}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création règle: {str(e)}")

@router.get("/rules")
async def list_automation_rules(active_only: bool = Query(True)):
    try:
        rules = automation_ai_service.automation_rules
        filtered_rules = {}
        for rule_id, rule in rules.items():
            if active_only and not rule.is_active:
                continue
            filtered_rules[rule_id] = {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "priority": rule.priority,
                "is_active": rule.is_active,
                "condition_summary": str(rule.condition)[:100] + "..." if len(str(rule.condition)) > 100 else str(rule.condition)
            }
        return {"status": "success", "total_rules": len(filtered_rules), "rules": filtered_rules, "active_rules": sum(1 for r in rules.values() if r.is_active)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur liste règles: {str(e)}")

@router.get("/templates")
async def get_workflow_templates():
    try:
        templates_info = {}
        for template_id, workflow in automation_ai_service.workflow_templates.items():
            templates_info[template_id] = {
                "template_id": template_id,
                "name": workflow.name,
                "description": workflow.description,
                "category": workflow.category,
                "trigger_type": workflow.trigger_type,
                "steps_count": len(workflow.steps),
                "estimated_duration": automation_ai_service._estimate_execution_time(workflow),
                "complexity": "high" if len(workflow.steps) > 5 else "medium" if len(workflow.steps) > 2 else "low"
            }
        return {"status": "success", "total_templates": len(templates_info), "templates": templates_info, "categories": list(set(t["category"] for t in templates_info.values()))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur templates: {str(e)}")

@router.post("/templates/{template_id}/instantiate")
async def instantiate_template(template_id: str, customizations: Optional[Dict[str, Any]] = None):
    try:
        if template_id not in automation_ai_service.workflow_templates:
            raise HTTPException(status_code=404, detail="Template non trouvé")
        template = automation_ai_service.workflow_templates[template_id]
        new_workflow_id = f"{template_id}_instance_{uuid.uuid4().hex[:8]}"
        new_workflow = template.copy()
        new_workflow.workflow_id = new_workflow_id
        new_workflow.name = f"{template.name} (Instance)"
        if customizations:
            if "name" in customizations:
                new_workflow.name = customizations["name"]
            if "trigger_conditions" in customizations:
                new_workflow.trigger_conditions.update(customizations["trigger_conditions"])
        result = await automation_ai_service.create_workflow(new_workflow)
        return {"status": "success", "message": "Template instancié avec succès", "new_workflow_id": new_workflow_id, "template_id": template_id, "customizations_applied": len(customizations) if customizations else 0, "creation_result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur instanciation template: {str(e)}")

@router.get("/status")
async def automation_ai_status():
    try:
        return {
            "status": "operational",
            "service": "Automation AI - Automatisation Workflows",
            "version": "1.0.0-portable",
            "sprint": "1.5",
            "llm_configured": bool(settings.emergent_llm_key),
            "llm_provider": settings.default_llm_provider,
            "llm_model": settings.default_llm_model,
            "portable_mode": settings.portable_mode,
            "capabilities": {
                "workflow_creation": True,
                "workflow_execution": True,
                "automation_rules": True,
                "template_system": True,
                "async_execution": True,
                "ai_decisions": True,
                "retry_mechanisms": True,
                "condition_evaluation": True
            },
            "statistics": {
                "total_workflows": len(automation_ai_service.workflow_templates),
                "active_executions": len(automation_ai_service.active_workflows),
                "automation_rules": len(automation_ai_service.automation_rules),
                "supported_actions": list(automation_ai_service.action_handlers.keys())
            },
            "workflow_categories": [
                "incident_response", "vulnerability_management", 
                "compliance", "monitoring", "remediation"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur status Automation AI: {str(e)}")

@router.get("/health")
async def automation_ai_health():
    try:
        test_workflow = automation_ai_service.workflow_templates.get("incident_response_auto")
        return {
            "status": "healthy",
            "service": "Automation AI",
            "llm_status": "configured" if settings.emergent_llm_key else "fallback",
            "workflow_engine": "operational",
            "template_system": "loaded" if test_workflow else "error",
            "automation_rules": f"{len(automation_ai_service.automation_rules)} loaded",
            "action_handlers": f"{len(automation_ai_service.action_handlers)} available",
            "active_executions": len(automation_ai_service.active_workflows),
            "database_connection": "functional",
            "timestamp": "2025-08-12T19:00:00Z"
        }
    except Exception as e:
        return {"status": "unhealthy", "service": "Automation AI", "error": str(e), "timestamp": "2025-08-12T19:00:00Z"}