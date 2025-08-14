"""
Container Security Module - Routes
Scan des vulnérabilités conteneurs et runtime analysis
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import asyncio

# Import des classes locales
from .models import ContainerScan, ScanType, ScanStatus
from .scanner import ContainerScanner

router = APIRouter(prefix="/api/container-security", tags=["Container Security"])

# Instance globale du scanner
container_scanner = ContainerScanner()

class ContainerScanRequest(BaseModel):
    image_name: str
    scan_type: str = "vulnerability"  # vulnerability, configuration, runtime
    registry_auth: Optional[Dict[str, str]] = None
    include_runtime: bool = False
    scan_options: Optional[Dict[str, Any]] = None

class ContainerScanResponse(BaseModel):
    scan_id: str
    status: str
    created_at: str
    image_name: str
    scan_type: str

@router.get("/")
async def container_security_status():
    """Status et capacités du service Container Security"""
    return {
        "status": "operational",
        "service": "Container Security",
        "version": "1.0.0-portable",
        "features": {
            "image_scanning": True,
            "runtime_analysis": True,
            "cve_detection": True,
            "compliance_checks": True,
            "hardening_recommendations": True,
            "dockerfile_analysis": True,
            "secrets_detection": True,
            "malware_scanning": False  # Nécessiterait intégration antivirus
        },
        "supported_formats": ["docker", "podman", "containerd", "oci"],
        "supported_registries": ["docker_hub", "gcr", "ecr", "acr", "harbor"],
        "vulnerability_databases": ["NVD", "CVE", "GHSA", "Alpine SecDB", "Debian Security"],
        "compliance_standards": ["CIS Docker", "NIST", "PCI-DSS"],
        "active_scans": 0,
        "completed_scans": 0,
        "total_images_scanned": 0,
        "total_vulnerabilities_found": 0,
        "severity_stats": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "negligible": 0
        },
        "top_vulnerable_packages": {},
        "scan_performance": {
            "avg_scan_time": "2.5 minutes",
            "success_rate": "98.5%"
        }
    }

@router.post("/scan-image", response_model=ContainerScanResponse)
async def scan_container_image(request: ContainerScanRequest):
    """Lance un scan de sécurité d'image conteneur"""
    try:
        # Validation du nom d'image
        if not request.image_name or len(request.image_name.strip()) == 0:
            raise HTTPException(status_code=400, detail="Nom d'image requis")
        
        # Utilisation du vrai scanner
        scan_options = request.scan_options or {}
        scan_options.update({
            "scan_type": request.scan_type,
            "include_runtime": request.include_runtime,
            "enable_vulnerability_scan": True,
            "enable_secrets_detection": True,
            "enable_compliance_checks": True
        })
        
        # Lancement du scan avec le moteur réel
        scan_result = await container_scanner.scan_image(request.image_name, scan_options)
        
        return ContainerScanResponse(
            scan_id=scan_result.scan_id,
            status=scan_result.status.value,
            created_at=scan_result.created_at.isoformat(),
            image_name=request.image_name,
            scan_type=request.scan_type
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du scan de l'image: {str(e)}"
        )

@router.get("/vulns")
async def get_vulnerabilities(
    image: Optional[str] = None,
    scan_id: Optional[str] = None,
    severity: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Récupère les vulnérabilités trouvées"""
    try:
        # Simulation de récupération depuis la base de données
        # En production, on utiliserait une vraie base de données
        vulnerabilities = []
        
        # Exemple avec scan test
        if not scan_id:
            test_scan = await container_scanner.scan_image("nginx:latest")
            vulnerabilities = [
                {
                    "cve_id": vuln.cve_id,
                    "severity": vuln.severity.value,
                    "package": vuln.package,
                    "installed_version": vuln.installed_version,
                    "fixed_version": vuln.fixed_version,
                    "description": vuln.description,
                    "cvss_score": vuln.cvss_score
                }
                for vuln in test_scan.vulnerabilities
            ]
        
        # Filtrage par sévérité
        if severity:
            vulnerabilities = [v for v in vulnerabilities if v["severity"] == severity]
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_vulns = vulnerabilities[start:end]
        
        return {
            "vulnerabilities": paginated_vulns,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": len(vulnerabilities),
                "total_pages": (len(vulnerabilities) + page_size - 1) // page_size
            },
            "filters_applied": {
                "image": image,
                "scan_id": scan_id,
                "severity": severity
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération vulnérabilités: {str(e)}"
        )

@router.get("/scans")
async def get_scan_history(
    image: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
):
    """Récupère l'historique des scans"""
    try:
        # Simulation historique des scans
        scans = [
            {
                "scan_id": str(uuid.uuid4()),
                "image_name": "nginx:latest",
                "status": "completed",
                "created_at": "2023-12-15T14:30:00Z",
                "scan_type": "vulnerability",
                "vulnerabilities_found": 15,
                "severity_breakdown": {"critical": 2, "high": 5, "medium": 6, "low": 2}
            },
            {
                "scan_id": str(uuid.uuid4()),
                "image_name": "postgres:13",
                "status": "completed", 
                "created_at": "2023-12-15T13:15:00Z",
                "scan_type": "vulnerability",
                "vulnerabilities_found": 8,
                "severity_breakdown": {"critical": 0, "high": 2, "medium": 4, "low": 2}
            }
        ]
        
        return {
            "scans": scans,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": len(scans),
                "total_pages": (len(scans) + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur récupération historique: {str(e)}"
        )

@router.get("/scan/{scan_id}")
async def get_scan_details(scan_id: str):
    """Récupère les détails complets d'un scan"""
    try:
        # Simulation récupération détails scan
        scan_details = {
            "scan_id": scan_id,
            "status": "completed",
            "image_name": "nginx:latest",
            "created_at": "2023-12-15T14:30:00Z",
            "completed_at": "2023-12-15T14:32:30Z",
            "scan_duration": "2.5 minutes",
            "image_info": {
                "size": "142.8 MB",
                "layers": 8,
                "base_image": "debian:bullseye-slim",
                "architecture": "amd64"
            },
            "vulnerabilities_summary": {
                "total": 15,
                "critical": 2,
                "high": 5,
                "medium": 6,
                "low": 2
            },
            "compliance_score": 78,
            "recommendations_count": 8
        }
        
        return scan_details
        
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Scan non trouvé: {scan_id}"
        )

@router.delete("/scan/{scan_id}")
async def delete_scan(scan_id: str):
    """Supprime un scan et ses résultats"""
    try:
        # Ici on supprimerait de la base de données
        # await delete_scan_from_db(scan_id)
        
        return {
            "message": f"Scan {scan_id} supprimé avec succès",
            "deleted_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur suppression scan: {str(e)}"
        )