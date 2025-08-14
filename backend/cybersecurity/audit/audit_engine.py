"""
Moteur d'Audit Automatisé avec support multi-frameworks
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
    AuditControl, Asset, AuditScope, Finding, Audit, RemediationPlan, ComplianceSnapshot,
    AuditFramework, AuditType, AuditStatus, FindingSeverity, FindingStatus, 
    RemediationStatus, AssetType, TestMethod,
    CreateAuditRequest, UpdateAuditRequest, CreateAssetRequest, CreateScopeRequest,
    CreateFindingRequest, UpdateFindingRequest, CreateRemediationPlanRequest,
    AuditSearchRequest, FindingSearchRequest, AuditStatistics, FindingStatistics,
    ComplianceReport, AuditInsight
)

logger = logging.getLogger(__name__)

class AuditEngine:
    """Moteur principal d'Audit Automatisé"""
    
    def __init__(self):
        self.audits: Dict[str, Audit] = {}
        self.assets: Dict[str, Asset] = {}
        self.scopes: Dict[str, AuditScope] = {}
        self.findings: Dict[str, Finding] = {}
        self.controls: Dict[str, AuditControl] = {}
        self.remediation_plans: Dict[str, RemediationPlan] = {}
        self.compliance_snapshots: Dict[str, ComplianceSnapshot] = {}
        
        # Status
        self.is_running = False
        self.audit_executor_task = None
        self.compliance_monitor_task = None
        
        # Performance tracking
        self.performance_stats = {
            "start_time": datetime.now(),
            "audits_completed": 0,
            "findings_identified": 0,
            "controls_tested": 0,
            "compliance_checks": 0,
            "remediation_plans_created": 0
        }
        
        # Framework definitions
        self.framework_definitions = self._load_framework_definitions()
        
        # Control libraries
        self.control_libraries = self._load_control_libraries()
        
        # Automation templates
        self.automation_templates = self._load_automation_templates()
        
        # Compliance baselines
        self.compliance_baselines = self._load_compliance_baselines()
    
    def _load_framework_definitions(self) -> Dict[str, Any]:
        """Charge les définitions des frameworks de compliance"""
        return {
            "iso27001": {
                "name": "ISO 27001:2022",
                "description": "Information Security Management Systems",
                "categories": [
                    "Information Security Policies",
                    "Organization of Information Security",
                    "Human Resource Security",
                    "Asset Management",
                    "Access Control",
                    "Cryptography",
                    "Physical and Environmental Security",
                    "Operations Security",
                    "Communications Security",
                    "System Acquisition, Development and Maintenance",
                    "Supplier Relationships",
                    "Information Security Incident Management",
                    "Business Continuity Management",
                    "Compliance"
                ],
                "total_controls": 114,
                "mandatory": True
            },
            "nist_csf": {
                "name": "NIST Cybersecurity Framework v1.1",
                "description": "Framework for Improving Critical Infrastructure Cybersecurity",
                "categories": [
                    "Identify", "Protect", "Detect", "Respond", "Recover"
                ],
                "functions": {
                    "identify": ["Asset Management", "Business Environment", "Governance", "Risk Assessment", "Risk Management Strategy"],
                    "protect": ["Access Control", "Awareness and Training", "Data Security", "Information Protection Processes", "Maintenance", "Protective Technology"],
                    "detect": ["Anomalies and Events", "Security Continuous Monitoring", "Detection Processes"],
                    "respond": ["Response Planning", "Communications", "Analysis", "Mitigation", "Improvements"],
                    "recover": ["Recovery Planning", "Improvements", "Communications"]
                },
                "total_controls": 108,
                "mandatory": False
            },
            "cis_controls": {
                "name": "CIS Controls v8",
                "description": "Center for Internet Security Critical Security Controls",
                "categories": [
                    "Basic CIS Controls", "Foundational CIS Controls", "Organizational CIS Controls"
                ],
                "implementation_groups": ["IG1", "IG2", "IG3"],
                "total_controls": 153,
                "mandatory": False
            },
            "pci_dss": {
                "name": "PCI DSS v4.0",
                "description": "Payment Card Industry Data Security Standard",
                "requirements": [
                    "Install and maintain network security controls",
                    "Apply secure configurations to all system components",
                    "Protect stored cardholder data",
                    "Protect cardholder data with strong cryptography during transmission",
                    "Protect all systems and networks from malicious software",
                    "Develop and maintain secure systems and software",
                    "Restrict access to cardholder data by business need to know",
                    "Identify users and authenticate access to system components",
                    "Restrict physical access to cardholder data",
                    "Log and monitor all access to network resources and cardholder data",
                    "Test security of systems and networks regularly",
                    "Support information security with organizational policies"
                ],
                "total_controls": 64,
                "mandatory": True
            }
        }
    
    def _load_control_libraries(self) -> Dict[str, List[AuditControl]]:
        """Charge les bibliothèques de contrôles pour chaque framework"""
        libraries = {}
        
        # ISO 27001 Controls samples
        iso_controls = [
            {
                "control_id": "A.5.1.1",
                "framework": AuditFramework.ISO27001,
                "title": "Information security policy",
                "description": "A set of policies for information security shall be defined, approved by management, published and communicated to employees and relevant external parties.",
                "objective": "To provide management direction and support for information security",
                "category": "Information Security Policies",
                "test_method": TestMethod.DOCUMENT_REVIEW,
                "is_automated": False
            },
            {
                "control_id": "A.8.1.1",
                "framework": AuditFramework.ISO27001,
                "title": "Inventory of assets",
                "description": "Assets associated with information and information processing facilities shall be identified and an inventory of these assets shall be drawn up and maintained.",
                "objective": "To identify organizational assets and define appropriate protection responsibilities",
                "category": "Asset Management",
                "test_method": TestMethod.AUTOMATED_SCAN,
                "is_automated": True
            },
            {
                "control_id": "A.9.1.1",
                "framework": AuditFramework.ISO27001,
                "title": "Access control policy",
                "description": "An access control policy shall be established, documented and reviewed based on business and information security requirements.",
                "objective": "To limit access to information and information processing facilities",
                "category": "Access Control",
                "test_method": TestMethod.DOCUMENT_REVIEW,
                "is_automated": False
            }
        ]
        
        libraries["iso27001"] = [
            AuditControl(**control_data) for control_data in iso_controls
        ]
        
        # NIST CSF Controls samples
        nist_controls = [
            {
                "control_id": "ID.AM-1",
                "framework": AuditFramework.NIST_CSF,
                "title": "Physical devices and systems within the organization are inventoried",
                "description": "Develop and maintain an accurate, complete, and current inventory of physical devices",
                "objective": "Enable asset visibility and management decisions",
                "category": "Asset Management",
                "test_method": TestMethod.AUTOMATED_SCAN,
                "is_automated": True
            },
            {
                "control_id": "PR.AC-1",
                "framework": AuditFramework.NIST_CSF,
                "title": "Identities and credentials are issued, managed, verified, revoked, and audited",
                "description": "Identity management processes and systems provide each user with unique identifiers",
                "objective": "Control access to systems and data",
                "category": "Access Control",
                "test_method": TestMethod.CONFIGURATION_CHECK,
                "is_automated": True
            },
            {
                "control_id": "DE.AE-1",
                "framework": AuditFramework.NIST_CSF,
                "title": "A baseline of network operations and expected data flows is established and managed",
                "description": "Network operations baseline includes expected network traffic, protocols, and connections",
                "objective": "Enable detection of anomalous network activity",
                "category": "Anomalies and Events",
                "test_method": TestMethod.MANUAL_REVIEW,
                "is_automated": False
            }
        ]
        
        libraries["nist_csf"] = [
            AuditControl(**control_data) for control_data in nist_controls
        ]
        
        # CIS Controls samples
        cis_controls = [
            {
                "control_id": "1.1",
                "framework": AuditFramework.CIS_CONTROLS,
                "title": "Establish and Maintain Detailed Asset Inventory",
                "description": "Establish and maintain an accurate, detailed, and up-to-date inventory of all enterprise assets",
                "objective": "Provide foundation for asset management and security controls",
                "category": "Inventory and Control of Enterprise Assets",
                "test_method": TestMethod.AUTOMATED_SCAN,
                "is_automated": True
            },
            {
                "control_id": "2.1",
                "framework": AuditFramework.CIS_CONTROLS,
                "title": "Establish and Maintain a Software Inventory",
                "description": "Establish and maintain a detailed inventory of all licensed software installed on enterprise assets",
                "objective": "Enable software asset management and vulnerability management",
                "category": "Inventory and Control of Software Assets",
                "test_method": TestMethod.AUTOMATED_SCAN,
                "is_automated": True
            },
            {
                "control_id": "5.1",
                "framework": AuditFramework.CIS_CONTROLS,
                "title": "Establish and Maintain an Account Management Process",
                "description": "Establish and maintain an account management process that includes creation, modification, and deletion of accounts",
                "objective": "Control account lifecycle and access privileges",
                "category": "Account Management",
                "test_method": TestMethod.CONFIGURATION_CHECK,
                "is_automated": True
            }
        ]
        
        libraries["cis_controls"] = [
            AuditControl(**control_data) for control_data in cis_controls
        ]
        
        return libraries
    
    def _load_automation_templates(self) -> Dict[str, Any]:
        """Charge les templates d'automatisation pour les tests"""
        return {
            "asset_inventory": {
                "name": "Automated Asset Discovery",
                "description": "Automatically discover and inventory network assets",
                "applicable_controls": ["A.8.1.1", "ID.AM-1", "1.1"],
                "test_commands": [
                    "nmap -sn network_range",
                    "arp-scan -l",
                    "Get-WmiObject Win32_ComputerSystem"
                ],
                "expected_output": "asset_inventory.json"
            },
            "access_control_review": {
                "name": "Access Control Configuration Check",
                "description": "Review access control configurations and user privileges",
                "applicable_controls": ["A.9.1.1", "PR.AC-1", "5.1"],
                "test_commands": [
                    "net user",
                    "Get-LocalUser",
                    "cat /etc/passwd"
                ],
                "expected_output": "access_control_report.json"
            },
            "vulnerability_assessment": {
                "name": "Automated Vulnerability Scanning",
                "description": "Perform automated vulnerability assessment",
                "applicable_controls": ["A.12.6.1", "DE.CM-8", "7.1"],
                "test_commands": [
                    "nessus_scan",
                    "openvas_scan",
                    "nmap --script vuln"
                ],
                "expected_output": "vulnerability_report.xml"
            },
            "configuration_review": {
                "name": "Security Configuration Assessment",
                "description": "Review security configurations against baselines",
                "applicable_controls": ["A.12.6.1", "PR.IP-1", "4.1"],
                "test_commands": [
                    "lynis audit system",
                    "oscap xccdf eval",
                    "powershell security baseline audit"
                ],
                "expected_output": "configuration_assessment.json"
            }
        }
    
    def _load_compliance_baselines(self) -> Dict[str, Any]:
        """Charge les baselines de compliance"""
        return {
            "minimum_compliance_scores": {
                "iso27001": 85.0,
                "nist_csf": 80.0,
                "cis_controls": 75.0,
                "pci_dss": 95.0
            },
            "risk_thresholds": {
                "critical": 9.0,
                "high": 7.0,
                "medium": 4.0,
                "low": 2.0
            },
            "audit_frequencies": {
                "critical_systems": "quarterly",
                "high_risk_systems": "semi_annual",
                "standard_systems": "annual",
                "low_risk_systems": "biennial"
            }
        }
    
    async def start_engine(self):
        """Démarre le moteur d'audit"""
        if self.is_running:
            return {"status": "already_running"}
        
        self.is_running = True
        
        # Démarrer l'exécuteur d'audits
        self.audit_executor_task = asyncio.create_task(self._audit_executor_loop())
        
        # Démarrer le moniteur de compliance
        self.compliance_monitor_task = asyncio.create_task(self._compliance_monitor_loop())
        
        # Charger les contrôles des frameworks
        for framework, controls in self.control_libraries.items():
            for control in controls:
                self.controls[control.id] = control
        
        logger.info("🔍 Moteur d'Audit démarré")
        
        return {
            "status": "started",
            "message": "Moteur d'Audit démarré avec succès",
            "start_time": datetime.now().isoformat(),
            "frameworks_loaded": len(self.framework_definitions),
            "controls_loaded": len(self.controls),
            "automation_templates": len(self.automation_templates)
        }
    
    async def stop_engine(self):
        """Arrête le moteur"""
        if not self.is_running:
            return {"status": "not_running"}
        
        self.is_running = False
        
        # Arrêter les tâches
        if self.audit_executor_task:
            self.audit_executor_task.cancel()
        if self.compliance_monitor_task:
            self.compliance_monitor_task.cancel()
        
        logger.info("⏹️ Moteur d'Audit arrêté")
        return {
            "status": "stopped",
            "message": "Moteur arrêté avec succès",
            "stop_time": datetime.now().isoformat()
        }
    
    async def _audit_executor_loop(self):
        """Boucle d'exécution des audits programmés"""
        try:
            while self.is_running:
                # Vérifier les audits à démarrer
                for audit in self.audits.values():
                    if (audit.status == AuditStatus.SCHEDULED and 
                        audit.planned_start_date and 
                        audit.planned_start_date <= datetime.now()):
                        await self._execute_audit(audit)
                
                await asyncio.sleep(300)  # Vérifier toutes les 5 minutes
                
        except asyncio.CancelledError:
            logger.info("Audit executor loop cancelled")
        except Exception as e:
            logger.error(f"Erreur dans audit executor loop: {e}")
    
    async def _compliance_monitor_loop(self):
        """Boucle de monitoring de compliance"""
        try:
            while self.is_running:
                # Générer des snapshots de compliance périodiques
                await self._generate_compliance_snapshots()
                
                # Vérifier les échéances de remediation
                await self._check_remediation_deadlines()
                
                await asyncio.sleep(3600)  # Vérifier toutes les heures
                
        except asyncio.CancelledError:
            logger.info("Compliance monitor loop cancelled")
        except Exception as e:
            logger.error(f"Erreur dans compliance monitor loop: {e}")
    
    async def _execute_audit(self, audit: Audit):
        """Exécute un audit complet"""
        try:
            logger.info(f"Exécution audit: {audit.name}")
            
            audit.status = AuditStatus.RUNNING
            audit.actual_start_date = datetime.now()
            
            # Récupérer le scope et les contrôles
            scope = self.scopes.get(audit.scope_id)
            if not scope:
                raise ValueError(f"Scope {audit.scope_id} non trouvé")
            
            # Identifier les contrôles à tester
            controls_to_test = []
            for framework in audit.frameworks:
                framework_controls = [c for c in self.controls.values() 
                                   if c.framework == framework]
                controls_to_test.extend(framework_controls)
            
            audit.controls_planned = len(controls_to_test)
            
            # Exécuter les tests pour chaque contrôle
            for control in controls_to_test:
                await self._test_control(audit, control, scope)
                audit.controls_tested += 1
            
            # Calculer le score de compliance
            await self._calculate_compliance_scores(audit)
            
            # Générer recommandations
            audit.recommendations = await self._generate_audit_recommendations(audit)
            
            # Créer les plans de remediation automatiques
            await self._create_automatic_remediation_plans(audit)
            
            audit.status = AuditStatus.COMPLETED
            audit.actual_end_date = datetime.now()
            
            self.performance_stats["audits_completed"] += 1
            logger.info(f"Audit {audit.name} terminé - Score: {audit.overall_compliance_score}%")
            
        except Exception as e:
            audit.status = AuditStatus.FAILED
            logger.error(f"Erreur exécution audit {audit.name}: {e}")
    
    async def _test_control(self, audit: Audit, control: AuditControl, scope: AuditScope):
        """Teste un contrôle spécifique"""
        try:
            logger.info(f"Test contrôle: {control.control_id}")
            
            # Récupérer les assets dans le scope
            assets_to_test = []
            for asset_id in scope.asset_ids:
                if asset_id in self.assets:
                    assets_to_test.append(self.assets[asset_id])
            
            # Exécuter le test selon la méthode
            if control.is_automated and control.test_method == TestMethod.AUTOMATED_SCAN:
                results = await self._execute_automated_test(control, assets_to_test)
            elif control.test_method == TestMethod.CONFIGURATION_CHECK:
                results = await self._execute_configuration_check(control, assets_to_test)
            else:
                results = await self._execute_manual_review(control, assets_to_test)
            
            # Analyser les résultats et créer des findings si nécessaire
            await self._analyze_test_results(audit, control, results, assets_to_test)
            
            self.performance_stats["controls_tested"] += 1
            
        except Exception as e:
            logger.error(f"Erreur test contrôle {control.control_id}: {e}")
            
            # Créer un finding pour l'erreur de test
            error_finding = await self.create_finding(CreateFindingRequest(
                title=f"Test Error - {control.title}",
                description=f"Erreur lors du test automatique: {str(e)}",
                severity=FindingSeverity.MEDIUM,
                audit_id=audit.id,
                control_id=control.id,
                test_method=TestMethod.AUTOMATED_SCAN,
                created_by="audit_engine"
            ))
    
    async def _execute_automated_test(self, control: AuditControl, assets: List[Asset]) -> Dict[str, Any]:
        """Exécute un test automatisé"""
        results = {
            "control_id": control.control_id,
            "test_method": "automated",
            "assets_tested": len(assets),
            "results": [],
            "overall_status": "pass"
        }
        
        # Simuler l'exécution selon le contrôle
        for asset in assets:
            asset_result = {
                "asset_id": asset.id,
                "asset_name": asset.name,
                "status": "pass",
                "findings": [],
                "evidence": []
            }
            
            # Logique de test simulée selon le contrôle
            if control.control_id in ["A.8.1.1", "ID.AM-1", "1.1"]:  # Asset inventory
                if not asset.hostname or not asset.ip_address:
                    asset_result["status"] = "fail"
                    asset_result["findings"].append("Asset manque d'informations d'identification complètes")
                    results["overall_status"] = "fail"
                else:
                    asset_result["evidence"].append(f"Asset correctement identifié: {asset.hostname} ({asset.ip_address})")
            
            elif control.control_id in ["A.9.1.1", "PR.AC-1", "5.1"]:  # Access control
                # Simuler vérification des contrôles d'accès
                if asset.type in [AssetType.DATABASE, AssetType.APPLICATION]:
                    # Simuler quelques problèmes d'accès
                    if hash(asset.id) % 3 == 0:  # 1/3 des assets ont des problèmes
                        asset_result["status"] = "fail"
                        asset_result["findings"].append("Contrôles d'accès insuffisants détectés")
                        results["overall_status"] = "fail"
                    else:
                        asset_result["evidence"].append("Contrôles d'accès appropriés en place")
            
            results["results"].append(asset_result)
        
        # Attendre pour simuler le test
        await asyncio.sleep(1)
        
        return results
    
    async def _execute_configuration_check(self, control: AuditControl, assets: List[Asset]) -> Dict[str, Any]:
        """Exécute une vérification de configuration"""
        results = {
            "control_id": control.control_id,
            "test_method": "configuration_check",
            "assets_tested": len(assets),
            "results": [],
            "overall_status": "pass"
        }
        
        for asset in assets:
            asset_result = {
                "asset_id": asset.id,
                "asset_name": asset.name,
                "status": "pass",
                "findings": [],
                "evidence": [],
                "configurations_checked": []
            }
            
            # Simuler vérifications de configuration
            config_checks = [
                "Password policy enforcement",
                "Account lockout settings", 
                "Audit logging enabled",
                "Security updates current",
                "Unnecessary services disabled"
            ]
            
            for check in config_checks:
                # Simuler des résultats de configuration
                if hash(f"{asset.id}{check}") % 4 == 0:  # 1/4 des checks échouent
                    asset_result["findings"].append(f"Configuration non conforme: {check}")
                    asset_result["status"] = "fail"
                    results["overall_status"] = "fail"
                else:
                    asset_result["evidence"].append(f"Configuration conforme: {check}")
                
                asset_result["configurations_checked"].append(check)
            
            results["results"].append(asset_result)
        
        await asyncio.sleep(1)
        return results
    
    async def _execute_manual_review(self, control: AuditControl, assets: List[Asset]) -> Dict[str, Any]:
        """Exécute une revue manuelle (simulée)"""
        results = {
            "control_id": control.control_id,
            "test_method": "manual_review",
            "assets_tested": len(assets),
            "results": [],
            "overall_status": "requires_review",
            "reviewer_notes": f"Revue manuelle requise pour {control.title}"
        }
        
        # Pour la simulation, marquer comme nécessitant une revue
        for asset in assets:
            asset_result = {
                "asset_id": asset.id,
                "asset_name": asset.name,
                "status": "requires_review",
                "findings": [],
                "evidence": [],
                "manual_review_required": True
            }
            results["results"].append(asset_result)
        
        return results
    
    async def _analyze_test_results(self, audit: Audit, control: AuditControl, results: Dict[str, Any], assets: List[Asset]):
        """Analyse les résultats de test et crée des findings"""
        if results["overall_status"] == "fail":
            # Compter les échecs
            failed_assets = [r for r in results["results"] if r["status"] == "fail"]
            
            # Déterminer la sévérité basée sur le pourcentage d'échec
            failure_rate = len(failed_assets) / max(len(results["results"]), 1)
            
            if failure_rate >= 0.8:
                severity = FindingSeverity.CRITICAL
            elif failure_rate >= 0.6:
                severity = FindingSeverity.HIGH
            elif failure_rate >= 0.3:
                severity = FindingSeverity.MEDIUM
            else:
                severity = FindingSeverity.LOW
            
            # Créer un finding pour chaque asset en échec
            for failed_result in failed_assets:
                asset_id = failed_result["asset_id"]
                findings_text = "; ".join(failed_result["findings"])
                
                finding_request = CreateFindingRequest(
                    title=f"{control.title} - Non-conformité détectée",
                    description=f"Contrôle {control.control_id} en échec sur l'asset {failed_result['asset_name']}: {findings_text}",
                    severity=severity,
                    audit_id=audit.id,
                    control_id=control.id,
                    asset_id=asset_id,
                    evidence=failed_result.get("evidence", []),
                    test_method=TestMethod.AUTOMATED_SCAN if control.is_automated else TestMethod.MANUAL_REVIEW,
                    business_impact=f"Non-compliance avec {control.framework.value} - {control.title}",
                    remediation_recommendation=f"Implémenter les contrôles requis pour {control.title}",
                    created_by="audit_engine"
                )
                
                finding = await self.create_finding(finding_request)
                audit.findings_count += 1
                
                # Incrémenter compteurs par sévérité
                if severity == FindingSeverity.CRITICAL:
                    audit.critical_findings += 1
                elif severity == FindingSeverity.HIGH:
                    audit.high_findings += 1
                elif severity == FindingSeverity.MEDIUM:
                    audit.medium_findings += 1
                else:
                    audit.low_findings += 1
            
            audit.controls_failed += 1
        else:
            audit.controls_passed += 1
    
    async def _calculate_compliance_scores(self, audit: Audit):
        """Calcule les scores de compliance pour l'audit"""
        try:
            # Score global
            total_controls = audit.controls_tested
            if total_controls > 0:
                audit.overall_compliance_score = (audit.controls_passed / total_controls) * 100
            else:
                audit.overall_compliance_score = 0.0
            
            # Scores par framework
            for framework in audit.frameworks:
                framework_controls = [c for c in self.controls.values() 
                                   if c.framework == framework]
                framework_findings = [f for f in self.findings.values() 
                                   if f.audit_id == audit.id and 
                                   any(c.framework == framework and c.id == f.control_id 
                                       for c in framework_controls)]
                
                failed_controls = len(set(f.control_id for f in framework_findings))
                total_framework_controls = len(framework_controls)
                
                if total_framework_controls > 0:
                    passed_controls = total_framework_controls - failed_controls
                    score = (passed_controls / total_framework_controls) * 100
                    audit.framework_scores[framework.value] = score
                else:
                    audit.framework_scores[framework.value] = 100.0
            
            logger.info(f"Scores calculés pour audit {audit.id}: {audit.overall_compliance_score}%")
            
        except Exception as e:
            logger.error(f"Erreur calcul scores compliance: {e}")
    
    async def _generate_audit_recommendations(self, audit: Audit) -> List[str]:
        """Génère des recommandations basées sur les findings"""
        recommendations = []
        
        # Recommandations basées sur les findings critiques et élevées
        critical_high_findings = [f for f in self.findings.values() 
                                if f.audit_id == audit.id and 
                                f.severity in [FindingSeverity.CRITICAL, FindingSeverity.HIGH]]
        
        if critical_high_findings:
            recommendations.append(f"Traiter en priorité {len(critical_high_findings)} findings critiques/élevées")
            
            # Recommandations par catégorie de contrôle
            control_categories = defaultdict(int)
            for finding in critical_high_findings:
                control = self.controls.get(finding.control_id)
                if control:
                    control_categories[control.category] += 1
            
            for category, count in control_categories.items():
                if count >= 2:
                    recommendations.append(f"Renforcer les contrôles de {category} ({count} findings)")
        
        # Recommandations par framework
        for framework, score in audit.framework_scores.items():
            baseline_score = self.compliance_baselines["minimum_compliance_scores"].get(framework, 80.0)
            if score < baseline_score:
                gap = baseline_score - score
                recommendations.append(f"Améliorer conformité {framework}: écart de {gap:.1f}% par rapport au baseline")
        
        # Recommandations générales
        if audit.overall_compliance_score < 80:
            recommendations.append("Mise en place d'un programme de compliance structuré")
            recommendations.append("Formation équipe sur les exigences de conformité")
        
        if audit.findings_count > 0:
            recommendations.append("Établir un processus de suivi des findings et remédiation")
        
        return recommendations[:10]  # Limiter à 10 recommandations
    
    async def _create_automatic_remediation_plans(self, audit: Audit):
        """Crée automatiquement des plans de remédiation pour les findings critiques"""
        try:
            critical_findings = [f for f in self.findings.values() 
                               if f.audit_id == audit.id and 
                               f.severity == FindingSeverity.CRITICAL and
                               f.status == FindingStatus.OPEN]
            
            if critical_findings:
                plan_request = CreateRemediationPlanRequest(
                    name=f"Plan de Remédiation Critique - {audit.name}",
                    description=f"Plan automatique pour traiter {len(critical_findings)} findings critiques",
                    audit_id=audit.id,
                    finding_ids=[f.id for f in critical_findings],
                    planned_start_date=datetime.now() + timedelta(days=1),
                    planned_end_date=datetime.now() + timedelta(days=30),
                    assigned_team=[audit.lead_auditor],
                    created_by="audit_engine"
                )
                
                plan = await self.create_remediation_plan(plan_request)
                self.performance_stats["remediation_plans_created"] += 1
                
                logger.info(f"Plan de remédiation automatique créé: {plan.id}")
        
        except Exception as e:
            logger.error(f"Erreur création plan remédiation automatique: {e}")
    
    async def _generate_compliance_snapshots(self):
        """Génère des snapshots périodiques de compliance"""
        try:
            # Générer un snapshot pour chaque framework actif
            active_frameworks = set()
            for audit in self.audits.values():
                if audit.status == AuditStatus.COMPLETED:
                    active_frameworks.update(audit.frameworks)
            
            for framework in active_frameworks:
                snapshot = ComplianceSnapshot(
                    name=f"Compliance Snapshot - {framework.value}",
                    frameworks=[framework],
                    snapshot_date=datetime.now()
                )
                
                # Calculer métriques de compliance
                framework_audits = [a for a in self.audits.values() 
                                  if framework in a.frameworks and 
                                  a.status == AuditStatus.COMPLETED]
                
                if framework_audits:
                    latest_audit = max(framework_audits, key=lambda x: x.actual_end_date or x.created_at)
                    snapshot.overall_compliance_percentage = latest_audit.framework_scores.get(framework.value, 0.0)
                    
                    # Compter les findings par sévérité
                    framework_findings = [f for f in self.findings.values() 
                                        if f.audit_id == latest_audit.id]
                    
                    snapshot.total_findings = len(framework_findings)
                    snapshot.critical_risk_findings = len([f for f in framework_findings if f.severity == FindingSeverity.CRITICAL])
                    snapshot.high_risk_findings = len([f for f in framework_findings if f.severity == FindingSeverity.HIGH])
                    snapshot.medium_risk_findings = len([f for f in framework_findings if f.severity == FindingSeverity.MEDIUM])
                    snapshot.low_risk_findings = len([f for f in framework_findings if f.severity == FindingSeverity.LOW])
                
                snapshot.created_by = "audit_engine"
                self.compliance_snapshots[snapshot.id] = snapshot
        
        except Exception as e:
            logger.error(f"Erreur génération snapshots compliance: {e}")
    
    async def _check_remediation_deadlines(self):
        """Vérifie les échéances de remédiation"""
        try:
            now = datetime.now()
            
            # Vérifier les findings avec échéances dépassées
            overdue_findings = [f for f in self.findings.values() 
                              if f.due_date and f.due_date < now and 
                              f.status not in [FindingStatus.RESOLVED, FindingStatus.ACCEPTED_RISK]]
            
            for finding in overdue_findings:
                logger.warning(f"Finding en retard: {finding.title} (échéance: {finding.due_date})")
                
            # Vérifier les plans de remédiation en retard
            overdue_plans = [p for p in self.remediation_plans.values() 
                           if p.planned_end_date and p.planned_end_date < now and 
                           p.status not in [RemediationStatus.COMPLETED, RemediationStatus.VERIFIED]]
            
            for plan in overdue_plans:
                logger.warning(f"Plan de remédiation en retard: {plan.name} (échéance: {plan.planned_end_date})")
        
        except Exception as e:
            logger.error(f"Erreur vérification échéances: {e}")
    
    # API publique du moteur
    
    async def create_audit(self, request: CreateAuditRequest) -> Audit:
        """Crée un nouveau audit"""
        audit = Audit(
            name=request.name,
            description=request.description,
            type=request.type,
            scope_id=request.scope_id,
            frameworks=request.frameworks,
            planned_start_date=request.planned_start_date,
            planned_end_date=request.planned_end_date,
            lead_auditor=request.lead_auditor,
            audit_team=request.audit_team,
            automated_tests_enabled=request.automated_tests_enabled,
            manual_review_required=request.manual_review_required,
            created_by=request.created_by
        )
        
        self.audits[audit.id] = audit
        logger.info(f"Nouvel audit créé: {audit.name}")
        
        return audit
    
    async def update_audit(self, audit_id: str, request: UpdateAuditRequest) -> Audit:
        """Met à jour un audit"""
        if audit_id not in self.audits:
            raise ValueError(f"Audit {audit_id} non trouvé")
        
        audit = self.audits[audit_id]
        
        if request.status:
            audit.status = request.status
        if request.description:
            audit.description = request.description
        if request.audit_team is not None:
            audit.audit_team = request.audit_team
        if request.executive_summary:
            audit.executive_summary = request.executive_summary
        if request.recommendations is not None:
            audit.recommendations = request.recommendations
        
        audit.updated_at = datetime.now()
        
        return audit
    
    async def create_asset(self, request: CreateAssetRequest) -> Asset:
        """Crée un nouvel asset"""
        asset = Asset(
            name=request.name,
            type=request.type,
            description=request.description,
            ip_address=request.ip_address,
            hostname=request.hostname,
            operating_system=request.operating_system,
            owner=request.owner,
            criticality=request.criticality,
            in_scope_frameworks=request.in_scope_frameworks
        )
        
        self.assets[asset.id] = asset
        logger.info(f"Nouvel asset créé: {asset.name}")
        
        return asset
    
    async def create_scope(self, request: CreateScopeRequest) -> AuditScope:
        """Crée un nouveau scope d'audit"""
        scope = AuditScope(
            name=request.name,
            description=request.description,
            frameworks=request.frameworks,
            control_ids=request.control_ids,
            asset_ids=request.asset_ids,
            audit_frequency=request.audit_frequency,
            created_by=request.created_by
        )
        
        self.scopes[scope.id] = scope
        logger.info(f"Nouveau scope créé: {scope.name}")
        
        return scope
    
    async def create_finding(self, request: CreateFindingRequest) -> Finding:
        """Crée un nouveau finding"""
        finding = Finding(
            title=request.title,
            description=request.description,
            severity=request.severity,
            audit_id=request.audit_id,
            control_id=request.control_id,
            asset_id=request.asset_id,
            evidence=request.evidence,
            test_method=request.test_method,
            business_impact=request.business_impact,
            remediation_recommendation=request.remediation_recommendation,
            created_by=request.created_by
        )
        
        self.findings[finding.id] = finding
        self.performance_stats["findings_identified"] += 1
        logger.info(f"Nouveau finding créé: {finding.title}")
        
        return finding
    
    async def update_finding(self, finding_id: str, request: UpdateFindingRequest) -> Finding:
        """Met à jour un finding"""
        if finding_id not in self.findings:
            raise ValueError(f"Finding {finding_id} non trouvé")
        
        finding = self.findings[finding_id]
        
        if request.status:
            finding.status = request.status
            if request.status == FindingStatus.RESOLVED:
                finding.resolved_date = datetime.now()
                finding.resolved_by = request.updated_by
        if request.assigned_to is not None:
            finding.assigned_to = request.assigned_to
            finding.assigned_date = datetime.now()
        if request.resolution_details is not None:
            finding.resolution_details = request.resolution_details
        if request.verification_evidence is not None:
            finding.verification_evidence = request.verification_evidence
        
        finding.updated_at = datetime.now()
        
        return finding
    
    async def create_remediation_plan(self, request: CreateRemediationPlanRequest) -> RemediationPlan:
        """Crée un nouveau plan de remédiation"""
        plan = RemediationPlan(
            name=request.name,
            description=request.description,
            audit_id=request.audit_id,
            finding_ids=request.finding_ids,
            planned_start_date=request.planned_start_date,
            planned_end_date=request.planned_end_date,
            assigned_team=request.assigned_team,
            project_manager=request.project_manager,
            created_by=request.created_by
        )
        
        self.remediation_plans[plan.id] = plan
        logger.info(f"Nouveau plan de remédiation créé: {plan.name}")
        
        return plan
    
    async def search_audits(self, request: AuditSearchRequest) -> Tuple[List[Audit], int]:
        """Recherche des audits"""
        results = []
        
        for audit in self.audits.values():
            # Appliquer filtres
            if request.query and request.query.lower() not in audit.name.lower() and request.query.lower() not in audit.description.lower():
                continue
            
            if request.type and audit.type != request.type:
                continue
            
            if request.status and audit.status not in request.status:
                continue
            
            if request.frameworks and not any(f in audit.frameworks for f in request.frameworks):
                continue
            
            if request.lead_auditor and audit.lead_auditor != request.lead_auditor:
                continue
            
            if request.date_from and audit.created_at.date() < request.date_from:
                continue
            
            if request.date_to and audit.created_at.date() > request.date_to:
                continue
            
            results.append(audit)
        
        # Trier par date de création
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        total = len(results)
        paginated_results = results[request.offset:request.offset + request.limit]
        
        return paginated_results, total
    
    async def search_findings(self, request: FindingSearchRequest) -> Tuple[List[Finding], int]:
        """Recherche des findings"""
        results = []
        
        for finding in self.findings.values():
            # Appliquer filtres
            if request.query and request.query.lower() not in finding.title.lower() and request.query.lower() not in finding.description.lower():
                continue
            
            if request.severity and finding.severity not in request.severity:
                continue
            
            if request.status and finding.status not in request.status:
                continue
            
            if request.audit_id and finding.audit_id != request.audit_id:
                continue
            
            if request.control_id and finding.control_id != request.control_id:
                continue
            
            if request.assigned_to and finding.assigned_to != request.assigned_to:
                continue
            
            if request.date_from and finding.created_at.date() < request.date_from:
                continue
            
            if request.date_to and finding.created_at.date() > request.date_to:
                continue
            
            results.append(finding)
        
        # Trier par sévérité puis date
        severity_order = {
            FindingSeverity.CRITICAL: 4,
            FindingSeverity.HIGH: 3,
            FindingSeverity.MEDIUM: 2,
            FindingSeverity.LOW: 1,
            FindingSeverity.INFORMATIONAL: 0
        }
        results.sort(key=lambda x: (severity_order.get(x.severity, 0), x.created_at), reverse=True)
        
        # Pagination
        total = len(results)
        paginated_results = results[request.offset:request.offset + request.limit]
        
        return paginated_results, total
    
    def get_audit_statistics(self) -> AuditStatistics:
        """Statistiques des audits"""
        total_audits = len(self.audits)
        
        by_status = {}
        by_type = {}
        by_framework = defaultdict(int)
        total_compliance_score = 0.0
        audits_with_score = 0
        
        for audit in self.audits.values():
            by_status[audit.status.value] = by_status.get(audit.status.value, 0) + 1
            by_type[audit.type.value] = by_type.get(audit.type.value, 0) + 1
            
            for framework in audit.frameworks:
                by_framework[framework.value] += 1
            
            if audit.overall_compliance_score is not None:
                total_compliance_score += audit.overall_compliance_score
                audits_with_score += 1
        
        # Statistiques des findings
        total_findings = len(self.findings)
        findings_by_severity = {}
        resolved_findings = 0
        
        for finding in self.findings.values():
            findings_by_severity[finding.severity.value] = findings_by_severity.get(finding.severity.value, 0) + 1
            if finding.status == FindingStatus.RESOLVED:
                resolved_findings += 1
        
        return AuditStatistics(
            total_audits=total_audits,
            by_status=by_status,
            by_type=by_type,
            by_framework=dict(by_framework),
            average_compliance_score=total_compliance_score / max(audits_with_score, 1),
            total_findings=total_findings,
            findings_by_severity=findings_by_severity,
            remediation_rate=(resolved_findings / max(total_findings, 1)) * 100,
            audit_frequency_compliance=85.0  # Métrique simulée
        )
    
    def get_finding_statistics(self) -> FindingStatistics:
        """Statistiques des findings"""
        total_findings = len(self.findings)
        
        by_severity = {}
        by_status = {}
        by_framework = defaultdict(int)
        resolution_times = []
        overdue_findings = 0
        
        now = datetime.now()
        
        for finding in self.findings.values():
            by_severity[finding.severity.value] = by_severity.get(finding.severity.value, 0) + 1
            by_status[finding.status.value] = by_status.get(finding.status.value, 0) + 1
            
            # Framework du finding (via le contrôle)
            control = self.controls.get(finding.control_id)
            if control:
                by_framework[control.framework.value] += 1
            
            # Temps de résolution
            if finding.resolved_date and finding.created_at:
                resolution_time = (finding.resolved_date - finding.created_at).days
                resolution_times.append(resolution_time)
            
            # Findings en retard
            if finding.due_date and finding.due_date < now and finding.status not in [FindingStatus.RESOLVED, FindingStatus.ACCEPTED_RISK]:
                overdue_findings += 1
        
        # Statistiques de remédiation
        remediation_progress = {}
        for plan in self.remediation_plans.values():
            remediation_progress[plan.status.value] = remediation_progress.get(plan.status.value, 0) + 1
        
        return FindingStatistics(
            total_findings=total_findings,
            by_severity=by_severity,
            by_status=by_status,
            by_framework=dict(by_framework),
            avg_resolution_time_days=sum(resolution_times) / max(len(resolution_times), 1),
            open_critical_findings=by_severity.get(FindingSeverity.CRITICAL.value, 0) if by_status.get(FindingStatus.OPEN.value, 0) > 0 else 0,
            overdue_findings=overdue_findings,
            remediation_progress=remediation_progress
        )
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Statut du moteur d'audit"""
        now = datetime.now()
        uptime = (now - self.performance_stats["start_time"]).total_seconds()
        
        active_audits = len([a for a in self.audits.values() if a.status in [AuditStatus.RUNNING, AuditStatus.SCHEDULED]])
        open_findings = len([f for f in self.findings.values() if f.status == FindingStatus.OPEN])
        
        return {
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "uptime_formatted": str(timedelta(seconds=int(uptime))),
            "performance": self.performance_stats,
            "active_audits": active_audits,
            "total_audits": len(self.audits),
            "open_findings": open_findings,
            "total_findings": len(self.findings),
            "assets_monitored": len(self.assets),
            "frameworks_supported": len(self.framework_definitions),
            "controls_loaded": len(self.controls),
            "remediation_plans": len(self.remediation_plans),
            "compliance_snapshots": len(self.compliance_snapshots)
        }