"""
Risk Assessment Module - Risk Analysis Engine
Moteur d'analyse des risques cybersécurité
"""
import uuid
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from .models import (
    Asset, ThreatActor, Threat, Vulnerability, RiskItem, RiskAssessmentResult,
    RiskTreatmentOption, RiskMatrix, RiskLevel, LikelihoodLevel, ImpactLevel,
    RiskCategory, ThreatActorType, AssessmentType, ComplianceFramework
)

class RiskAssessmentEngine:
    """Moteur principal d'évaluation des risques"""
    
    def __init__(self):
        self.risk_matrix = self._create_default_risk_matrix()
        self.threat_actors = self._load_threat_actors()
        self.frameworks = self._load_compliance_frameworks()
        
    def _create_default_risk_matrix(self) -> RiskMatrix:
        """Crée une matrice de risque par défaut"""
        return RiskMatrix(
            matrix_id="default_matrix",
            name="Matrice de Risque Standard NIST",
            likelihood_levels=[
                {"level": "very_low", "value": 1, "description": "Très improbable (< 5%)"},
                {"level": "low", "value": 2, "description": "Improbable (5-25%)"},
                {"level": "medium", "value": 3, "description": "Possible (25-75%)"},
                {"level": "high", "value": 4, "description": "Probable (75-95%)"},
                {"level": "very_high", "value": 5, "description": "Très probable (> 95%)"}
            ],
            impact_levels=[
                {"level": "very_low", "value": 1, "description": "Impact négligeable"},
                {"level": "low", "value": 2, "description": "Impact mineur"},
                {"level": "medium", "value": 3, "description": "Impact modéré"},
                {"level": "high", "value": 4, "description": "Impact majeur"},
                {"level": "very_high", "value": 5, "description": "Impact catastrophique"}
            ],
            risk_scoring={
                "very_low": {"very_low": 1, "low": 2, "medium": 3, "high": 4, "very_high": 5},
                "low": {"very_low": 2, "low": 4, "medium": 6, "high": 8, "very_high": 10},
                "medium": {"very_low": 3, "low": 6, "medium": 9, "high": 12, "very_high": 15},
                "high": {"very_low": 4, "low": 8, "medium": 12, "high": 16, "very_high": 20},
                "very_high": {"very_low": 5, "low": 10, "medium": 15, "high": 20, "very_high": 25}
            },
            risk_thresholds={
                "very_low": 2,
                "low": 6,
                "medium": 12,
                "high": 20,
                "critical": 25
            }
        )
    
    def _load_threat_actors(self) -> List[ThreatActor]:
        """Charge les acteurs de menace connus"""
        return [
            ThreatActor(
                actor_id="ta_cybercriminal",
                name="Cybercriminels Opportunistes",
                type=ThreatActorType.CYBERCRIMINAL,
                sophistication="medium",
                motivation=["financial_gain", "data_theft"],
                capabilities=["malware", "phishing", "social_engineering", "ransomware"],
                target_preferences=["financial_data", "personal_information", "business_systems"]
            ),
            ThreatActor(
                actor_id="ta_nation_state",
                name="Acteur Étatique APT",
                type=ThreatActorType.NATION_STATE,
                sophistication="very_high",
                motivation=["espionage", "sabotage", "strategic_advantage"],
                capabilities=["advanced_malware", "zero_day_exploits", "supply_chain_attacks", "infrastructure_targeting"],
                target_preferences=["government", "critical_infrastructure", "intellectual_property"]
            ),
            ThreatActor(
                actor_id="ta_insider",
                name="Menace Interne",
                type=ThreatActorType.INSIDER,
                sophistication="medium",
                motivation=["revenge", "financial_gain", "ideology"],
                capabilities=["legitimate_access", "data_exfiltration", "system_sabotage"],
                target_preferences=["sensitive_data", "business_systems", "customer_information"]
            ),
            ThreatActor(
                actor_id="ta_hacktivist",
                name="Hacktivistes",
                type=ThreatActorType.HACKTIVIST,
                sophistication="medium",
                motivation=["ideology", "protest", "publicity"],
                capabilities=["ddos", "website_defacement", "data_leaks", "social_media_attacks"],
                target_preferences=["public_systems", "websites", "social_media"]
            )
        ]
    
    def _load_compliance_frameworks(self) -> List[ComplianceFramework]:
        """Charge les frameworks de conformité"""
        return [
            ComplianceFramework(
                framework_id="nist_csf",
                name="NIST Cybersecurity Framework",
                description="Framework de cybersécurité du NIST",
                version="1.1",
                controls=[
                    {"id": "ID.AM", "category": "Identify", "subcategory": "Asset Management"},
                    {"id": "PR.AC", "category": "Protect", "subcategory": "Access Control"},
                    {"id": "DE.AE", "category": "Detect", "subcategory": "Anomalies and Events"},
                    {"id": "RS.RP", "category": "Respond", "subcategory": "Response Planning"},
                    {"id": "RC.RP", "category": "Recover", "subcategory": "Recovery Planning"}
                ],
                risk_categories=["technical", "operational", "strategic"],
                assessment_criteria={"maturity_levels": 5, "scoring": "qualitative"}
            ),
            ComplianceFramework(
                framework_id="iso27001",
                name="ISO 27001:2013",
                description="Norme internationale pour la gestion de la sécurité de l'information",
                version="2013",
                controls=[
                    {"id": "A.8", "category": "Asset management"},
                    {"id": "A.9", "category": "Access control"},
                    {"id": "A.12", "category": "Operations security"},
                    {"id": "A.16", "category": "Information security incident management"}
                ],
                risk_categories=["technical", "operational", "regulatory"],
                assessment_criteria={"approach": "risk_based", "controls": 114}
            )
        ]
    
    async def conduct_risk_assessment(self, request) -> RiskAssessmentResult:
        """Conduit une évaluation complète des risques"""
        assessment_id = str(uuid.uuid4())
        
        # Génère les actifs basés sur le scope
        assets = self._generate_assets(request.scope, request.target_identifier)
        
        # Identifie les menaces applicables
        threats = self._identify_threats(assets, request.assessment_type)
        
        # Découvre les vulnérabilités
        vulnerabilities = []
        if request.include_vulnerability_scan:
            vulnerabilities = self._discover_vulnerabilities(assets)
        
        # Évalue les risques
        risks = self._assess_risks(assets, threats, vulnerabilities)
        
        # Génère les options de traitement
        treatment_options = self._generate_treatment_options(risks)
        
        # Calcule les métriques globales
        risk_summary = self._calculate_risk_summary(risks)
        overall_risk_score = self._calculate_overall_risk_score(risks)
        overall_risk_level = self._determine_risk_level(overall_risk_score)
        
        # Génère les recommandations
        recommendations = self._generate_recommendations(risks, request.frameworks)
        
        return RiskAssessmentResult(
            assessment_id=assessment_id,
            assessment_name=request.assessment_name,
            scope=request.scope,
            target_identifier=request.target_identifier,
            assessment_type=request.assessment_type,
            status="completed",
            created_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
            frameworks_used=request.frameworks,
            total_assets=len(assets),
            total_threats=len(threats),
            total_vulnerabilities=len(vulnerabilities),
            total_risks=len(risks),
            risk_summary=risk_summary,
            overall_risk_score=overall_risk_score,
            overall_risk_level=overall_risk_level,
            assets=assets,
            threats=self.threat_actors,  # Utilise les threat actors globaux
            vulnerabilities=vulnerabilities,
            risks=risks,
            treatment_options=treatment_options,
            recommendations=recommendations
        )
    
    def _generate_assets(self, scope: str, target_identifier: str) -> List[Asset]:
        """Génère les actifs basés sur le scope d'évaluation"""
        assets = []
        
        # Types d'actifs selon le scope
        if scope == "organization":
            asset_types = ["server", "workstation", "database", "application", "network_device", "mobile_device"]
            asset_count = random.randint(50, 200)
        elif scope == "department":
            asset_types = ["server", "workstation", "application", "database"]
            asset_count = random.randint(20, 80)
        elif scope == "project":
            asset_types = ["application", "database", "server"]
            asset_count = random.randint(5, 30)
        else:  # asset specific
            asset_types = ["server"]
            asset_count = random.randint(1, 5)
        
        for i in range(asset_count):
            asset_type = random.choice(asset_types)
            criticality = random.choice(["low", "medium", "high", "critical"])
            value = {"low": 1, "medium": 2, "high": 3, "critical": 4}[criticality] + random.randint(0, 1)
            
            assets.append(Asset(
                asset_id=str(uuid.uuid4()),
                name=f"{asset_type}_{target_identifier}_{i+1}",
                type=asset_type,
                category="hardware" if asset_type in ["server", "workstation", "network_device"] else "software",
                value=value,
                criticality=criticality,
                location=f"Site_{random.randint(1, 5)}",
                owner=f"team_{random.choice(['it', 'security', 'ops', 'dev'])}",
                dependencies=[],
                vulnerabilities=[]
            ))
        
        return assets
    
    def _identify_threats(self, assets: List[Asset], assessment_type: AssessmentType) -> List[Threat]:
        """Identifie les menaces applicables aux actifs"""
        threats = []
        
        # Menaces communes selon le type d'actif
        threat_mapping = {
            "server": ["malware", "unauthorized_access", "ddos", "data_breach"],
            "workstation": ["malware", "phishing", "insider_threat", "physical_theft"],
            "database": ["sql_injection", "data_breach", "unauthorized_access", "backup_failure"],
            "application": ["code_injection", "authentication_bypass", "data_exposure", "api_abuse"],
            "network_device": ["configuration_tampering", "unauthorized_access", "ddos", "firmware_exploit"],
            "mobile_device": ["malware", "data_leakage", "physical_theft", "insecure_communication"]
        }
        
        # Génère les menaces pour chaque type d'actif présent
        asset_types = list(set(asset.type for asset in assets))
        
        for asset_type in asset_types:
            applicable_threats = threat_mapping.get(asset_type, ["generic_attack"])
            
            for threat_name in applicable_threats:
                # Détermine la probabilité basée sur le type d'évaluation
                if assessment_type == AssessmentType.COMPREHENSIVE:
                    likelihood = random.choice(list(LikelihoodLevel))
                else:
                    # Pour les évaluations rapides, focus sur les menaces plus probables
                    likelihood = random.choice([LikelihoodLevel.MEDIUM, LikelihoodLevel.HIGH, LikelihoodLevel.VERY_HIGH])
                
                threats.append(Threat(
                    threat_id=str(uuid.uuid4()),
                    name=threat_name.replace("_", " ").title(),
                    description=f"Menace {threat_name} ciblant les actifs {asset_type}",
                    category=self._categorize_threat(threat_name),
                    threat_actors=[random.choice(self.threat_actors).actor_id],
                    attack_vectors=self._get_attack_vectors(threat_name),
                    targeted_assets=[asset.asset_id for asset in assets if asset.type == asset_type],
                    likelihood=likelihood,
                    impact_types=["confidentiality", "integrity", "availability"]
                ))
        
        return threats
    
    def _categorize_threat(self, threat_name: str) -> str:
        """Catégorise une menace"""
        categories = {
            "malware": "malware",
            "phishing": "social_engineering",
            "ddos": "network",
            "sql_injection": "application",
            "unauthorized_access": "access_control",
            "data_breach": "data_security",
            "insider_threat": "insider",
            "physical_theft": "physical"
        }
        return categories.get(threat_name, "other")
    
    def _get_attack_vectors(self, threat_name: str) -> List[str]:
        """Retourne les vecteurs d'attaque pour une menace"""
        vectors = {
            "malware": ["email", "web", "usb", "network"],
            "phishing": ["email", "social_media", "phone"],
            "ddos": ["network", "application"],
            "sql_injection": ["web_application"],
            "unauthorized_access": ["network", "physical", "credential_theft"],
            "data_breach": ["network", "application", "database"],
            "insider_threat": ["legitimate_access"],
            "physical_theft": ["physical_access"]
        }
        return vectors.get(threat_name, ["unknown"])
    
    def _discover_vulnerabilities(self, assets: List[Asset]) -> List[Vulnerability]:
        """Découvre les vulnérabilités potentielles"""
        vulnerabilities = []
        
        # Vulnérabilités communes par type d'actif
        vuln_templates = {
            "server": [
                {"name": "OS Patch Missing", "severity": "high", "cvss": 7.5},
                {"name": "Weak Authentication", "severity": "medium", "cvss": 5.3},
                {"name": "Unencrypted Communication", "severity": "medium", "cvss": 5.9}
            ],
            "application": [
                {"name": "SQL Injection", "severity": "critical", "cvss": 9.1},
                {"name": "Cross-Site Scripting", "severity": "medium", "cvss": 6.1},
                {"name": "Insecure Direct Object Reference", "severity": "high", "cvss": 7.7}
            ],
            "database": [
                {"name": "Default Credentials", "severity": "critical", "cvss": 9.8},
                {"name": "Unencrypted Data", "severity": "high", "cvss": 7.2},
                {"name": "Excessive Privileges", "severity": "medium", "cvss": 5.4}
            ]
        }
        
        for asset in assets:
            if asset.type in vuln_templates:
                # Génère 1-3 vulnérabilités par actif
                num_vulns = random.randint(1, 3)
                asset_vulns = random.sample(vuln_templates[asset.type], min(num_vulns, len(vuln_templates[asset.type])))
                
                for vuln_template in asset_vulns:
                    vuln_id = str(uuid.uuid4())
                    vulnerabilities.append(Vulnerability(
                        vulnerability_id=vuln_id,
                        name=vuln_template["name"],
                        description=f"{vuln_template['name']} détectée sur {asset.name}",
                        cve_id=f"CVE-2024-{random.randint(1000, 9999)}" if random.random() > 0.3 else None,
                        cvss_score=vuln_template["cvss"],
                        severity=vuln_template["severity"],
                        affected_assets=[asset.asset_id],
                        exploit_available=random.random() > 0.6,
                        patch_available=random.random() > 0.4,
                        remediation_effort=random.choice(["low", "medium", "high"])
                    ))
                    
                    # Ajoute la vulnérabilité à l'actif
                    asset.vulnerabilities.append(vuln_id)
        
        return vulnerabilities
    
    def _assess_risks(self, assets: List[Asset], threats: List[Threat], vulnerabilities: List[Vulnerability]) -> List[RiskItem]:
        """Évalue les risques en croisant menaces, vulnérabilités et actifs"""
        risks = []
        
        for threat in threats:
            for asset_id in threat.targeted_assets:
                asset = next((a for a in assets if a.asset_id == asset_id), None)
                if not asset:
                    continue
                
                # Trouve les vulnérabilités applicables
                applicable_vulns = [v for v in vulnerabilities if asset_id in v.affected_assets]
                
                if applicable_vulns:
                    # Risque avec vulnérabilité spécifique
                    for vuln in applicable_vulns:
                        risk = self._calculate_risk(threat, asset, vuln)
                        risks.append(risk)
                else:
                    # Risque général sans vulnérabilité spécifique
                    risk = self._calculate_risk(threat, asset, None)
                    risks.append(risk)
        
        return risks
    
    def _calculate_risk(self, threat: Threat, asset: Asset, vulnerability: Optional[Vulnerability] = None) -> RiskItem:
        """Calcule un risque spécifique"""
        
        # Détermine l'impact basé sur la criticité de l'actif
        impact_mapping = {
            "low": ImpactLevel.LOW,
            "medium": ImpactLevel.MEDIUM,
            "high": ImpactLevel.HIGH,
            "critical": ImpactLevel.VERY_HIGH
        }
        
        impact = impact_mapping.get(asset.criticality, ImpactLevel.MEDIUM)
        
        # Ajuste la probabilité si vulnérabilité présente
        likelihood = threat.likelihood
        if vulnerability:
            # Augmente la probabilité si vulnérabilité exploitable
            if vulnerability.exploit_available:
                likelihood_values = list(LikelihoodLevel)
                current_index = likelihood_values.index(likelihood)
                if current_index < len(likelihood_values) - 1:
                    likelihood = likelihood_values[current_index + 1]
        
        # Calcule le score de risque
        likelihood_value = self._get_likelihood_value(likelihood)
        impact_value = self._get_impact_value(impact)
        risk_score = likelihood_value * impact_value
        
        # Simule l'effet des contrôles existants
        existing_controls = self._get_existing_controls(threat.category, asset.type)
        control_effectiveness = random.choice(["low", "medium", "high"])
        
        # Calcule le risque résiduel
        control_reduction = {"low": 0.1, "medium": 0.3, "high": 0.5}[control_effectiveness]
        residual_risk_score = risk_score * (1 - control_reduction)
        
        # Détermine les niveaux de risque
        risk_level = self._determine_risk_level(risk_score)
        residual_risk_level = self._determine_risk_level(residual_risk_score)
        
        # Détermine la catégorie de risque
        category = self._determine_risk_category(threat.category, asset.type)
        
        risk_id = str(uuid.uuid4())
        title = f"{threat.name} sur {asset.name}"
        if vulnerability:
            title += f" (via {vulnerability.name})"
        
        return RiskItem(
            risk_id=risk_id,
            title=title,
            description=f"Risque de {threat.name} affectant {asset.name} avec impact {impact.value}",
            category=category,
            threat_id=threat.threat_id,
            vulnerability_id=vulnerability.vulnerability_id if vulnerability else None,
            affected_assets=[asset.asset_id],
            likelihood=likelihood,
            impact=impact,
            risk_score=risk_score,
            risk_level=risk_level,
            existing_controls=existing_controls,
            control_effectiveness=control_effectiveness,
            residual_risk_score=residual_risk_score,
            residual_risk_level=residual_risk_level
        )
    
    def _get_likelihood_value(self, likelihood: LikelihoodLevel) -> float:
        """Convertit le niveau de probabilité en valeur numérique"""
        mapping = {
            LikelihoodLevel.VERY_LOW: 1,
            LikelihoodLevel.LOW: 2,
            LikelihoodLevel.MEDIUM: 3,
            LikelihoodLevel.HIGH: 4,
            LikelihoodLevel.VERY_HIGH: 5
        }
        return mapping[likelihood]
    
    def _get_impact_value(self, impact: ImpactLevel) -> float:
        """Convertit le niveau d'impact en valeur numérique"""
        mapping = {
            ImpactLevel.VERY_LOW: 1,
            ImpactLevel.LOW: 2,
            ImpactLevel.MEDIUM: 3,
            ImpactLevel.HIGH: 4,
            ImpactLevel.VERY_HIGH: 5
        }
        return mapping[impact]
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Détermine le niveau de risque basé sur le score"""
        if risk_score <= 4:
            return RiskLevel.LOW
        elif risk_score <= 9:
            return RiskLevel.MEDIUM
        elif risk_score <= 16:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _determine_risk_category(self, threat_category: str, asset_type: str) -> RiskCategory:
        """Détermine la catégorie de risque"""
        if threat_category in ["malware", "network", "application"]:
            return RiskCategory.TECHNICAL
        elif threat_category in ["insider", "physical"]:
            return RiskCategory.OPERATIONAL
        elif threat_category in ["data_security"]:
            return RiskCategory.REGULATORY
        else:
            return RiskCategory.OPERATIONAL
    
    def _get_existing_controls(self, threat_category: str, asset_type: str) -> List[str]:
        """Retourne les contrôles existants supposés"""
        controls = {
            "malware": ["antivirus", "email_filtering", "web_filtering"],
            "network": ["firewall", "ids_ips", "network_segmentation"],
            "application": ["waf", "code_review", "input_validation"],
            "physical": ["access_control", "surveillance", "security_guards"],
            "insider": ["background_checks", "privilege_management", "monitoring"]
        }
        return controls.get(threat_category, ["basic_security"])
    
    def _generate_treatment_options(self, risks: List[RiskItem]) -> List[RiskTreatmentOption]:
        """Génère les options de traitement pour les risques"""
        treatment_options = []
        
        for risk in risks:
            # Génère 2-4 options de traitement par risque
            num_options = random.randint(2, 4)
            
            for i in range(num_options):
                treatment_type = random.choice(["mitigate", "accept", "transfer", "avoid"])
                
                option = RiskTreatmentOption(
                    option_id=str(uuid.uuid4()),
                    risk_id=risk.risk_id,
                    treatment_type=treatment_type,
                    description=self._get_treatment_description(treatment_type, risk),
                    implementation_cost=random.randint(1, 5),
                    implementation_time=random.choice(["1-2 semaines", "1-2 mois", "3-6 mois", "6-12 mois"]),
                    effectiveness=random.choice(["low", "medium", "high"]),
                    priority=self._calculate_treatment_priority(risk, treatment_type),
                    recommended=(i == 0 and risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL])
                )
                
                treatment_options.append(option)
        
        return treatment_options
    
    def _get_treatment_description(self, treatment_type: str, risk: RiskItem) -> str:
        """Génère une description pour l'option de traitement"""
        descriptions = {
            "mitigate": f"Implémenter des contrôles supplémentaires pour réduire {risk.title.lower()}",
            "accept": f"Accepter le risque {risk.title.lower()} avec surveillance continue",
            "transfer": f"Transférer le risque {risk.title.lower()} via assurance ou tiers",
            "avoid": f"Éviter le risque {risk.title.lower()} en éliminant l'activité ou l'actif"
        }
        return descriptions[treatment_type]
    
    def _calculate_treatment_priority(self, risk: RiskItem, treatment_type: str) -> int:
        """Calcule la priorité de traitement"""
        base_priority = {
            RiskLevel.CRITICAL: 5,
            RiskLevel.HIGH: 4,
            RiskLevel.MEDIUM: 3,
            RiskLevel.LOW: 2,
            RiskLevel.VERY_LOW: 1
        }[risk.risk_level]
        
        # Ajuste selon le type de traitement
        if treatment_type == "mitigate" and risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return min(5, base_priority + 1)
        
        return base_priority
    
    def _calculate_risk_summary(self, risks: List[RiskItem]) -> Dict[str, int]:
        """Calcule le résumé des risques par niveau"""
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "very_low": 0
        }
        
        for risk in risks:
            summary[risk.risk_level.value] += 1
        
        return summary
    
    def _calculate_overall_risk_score(self, risks: List[RiskItem]) -> float:
        """Calcule le score de risque global"""
        if not risks:
            return 0.0
        
        # Pondère les risques selon leur niveau
        weights = {
            RiskLevel.CRITICAL: 5,
            RiskLevel.HIGH: 4,
            RiskLevel.MEDIUM: 3,
            RiskLevel.LOW: 2,
            RiskLevel.VERY_LOW: 1
        }
        
        weighted_sum = sum(weights[risk.risk_level] * risk.residual_risk_score for risk in risks)
        max_possible = len(risks) * weights[RiskLevel.CRITICAL] * 25  # Score max possible
        
        return round((weighted_sum / max_possible) * 100, 2) if max_possible > 0 else 0.0
    
    def _generate_recommendations(self, risks: List[RiskItem], frameworks: List[str]) -> List[str]:
        """Génère les recommandations basées sur l'évaluation"""
        recommendations = []
        
        # Recommandations basées sur les niveaux de risque
        critical_risks = [r for r in risks if r.risk_level == RiskLevel.CRITICAL]
        high_risks = [r for r in risks if r.risk_level == RiskLevel.HIGH]
        
        if critical_risks:
            recommendations.append(f"🚨 URGENT: {len(critical_risks)} risque(s) critique(s) nécessitent une action immédiate")
        
        if high_risks:
            recommendations.append(f"⚠️ {len(high_risks)} risque(s) de niveau élevé à traiter en priorité")
        
        # Recommandations par catégorie
        categories = {}
        for risk in risks:
            if risk.category not in categories:
                categories[risk.category] = []
            categories[risk.category].append(risk)
        
        for category, category_risks in categories.items():
            if len(category_risks) > 5:
                recommendations.append(f"📊 Révision des contrôles {category.value} recommandée ({len(category_risks)} risques)")
        
        # Recommandations génériques
        recommendations.extend([
            "🔍 Effectuer des évaluations de risque trimestrielles",
            "📚 Mettre à jour les procédures de gestion des risques",
            "🎓 Former le personnel sur la gestion des risques",
            "📈 Surveiller en continu l'évolution du paysage des menaces"
        ])
        
        return recommendations

# Instance globale du moteur d'évaluation des risques
risk_assessment_engine = RiskAssessmentEngine()