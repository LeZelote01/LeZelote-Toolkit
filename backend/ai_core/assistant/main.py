"""
Assistant IA Principal - CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.1 - Implémentation de l'assistant conversationnel expert cybersécurité
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from fastapi import HTTPException
from pydantic import BaseModel, Field

# Intégration Emergent LLM
try:
    from emergentintegrations import EmergentLLM
except ImportError:
    print("⚠️ EmergentLLM non disponible - Mode fallback activé")
    EmergentLLM = None

from backend.config import settings
from backend.database import get_collection

# Modèles de données
class ChatMessage(BaseModel):
    role: str = Field(..., description="Rôle: 'user' ou 'assistant'")
    content: str = Field(..., description="Contenu du message")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    message: str = Field(..., description="Message de l'utilisateur")
    session_id: Optional[str] = Field(None, description="ID de session pour continuité")
    context: Optional[str] = Field(None, description="Contexte cybersécurité spécifique")

class ChatResponse(BaseModel):
    response: str = Field(..., description="Réponse de l'assistant")
    session_id: str = Field(..., description="ID de session")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    tokens_used: Optional[int] = Field(None, description="Tokens utilisés")
    model_used: Optional[str] = Field(None, description="Modèle LLM utilisé")

class AssistantService:
    """Service principal de l'Assistant IA Cybersécurité"""
    
    def __init__(self):
        self.llm_client = None
        self.knowledge_base = self._load_knowledge_base()
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialise le client LLM Emergent"""
        try:
            if EmergentLLM and settings.emergent_llm_key:
                self.llm_client = EmergentLLM(
                    api_key=settings.emergent_llm_key,
                    default_provider=settings.default_llm_provider,
                    default_model=settings.default_llm_model
                )
                print("✅ Assistant IA initialisé avec Emergent LLM")
            else:
                print("⚠️ Emergent LLM non configuré - Mode simulation activé")
        except Exception as e:
            print(f"❌ Erreur initialisation LLM: {e}")
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Charge la base de connaissances cybersécurité"""
        return {
            "cybersecurity_domains": [
                "Audit de sécurité", "Tests de pénétration", "Réponse aux incidents",
                "Forensique numérique", "Gestion des vulnérabilités", "Conformité",
                "Monitoring sécurité", "Red Team", "Blue Team", "Sécurité Cloud",
                "Sécurité Mobile", "Sécurité IoT", "Sécurité Web3", "Sécurité IA",
                "Sécurité réseau", "Sécurité API", "Sécurité containers",
                "Infrastructure as Code", "Social Engineering", "Threat Intelligence",
                "Orchestration sécurité", "Évaluation des risques", "Formation sécurité"
            ],
            "common_vulnerabilities": [
                "OWASP Top 10", "CVE Database", "CWE/SANS Top 25", "NIST Cybersecurity Framework",
                "ISO 27001", "GDPR", "HIPAA", "PCI-DSS", "SOC 2", "FISMA"
            ],
            "security_tools": [
                "Nmap", "Burp Suite", "Metasploit", "Wireshark", "OSSEC", "Snort",
                "OpenVAS", "Nessus", "Qualys", "Rapid7", "Splunk", "ELK Stack"
            ],
            "methodologies": [
                "OWASP Testing Guide", "PTES", "NIST SP 800-115", "OSSTMM",
                "ISSAF", "WAHH", "SANS Methodology"
            ]
        }
    
    def _create_system_prompt(self, context: Optional[str] = None) -> str:
        """Crée le prompt système pour l'assistant cybersécurité"""
        base_prompt = """Tu es un expert cybersécurité senior travaillant avec CyberSec Toolkit Pro 2025, 
l'outil portable le plus avancé pour les professionnels cybersécurité freelance.

🎯 TON RÔLE:
- Expert consultant cybersécurité avec 15+ ans d'expérience
- Spécialiste en audit, pentest, incident response, forensique
- Maîtrise parfaite des frameworks (NIST, ISO 27001, OWASP)
- Expérience terrain et conseil stratégique

🛡️ DOMAINES D'EXPERTISE:
- Tests de pénétration (Web, réseau, mobile, IoT, cloud)
- Audit de sécurité et conformité (GDPR, HIPAA, PCI-DSS)
- Réponse aux incidents et forensique numérique
- Architecture sécurisée et threat modeling
- Sécurité DevSecOps et containers
- Threat Intelligence et SOC

💼 STYLE DE RÉPONSE:
- Précis, actionnable et pratique
- Références méthodologies reconnues
- Exemples concrets et commandes pratiques
- Priorise sécurité et conformité
- Adapté au niveau technique de l'interlocuteur

🚀 OUTILS DISPONIBLES:
Tu as accès aux 35 services CyberSec Toolkit Pro 2025 portables incluant tous les outils d'audit, pentest, forensique, et business."""

        if context:
            base_prompt += f"\n\n🎯 CONTEXTE SPÉCIFIQUE: {context}"
        
        return base_prompt
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Traite une demande de chat avec l'assistant IA"""
        try:
            # Générer session ID si nécessaire
            session_id = request.session_id or str(uuid.uuid4())
            
            # Récupérer l'historique de conversation
            conversation_history = await self._get_conversation_history(session_id)
            
            # Créer le prompt système
            system_prompt = self._create_system_prompt(request.context)
            
            # Préparer les messages pour le LLM
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": request.message})
            
            # Générer la réponse
            if self.llm_client:
                response = await self._generate_llm_response(messages)
            else:
                response = await self._generate_fallback_response(request.message, request.context)
            
            # Sauvegarder la conversation
            await self._save_conversation(session_id, request.message, response["content"])
            
            return ChatResponse(
                response=response["content"],
                session_id=session_id,
                tokens_used=response.get("tokens_used"),
                model_used=response.get("model_used", settings.default_llm_model)
            )
            
        except Exception as e:
            print(f"❌ Erreur chat assistant: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur assistant IA: {str(e)}")
    
    async def _generate_llm_response(self, messages: List[Dict]) -> Dict[str, Any]:
        """Génère une réponse via Emergent LLM"""
        try:
            # Appel à l'API Emergent LLM
            response = await asyncio.to_thread(
                self.llm_client.chat.completions.create,
                model=settings.default_llm_model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            return {
                "content": response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None,
                "model_used": settings.default_llm_model
            }
            
        except Exception as e:
            print(f"⚠️ Erreur LLM: {e} - Utilisation du fallback")
            return await self._generate_fallback_response(messages[-1]["content"])
    
    async def _generate_fallback_response(self, user_message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Génère une réponse de fallback intelligente"""
        user_lower = user_message.lower()
        
        # Réponses contextuelles cybersécurité
        if any(word in user_lower for word in ["pentest", "penetration", "test"]):
            response = """🛡️ **Tests de Pénétration avec CyberSec Toolkit Pro 2025**

Pour un audit de pentest complet, je recommande cette approche méthodologique :

**📋 Phase 1 : Reconnaissance**
- Nmap pour découverte réseau
- OSINT avec outils intégrés
- Énumération services et versions

**🎯 Phase 2 : Scanning & Énumération** 
- Scan vulnérabilités (OpenVAS/Nessus intégré)
- Énumération web (Burp Suite intégré)
- Analyse ports et services

**⚔️ Phase 3 : Exploitation**
- Tests OWASP Top 10
- Exploitation manuelle ciblée
- Documentation preuves de concept

**📊 Phase 4 : Rapport**
- Génération rapport automatique
- Recommandations priorisées
- Plan de remédiation

Voulez-vous que je vous guide sur une phase spécifique ?"""

        elif any(word in user_lower for word in ["audit", "conformité", "compliance"]):
            response = """📋 **Audit de Sécurité & Conformité**

CyberSec Toolkit Pro 2025 couvre tous les standards majeurs :

**🏛️ Frameworks Supportés:**
- NIST Cybersecurity Framework
- ISO 27001/27002
- GDPR (Conformité données)
- HIPAA (Secteur santé)
- PCI-DSS (Paiements)
- SOC 2 Type II

**🔍 Méthodologie d'Audit:**
1. **Gap Analysis** - État actuel vs. standard
2. **Risk Assessment** - Évaluation des risques
3. **Controls Testing** - Tests des contrôles
4. **Remediation Plan** - Plan de mise en conformité

**📊 Livrables:**
- Rapport d'audit détaillé
- Matrice de conformité  
- Feuille de route remédiation
- Templates politiques sécurité

Quel standard vous intéresse le plus ?"""

        elif any(word in user_lower for word in ["incident", "forensique", "investigation"]):
            response = """🚨 **Réponse aux Incidents & Forensique**

**⚡ Processus IR Intégré:**

**Phase 1 : Détection & Analyse**
- Monitoring temps réel
- Corrélation des événements
- Classification des incidents

**Phase 2 : Containment & Éradication**
- Isolation systèmes compromis
- Analyse forensique live
- Suppression des menaces

**Phase 3 : Recovery & Lessons Learned**
- Restauration services
- Monitoring post-incident
- Amélioration continue

**🔬 Outils Forensique Intégrés:**
- Acquisition mémoire/disque
- Analyse timeline
- Recherche IOCs
- Corrélation logs

**📋 Documentation Automatique:**
- Chain of custody
- Rapport technique détaillé
- Recommandations préventives

Avez-vous un incident en cours à analyser ?"""

        elif any(word in user_lower for word in ["owasp", "web", "application"]):
            response = """🌐 **Sécurité Applications Web - OWASP**

**🎯 OWASP Top 10 2021 - Tests Intégrés:**

1. **Broken Access Control** - Tests d'autorisation
2. **Cryptographic Failures** - Analyse chiffrement
3. **Injection** - SQL, NoSQL, LDAP, OS injection
4. **Insecure Design** - Threat modeling
5. **Security Misconfiguration** - Audit configuration
6. **Vulnerable Components** - Scan dépendances
7. **ID&A Failures** - Tests authentification
8. **Software Integrity** - Vérification intégrité
9. **Logging Failures** - Audit logs sécurité
10. **SSRF** - Tests Server-Side Request Forgery

**🛠️ Outils Intégrés:**
- Scanner automatisé OWASP ZAP
- Burp Suite Professional
- Tests manuels guidés
- Validation OWASP ASVS

**📊 Reporting:**
- Rapport OWASP standard
- Matrice risques business
- Guide remédiation développeur

Quelle application souhaitez-vous auditer ?"""

        else:
            response = f"""🛡️ **Assistant Cybersécurité CyberSec Toolkit Pro 2025**

Bonjour ! Je suis votre expert cybersécurité dédié, spécialisé dans l'ensemble des 35 services intégrés.

**🎯 Je peux vous aider avec :**
- **Tests de pénétration** complets (web, réseau, mobile, IoT)
- **Audits de sécurité** et conformité (NIST, ISO 27001, GDPR)
- **Réponse aux incidents** et forensique numérique
- **Architecture sécurisée** et threat modeling
- **Évaluation des risques** et gouvernance
- **Formation** et sensibilisation sécurité

**📱 Mode Portable Unique :**
Tous nos outils fonctionnent 100% portable sur clé USB, parfait pour :
- Interventions client sur site
- Audits en environnement déconnecté
- Démonstrations plug & play
- Formations mobiles

**💬 Comment puis-je vous accompagner aujourd'hui ?**

Décrivez votre besoin ou contexte sécurité, je vous guiderai avec l'expertise et les outils appropriés !

{f"**Contexte spécifique :** {context}" if context else ""}"""

        return {
            "content": response,
            "tokens_used": len(response.split()),
            "model_used": "fallback-expert"
        }
    
    async def _get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Récupère l'historique de conversation"""
        try:
            conversations = await get_collection("conversations")
            conversation = await conversations.find_one({"session_id": session_id})
            
            if conversation and "messages" in conversation:
                return conversation["messages"][-10:]  # Garder les 10 derniers messages
            return []
            
        except Exception as e:
            print(f"⚠️ Erreur récupération historique: {e}")
            return []
    
    async def _save_conversation(self, session_id: str, user_message: str, assistant_response: str):
        """Sauvegarde la conversation"""
        try:
            conversations = await get_collection("conversations")
            
            # Préparer les nouveaux messages
            new_messages = [
                {
                    "role": "user", 
                    "content": user_message,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                {
                    "role": "assistant", 
                    "content": assistant_response,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            ]
            
            # Mettre à jour ou créer la conversation
            await conversations.update_one(
                {"session_id": session_id},
                {
                    "$push": {"messages": {"$each": new_messages}},
                    "$set": {"updated_at": datetime.now(timezone.utc)}
                },
                upsert=True
            )
            
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde conversation: {e}")
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Récupère les informations d'une session"""
        try:
            conversations = await get_collection("conversations")
            conversation = await conversations.find_one({"session_id": session_id})
            
            if conversation:
                return {
                    "session_id": session_id,
                    "messages_count": len(conversation.get("messages", [])),
                    "created_at": conversation.get("created_at"),
                    "updated_at": conversation.get("updated_at"),
                    "last_messages": conversation.get("messages", [])[-3:]  # 3 derniers messages
                }
            
            return None
            
        except Exception as e:
            print(f"❌ Erreur récupération session: {e}")
            return None
    
    async def list_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Liste les sessions récentes"""
        try:
            conversations = await get_collection("conversations")
            sessions = await conversations.find(
                {},
                {"session_id": 1, "updated_at": 1, "messages": {"$slice": -1}}
            ).sort("updated_at", -1).limit(limit).to_list(length=limit)
            
            return [
                {
                    "session_id": session["session_id"],
                    "last_activity": session.get("updated_at"),
                    "last_message": session.get("messages", [{}])[-1].get("content", "")[:100] if session.get("messages") else ""
                }
                for session in sessions
            ]
            
        except Exception as e:
            print(f"❌ Erreur liste sessions: {e}")
            return []

# Instance globale du service
assistant_service = AssistantService()