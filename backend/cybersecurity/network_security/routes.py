"""
Network Security Routes
API endpoints pour la sécurité réseau
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from .models import (
    NetworkScanRequest, NetworkScanResult, NetworkVulnerability,
    NetworkSecurityStatus, NetworkSecurityMetrics, NetworkTopology,
    ScanType, Severity
)
from .scanner import NetworkSecurityScanner
from database import get_database

router = APIRouter(prefix="/api/network-security", tags=["Network Security"])

# Cache des scans et métriques
active_scans: Dict[str, Dict] = {}
completed_scans: Dict[str, NetworkScanResult] = {}
network_topologies: Dict[str, NetworkTopology] = {}
# metrics_storage = NetworkSecurityMetrics()  # Commenté pour éviter les erreurs d'initialisation

@router.get("/")
async def network_security_status():
    """Status du service Network Security"""
    
    # Calculer les métriques actuelles
    active_scans_count = len([s for s in active_scans.values() if s.get("status") in ["pending", "running"]])
    completed_scans_count = len(completed_scans)
    
    # Stats par type de scan
    scan_type_stats = {}
    for scan in completed_scans.values():
        scan_type = scan.scan_type.value
        scan_type_stats[scan_type] = scan_type_stats.get(scan_type, 0) + 1
    
    # Stats par sévérité de vulnérabilités
    severity_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for scan in completed_scans.values():
        for vuln in scan.vulnerabilities:
            severity_stats[vuln.severity.value] = severity_stats.get(vuln.severity.value, 0) + 1
    
    # Stats des services détectés
    top_services = {}
    for scan in completed_scans.values():
        for service, count in scan.services_detected.items():
            top_services[service] = top_services.get(service, 0) + count
    
    # Stats des OS détectés
    top_os = {}
    for scan in completed_scans.values():
        for os_name, count in scan.os_detected.items():
            top_os[os_name] = top_os.get(os_name, 0) + count
    
    # Calculer les totaux
    total_hosts_scanned = sum(scan.total_hosts for scan in completed_scans.values())
    total_ports_scanned = sum(scan.total_ports_scanned for scan in completed_scans.values())
    total_vulnerabilities = sum(len(scan.vulnerabilities) for scan in completed_scans.values())
    
    # Vérifier la disponibilité de Nmap
    scanner = NetworkSecurityScanner()
    
    return {
        "status": "operational",
        "service": "Network Security",
        "version": "1.0.0-portable",
        "features": {
            "nmap_integration": scanner.nmap_available,
            "port_scanning": True,
            "service_detection": True,
            "os_detection": True,
            "vulnerability_detection": True,
            "topology_mapping": True,
            "stealth_scanning": True,
            "udp_scanning": True,
            "script_scanning": True
        },
        "supported_scan_types": [
            "port_scan", "host_discovery", "service_detection", 
            "os_detection", "vulnerability_scan", "full_scan",
            "stealth_scan", "udp_scan"
        ],
        "nmap_available": scanner.nmap_available,
        "active_scans": active_scans_count,
        "completed_scans": completed_scans_count,
        "scan_type_stats": scan_type_stats,
        "severity_stats": severity_stats,
        "total_hosts_scanned": total_hosts_scanned,
        "total_ports_scanned": total_ports_scanned,
        "total_vulnerabilities": total_vulnerabilities,
        "top_services": dict(sorted(top_services.items(), key=lambda x: x[1], reverse=True)[:10]),
        "top_os": dict(sorted(top_os.items(), key=lambda x: x[1], reverse=True)[:10])
    }

@router.post("/scan")
async def start_network_scan(scan_request: NetworkScanRequest, background_tasks: BackgroundTasks):
    """Lance un scan réseau"""
    try:
        # Générer un ID unique pour le scan
        scan_id = str(uuid.uuid4())
        
        # Valider les paramètres
        if not scan_request.target.ip_range and not scan_request.target.specific_hosts:
            raise HTTPException(
                status_code=400,
                detail="Au moins une cible (ip_range ou specific_hosts) est requise"
            )
        
        # Initialiser le scan
        scan_info = {
            "scan_id": scan_id,
            "scan_type": scan_request.scan_type,
            "target": scan_request.target.dict(),
            "status": "starting",
            "start_time": datetime.now(),
            "options": scan_request.scan_options.dict()
        }
        
        active_scans[scan_id] = scan_info
        
        # Démarrer le scan en arrière-plan
        background_tasks.add_task(
            execute_network_scan,
            scan_id,
            scan_request.dict()
        )
        
        return {
            "scan_id": scan_id,
            "status": "started",
            "message": f"Scan réseau démarré ({scan_request.scan_type})",
            "target": scan_request.target.ip_range or f"{len(scan_request.target.specific_hosts)} hôtes spécifiques",
            "scan_type": scan_request.scan_type,
            "estimated_duration": _estimate_scan_duration(scan_request),
            "check_status_url": f"/api/network-security/scan/{scan_id}/status"
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
            "progress": _estimate_scan_progress(scan_info["status"], duration, scan_info["scan_type"]),
            "message": _get_scan_status_message(scan_info["status"])
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
            "hosts_discovered": scan_result.total_hosts,
            "hosts_up": scan_result.hosts_up,
            "hosts_down": scan_result.hosts_down,
            "ports_scanned": scan_result.total_ports_scanned,
            "open_ports": scan_result.open_ports,
            "vulnerabilities_found": len(scan_result.vulnerabilities),
            "critical_vulnerabilities": scan_result.critical_vulnerabilities,
            "high_vulnerabilities": scan_result.high_vulnerabilities
        }
    
    else:
        raise HTTPException(status_code=404, detail="Scan non trouvé")

@router.get("/scan/{scan_id}/hosts")
async def get_scan_hosts(
    scan_id: str,
    state: Optional[str] = None,
    os_family: Optional[str] = None,
    service: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Récupère les hôtes découverts lors d'un scan"""
    
    if scan_id not in completed_scans:
        if scan_id in active_scans:
            raise HTTPException(status_code=202, detail="Scan en cours, hôtes pas encore disponibles")
        else:
            raise HTTPException(status_code=404, detail="Scan non trouvé")
    
    scan_result = completed_scans[scan_id]
    hosts = scan_result.hosts_discovered
    
    # Filtres
    if state:
        hosts = [h for h in hosts if h.state == state]
    
    if os_family:
        hosts = [h for h in hosts if any(os_family.lower() in os_match.get("name", "").lower() 
                                        for os_match in h.os_matches)]
    
    if service:
        hosts = [h for h in hosts if any(service.lower() in (port.service or "").lower() 
                                        for port in h.ports)]
    
    # Pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_hosts = hosts[start_idx:end_idx]
    
    return {
        "scan_id": scan_id,
        "hosts": [host.dict() for host in paginated_hosts],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_hosts": len(hosts),
            "total_pages": (len(hosts) + page_size - 1) // page_size
        },
        "filters_applied": {
            "state": state,
            "os_family": os_family,
            "service": service
        }
    }

@router.get("/scan/{scan_id}/vulnerabilities")
async def get_scan_vulnerabilities(
    scan_id: str,
    severity: Optional[str] = None,
    host_ip: Optional[str] = None,
    category: Optional[str] = None,
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
        vulnerabilities = [v for v in vulnerabilities if v.severity.value == severity]
    
    if host_ip:
        vulnerabilities = [v for v in vulnerabilities if v.host_ip == host_ip]
    
    if category:
        vulnerabilities = [v for v in vulnerabilities if v.category == category]
    
    # Trier par sévérité et confidence
    severity_order = {"critical": 5, "high": 4, "medium": 3, "low": 2, "info": 1}
    vulnerabilities.sort(
        key=lambda x: (severity_order.get(x.severity.value, 0), x.confidence),
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
            "critical": len([v for v in vulnerabilities if v.severity == Severity.CRITICAL]),
            "high": len([v for v in vulnerabilities if v.severity == Severity.HIGH]),
            "medium": len([v for v in vulnerabilities if v.severity == Severity.MEDIUM]),
            "low": len([v for v in vulnerabilities if v.severity == Severity.LOW]),
            "info": len([v for v in vulnerabilities if v.severity == Severity.INFO])
        },
        "filters_applied": {
            "severity": severity,
            "host_ip": host_ip,
            "category": category
        }
    }

@router.get("/scan/{scan_id}/services")
async def get_scan_services(scan_id: str):
    """Récupère les services détectés lors d'un scan"""
    
    if scan_id not in completed_scans:
        if scan_id in active_scans:
            raise HTTPException(status_code=202, detail="Scan en cours, services pas encore disponibles")
        else:
            raise HTTPException(status_code=404, detail="Scan non trouvé")
    
    scan_result = completed_scans[scan_id]
    
    # Construire la liste détaillée des services
    services_detail = []
    for host in scan_result.hosts_discovered:
        for service in host.services:
            services_detail.append({
                "host_ip": host.ip,
                "hostname": host.hostname,
                "service_name": service.name,
                "port": service.port,
                "protocol": service.protocol,
                "state": service.state,
                "version": service.version,
                "product": service.product,
                "confidence": service.confidence
            })
    
    return {
        "scan_id": scan_id,
        "services_summary": scan_result.services_detected,
        "services_detail": services_detail,
        "total_services": len(services_detail),
        "unique_services": len(scan_result.services_detected)
    }

@router.get("/scan/{scan_id}/topology")
async def get_scan_topology(scan_id: str):
    """Génère la topologie réseau basée sur un scan"""
    
    if scan_id not in completed_scans:
        if scan_id in active_scans:
            raise HTTPException(status_code=202, detail="Scan en cours, topologie pas encore disponible")
        else:
            raise HTTPException(status_code=404, detail="Scan non trouvé")
    
    scan_result = completed_scans[scan_id]
    
    # Générer ou récupérer la topologie
    topology_id = f"topo_{scan_id}"
    if topology_id not in network_topologies:
        scanner = NetworkSecurityScanner()
        topology = scanner.generate_network_topology([scan_result])
        topology.id = topology_id
        network_topologies[topology_id] = topology
    
    topology = network_topologies[topology_id]
    
    return {
        "scan_id": scan_id,
        "topology": topology.dict()
    }

@router.get("/scans")
async def list_scans(
    scan_type: Optional[str] = None,
    status: Optional[str] = None,
    target_filter: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Liste les scans réseau avec filtres"""
    
    all_scans = []
    
    # Ajouter les scans actifs
    for scan_id, scan_info in active_scans.items():
        scan_data = {
            "scan_id": scan_id,
            "scan_type": scan_info["scan_type"].value,
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
            "scan_type": scan_result.scan_type.value,
            "status": scan_result.status,
            "start_time": scan_result.started_at,
            "target_range": scan_result.target_range,
            "duration": scan_result.duration,
            "hosts_discovered": scan_result.total_hosts,
            "hosts_up": scan_result.hosts_up,
            "vulnerabilities_found": len(scan_result.vulnerabilities)
        }
        all_scans.append(scan_data)
    
    # Filtres
    if scan_type:
        all_scans = [s for s in all_scans if s["scan_type"] == scan_type]
    
    if status:
        all_scans = [s for s in all_scans if s["status"] == status]
    
    if target_filter:
        all_scans = [s for s in all_scans if target_filter in str(s.get("target", s.get("target_range", "")))]
    
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
            "status": status,
            "target_filter": target_filter
        },
        "summary": {
            "active_scans": len(active_scans),
            "completed_scans": len(completed_scans)
        }
    }

@router.get("/stats")
async def get_network_security_stats():
    """Statistiques détaillées Network Security"""
    
    if not completed_scans:
        return {
            "total_scans": 0,
            "total_hosts": 0,
            "total_ports": 0,
            "scan_types": {},
            "services": {},
            "os_systems": {},
            "vulnerabilities": {}
        }
    
    # Stats générales
    total_hosts = sum(scan.total_hosts for scan in completed_scans.values())
    total_ports = sum(scan.total_ports_scanned for scan in completed_scans.values())
    total_vulnerabilities = sum(len(scan.vulnerabilities) for scan in completed_scans.values())
    
    # Stats par type de scan
    scan_types_stats = {}
    services_stats = {}
    os_stats = {}
    vulnerability_stats = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    
    for scan in completed_scans.values():
        # Types de scans
        scan_types_stats[scan.scan_type.value] = scan_types_stats.get(scan.scan_type.value, 0) + 1
        
        # Services
        for service, count in scan.services_detected.items():
            services_stats[service] = services_stats.get(service, 0) + count
        
        # OS
        for os_name, count in scan.os_detected.items():
            os_stats[os_name] = os_stats.get(os_name, 0) + count
        
        # Vulnérabilités par sévérité
        for vuln in scan.vulnerabilities:
            vulnerability_stats[vuln.severity.value] = vulnerability_stats.get(vuln.severity.value, 0) + 1
    
    # Calculs de moyennes
    avg_hosts_per_scan = total_hosts / len(completed_scans) if completed_scans else 0
    avg_ports_per_scan = total_ports / len(completed_scans) if completed_scans else 0
    avg_vulns_per_scan = total_vulnerabilities / len(completed_scans) if completed_scans else 0
    
    return {
        "total_scans": len(completed_scans),
        "total_hosts": total_hosts,
        "total_ports": total_ports,
        "total_vulnerabilities": total_vulnerabilities,
        "scan_types": scan_types_stats,
        "top_services": dict(sorted(services_stats.items(), key=lambda x: x[1], reverse=True)[:15]),
        "top_os": dict(sorted(os_stats.items(), key=lambda x: x[1], reverse=True)[:10]),
        "vulnerabilities": vulnerability_stats,
        "averages": {
            "hosts_per_scan": round(avg_hosts_per_scan, 1),
            "ports_per_scan": round(avg_ports_per_scan, 1),
            "vulnerabilities_per_scan": round(avg_vulns_per_scan, 1)
        },
        "scan_efficiency": {
            "hosts_per_minute": round(total_hosts / max(1, sum(s.duration for s in completed_scans.values()) / 60), 1),
            "ports_per_minute": round(total_ports / max(1, sum(s.duration for s in completed_scans.values()) / 60), 1)
        }
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
    
    # Supprimer la topologie associée si elle existe
    topology_id = f"topo_{scan_id}"
    if topology_id in network_topologies:
        del network_topologies[topology_id]
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan non trouvé")
    
    return {"message": f"Scan {scan_id} supprimé avec succès"}

@router.get("/topologies")
async def list_topologies():
    """Liste les topologies réseau disponibles"""
    
    topologies_list = []
    for topology_id, topology in network_topologies.items():
        topologies_list.append({
            "topology_id": topology_id,
            "name": topology.name,
            "description": topology.description,
            "total_hosts": topology.total_hosts,
            "total_services": topology.total_services,
            "total_vulnerabilities": topology.total_vulnerabilities,
            "created_at": topology.created_at,
            "updated_at": topology.updated_at,
            "scan_ids": topology.scan_ids
        })
    
    return {
        "topologies": topologies_list,
        "total_topologies": len(topologies_list)
    }

# Fonctions utilitaires

async def execute_network_scan(scan_id: str, scan_request: Dict[str, Any]):
    """Exécute le scan réseau en arrière-plan"""
    
    try:
        # Mettre à jour le statut
        active_scans[scan_id]["status"] = "running"
        
        # Exécuter le scan
        scanner = NetworkSecurityScanner()
        result = await scanner.scan_network(scan_request)
        
        # Mettre à jour l'ID du résultat
        result.id = scan_id
        
        # Mettre à jour les IDs des vulnérabilités
        for vuln in result.vulnerabilities:
            vuln.scan_id = scan_id
        
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

def _estimate_scan_duration(request: NetworkScanRequest) -> str:
    """Estime la durée du scan"""
    base_time = 30  # secondes de base
    
    # Facteur selon le type de scan
    type_factors = {
        ScanType.HOST_DISCOVERY: 0.5,
        ScanType.PORT_SCAN: 1.0,
        ScanType.SERVICE_DETECTION: 1.5,
        ScanType.OS_DETECTION: 2.0,
        ScanType.VULNERABILITY_SCAN: 3.0,
        ScanType.FULL_SCAN: 4.0,
        ScanType.STEALTH_SCAN: 2.5,
        ScanType.UDP_SCAN: 3.5
    }
    
    factor = type_factors.get(request.scan_type, 1.0)
    
    # Estimation basée sur les cibles
    if request.target.ip_range:
        if "/24" in request.target.ip_range:
            estimated = base_time * factor * 10  # ~256 IPs
        elif "/16" in request.target.ip_range:
            estimated = base_time * factor * 100  # Beaucoup d'IPs
        else:
            estimated = base_time * factor
    else:
        host_count = len(request.target.specific_hosts) if request.target.specific_hosts else 1
        estimated = base_time * factor * (host_count / 10)
    
    if estimated < 60:
        return f"{int(estimated)} secondes"
    elif estimated < 3600:
        return f"{int(estimated/60)} minutes"
    else:
        return f"{int(estimated/3600)} heures"

def _estimate_scan_progress(status: str, duration: float, scan_type: ScanType) -> int:
    """Estime le pourcentage de progression"""
    if status == "starting":
        return 5
    elif status == "running":
        # Temps estimé selon le type de scan
        estimated_times = {
            ScanType.HOST_DISCOVERY: 60,
            ScanType.PORT_SCAN: 180,
            ScanType.SERVICE_DETECTION: 300,
            ScanType.OS_DETECTION: 420,
            ScanType.VULNERABILITY_SCAN: 900,
            ScanType.FULL_SCAN: 1200,
            ScanType.STEALTH_SCAN: 600,
            ScanType.UDP_SCAN: 800
        }
        
        estimated_duration = estimated_times.get(scan_type, 300)
        progress = min(95, 10 + int((duration / estimated_duration) * 85))
        return progress
    elif status == "completed":
        return 100
    elif status == "failed":
        return 0
    else:
        return 0

def _get_scan_status_message(status: str) -> str:
    """Messages de statut conviviaux"""
    messages = {
        "starting": "Initialisation du scan réseau...",
        "running": "Scan en cours - Découverte des hôtes et services...",
        "completed": "Scan terminé avec succès",
        "failed": "Erreur lors du scan"
    }
    return messages.get(status, "Statut inconnu")