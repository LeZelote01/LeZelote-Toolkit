"""
Cyber AI - IA spécialisée cybersécurité CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - Intelligence artificielle dédiée aux analyses de sécurité avancées
"""
import asyncio
import json
import uuid
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from fastapi import HTTPException
from pydantic import BaseModel, Field

# Intégration Emergent LLM
try:
    from emergentintegrations import EmergentLLM
except ImportError:
    print("⚠️ EmergentLLM non disponible pour Cyber AI - Mode fallback activé")
    EmergentLLM = None

from backend.config import settings
from backend.database import get_collection

# Modèles de données Cyber AI
class ThreatAnalysisRequest(BaseModel):
    target: str = Field(..., description="Cible à analyser (IP, domaine, fichier, etc.)")
    analysis_type: str = Field(..., description="Type d'analyse: network, malware, behavioral, code")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexte supplémentaire")
    severity_threshold: Optional[str] = Field("medium", description="Seuil de sévérité: low, medium, high, critical")

class VulnerabilityPrediction(BaseModel):
    vulnerability_score: float = Field(..., description="Score de vulnérabilité (0-100)")
    risk_level: str = Field(..., description="Niveau de risque: low, medium, high, critical")
    attack_vectors: List[str] = Field(..., description="Vecteurs d'attaque potentiels")
    mitigation_priority: int = Field(..., description="Priorité de remédiation (1-10)")
    predicted_exploitability: float = Field(..., description="Probabilité d'exploitation (0-1)")

class CyberAIAnalysisResult(BaseModel):
    target: str = Field(..., description="Cible analysée")
    analysis_type: str = Field(..., description="Type d'analyse effectuée")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    threat_score: float = Field(..., description="Score de menace global (0-100)")
    confidence_level: float = Field(..., description="Niveau de confiance de l'analyse (0-1)")
    vulnerabilities: List[VulnerabilityPrediction] = Field(..., description="Vulnérabilités identifiées")
    recommendations: List[str] = Field(..., description="Recommandations de sécurité")
    technical_details: Dict[str, Any] = Field(..., description="Détails techniques de l'analyse")
    ai_insights: str = Field(..., description="Analyse IA contextuelle")

class AttackSimulationRequest(BaseModel):
    attack_type: str = Field(..., description="Type d'attaque: phishing, malware, apt, insider_threat")
    target_profile: Dict[str, Any] = Field(..., description="Profil de la cible")
    scenario_parameters: Optional[Dict[str, Any]] = Field(None, description="Paramètres du scénario")

class CyberAIService:
    """Service IA Cybersécurité - Analyses avancées et prédictions"""
    
    def __init__(self):
        self.llm_client = None
        self.threat_database = self._initialize_threat_database()
        self.attack_patterns = self._load_attack_patterns()
        self.vulnerability_models = self._load_vulnerability_models()
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialise le client LLM pour Cyber AI"""
        try:
            if EmergentLLM and settings.emergent_llm_key:
                self.llm_client = EmergentLLM(
                    api_key=settings.emergent_llm_key,
                    default_provider=settings.default_llm_provider,
                    default_model=settings.default_llm_model
                )
                print("✅ Cyber AI initialisé avec Emergent LLM")
            else:
                print("⚠️ Cyber AI - Mode simulation activé")
        except Exception as e:
            print(f"❌ Erreur initialisation Cyber AI LLM: {e}")
    
    def _initialize_threat_database(self) -> Dict[str, Any]:
        """Initialise la base de données des menaces"""
        return {
            "malware_families": {
                "ransomware": ["lockbit", "conti", "ryuk", "maze", "sodinokibi"],
                "trojan": ["emotet", "trickbot", "dridex", "icedid", "qakbot"],
                "apt_groups": ["apt1", "apt28", "apt29", "lazarus", "carbanak"]
            },
            "attack_techniques": {
                "mitre_tactics": [
                    "initial_access", "execution", "persistence", "privilege_escalation",
                    "defense_evasion", "credential_access", "discovery", "lateral_movement",
                    "collection", "command_control", "exfiltration", "impact"
                ],
                "common_techniques": [
                    "T1566.001", "T1059.001", "T1055", "T1003", "T1078", "T1083", "T1021.001"
                ]
            },
            "vulnerability_patterns": {
                "owasp_top10": ["injection", "broken_auth", "sensitive_exposure", "xxe", "broken_access"],
                "cve_categories": ["buffer_overflow", "sql_injection", "xss", "privilege_escalation", "rce"]
            }
        }
    
    def _load_attack_patterns(self) -> Dict[str, Any]:
        """Charge les modèles de patterns d'attaque"""
        return {
            "phishing_indicators": [
                "suspicious_domains", "url_shorteners", "spelling_errors", "urgency_language", "brand_impersonation"
            ],
            "malware_signatures": [
                "file_entropy", "pe_sections", "api_calls", "network_behavior", "registry_modifications"
            ],
            "network_anomalies": [
                "traffic_spikes", "unusual_ports", "dns_tunneling", "beaconing", "lateral_movement"
            ]
        }
    
    def _load_vulnerability_models(self) -> Dict[str, Any]:
        """Charge les modèles de prédiction de vulnérabilités"""
        return {
            "cvss_weights": {
                "attack_vector": 0.3, "attack_complexity": 0.2,
                "privileges_required": 0.2, "user_interaction": 0.1,
                "scope": 0.1, "impact": 0.1
            },
            "exploitability_factors": [
                "public_exploit_available", "metasploit_module", "known_attacks",
                "vendor_patch_available", "attack_complexity_low"
            ]
        }
    
    async def analyze_threat(self, request: ThreatAnalysisRequest) -> CyberAIAnalysisResult:
        """Analyse approfondie de menace avec IA"""
        try:
            print(f"🧠 Cyber AI - Analyse de {request.target} (type: {request.analysis_type})")
            
            # Analyse selon le type
            if request.analysis_type == "network":
                analysis_result = await self._analyze_network_threat(request)
            elif request.analysis_type == "malware":
                analysis_result = await self._analyze_malware_threat(request)
            elif request.analysis_type == "behavioral":
                analysis_result = await self._analyze_behavioral_threat(request)
            elif request.analysis_type == "code":
                analysis_result = await self._analyze_code_security(request)
            else:
                analysis_result = await self._analyze_generic_threat(request)
            
            # Enrichissement avec IA
            ai_insights = await self._generate_ai_insights(request, analysis_result)
            
            # Sauvegarder l'analyse
            await self._save_analysis(request.target, analysis_result)
            
            return CyberAIAnalysisResult(
                target=request.target,
                analysis_type=request.analysis_type,
                threat_score=analysis_result["threat_score"],
                confidence_level=analysis_result["confidence_level"],
                vulnerabilities=analysis_result["vulnerabilities"],
                recommendations=analysis_result["recommendations"],
                technical_details=analysis_result["technical_details"],
                ai_insights=ai_insights
            )
            
        except Exception as e:
            print(f"❌ Erreur analyse Cyber AI: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur analyse cyber AI: {str(e)}")
    
    async def _analyze_network_threat(self, request: ThreatAnalysisRequest) -> Dict[str, Any]:
        """Analyse des menaces réseau"""
        # Simulation d'analyse réseau avancée
        threat_indicators = self._calculate_network_threat_indicators(request.target)
        
        vulnerabilities = []
        recommendations = []
        
        # Analyse des ports ouverts (simulation)
        open_ports = [22, 80, 443, 8080]  # Simulation
        for port in open_ports:
            vuln_score = self._calculate_port_vulnerability_score(port)
            if vuln_score > 30:
                vulnerability = VulnerabilityPrediction(
                    vulnerability_score=vuln_score,
                    risk_level=self._get_risk_level(vuln_score),
                    attack_vectors=[f"port_{port}_exploitation", "service_enumeration"],
                    mitigation_priority=self._calculate_mitigation_priority(vuln_score),
                    predicted_exploitability=vuln_score / 100
                )
                vulnerabilities.append(vulnerability)
                
                if port == 22:
                    recommendations.append("Sécuriser SSH: clés au lieu de mots de passe, fail2ban")
                elif port == 80:
                    recommendations.append("Rediriger HTTP vers HTTPS, désactiver si non nécessaire")
        
        return {
            "threat_score": threat_indicators["overall_score"],
            "confidence_level": 0.85,
            "vulnerabilities": vulnerabilities,
            "recommendations": recommendations,
            "technical_details": {
                "scan_method": "nmap_stealth",
                "ports_analyzed": open_ports,
                "threat_indicators": threat_indicators,
                "geolocation_risk": "medium"
            }
        }
    
    async def _analyze_malware_threat(self, request: ThreatAnalysisRequest) -> Dict[str, Any]:
        """Analyse des menaces malware"""
        # Simulation d'analyse malware avancée
        file_hash = request.target  # Supposons que target est un hash de fichier
        
        malware_indicators = {
            "entropy": 7.8,  # Haute entropie = potentiel packing
            "suspicious_apis": ["WriteProcessMemory", "CreateRemoteThread", "VirtualAllocEx"],
            "network_connections": 5,
            "registry_modifications": True,
            "packer_detected": "UPX"
        }
        
        # Score de menace basé sur les indicateurs
        threat_score = self._calculate_malware_threat_score(malware_indicators)
        
        vulnerabilities = [
            VulnerabilityPrediction(
                vulnerability_score=threat_score,
                risk_level=self._get_risk_level(threat_score),
                attack_vectors=["process_injection", "persistence_mechanism", "data_exfiltration"],
                mitigation_priority=9 if threat_score > 80 else 6,
                predicted_exploitability=0.9 if threat_score > 80 else 0.6
            )
        ]
        
        recommendations = [
            "Isoler le fichier en quarantaine",
            "Analyser en environnement sandbox",
            "Vérifier les IOCs sur le réseau",
            "Mettre à jour les signatures antivirus"
        ]
        
        return {
            "threat_score": threat_score,
            "confidence_level": 0.92,
            "vulnerabilities": vulnerabilities,
            "recommendations": recommendations,
            "technical_details": {
                "file_hash": file_hash,
                "malware_family": "trojan.generic" if threat_score > 70 else "suspicious",
                "indicators": malware_indicators,
                "yara_matches": ["suspicious_api_calls", "high_entropy"]
            }
        }
    
    async def _analyze_behavioral_threat(self, request: ThreatAnalysisRequest) -> Dict[str, Any]:
        """Analyse comportementale des menaces"""
        behavioral_patterns = {
            "login_anomalies": True,
            "data_access_patterns": "suspicious",
            "time_based_analysis": "after_hours_activity",
            "geolocation_changes": True,
            "privilege_escalation_attempts": 3
        }
        
        threat_score = self._calculate_behavioral_threat_score(behavioral_patterns)
        
        vulnerabilities = [
            VulnerabilityPrediction(
                vulnerability_score=threat_score,
                risk_level=self._get_risk_level(threat_score),
                attack_vectors=["insider_threat", "account_compromise", "privilege_abuse"],
                mitigation_priority=8,
                predicted_exploitability=0.7
            )
        ]
        
        recommendations = [
            "Renforcer la surveillance utilisateur",
            "Implémenter l'authentification multi-facteurs",
            "Réviser les permissions d'accès",
            "Activer l'audit détaillé"
        ]
        
        return {
            "threat_score": threat_score,
            "confidence_level": 0.78,
            "vulnerabilities": vulnerabilities,
            "recommendations": recommendations,
            "technical_details": {
                "analysis_period": "30_days",
                "behavioral_patterns": behavioral_patterns,
                "risk_indicators": ["anomalous_access", "suspicious_timing"]
            }
        }
    
    async def _analyze_code_security(self, request: ThreatAnalysisRequest) -> Dict[str, Any]:
        """Analyse de sécurité du code"""
        # Simulation d'analyse statique de code
        code_vulnerabilities = {
            "sql_injection": 2,
            "xss_vulnerabilities": 3,
            "hardcoded_credentials": 1,
            "insecure_crypto": 1,
            "path_traversal": 1
        }
        
        threat_score = sum(code_vulnerabilities.values()) * 12  # Score approximatif
        
        vulnerabilities = []
        recommendations = []
        
        for vuln_type, count in code_vulnerabilities.items():
            if count > 0:
                vuln_score = count * 20
                vulnerability = VulnerabilityPrediction(
                    vulnerability_score=vuln_score,
                    risk_level=self._get_risk_level(vuln_score),
                    attack_vectors=[vuln_type, "code_exploitation"],
                    mitigation_priority=8 if vuln_type in ["sql_injection", "xss_vulnerabilities"] else 6,
                    predicted_exploitability=0.8 if vuln_type == "sql_injection" else 0.6
                )
                vulnerabilities.append(vulnerability)
                
                # Recommandations spécifiques
                if vuln_type == "sql_injection":
                    recommendations.append("Utiliser des requêtes préparées/paramétrées")
                elif vuln_type == "xss_vulnerabilities":
                    recommendations.append("Implémenter l'échappement des données utilisateur")
                elif vuln_type == "hardcoded_credentials":
                    recommendations.append("Externaliser les credentials dans des variables d'environnement")
        
        return {
            "threat_score": min(threat_score, 100),
            "confidence_level": 0.88,
            "vulnerabilities": vulnerabilities,
            "recommendations": recommendations,
            "technical_details": {
                "scan_type": "static_analysis",
                "vulnerabilities_found": code_vulnerabilities,
                "lines_analyzed": 15000,
                "security_rules": "owasp_top10"
            }
        }
    
    async def _analyze_generic_threat(self, request: ThreatAnalysisRequest) -> Dict[str, Any]:
        """Analyse générique de menace"""
        threat_score = 65.0  # Score par défaut
        
        vulnerability = VulnerabilityPrediction(
            vulnerability_score=threat_score,
            risk_level=self._get_risk_level(threat_score),
            attack_vectors=["generic_attack"],
            mitigation_priority=5,
            predicted_exploitability=0.5
        )
        
        return {
            "threat_score": threat_score,
            "confidence_level": 0.65,
            "vulnerabilities": [vulnerability],
            "recommendations": ["Effectuer une analyse plus spécifique", "Surveiller l'activité"],
            "technical_details": {"analysis_type": "generic", "target": request.target}
        }
    
    def _calculate_network_threat_indicators(self, target: str) -> Dict[str, Any]:
        """Calcule les indicateurs de menace réseau"""
        # Simulation basée sur le target
        base_score = len(target) % 50 + 30
        
        return {
            "overall_score": base_score,
            "open_ports_risk": base_score * 0.3,
            "service_versions_risk": base_score * 0.2,
            "configuration_risk": base_score * 0.5
        }
    
    def _calculate_port_vulnerability_score(self, port: int) -> float:
        """Calcule le score de vulnérabilité d'un port"""
        # Ports à haut risque
        high_risk_ports = {22: 40, 23: 80, 21: 70, 3389: 60}
        medium_risk_ports = {80: 30, 443: 20, 8080: 35}
        
        if port in high_risk_ports:
            return high_risk_ports[port]
        elif port in medium_risk_ports:
            return medium_risk_ports[port]
        else:
            return 15  # Score de base pour les autres ports
    
    def _calculate_malware_threat_score(self, indicators: Dict[str, Any]) -> float:
        """Calcule le score de menace malware"""
        score = 0
        
        # Entropie élevée
        if indicators.get("entropy", 0) > 7:
            score += 30
        
        # APIs suspectes
        score += len(indicators.get("suspicious_apis", [])) * 15
        
        # Connexions réseau
        score += indicators.get("network_connections", 0) * 5
        
        # Modifications registre
        if indicators.get("registry_modifications"):
            score += 20
        
        # Packer détecté
        if indicators.get("packer_detected"):
            score += 25
        
        return min(score, 100)
    
    def _calculate_behavioral_threat_score(self, patterns: Dict[str, Any]) -> float:
        """Calcule le score de menace comportementale"""
        score = 0
        
        if patterns.get("login_anomalies"):
            score += 25
        
        if patterns.get("data_access_patterns") == "suspicious":
            score += 30
        
        if patterns.get("geolocation_changes"):
            score += 20
        
        score += patterns.get("privilege_escalation_attempts", 0) * 10
        
        return min(score, 100)
    
    def _get_risk_level(self, score: float) -> str:
        """Détermine le niveau de risque selon le score"""
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        else:
            return "low"
    
    def _calculate_mitigation_priority(self, score: float) -> int:
        """Calcule la priorité de remédiation"""
        if score >= 80:
            return 10
        elif score >= 60:
            return 8
        elif score >= 40:
            return 6
        else:
            return 4
    
    async def _generate_ai_insights(self, request: ThreatAnalysisRequest, analysis_result: Dict[str, Any]) -> str:
        """Génère des insights IA contextuels"""
        if self.llm_client:
            return await self._generate_llm_insights(request, analysis_result)
        else:
            return self._generate_fallback_insights(request, analysis_result)
    
    async def _generate_llm_insights(self, request: ThreatAnalysisRequest, analysis_result: Dict[str, Any]) -> str:
        """Génère des insights via LLM"""
        try:
            prompt = f"""En tant qu'expert cybersécurité senior, analysez ces résultats d'analyse de menace:

Cible: {request.target}
Type d'analyse: {request.analysis_type}
Score de menace: {analysis_result['threat_score']}/100
Niveau de confiance: {analysis_result['confidence_level']}

Fournissez une analyse experte incluant:
1. Évaluation du niveau de risque
2. Contexte de la menace dans l'écosystème actuel
3. Priorités d'action immédiate
4. Stratégies de remédiation à long terme
5. Indicateurs de surveillance continue

Réponse concise et actionnable pour un RSSI."""

            messages = [
                {"role": "system", "content": "Tu es un expert cybersécurité senior spécialisé dans l'analyse de menaces."},
                {"role": "user", "content": prompt}
            ]
            
            response = await asyncio.to_thread(
                self.llm_client.chat.completions.create,
                model=settings.default_llm_model,
                messages=messages,
                max_tokens=1500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"⚠️ Erreur insights LLM: {e}")
            return self._generate_fallback_insights(request, analysis_result)
    
    def _generate_fallback_insights(self, request: ThreatAnalysisRequest, analysis_result: Dict[str, Any]) -> str:
        """Génère des insights de fallback"""
        threat_score = analysis_result['threat_score']
        analysis_type = request.analysis_type
        
        if threat_score >= 80:
            urgency = "🚨 **CRITIQUE - ACTION IMMÉDIATE REQUISE**"
            priority = "Priorité maximale"
        elif threat_score >= 60:
            urgency = "⚠️ **ÉLEVÉ - Action rapide recommandée**"
            priority = "Priorité élevée"
        elif threat_score >= 40:
            urgency = "📋 **MOYEN - Surveillance renforcée**"
            priority = "Priorité modérée"
        else:
            urgency = "ℹ️ **FAIBLE - Surveillance standard**"
            priority = "Priorité faible"
        
        insights = f"""## {urgency}

### 🎯 Évaluation Cyber AI

**Score de menace:** {threat_score}/100 ({self._get_risk_level(threat_score).upper()})
**Type d'analyse:** {analysis_type.title()}
**Priorité:** {priority}

### 📊 Contexte de la menace
Basé sur l'analyse {analysis_type}, la cible présente {'un risque significatif' if threat_score > 60 else 'un niveau de risque modéré'} nécessitant {'une intervention immédiate' if threat_score > 80 else 'une surveillance appropriée'}.

### ⚡ Actions recommandées
1. **Immédiat:** {'Isolation et containment' if threat_score > 80 else 'Analyse approfondie'}
2. **Court terme:** Implémentation des recommandations de sécurité
3. **Long terme:** Surveillance continue et amélioration de la posture

### 🔍 Surveillance continue
- Monitoring des indicateurs identifiés
- Révision périodique des mesures de sécurité
- Mise à jour des règles de détection

*Analyse générée par Cyber AI v1.0 - CyberSec Toolkit Pro 2025*"""
        
        return insights
    
    async def simulate_attack(self, request: AttackSimulationRequest) -> Dict[str, Any]:
        """Simule un scénario d'attaque pour évaluer la résistance"""
        try:
            print(f"🎯 Cyber AI - Simulation d'attaque {request.attack_type}")
            
            # Simuler selon le type d'attaque
            if request.attack_type == "phishing":
                simulation_result = await self._simulate_phishing_attack(request)
            elif request.attack_type == "malware":
                simulation_result = await self._simulate_malware_attack(request)
            elif request.attack_type == "apt":
                simulation_result = await self._simulate_apt_attack(request)
            elif request.attack_type == "insider_threat":
                simulation_result = await self._simulate_insider_threat(request)
            else:
                simulation_result = await self._simulate_generic_attack(request)
            
            return simulation_result
            
        except Exception as e:
            print(f"❌ Erreur simulation attaque: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur simulation: {str(e)}")
    
    async def _simulate_phishing_attack(self, request: AttackSimulationRequest) -> Dict[str, Any]:
        """Simule une attaque de phishing"""
        success_probability = 0.3  # 30% de base
        
        # Ajustements basés sur le profil cible
        profile = request.target_profile
        if profile.get("security_awareness_training", False):
            success_probability *= 0.5
        
        if profile.get("email_filtering", "basic") == "advanced":
            success_probability *= 0.3
        
        return {
            "attack_type": "phishing",
            "success_probability": success_probability,
            "impact_assessment": "medium" if success_probability > 0.2 else "low",
            "countermeasures_effectiveness": 1 - success_probability,
            "recommendations": [
                "Améliorer la formation de sensibilisation",
                "Renforcer le filtrage email",
                "Implémenter DMARC/SPF/DKIM",
                "Tests de phishing réguliers"
            ]
        }
    
    async def _simulate_malware_attack(self, request: AttackSimulationRequest) -> Dict[str, Any]:
        """Simule une attaque malware"""
        success_probability = 0.4
        
        profile = request.target_profile
        if profile.get("antivirus_protection", "basic") == "advanced":
            success_probability *= 0.2
        
        if profile.get("endpoint_detection", False):
            success_probability *= 0.3
        
        return {
            "attack_type": "malware",
            "success_probability": success_probability,
            "impact_assessment": "high" if success_probability > 0.3 else "medium",
            "countermeasures_effectiveness": 1 - success_probability,
            "recommendations": [
                "Déployer EDR/XDR avancé",
                "Renforcer l'isolation réseau",
                "Backup et recovery testés",
                "Sandboxing des fichiers suspects"
            ]
        }
    
    async def _simulate_apt_attack(self, request: AttackSimulationRequest) -> Dict[str, Any]:
        """Simule une attaque APT"""
        return {
            "attack_type": "apt",
            "success_probability": 0.6,  # APT sont généralement sophistiquées
            "impact_assessment": "critical",
            "countermeasures_effectiveness": 0.4,
            "recommendations": [
                "Threat hunting proactif",
                "Segmentation réseau avancée",
                "Monitoring comportemental",
                "Intelligence sur les menaces"
            ]
        }
    
    async def _simulate_insider_threat(self, request: AttackSimulationRequest) -> Dict[str, Any]:
        """Simule une menace interne"""
        return {
            "attack_type": "insider_threat",
            "success_probability": 0.5,
            "impact_assessment": "high",
            "countermeasures_effectiveness": 0.5,
            "recommendations": [
                "Principe du moindre privilège",
                "Surveillance des accès privilégiés",
                "Analyse comportementale",
                "Contrôles d'intégrité des données"
            ]
        }
    
    async def _simulate_generic_attack(self, request: AttackSimulationRequest) -> Dict[str, Any]:
        """Simulation générique"""
        return {
            "attack_type": request.attack_type,
            "success_probability": 0.4,
            "impact_assessment": "medium",
            "countermeasures_effectiveness": 0.6,
            "recommendations": ["Évaluation spécialisée recommandée"]
        }
    
    async def _save_analysis(self, target: str, analysis_result: Dict[str, Any]):
        """Sauvegarde l'analyse en base"""
        try:
            cyber_analyses = await get_collection("cyber_ai_analyses")
            
            document = {
                "_id": str(uuid.uuid4()),
                "target": target,
                "analysis_result": analysis_result,
                "created_at": datetime.now(timezone.utc),
                "service": "cyber_ai"
            }
            
            await cyber_analyses.insert_one(document)
            print(f"✅ Analyse Cyber AI sauvegardée pour {target}")
            
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde analyse Cyber AI: {e}")
    
    async def get_threat_trends(self, days: int = 30) -> Dict[str, Any]:
        """Récupère les tendances de menaces"""
        try:
            cyber_analyses = await get_collection("cyber_ai_analyses")
            
            # Récupérer les analyses récentes
            from datetime import timedelta
            since_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            recent_analyses = await cyber_analyses.find({
                "created_at": {"$gte": since_date}
            }).to_list(length=100)
            
            # Analyser les tendances
            if recent_analyses:
                avg_threat_score = sum(a["analysis_result"]["threat_score"] for a in recent_analyses) / len(recent_analyses)
                threat_types = {}
                
                for analysis in recent_analyses:
                    for vuln in analysis["analysis_result"].get("vulnerabilities", []):
                        for vector in vuln.attack_vectors:
                            threat_types[vector] = threat_types.get(vector, 0) + 1
                
                return {
                    "period_days": days,
                    "total_analyses": len(recent_analyses),
                    "average_threat_score": round(avg_threat_score, 2),
                    "common_attack_vectors": sorted(threat_types.items(), key=lambda x: x[1], reverse=True)[:10],
                    "trend": "increasing" if avg_threat_score > 60 else "stable"
                }
            
            return {
                "period_days": days,
                "total_analyses": 0,
                "message": "Pas assez de données pour analyser les tendances"
            }
            
        except Exception as e:
            print(f"❌ Erreur récupération tendances: {e}")
            return {"error": str(e)}

# Instance globale du service Cyber AI
cyber_ai_service = CyberAIService()