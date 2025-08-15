"""
IoT Security Routes  
API endpoints pour la sécurité IoT
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
import uuid
import asyncio
from datetime import datetime

from .models import (
    IoTScanRequest, IoTScanResult, IoTDevice, IoTVulnerability,
    IoTSecurityStatus, IoTSecurityMetrics
)
from .scanner import IoTSecurityScanner
from database import get_database

router = APIRouter(prefix="/api/iot-security", tags=["IoT Security"])

# Cache des scans et métriques
active_scans: Dict[str, Dict] = {}
completed_scans: Dict[str, IoTScanResult] = {}
metrics_storage = IoTSecurityMetrics()

@router.get("/")
async def iot_security_status():
    """Status du service IoT Security"""
    
    # Calculer les métriques actuelles
    active_scans_count = len([s for s in active_scans.values() if s.get("status") in ["pending", "running"]])
    completed_scans_count = len(completed_scans)
    
    # Stats des dispositifs découverts
    total_devices = sum(len(scan.devices_discovered) for scan in completed_scans.values())
    
    # Stats par type de dispositif
    device_types = {}
    for scan in completed_scans.values():
        for device in scan.devices_discovered:
            device_types[device.device_type] = device_types.get(device.device_type, 0) + 1
    
    # Stats protocoles
    protocol_stats = {}
    for scan in completed_scans.values():
        for protocol, count in scan.protocols_detected.items():
            protocol_stats[protocol] = protocol_stats.get(protocol, 0) + count
    
    return {
        "status": "operational",
        "service": "IoT Security",
        "version": "1.0.0-portable",
        "features": {
            "device_discovery": True,
            "protocol_analysis": True,
            "vulnerability_scanning": True,
            "configuration_audit": True,
            "mqtt_analysis": True,
            "coap_analysis": True,
            "modbus_analysis": True,
            "network_mapping": True
        },
        "supported_protocols": [
            "MQTT", "CoAP", "Modbus", "BLE", "Zigbee", 
            "HTTP", "HTTPS", "FTP", "SSH", "Telnet"
        ],
        "supported_scan_types": [
            "discovery", "vulnerability", "configuration", "protocol_analysis"
        ],
        "active_scans": active_scans_count,
        "completed_scans": completed_scans_count,
        "total_devices_discovered": total_devices,
        "device_types_stats": device_types,
        "protocol_stats": protocol_stats
    }

@router.post("/scan/device")
async def start_iot_scan(scan_request: IoTScanRequest, background_tasks: BackgroundTasks):
    """Lance un scan de dispositifs IoT"""
    try:
        # Générer un ID unique pour le scan
        scan_id = str(uuid.uuid4())
        
        # Valider les paramètres
        if not scan_request.target.ip_range and not scan_request.target.specific_devices:
            raise HTTPException(
                status_code=400, 
                detail="Au moins une cible (ip_range ou specific_devices) est requise"
            )
        
        # Initialiser le scan
        scan_info = {
            "scan_id": scan_id,
            "target": scan_request.target.dict(),
            "protocols": scan_request.protocols,
            "scan_type": scan_request.scan_type,
            "status": "starting",
            "start_time": datetime.now(),
            "options": scan_request.scan_options
        }
        
        active_scans[scan_id] = scan_info
        
        # Démarrer le scan en arrière-plan
        background_tasks.add_task(
            execute_iot_scan,
            scan_id,
            scan_request.dict()
        )
        
        return {
            "scan_id": scan_id,
            "status": "started",
            "message": f"Scan IoT démarré ({scan_request.scan_type})",
            "target": scan_request.target.ip_range or f"{len(scan_request.target.specific_devices)} dispositifs spécifiques",
            "protocols": scan_request.protocols,
            "estimated_duration": "2-10 minutes",
            "check_status_url": f"/api/iot-security/scan/{scan_id}/status"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors du démarrage du scan: {str(e)}"
        )

@router.get("/scan/{scan_id}/status")
async def get_scan_status(scan_id: str):
    """Récupère le statut d'un scan"""
    
    # Vérifier dans les scans actifs
    if scan_id in active_scans:
        scan_info = active_scans[scan_id]
        duration = (datetime.now() - scan_info["start_time"]).total_seconds()
        
        return {
            "scan_id": scan_id,
            "status": scan_info["status"],
            "scan_type": scan_info["scan_type"],
            "target": scan_info["target"],
            "duration": round(duration, 2),
            "progress": _estimate_progress(scan_info["status"], duration),
            "message": _get_status_message(scan_info["status"])
        }
    
    # Vérifier dans les scans terminés
    elif scan_id in completed_scans:
        scan_result = completed_scans[scan_id]
        
        return {
            "scan_id": scan_id,
            "status": scan_result.status,
            "scan_type": scan_result.scan_type,
            "target_range": scan_result.target_range,
            "duration": scan_result.duration,
            "progress": 100,
            "devices_discovered": scan_result.total_devices,
            "vulnerabilities_found": len(scan_result.vulnerabilities),
            "vulnerable_devices": scan_result.vulnerable_devices,
            "critical_vulnerabilities": scan_result.critical_vulnerabilities,
            "protocols_detected": scan_result.protocols_detected
        }
    
    else:
        raise HTTPException(status_code=404, detail="Scan non trouvé")

@router.get("/scan/{scan_id}/devices")
async def get_scan_devices(
    scan_id: str, 
    device_type: Optional[str] = None,
    protocol: Optional[str] = None,
    page: int = 1, 
    page_size: int = 20
):
    """Récupère les dispositifs découverts lors d'un scan"""
    
    if scan_id not in completed_scans:
        if scan_id in active_scans:
            raise HTTPException(status_code=202, detail="Scan en cours, dispositifs pas encore disponibles")
        else:
            raise HTTPException(status_code=404, detail="Scan non trouvé")
    
    scan_result = completed_scans[scan_id]
    devices = scan_result.devices_discovered
    
    # Filtres
    if device_type:
        devices = [d for d in devices if d.device_type == device_type]
    
    if protocol:
        devices = [d for d in devices if protocol in d.protocols]
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_devices = devices[start_idx:end_idx]
    
    return {
        "scan_id": scan_id,
        "devices": [device.dict() for device in paginated_devices],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_devices": len(devices),
            "total_pages": (len(devices) + page_size - 1) // page_size
        },
        "filters_applied": {
            "device_type": device_type,
            "protocol": protocol
        }
    }

@router.get("/scan/{scan_id}/vulnerabilities")
async def get_scan_vulnerabilities(
    scan_id: str,
    severity: Optional[str] = None,
    device_type: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
):
    """Récupère les vulnérabilités trouvées lors d'un scan"""
    
    if scan_id not in completed_scans:
        if scan_id in active_scans:
            raise HTTPException(status_code=202, detail="Scan en cours, vulnérabilités pas encore disponibles")
        else:
            raise HTTPException(status_code=404, detail="Scan non trouvé")
    
    scan_result = completed_scans[scan_id]
    vulnerabilities = scan_result.vulnerabilities
    
    # Filtres
    if severity:
        vulnerabilities = [v for v in vulnerabilities if v.severity == severity]
    
    if device_type:
        # Filtrer par type de dispositif (nécessite de joindre avec les devices)
        device_ids_by_type = [
            d.id for d in scan_result.devices_discovered 
            if d.device_type == device_type
        ]
        vulnerabilities = [v for v in vulnerabilities if v.device_id in device_ids_by_type]
    
    # Trier par sévérité
    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    vulnerabilities.sort(
        key=lambda x: (severity_order.get(x.severity, 0), x.detected_at), 
        reverse=True
    )
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_vulns = vulnerabilities[start_idx:end_idx]
    
    return {
        "scan_id": scan_id,
        "vulnerabilities": [vuln.dict() for vuln in paginated_vulns],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_vulnerabilities": len(vulnerabilities),
            "total_pages": (len(vulnerabilities) + page_size - 1) // page_size
        },
        "summary": {
            "critical": len([v for v in vulnerabilities if v.severity == "critical"]),
            "high": len([v for v in vulnerabilities if v.severity == "high"]),
            "medium": len([v for v in vulnerabilities if v.severity == "medium"]),
            "low": len([v for v in vulnerabilities if v.severity == "low"])
        }
    }

@router.get("/scans")
async def list_scans(
    scan_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Liste les scans IoT avec filtres"""
    
    all_scans = []
    
    # Ajouter les scans actifs
    for scan_id, scan_info in active_scans.items():
        scan_data = {
            "scan_id": scan_id, 
            "scan_type": scan_info["scan_type"],
            "status": scan_info["status"],
            "start_time": scan_info["start_time"],
            "target": scan_info["target"],
            "duration": (datetime.now() - scan_info["start_time"]).total_seconds()
        }
        all_scans.append(scan_data)
    
    # Ajouter les scans terminés
    for scan_id, scan_result in completed_scans.items():
        scan_data = {
            "scan_id": scan_id,
            "scan_type": scan_result.scan_type,
            "status": scan_result.status,
            "start_time": scan_result.started_at,
            "target_range": scan_result.target_range,
            "duration": scan_result.duration,
            "devices_discovered": scan_result.total_devices,
            "vulnerabilities_found": len(scan_result.vulnerabilities)
        }
        all_scans.append(scan_data)
    
    # Filtres
    if scan_type:
        all_scans = [s for s in all_scans if s["scan_type"] == scan_type]
    
    if status:
        all_scans = [s for s in all_scans if s["status"] == status]
    
    # Trier par date de début (plus récent en premier)
    all_scans.sort(key=lambda x: x["start_time"], reverse=True)
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_scans = all_scans[start_idx:end_idx]
    
    return {
        "scans": paginated_scans,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_scans": len(all_scans),
            "total_pages": (len(all_scans) + page_size - 1) // page_size
        },
        "filters_applied": {
            "scan_type": scan_type,
            "status": status  
        },
        "summary": {
            "active_scans": len(active_scans),
            "completed_scans": len(completed_scans)
        }
    }

@router.get("/devices")
async def list_all_devices(
    device_type: Optional[str] = None,
    protocol: Optional[str] = None,
    manufacturer: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Liste tous les dispositifs découverts"""
    
    all_devices = []
    
    # Collecter tous les dispositifs des scans terminés
    for scan_result in completed_scans.values():
        for device in scan_result.devices_discovered:
            device_dict = device.dict()
            device_dict["scan_id"] = scan_result.id
            all_devices.append(device_dict)
    
    # Filtres
    if device_type:
        all_devices = [d for d in all_devices if d["device_type"] == device_type]
    
    if protocol:
        all_devices = [d for d in all_devices if protocol in d["protocols"]]
    
    if manufacturer:
        all_devices = [d for d in all_devices if d.get("manufacturer") == manufacturer]
    
    # Trier par date de découverte (plus récent en premier)
    all_devices.sort(key=lambda x: x["discovered_at"], reverse=True)
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_devices = all_devices[start_idx:end_idx]
    
    return {
        "devices": paginated_devices,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_devices": len(all_devices),
            "total_pages": (len(all_devices) + page_size - 1) // page_size
        },
        "filters_applied": {
            "device_type": device_type,
            "protocol": protocol,
            "manufacturer": manufacturer
        }
    }

@router.get("/stats")
async def get_iot_security_stats():
    """Statistiques détaillées IoT Security"""
    
    if not completed_scans:
        return {
            "total_scans": 0,
            "total_devices": 0,
            "device_types": {},
            "protocols": {},
            "vulnerabilities": {}
        }
    
    # Stats générales
    total_devices = sum(scan.total_devices for scan in completed_scans.values())
    total_vulnerabilities = sum(len(scan.vulnerabilities) for scan in completed_scans.values())
    
    # Stats par type de dispositif
    device_types = {}
    protocols_stats = {}
    vulnerability_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for scan in completed_scans.values():
        # Types de dispositifs
        for device in scan.devices_discovered:
            device_types[device.device_type] = device_types.get(device.device_type, 0) + 1
        
        # Protocoles
        for protocol, count in scan.protocols_detected.items():
            protocols_stats[protocol] = protocols_stats.get(protocol, 0) + count
        
        # Vulnérabilités par sévérité
        for vuln in scan.vulnerabilities:
            vulnerability_stats[vuln.severity] = vulnerability_stats.get(vuln.severity, 0) + 1
    
    return {
        "total_scans": len(completed_scans),
        "total_devices": total_devices,
        "total_vulnerabilities": total_vulnerabilities,
        "device_types": device_types,
        "protocols": protocols_stats,
        "vulnerabilities": vulnerability_stats,
        "security_score": round(
            max(0, 100 - (total_vulnerabilities / max(1, total_devices) * 10)), 1
        ) if total_devices > 0 else 100
    }

@router.delete("/scan/{scan_id}")
async def delete_scan(scan_id: str):
    """Supprime un scan et ses résultats"""
    
    deleted = False
    
    if scan_id in active_scans:
        del active_scans[scan_id]
        deleted = True
    
    if scan_id in completed_scans:
        del completed_scans[scan_id]
        deleted = True
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan non trouvé")
    
    return {"message": f"Scan {scan_id} supprimé avec succès"}

# Fonctions utilitaires

async def execute_iot_scan(scan_id: str, scan_request: Dict[str, Any]):
    """Exécute le scan IoT en arrière-plan"""
    
    try:
        # Mettre à jour le statut
        active_scans[scan_id]["status"] = "running"
        
        # Exécuter le scan
        scanner = IoTSecurityScanner()
        result = await scanner.scan_iot_devices(scan_request)
        
        # Mettre à jour l'ID du résultat
        result.id = scan_id
        
        # Déplacer vers les scans terminés
        completed_scans[scan_id] = result  
        del active_scans[scan_id]
        
        # Sauvegarder en base de données si possible
        try:
            db = await get_database()
            await db.save_scan_result(result.dict())
        except:
            pass  # Continuer même si la sauvegarde échoue
            
    except Exception as e:
        # Marquer le scan comme échoué
        active_scans[scan_id]["status"] = "failed"
        active_scans[scan_id]["error"] = str(e)
        print(f"Erreur lors du scan {scan_id}: {e}")

def _estimate_progress(status: str, duration: float) -> int:
    """Estime le pourcentage de progression"""
    if status == "starting":
        return 5
    elif status == "running":
        # Progression basée sur le temps (estimation 5 minutes max)
        return min(95, 10 + int((duration / 300) * 85))
    elif status == "completed":
        return 100
    elif status == "failed":
        return 0
    else:
        return 0

def _get_status_message(status: str) -> str:
    """Messages de statut conviviaux"""
    messages = {
        "starting": "Initialisation du scan IoT...",
        "running": "Scan en cours - Découverte des dispositifs...",
        "completed": "Scan terminé avec succès",
        "failed": "Erreur lors du scan"
    }
    return messages.get(status, "Statut inconnu")