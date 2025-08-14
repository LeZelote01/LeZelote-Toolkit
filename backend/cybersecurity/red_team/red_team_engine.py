"""
Moteur Red Team Operations avec gestion de campagnes et TTPs
CyberSec Toolkit Pro 2025 - PORTABLE
"""
import asyncio
import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from .models import (
    Campaign, Operation, Target, TTPTechnique, RedTeamAsset, PurpleTeamExercise,
    RedTeamReport, CampaignStatus, OperationStatus, AttackPhase, OperationSeverity,
    CreateCampaignRequest, UpdateCampaignRequest, CreateOperationRequest, 
    UpdateOperationRequest, CreateTargetRequest, CreatePurpleTeamExerciseRequest,
    CampaignSearchRequest, OperationSearchRequest, CampaignStatistics,
    OperationStatistics, RedTeamInsight
)

logger = logging.getLogger(__name__)

class RedTeamEngine:
    """Moteur principal Red Team Operations"""
    
    def __init__(self):
        self.campaigns: Dict[str, Campaign] = {}
        self.operations: Dict[str, Operation] = {}
        self.targets: Dict[str, Target] = {}
        self.techniques: Dict[str, TTPTechnique] = {}
        self.assets: Dict[str, RedTeamAsset] = {}
        self.purple_team_exercises: Dict[str, PurpleTeamExercise] = {}
        self.reports: Dict[str, RedTeamReport] = {}
        
        # Status
        self.is_running = False
        self.operation_executor_task = None
        
        # Performance tracking
        self.performance_stats = {
            "start_time": datetime.now(),
            "campaigns_created": 0,
            "operations_executed": 0,
            "purple_team_exercises": 0,
            "reports_generated": 0
        }
        
        # MITRE ATT&CK TTPs de base
        self.mitre_techniques = self._load_mitre_techniques()
        
        # Outils Red Team
        self.red_team_tools = self._load_red_team_tools()
        
        # Templates de campagne
        self.campaign_templates = self._load_campaign_templates()
    
    def _load_mitre_techniques(self) -> Dict[str, TTPTechnique]:
        """Charge les techniques MITRE ATT&CK communes"""
        techniques = {}
        
        # Quelques techniques populaires pour démarrer
        common_techniques = [
            {
                "technique_id": "T1566.001",
                "name": "Spearphishing Attachment",
                "description": "Spearphishing avec pièce jointe malveillante",
                "phase": AttackPhase.INITIAL_ACCESS,
                "platforms": ["Windows", "macOS", "Linux"],
                "difficulty": "medium",
                "stealth_level": "medium",
                "success_rate": 0.7,
                "detection_rate": 0.4
            },
            {
                "technique_id": "T1055",
                "name": "Process Injection",
                "description": "Injection de code dans des processus légitimes",
                "phase": AttackPhase.DEFENSE_EVASION,
                "platforms": ["Windows", "Linux", "macOS"],
                "difficulty": "hard",
                "stealth_level": "high",
                "success_rate": 0.8,
                "detection_rate": 0.3
            },
            {
                "technique_id": "T1082",
                "name": "System Information Discovery",
                "description": "Collecte d'informations système",
                "phase": AttackPhase.DISCOVERY,
                "platforms": ["Windows", "Linux", "macOS"],
                "difficulty": "easy",
                "stealth_level": "low",
                "success_rate": 0.9,
                "detection_rate": 0.6
            },
            {
                "technique_id": "T1071.001",
                "name": "Web Protocols",
                "description": "Communication via protocoles web standards",
                "phase": AttackPhase.COMMAND_AND_CONTROL,
                "platforms": ["Windows", "Linux", "macOS"],
                "difficulty": "medium",
                "stealth_level": "high",
                "success_rate": 0.85,
                "detection_rate": 0.2
            },
            {
                "technique_id": "T1078",
                "name": "Valid Accounts",
                "description": "Utilisation de comptes valides compromis",
                "phase": AttackPhase.PERSISTENCE,
                "platforms": ["Windows", "Linux", "macOS", "Cloud"],
                "difficulty": "medium",
                "stealth_level": "high",
                "success_rate": 0.9,
                "detection_rate": 0.1
            }
        ]
        
        for tech_data in common_techniques:
            technique = TTPTechnique(
                technique_id=tech_data["technique_id"],
                name=tech_data["name"],
                description=tech_data["description"],
                tactic="mitre_attck",
                phase=tech_data["phase"],
                platforms=tech_data["platforms"],
                difficulty=tech_data["difficulty"],
                stealth_level=tech_data["stealth_level"],
                success_rate=tech_data["success_rate"],
                detection_rate=tech_data["detection_rate"]
            )
            techniques[technique.id] = technique
            
        return techniques
    
    def _load_red_team_tools(self) -> Dict[str, Any]:
        """Charge la liste des outils Red Team"""
        return {
            "reconnaissance": [
                "nmap", "masscan", "amass", "recon-ng", "theharvester", 
                "shodan", "censys", "dnsrecon", "gobuster", "dirb"
            ],
            "initial_access": [
                "metasploit", "cobalt_strike", "empire", "covenant", 
                "mythic", "social_engineer_toolkit", "gophish"
            ],
            "execution": [
                "powershell", "cmd", "wmi", "psexec", "winrm", 
                "ssh", "python", "bash", "macro", "rundll32"
            ],
            "persistence": [
                "scheduled_tasks", "services", "registry", "startup_folder",
                "wmi_events", "logon_scripts", "dll_hijacking"
            ],
            "privilege_escalation": [
                "mimikatz", "bloodhound", "powerup", "privesc", 
                "linpeas", "winpeas", "exploit_suggester"
            ],
            "credential_access": [
                "mimikatz", "lazagne", "hashdump", "dcsync", 
                "kerberoasting", "asreproasting", "golden_ticket"
            ],
            "lateral_movement": [
                "psexec", "wmi", "dcom", "rdp", "ssh", 
                "powershell_remoting", "smbexec", "atexec"
            ],
            "command_control": [
                "cobalt_strike", "empire", "covenant", "mythic",
                "dns_tunneling", "http_https", "custom_protocols"
            ]
        }
    
    def _load_campaign_templates(self) -> Dict[str, Any]:
        """Charge les templates de campagne"""
        return {
            "apt_simulation": {
                "name": "APT Simulation Campaign",
                "description": "Simulation d'attaque APT sophistiquée",
                "phases": [
                    AttackPhase.RECONNAISSANCE,
                    AttackPhase.INITIAL_ACCESS,
                    AttackPhase.EXECUTION,
                    AttackPhase.PERSISTENCE,
                    AttackPhase.PRIVILEGE_ESCALATION,
                    AttackPhase.CREDENTIAL_ACCESS,
                    AttackPhase.LATERAL_MOVEMENT,
                    AttackPhase.COLLECTION,
                    AttackPhase.EXFILTRATION
                ],
                "duration_days": 14,
                "techniques": ["T1566.001", "T1055", "T1078", "T1071.001"]
            },
            "ransomware_simulation": {
                "name": "Ransomware Attack Simulation",
                "description": "Simulation d'attaque ransomware",
                "phases": [
                    AttackPhase.INITIAL_ACCESS,
                    AttackPhase.EXECUTION,
                    AttackPhase.PERSISTENCE,
                    AttackPhase.LATERAL_MOVEMENT,
                    AttackPhase.IMPACT
                ],
                "duration_days": 7,
                "techniques": ["T1566.001", "T1055", "T1078"]
            },
            "insider_threat": {
                "name": "Insider Threat Simulation",
                "description": "Simulation de menace interne",
                "phases": [
                    AttackPhase.COLLECTION,
                    AttackPhase.CREDENTIAL_ACCESS,
                    AttackPhase.LATERAL_MOVEMENT,
                    AttackPhase.EXFILTRATION
                ],
                "duration_days": 5,
                "techniques": ["T1078", "T1071.001"]
            }
        }
    
    async def start_engine(self):
        """Démarre le moteur Red Team"""
        if self.is_running:
            return {"status": "already_running"}
        
        self.is_running = True
        
        # Démarrer l'exécuteur d'opérations
        self.operation_executor_task = asyncio.create_task(self._operation_executor_loop())
        
        # Charger techniques MITRE
        self.techniques.update(self.mitre_techniques)
        
        logger.info("🔴 Moteur Red Team démarré")
        
        return {
            "status": "started",
            "message": "Moteur Red Team démarré avec succès",
            "start_time": datetime.now().isoformat(),
            "techniques_loaded": len(self.techniques),
            "tools_available": sum(len(tools) for tools in self.red_team_tools.values())
        }
    
    async def stop_engine(self):
        """Arrête le moteur"""
        if not self.is_running:
            return {"status": "not_running"}
        
        self.is_running = False
        
        # Arrêter les tâches
        if self.operation_executor_task:
            self.operation_executor_task.cancel()
        
        logger.info("⏹️ Moteur Red Team arrêté")
        return {
            "status": "stopped",
            "message": "Moteur arrêté avec succès",
            "stop_time": datetime.now().isoformat()
        }
    
    async def _operation_executor_loop(self):
        """Boucle d'exécution des opérations programmées"""
        try:
            while self.is_running:
                # Vérifier les opérations à exécuter
                for operation in self.operations.values():
                    if (operation.status == OperationStatus.PLANNED and 
                        operation.start_time and 
                        operation.start_time <= datetime.now()):
                        await self._execute_operation(operation)
                
                # Attendre 30 secondes
                await asyncio.sleep(30)
                
        except asyncio.CancelledError:
            logger.info("Operation executor loop cancelled")
        except Exception as e:
            logger.error(f"Erreur dans operation executor loop: {e}")
    
    async def _execute_operation(self, operation: Operation):
        """Exécute une opération Red Team"""
        try:
            logger.info(f"Exécution opération: {operation.name}")
            
            operation.status = OperationStatus.RUNNING
            operation.start_time = datetime.now()
            
            # Simuler l'exécution selon la technique
            technique = self.techniques.get(operation.technique.id)
            if technique:
                # Simuler durée d'exécution
                execution_time = self._calculate_execution_time(technique)
                await asyncio.sleep(min(execution_time, 5))  # Max 5 sec pour démo
                
                # Simuler résultats
                success_probability = technique.success_rate
                detection_probability = technique.detection_rate
                
                operation.success = success_probability > 0.5
                operation.detection_triggered = detection_probability > 0.3
                
                # Générer output simulé
                operation.output = await self._generate_operation_output(operation, technique)
                
                # Générer IOCs si succès
                if operation.success:
                    operation.iocs_generated = await self._generate_iocs(operation, technique)
                
                # Recommandations
                operation.recommendations = await self._generate_operation_recommendations(operation, technique)
            
            operation.status = OperationStatus.COMPLETED
            operation.end_time = datetime.now()
            operation.duration = int((operation.end_time - operation.start_time).total_seconds())
            
            self.performance_stats["operations_executed"] += 1
            logger.info(f"Opération {operation.name} terminée - Succès: {operation.success}")
            
        except Exception as e:
            operation.status = OperationStatus.FAILED
            operation.output = f"Erreur d'exécution: {str(e)}"
            logger.error(f"Erreur exécution opération {operation.name}: {e}")
    
    def _calculate_execution_time(self, technique: TTPTechnique) -> int:
        """Calcule le temps d'exécution simulé"""
        base_time = 10  # 10 secondes de base
        
        if technique.difficulty == "easy":
            return base_time
        elif technique.difficulty == "medium":
            return base_time * 2
        else:  # hard
            return base_time * 4
    
    async def _generate_operation_output(self, operation: Operation, technique: TTPTechnique) -> str:
        """Génère la sortie simulée d'une opération"""
        if operation.success:
            outputs = {
                "T1566.001": "Email de phishing envoyé avec succès. 3 utilisateurs ont cliqué sur le lien.",
                "T1055": "Injection de processus réussie dans explorer.exe. Code malveillant exécuté.",
                "T1082": "Informations système collectées: Windows 10, 16GB RAM, Domaine CORPORATE",
                "T1071.001": "Communication C2 établie via HTTPS. Beacon actif.",
                "T1078": "Authentification réussie avec compte compromis: jdoe@company.com"
            }
            return outputs.get(technique.technique_id, f"Technique {technique.name} exécutée avec succès")
        else:
            failures = {
                "T1566.001": "Email bloqué par la passerelle de sécurité",
                "T1055": "Injection bloquée par l'EDR",
                "T1082": "Commande bloquée par la politique de sécurité",
                "T1071.001": "Trafic C2 détecté et bloqué par le firewall",
                "T1078": "Authentification échouée - compte verrouillé"
            }
            return failures.get(technique.technique_id, f"Échec de la technique {technique.name}")
    
    async def _generate_iocs(self, operation: Operation, technique: TTPTechnique) -> List[str]:
        """Génère des IOCs simulés"""
        iocs = []
        
        if technique.technique_id == "T1566.001":
            iocs = [
                "malicious@fake-domain.com",
                "http://fake-domain.com/payload.exe",
                "5d41402abc4b2a76b9719d911017c592"  # MD5 hash
            ]
        elif technique.technique_id == "T1055":
            iocs = [
                "explorer.exe",
                "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
            ]
        elif technique.technique_id == "T1071.001":
            iocs = [
                "192.168.1.100:443",
                "c2-server.evil.com",
                "User-Agent: Mozilla/5.0 (RedTeam)"
            ]
        
        return iocs
    
    async def _generate_operation_recommendations(self, operation: Operation, technique: TTPTechnique) -> List[str]:
        """Génère des recommandations post-opération"""
        recommendations = []
        
        if operation.success:
            recommendations.extend([
                f"Technique {technique.name} réussie - Vulnérabilité confirmée",
                "Recommander implémentation de contrôles préventifs",
                "Mettre à jour les règles de détection"
            ])
        
        if operation.detection_triggered:
            recommendations.extend([
                "Détection fonctionnelle - Vérifier temps de réponse",
                "Analyser la qualité des alertes générées"
            ])
        else:
            recommendations.extend([
                "Aucune détection - Gap de sécurité identifié",
                "Créer/améliorer règles de détection pour cette technique"
            ])
        
        return recommendations
    
    # API publique du moteur
    
    async def create_campaign(self, request: CreateCampaignRequest) -> Campaign:
        """Crée une nouvelle campagne Red Team"""
        campaign = Campaign(
            name=request.name,
            description=request.description,
            objective=request.objective,
            scope_description=request.scope_description,
            start_date=request.start_date,
            end_date=request.end_date,
            red_team_lead=request.red_team_lead,
            operators=request.operators,
            blue_team_contacts=request.blue_team_contacts,
            authorized_techniques=request.authorized_techniques,
            business_hours_only=request.business_hours_only,
            notification_required=request.notification_required,
            created_by=request.created_by
        )
        
        self.campaigns[campaign.id] = campaign
        self.performance_stats["campaigns_created"] += 1
        
        logger.info(f"Nouvelle campagne créée: {campaign.name}")
        return campaign
    
    async def update_campaign(self, campaign_id: str, request: UpdateCampaignRequest) -> Campaign:
        """Met à jour une campagne"""
        if campaign_id not in self.campaigns:
            raise ValueError(f"Campagne {campaign_id} non trouvée")
        
        campaign = self.campaigns[campaign_id]
        
        if request.status:
            campaign.status = request.status
        if request.description:
            campaign.description = request.description
        if request.operators is not None:
            campaign.operators = request.operators
        if request.phases_completed is not None:
            campaign.phases_completed = request.phases_completed
        
        campaign.updated_at = datetime.now()
        
        return campaign
    
    async def create_operation(self, request: CreateOperationRequest) -> Operation:
        """Crée une nouvelle opération"""
        # Récupérer la technique
        technique = None
        for tech in self.techniques.values():
            if tech.technique_id == request.technique_id:
                technique = tech
                break
        
        if not technique:
            raise ValueError(f"Technique {request.technique_id} non trouvée")
        
        operation = Operation(
            name=request.name,
            description=request.description,
            technique=technique,
            target_id=request.target_id,
            campaign_id=request.campaign_id,
            commands=request.commands,
            tools=request.tools,
            payload=request.payload,
            operator=request.operator
        )
        
        self.operations[operation.id] = operation
        
        # Mettre à jour compteurs campagne
        if request.campaign_id and request.campaign_id in self.campaigns:
            self.campaigns[request.campaign_id].operations_planned += 1
        
        logger.info(f"Nouvelle opération créée: {operation.name}")
        return operation
    
    async def update_operation(self, operation_id: str, request: UpdateOperationRequest) -> Operation:
        """Met à jour une opération"""
        if operation_id not in self.operations:
            raise ValueError(f"Opération {operation_id} non trouvée")
        
        operation = self.operations[operation_id]
        
        if request.status:
            operation.status = request.status
        if request.output is not None:
            operation.output = request.output
        if request.success is not None:
            operation.success = request.success
        if request.detection_triggered is not None:
            operation.detection_triggered = request.detection_triggered
        if request.blue_team_response is not None:
            operation.blue_team_response = request.blue_team_response
        if request.lessons_learned is not None:
            operation.lessons_learned = request.lessons_learned
        if request.recommendations is not None:
            operation.recommendations = request.recommendations
        
        operation.updated_at = datetime.now()
        
        return operation
    
    async def create_target(self, request: CreateTargetRequest) -> Target:
        """Crée une nouvelle cible"""
        target = Target(
            name=request.name,
            type=request.type,
            description=request.description,
            ip_ranges=request.ip_ranges,
            domains=request.domains,
            applications=request.applications,
            criticality=request.criticality,
            business_impact=request.business_impact
        )
        
        self.targets[target.id] = target
        logger.info(f"Nouvelle cible créée: {target.name}")
        
        return target
    
    async def search_campaigns(self, request: CampaignSearchRequest) -> Tuple[List[Campaign], int]:
        """Recherche des campagnes"""
        results = []
        
        for campaign in self.campaigns.values():
            # Appliquer filtres
            if request.query and request.query.lower() not in campaign.name.lower() and request.query.lower() not in campaign.description.lower():
                continue
            
            if request.status and campaign.status not in request.status:
                continue
            
            if request.red_team_lead and campaign.red_team_lead != request.red_team_lead:
                continue
            
            if request.date_from and campaign.start_date and campaign.start_date.date() < request.date_from:
                continue
            
            if request.date_to and campaign.start_date and campaign.start_date.date() > request.date_to:
                continue
            
            results.append(campaign)
        
        # Trier par date de création (plus récent en premier)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        total = len(results)
        paginated_results = results[request.offset:request.offset + request.limit]
        
        return paginated_results, total
    
    async def search_operations(self, request: OperationSearchRequest) -> Tuple[List[Operation], int]:
        """Recherche des opérations"""
        results = []
        
        for operation in self.operations.values():
            # Appliquer filtres
            if request.query and request.query.lower() not in operation.name.lower():
                continue
            
            if request.status and operation.status not in request.status:
                continue
            
            if request.campaign_id and operation.campaign_id != request.campaign_id:
                continue
            
            if request.technique and request.technique not in operation.technique.technique_id:
                continue
            
            if request.operator and operation.operator != request.operator:
                continue
            
            if request.success is not None and operation.success != request.success:
                continue
            
            results.append(operation)
        
        # Trier par date de création (plus récent en premier)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        total = len(results)
        paginated_results = results[request.offset:request.offset + request.limit]
        
        return paginated_results, total
    
    def get_campaign_statistics(self) -> CampaignStatistics:
        """Retourne les statistiques des campagnes"""
        total_campaigns = len(self.campaigns)
        
        by_status = {}
        by_red_team_lead = {}
        operations_total = 0
        operations_successful = 0
        techniques_used = defaultdict(int)
        
        for campaign in self.campaigns.values():
            by_status[campaign.status.value] = by_status.get(campaign.status.value, 0) + 1
            by_red_team_lead[campaign.red_team_lead] = by_red_team_lead.get(campaign.red_team_lead, 0) + 1
            operations_total += campaign.operations_planned
            operations_successful += campaign.operations_successful
        
        for operation in self.operations.values():
            techniques_used[operation.technique.technique_id] += 1
        
        # Top opérateurs
        operator_stats = defaultdict(lambda: {"operations": 0, "success": 0})
        for operation in self.operations.values():
            operator_stats[operation.operator]["operations"] += 1
            if operation.success:
                operator_stats[operation.operator]["success"] += 1
        
        top_operators = [
            {
                "operator": op, 
                "operations": stats["operations"],
                "success_rate": stats["success"] / max(stats["operations"], 1)
            }
            for op, stats in sorted(operator_stats.items(), key=lambda x: x[1]["operations"], reverse=True)[:5]
        ]
        
        return CampaignStatistics(
            total_campaigns=total_campaigns,
            by_status=by_status,
            by_red_team_lead=by_red_team_lead,
            active_campaigns=by_status.get("active", 0),
            completed_campaigns=by_status.get("completed", 0),
            avg_duration_days=14.0,  # Moyenne simulée
            success_rate=(operations_successful / max(operations_total, 1)) * 100,
            operations_total=operations_total,
            operations_successful=operations_successful,
            techniques_used=dict(techniques_used),
            top_operators=top_operators
        )
    
    def get_operation_statistics(self) -> OperationStatistics:
        """Retourne les statistiques des opérations"""
        total_operations = len(self.operations)
        
        by_status = {}
        by_technique = {}
        by_phase = {}
        success_count = 0
        detection_count = 0
        total_duration = 0
        operation_count = 0
        
        for operation in self.operations.values():
            by_status[operation.status.value] = by_status.get(operation.status.value, 0) + 1
            by_technique[operation.technique.technique_id] = by_technique.get(operation.technique.technique_id, 0) + 1
            by_phase[operation.technique.phase.value] = by_phase.get(operation.technique.phase.value, 0) + 1
            
            if operation.success:
                success_count += 1
            if operation.detection_triggered:
                detection_count += 1
            if operation.duration:
                total_duration += operation.duration
                operation_count += 1
        
        return OperationStatistics(
            total_operations=total_operations,
            by_status=by_status,
            by_technique=by_technique,
            by_phase=by_phase,
            success_rate=(success_count / max(total_operations, 1)) * 100,
            detection_rate=(detection_count / max(total_operations, 1)) * 100,
            avg_duration_minutes=(total_duration / max(operation_count, 1)) / 60,
            most_successful_techniques=[],  # TODO: Implémenter
            most_detected_techniques=[]     # TODO: Implémenter
        )
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Retourne le statut du moteur"""
        now = datetime.now()
        uptime = (now - self.performance_stats["start_time"]).total_seconds()
        
        active_campaigns = len([c for c in self.campaigns.values() if c.status == CampaignStatus.ACTIVE])
        running_operations = len([o for o in self.operations.values() if o.status == OperationStatus.RUNNING])
        
        return {
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "performance": self.performance_stats,
            "active_campaigns": active_campaigns,
            "total_campaigns": len(self.campaigns),
            "running_operations": running_operations,
            "total_operations": len(self.operations),
            "targets": len(self.targets),
            "techniques_loaded": len(self.techniques),
            "purple_team_exercises": len(self.purple_team_exercises)
        }