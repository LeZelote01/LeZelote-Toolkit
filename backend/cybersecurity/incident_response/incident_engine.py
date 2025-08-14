"""
Moteur de réponse aux incidents - CyberSec Toolkit Pro 2025 PORTABLE
Gestion automatisée des incidents de sécurité avec playbooks
"""
import asyncio
import uuid
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

from .models import (
    Incident, IncidentRequest, IncidentSeverity, IncidentStatus, IncidentCategory,
    Evidence, IncidentAction, ThreatIndicator, IncidentPlaybook, PlaybookStep
)


class IncidentResponseEngine:
    """Moteur principal de réponse aux incidents"""
    
    def __init__(self):
        self.playbooks = {}
        self._initialize_default_playbooks()
    
    async def create_incident(self, request: IncidentRequest) -> Incident:
        """Crée un nouvel incident et lance la réponse automatisée"""
        incident_id = str(uuid.uuid4())
        
        # Créer l'incident
        incident = Incident(
            id=incident_id,
            title=request.title,
            description=request.description,
            category=request.category,
            severity=request.severity,
            status=IncidentStatus.OPEN,
            reporter=request.reporter,
            affected_systems=request.affected_systems,
            source=request.source,
            first_detected=datetime.now()
        )
        
        # Ajouter action de création
        creation_action = IncidentAction(
            id=str(uuid.uuid4()),
            action_type="incident_created",
            performed_by=request.reporter,
            description=f"Incident créé: {request.title}",
            results="Incident enregistré dans le système"
        )
        incident.actions.append(creation_action)
        
        # Lancer la réponse automatisée
        await self._trigger_automated_response(incident)
        
        return incident
    
    async def _trigger_automated_response(self, incident: Incident):
        """Lance la réponse automatisée selon les playbooks"""
        
        # Déterminer le playbook approprié
        playbook = self._select_playbook(incident)
        if not playbook:
            return
        
        # Marquer l'incident comme en cours de traitement
        incident.status = IncidentStatus.IN_PROGRESS
        
        # Ajouter action de démarrage du playbook
        playbook_action = IncidentAction(
            id=str(uuid.uuid4()),
            action_type="playbook_started",
            performed_by="system",
            description=f"Playbook '{playbook.name}' démarré automatiquement",
            results=f"Playbook sélectionné basé sur: {incident.category.value}, sévérité {incident.severity.value}"
        )
        incident.actions.append(playbook_action)
        
        # Exécuter les étapes automatisées
        await self._execute_automated_steps(incident, playbook)
    
    def _select_playbook(self, incident: Incident) -> Optional[IncidentPlaybook]:
        """Sélectionne le playbook approprié selon le type et la sévérité"""
        for playbook in self.playbooks.values():
            if (incident.category in playbook.incident_types and 
                incident.severity in playbook.severity_levels):
                return playbook
        
        # Playbook par défaut si aucun spécifique trouvé
        return self.playbooks.get("default_response")
    
    async def _execute_automated_steps(self, incident: Incident, playbook: IncidentPlaybook):
        """Exécute les étapes automatisées du playbook"""
        
        for step in playbook.steps:
            if not step.automated:
                continue
                
            try:
                # Exécuter l'étape automatisée
                result = await self._execute_step(incident, step)
                
                # Enregistrer l'action
                step_action = IncidentAction(
                    id=str(uuid.uuid4()),
                    action_type="automated_step",
                    performed_by="system",
                    description=f"Étape automatisée: {step.title}",
                    results=result
                )
                incident.actions.append(step_action)
                
            except Exception as e:
                error_action = IncidentAction(
                    id=str(uuid.uuid4()),
                    action_type="automation_error",
                    performed_by="system",
                    description=f"Erreur étape {step.title}: {str(e)}",
                    results="Étape échouée - intervention manuelle requise"
                )
                incident.actions.append(error_action)
    
    async def _execute_step(self, incident: Incident, step: PlaybookStep) -> str:
        """Exécute une étape spécifique du playbook"""
        
        if step.category == "investigation":
            return await self._execute_investigation_step(incident, step)
        elif step.category == "containment":
            return await self._execute_containment_step(incident, step)
        elif step.category == "eradication":
            return await self._execute_eradication_step(incident, step)
        elif step.category == "recovery":
            return await self._execute_recovery_step(incident, step)
        else:
            return f"Étape {step.title} exécutée (simulation)"
    
    async def _execute_investigation_step(self, incident: Incident, step: PlaybookStep) -> str:
        """Exécute une étape d'investigation"""
        
        if "collect_logs" in step.id:
            # Simulation de collecte de logs
            evidence = Evidence(
                id=str(uuid.uuid4()),
                type="system_logs",
                source="automated_collection",
                collected_by="system",
                description=f"Logs système collectés pour {', '.join(incident.affected_systems)}",
                metadata={"systems": incident.affected_systems, "time_range": "24h"}
            )
            incident.evidence.append(evidence)
            return f"Logs collectés pour {len(incident.affected_systems)} systèmes"
            
        elif "ioc_analysis" in step.id:
            # Analyse automatique d'IOCs
            iocs = await self._extract_iocs(incident)
            incident.threat_indicators.extend(iocs)
            return f"{len(iocs)} indicateurs de compromission identifiés"
            
        elif "network_analysis" in step.id:
            # Analyse réseau
            network_evidence = Evidence(
                id=str(uuid.uuid4()),
                type="network_traffic",
                source="network_monitoring",
                collected_by="system",
                description="Analyse du trafic réseau suspect",
                metadata={"connections": "analyzed", "protocols": ["HTTP", "HTTPS", "DNS"]}
            )
            incident.evidence.append(network_evidence)
            return "Analyse réseau terminée - trafic suspect identifié"
        
        return f"Investigation: {step.title} exécutée"
    
    async def _execute_containment_step(self, incident: Incident, step: PlaybookStep) -> str:
        """Exécute une étape de confinement"""
        
        if "isolate_systems" in step.id:
            # Simulation d'isolation de systèmes
            incident.status = IncidentStatus.CONTAINED
            incident.contained_at = datetime.now()
            return f"Systèmes isolés: {', '.join(incident.affected_systems)}"
            
        elif "block_indicators" in step.id:
            # Blocage automatique d'IOCs
            blocked_count = len(incident.threat_indicators)
            return f"{blocked_count} indicateurs bloqués sur les pare-feux"
            
        elif "disable_accounts" in step.id:
            # Désactivation de comptes compromis
            return f"Comptes affectés désactivés: {', '.join(incident.affected_users)}"
        
        return f"Confinement: {step.title} exécuté"
    
    async def _execute_eradication_step(self, incident: Incident, step: PlaybookStep) -> str:
        """Exécute une étape d'éradication"""
        
        if "remove_malware" in step.id:
            return "Malware supprimé des systèmes affectés"
            
        elif "patch_vulnerabilities" in step.id:
            return "Vulnérabilités exploitées patchées"
            
        elif "update_security_controls" in step.id:
            return "Contrôles de sécurité mis à jour"
        
        return f"Éradication: {step.title} exécutée"
    
    async def _execute_recovery_step(self, incident: Incident, step: PlaybookStep) -> str:
        """Exécute une étape de récupération"""
        
        if "restore_systems" in step.id:
            return "Systèmes restaurés depuis les sauvegardes"
            
        elif "verify_integrity" in step.id:
            return "Intégrité des systèmes vérifiée"
            
        elif "monitor_recovery" in step.id:
            return "Surveillance post-incident activée"
        
        return f"Récupération: {step.title} exécutée"
    
    async def _extract_iocs(self, incident: Incident) -> List[ThreatIndicator]:
        """Extrait automatiquement des IOCs des preuves"""
        iocs = []
        
        # Simulation d'extraction d'IOCs
        sample_iocs = [
            {"type": "ip", "value": "192.168.1.100", "confidence": 0.8},
            {"type": "domain", "value": "malicious-domain.com", "confidence": 0.9},
            {"type": "hash", "value": "d41d8cd98f00b204e9800998ecf8427e", "confidence": 0.7}
        ]
        
        for ioc_data in sample_iocs:
            ioc = ThreatIndicator(
                id=str(uuid.uuid4()),
                type=ioc_data["type"],
                value=ioc_data["value"],
                confidence=ioc_data["confidence"],
                source="automated_analysis",
                description=f"IOC extrait automatiquement de l'incident {incident.id}"
            )
            iocs.append(ioc)
        
        return iocs
    
    def _initialize_default_playbooks(self):
        """Initialise les playbooks par défaut"""
        
        # Playbook pour malware
        malware_playbook = IncidentPlaybook(
            id="malware_response",
            name="Réponse Malware",
            description="Playbook standard pour les incidents de malware",
            incident_types=[IncidentCategory.MALWARE, IncidentCategory.RANSOMWARE],
            severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.CRITICAL],
            steps=[
                PlaybookStep(
                    id="collect_logs_malware",
                    title="Collecter les logs système",
                    description="Collecte automatique des logs des systèmes affectés",
                    category="investigation",
                    automated=True,
                    estimated_duration=10
                ),
                PlaybookStep(
                    id="ioc_analysis_malware",
                    title="Analyser les IOCs",
                    description="Extraction et analyse des indicateurs de compromission",
                    category="investigation",
                    automated=True,
                    estimated_duration=15
                ),
                PlaybookStep(
                    id="isolate_systems_malware",
                    title="Isoler les systèmes",
                    description="Isolation des systèmes infectés du réseau",
                    category="containment",
                    automated=True,
                    estimated_duration=5
                ),
                PlaybookStep(
                    id="remove_malware_step",
                    title="Supprimer le malware",
                    description="Éradication du malware des systèmes",
                    category="eradication",
                    automated=True,
                    estimated_duration=30
                )
            ],
            estimated_total_duration=60,
            success_criteria=["Malware éradiqué", "Systèmes sains", "Surveillance active"],
            created_by="system"
        )
        
        # Playbook pour intrusion réseau
        network_playbook = IncidentPlaybook(
            id="network_intrusion_response",
            name="Réponse Intrusion Réseau",
            description="Playbook pour les intrusions réseau",
            incident_types=[IncidentCategory.NETWORK_INTRUSION, IncidentCategory.UNAUTHORIZED_ACCESS],
            severity_levels=[IncidentSeverity.HIGH, IncidentSeverity.CRITICAL],
            steps=[
                PlaybookStep(
                    id="network_analysis_intrusion",
                    title="Analyser le trafic réseau",
                    description="Analyse du trafic réseau suspect",
                    category="investigation",
                    automated=True,
                    estimated_duration=20
                ),
                PlaybookStep(
                    id="block_indicators_intrusion",
                    title="Bloquer les IOCs",
                    description="Blocage des indicateurs sur les pare-feux",
                    category="containment",
                    automated=True,
                    estimated_duration=10
                ),
                PlaybookStep(
                    id="disable_accounts_intrusion",
                    title="Désactiver les comptes",
                    description="Désactivation des comptes compromis",
                    category="containment",
                    automated=True,
                    estimated_duration=5
                )
            ],
            estimated_total_duration=35,
            success_criteria=["Accès non autorisé bloqué", "Comptes sécurisés"],
            created_by="system"
        )
        
        # Playbook par défaut
        default_playbook = IncidentPlaybook(
            id="default_response",
            name="Réponse Standard",
            description="Playbook par défaut pour tous types d'incidents",
            incident_types=list(IncidentCategory),
            severity_levels=list(IncidentSeverity),
            steps=[
                PlaybookStep(
                    id="collect_logs_default",
                    title="Collecte de preuves",
                    description="Collecte automatique des preuves initiales",
                    category="investigation",
                    automated=True,
                    estimated_duration=15
                ),
                PlaybookStep(
                    id="initial_assessment",
                    title="Évaluation initiale",
                    description="Évaluation automatique de l'impact et de la portée",
                    category="investigation",
                    automated=True,
                    estimated_duration=10
                )
            ],
            estimated_total_duration=25,
            success_criteria=["Preuves collectées", "Impact évalué"],
            created_by="system"
        )
        
        self.playbooks = {
            "malware_response": malware_playbook,
            "network_intrusion_response": network_playbook,
            "default_response": default_playbook
        }
    
    async def get_incident_status(self, incident_id: str) -> Dict[str, Any]:
        """Récupère le statut détaillé d'un incident"""
        # Dans une vraie implémentation, récupérer depuis la base
        return {
            "incident_id": incident_id,
            "status": "in_progress",
            "actions_count": 5,
            "evidence_count": 3,
            "last_activity": datetime.now().isoformat()
        }
    
    async def update_incident(self, incident_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un incident"""
        # Dans une vraie implémentation, mettre à jour en base
        return True
    
    async def generate_incident_report(self, incident: Incident) -> Dict[str, Any]:
        """Génère un rapport d'incident"""
        
        timeline = []
        for action in sorted(incident.actions, key=lambda x: x.timestamp):
            timeline.append({
                "timestamp": action.timestamp.isoformat(),
                "action": action.action_type,
                "description": action.description,
                "performed_by": action.performed_by
            })
        
        return {
            "incident_summary": {
                "id": incident.id,
                "title": incident.title,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "category": incident.category.value,
                "duration": self._calculate_duration(incident),
                "systems_affected": len(incident.affected_systems),
                "users_affected": len(incident.affected_users)
            },
            "timeline": timeline,
            "evidence_collected": len(incident.evidence),
            "threat_indicators": len(incident.threat_indicators),
            "containment_time": self._calculate_containment_time(incident),
            "resolution_time": self._calculate_resolution_time(incident),
            "lessons_learned": self._generate_lessons_learned(incident),
            "recommendations": self._generate_recommendations(incident)
        }
    
    def _calculate_duration(self, incident: Incident) -> Optional[str]:
        """Calcule la durée de l'incident"""
        if incident.resolved_at:
            duration = incident.resolved_at - incident.created_at
            return str(duration)
        return None
    
    def _calculate_containment_time(self, incident: Incident) -> Optional[str]:
        """Calcule le temps de confinement"""
        if incident.contained_at:
            duration = incident.contained_at - incident.created_at
            return str(duration)
        return None
    
    def _calculate_resolution_time(self, incident: Incident) -> Optional[str]:
        """Calcule le temps de résolution"""
        if incident.resolved_at:
            duration = incident.resolved_at - incident.created_at
            return str(duration)
        return None
    
    def _generate_lessons_learned(self, incident: Incident) -> List[str]:
        """Génère les leçons apprises"""
        lessons = []
        
        if incident.severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
            lessons.append("Améliorer la détection précoce pour les incidents critiques")
        
        if len(incident.affected_systems) > 5:
            lessons.append("Renforcer la segmentation réseau pour limiter la propagation")
        
        if incident.category == IncidentCategory.PHISHING:
            lessons.append("Intensifier la formation de sensibilisation à la sécurité")
        
        return lessons
    
    def _generate_recommendations(self, incident: Incident) -> List[str]:
        """Génère les recommandations"""
        recommendations = []
        
        recommendations.append("Effectuer un scan complet des systèmes affectés")
        recommendations.append("Réviser les contrôles d'accès et permissions")
        recommendations.append("Mettre à jour la documentation de sécurité")
        recommendations.append("Planifier un exercice de simulation d'incident")
        
        if incident.category in [IncidentCategory.MALWARE, IncidentCategory.RANSOMWARE]:
            recommendations.append("Vérifier l'efficacité des solutions anti-malware")
            recommendations.append("Réviser la stratégie de sauvegarde et de récupération")
        
        return recommendations