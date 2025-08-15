"""
Routes FastAPI pour Conversational AI - CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - IA conversationnelle spécialisée en cybersécurité
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel
import uuid

router = APIRouter(
    prefix="/api/conversational-ai",
    tags=["conversational-ai"],
    responses={404: {"description": "Conversational AI service not found"}}
)

class ConversationalAIStatusResponse(BaseModel):
    status: str
    service: str
    version: str
    features: Dict[str, bool]
    active_sessions: int
    llm_configured: bool

class ConversationRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[str] = None
    expertise_level: str = "intermediate"
    language: str = "fr"

class ConversationResponse(BaseModel):
    success: bool
    session_id: str
    response: str
    confidence: float
    suggested_actions: List[str]

# Stockage en mémoire des sessions
active_sessions: Dict[str, Dict] = {}
conversation_history: Dict[str, List] = {}

@router.get("/", response_model=ConversationalAIStatusResponse)
async def conversational_ai_status():
    """Status du service Conversational AI"""
    return ConversationalAIStatusResponse(
        status="operational",
        service="Conversational AI - IA Conversationnelle Cybersécurité",
        version="1.0.0-portable",
        features={
            "cybersecurity_expertise": True,
            "multi_language_support": True,
            "context_awareness": True,
            "technical_explanations": True,
            "vulnerability_analysis": True,
            "threat_discussion": True,
            "best_practices_guidance": True,
            "incident_support": True
        },
        active_sessions=len(active_sessions),
        llm_configured=False  # Will be configured with LLM integration
    )

@router.post("/chat", response_model=ConversationResponse)
async def chat_with_ai(request: ConversationRequest):
    """Conversation avec l'IA spécialisée en cybersécurité"""
    try:
        # Validation des paramètres
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message requis")
        
        valid_levels = ["beginner", "intermediate", "expert"]
        if request.expertise_level not in valid_levels:
            raise HTTPException(
                status_code=400,
                detail=f"Niveau d'expertise invalide. Options: {', '.join(valid_levels)}"
            )
        
        # Gestion de la session
        session_id = request.session_id or str(uuid.uuid4())
        
        if session_id not in active_sessions:
            active_sessions[session_id] = {
                "session_id": session_id,
                "created_at": datetime.now().isoformat(),
                "expertise_level": request.expertise_level,
                "language": request.language,
                "message_count": 0
            }
            conversation_history[session_id] = []
        
        session = active_sessions[session_id]
        session["message_count"] += 1
        session["last_active"] = datetime.now().isoformat()
        
        # Analyser le message pour déterminer le type de réponse
        response_data = await _generate_cybersecurity_response(
            request.message,
            session,
            request.context,
            conversation_history[session_id]
        )
        
        # Enregistrer dans l'historique
        conversation_history[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": request.message,
            "ai_response": response_data["response"],
            "context": request.context
        })
        
        # Limiter l'historique à 50 messages
        if len(conversation_history[session_id]) > 50:
            conversation_history[session_id] = conversation_history[session_id][-50:]
        
        return ConversationResponse(
            success=True,
            session_id=session_id,
            response=response_data["response"],
            confidence=response_data["confidence"],
            suggested_actions=response_data["suggested_actions"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la conversation: {str(e)}"
        )

@router.get("/sessions")
async def list_sessions():
    """Liste les sessions de conversation actives"""
    try:
        sessions_list = []
        for session_id, session in active_sessions.items():
            sessions_list.append({
                "session_id": session_id,
                "created_at": session["created_at"],
                "last_active": session.get("last_active", session["created_at"]),
                "message_count": session["message_count"],
                "expertise_level": session["expertise_level"],
                "language": session["language"]
            })
        
        return {
            "success": True,
            "sessions": sessions_list,
            "total_sessions": len(sessions_list),
            "active_sessions": len([s for s in sessions_list if s["message_count"] > 0])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des sessions: {str(e)}"
        )

@router.get("/session/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Récupère l'historique d'une session"""
    try:
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session non trouvée")
        
        history = conversation_history.get(session_id, [])
        session = active_sessions[session_id]
        
        return {
            "success": True,
            "session_id": session_id,
            "session_info": session,
            "conversation_history": history,
            "total_messages": len(history)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de l'historique: {str(e)}"
        )

@router.post("/analyze-question")
async def analyze_question(question: str):
    """Analyse une question pour déterminer le domaine cybersécurité"""
    try:
        if not question.strip():
            raise HTTPException(status_code=400, detail="Question requise")
        
        analysis = await _analyze_cybersecurity_question(question)
        
        return {
            "success": True,
            "question": question,
            "analysis": analysis,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'analyse de la question: {str(e)}"
        )

@router.get("/topics")
async def get_supported_topics():
    """Liste les sujets cybersécurité supportés"""
    try:
        topics = {
            "security_domains": [
                {
                    "domain": "Penetration Testing",
                    "description": "Tests d'intrusion et évaluation de sécurité",
                    "expertise_areas": ["OWASP Top 10", "Network Scanning", "Web App Testing"]
                },
                {
                    "domain": "Incident Response",
                    "description": "Réponse aux incidents de sécurité",
                    "expertise_areas": ["Digital Forensics", "Containment", "Evidence Collection"]
                },
                {
                    "domain": "Vulnerability Management",
                    "description": "Gestion des vulnérabilités",
                    "expertise_areas": ["CVE Analysis", "Patch Management", "Risk Assessment"]
                },
                {
                    "domain": "Cloud Security",
                    "description": "Sécurité des environnements cloud",
                    "expertise_areas": ["AWS Security", "Azure Security", "GCP Security"]
                },
                {
                    "domain": "Network Security",
                    "description": "Sécurité des réseaux",
                    "expertise_areas": ["Firewall Config", "IDS/IPS", "Network Monitoring"]
                }
            ],
            "technical_areas": [
                "Malware Analysis",
                "Cryptography",
                "Authentication & Authorization",
                "Secure Coding",
                "Compliance (GDPR, PCI-DSS, etc.)",
                "Risk Management",
                "Security Architecture",
                "Threat Intelligence"
            ],
            "tools_and_technologies": [
                "Burp Suite", "Nmap", "Metasploit", "Wireshark",
                "Splunk", "ELK Stack", "SIEM Tools",
                "Docker Security", "Kubernetes Security"
            ]
        }
        
        return {
            "success": True,
            "supported_topics": topics,
            "total_domains": len(topics["security_domains"]),
            "total_areas": len(topics["technical_areas"]),
            "total_tools": len(topics["tools_and_technologies"])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des sujets: {str(e)}"
        )

@router.get("/examples")
async def get_conversation_examples():
    """Exemples de conversations typiques"""
    try:
        examples = [
            {
                "category": "Vulnerability Analysis",
                "question": "Comment analyser une vulnérabilité SQL Injection ?",
                "expected_response_type": "Technical explanation with examples and remediation steps"
            },
            {
                "category": "Incident Response",
                "question": "Quelles sont les étapes pour répondre à un incident de malware ?",
                "expected_response_type": "Step-by-step incident response procedure"
            },
            {
                "category": "Penetration Testing",
                "question": "Comment effectuer un test de pénétration sur une application web ?",
                "expected_response_type": "Methodology and tools explanation"
            },
            {
                "category": "Cloud Security",
                "question": "Quels sont les risques de sécurité dans AWS S3 ?",
                "expected_response_type": "Risk analysis and security best practices"
            },
            {
                "category": "Threat Intelligence",
                "question": "Comment identifier les indicateurs de compromission ?",
                "expected_response_type": "IOC types and detection methods"
            }
        ]
        
        return {
            "success": True,
            "examples": examples,
            "total_examples": len(examples),
            "categories": list(set(e["category"] for e in examples))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des exemples: {str(e)}"
        )

# Fonctions utilitaires
async def _generate_cybersecurity_response(message: str, session: Dict, context: Optional[str], history: List) -> Dict:
    """Génère une réponse spécialisée en cybersécurité"""
    
    message_lower = message.lower()
    
    # Analyser le type de question
    if any(word in message_lower for word in ["sql injection", "sqli", "injection sql"]):
        return {
            "response": """🔍 **SQL Injection - Analyse et Remédiation**

Les attaques par injection SQL exploitent les entrées non validées pour exécuter du code SQL malveillant.

**Types principaux :**
- **Union-based** : Utilise UNION pour extraire des données
- **Boolean-based** : Utilise des conditions vraies/fausses
- **Time-based** : Utilise des délais pour confirmer l'injection
- **Error-based** : Exploite les messages d'erreur

**Détection :**
1. Tester avec des caractères spéciaux : `'`, `"`, `;`
2. Utiliser des payloads basiques : `' OR '1'='1`
3. Analyser les réponses et erreurs

**Remédiation :**
1. **Requêtes préparées** (Prepared Statements)
2. **Validation stricte** des entrées
3. **Principe du moindre privilège** pour les comptes DB
4. **WAF** pour filtrer les requêtes malveillantes

Souhaitez-vous des exemples de code sécurisé ?""",
            "confidence": 0.95,
            "suggested_actions": [
                "Tester votre application avec des outils comme SQLmap",
                "Implémenter des requêtes préparées",
                "Configurer un WAF",
                "Effectuer une revue de code"
            ]
        }
    
    elif any(word in message_lower for word in ["incident", "réponse", "malware", "compromis"]):
        return {
            "response": """🚨 **Réponse aux Incidents de Sécurité**

Processus structuré de gestion des incidents :

**Phase 1 : Préparation**
- Plans de réponse documentés
- Équipe d'intervention formée
- Outils de forensique prêts

**Phase 2 : Détection & Analyse**
- Identifier les indicateurs de compromission
- Évaluer la portée de l'incident
- Classifier la sévérité

**Phase 3 : Confinement**
- **Confinement immédiat** : Isoler les systèmes compromis
- **Confinement à long terme** : Solutions temporaires
- Préserver les preuves

**Phase 4 : Éradication & Récupération**
- Éliminer la cause racine
- Restaurer les systèmes
- Surveiller la récurrence

**Phase 5 : Leçons Apprises**
- Documentation complète
- Amélioration des processus
- Formation de l'équipe

Quel type d'incident traitez-vous ?""",
            "confidence": 0.92,
            "suggested_actions": [
                "Documenter tous les détails de l'incident",
                "Isoler les systèmes compromis",
                "Collecter les artefacts forensiques",
                "Notifier les parties prenantes"
            ]
        }
    
    elif any(word in message_lower for word in ["pentest", "pénétration", "test intrusion"]):
        return {
            "response": """🎯 **Tests de Pénétration - Méthodologie**

Approche structurée pour les tests d'intrusion :

**1. Reconnaissance (Reconnaissance)**
- **OSINT** : Collecte d'informations publiques
- **DNS Enumeration** : nslookup, dig, dnsrecon
- **Port Scanning** : Nmap, Masscan

**2. Scan & Énumération**
- **Service Detection** : Identification des services
- **Version Detection** : Versions des applications
- **OS Fingerprinting** : Identification de l'OS

**3. Exploitation**
- **Exploitation manuelle** : Techniques ciblées
- **Frameworks** : Metasploit, Cobalt Strike
- **Custom Exploits** : Développement spécifique

**4. Post-Exploitation**
- **Persistence** : Maintenir l'accès
- **Privilege Escalation** : Élévation de privilèges
- **Lateral Movement** : Mouvement latéral

**5. Reporting**
- **Executive Summary** : Résumé pour la direction
- **Technical Details** : Détails techniques
- **Remediation** : Recommandations

Quel type de test souhaitez-vous réaliser ?""",
            "confidence": 0.94,
            "suggested_actions": [
                "Définir le scope du test",
                "Obtenir les autorisations écrites",
                "Préparer l'environnement de test",
                "Planifier les tests selon OWASP"
            ]
        }
    
    else:
        return {
            "response": f"""🛡️ **Assistant Cybersécurité - Mode Conversationnel**

Je suis spécialisé dans tous les domaines de la cybersécurité. Votre question : "{message}"

**Domaines d'expertise :**
- Tests de pénétration et évaluation de sécurité
- Réponse aux incidents et forensique numérique
- Gestion des vulnérabilités et analyse de risques
- Sécurité des applications et développement sécurisé
- Architecture de sécurité et gouvernance
- Conformité réglementaire (GDPR, PCI-DSS, ISO 27001)

**Comment puis-je vous aider ?**
- Expliquer des concepts techniques
- Guider dans la résolution d'incidents
- Recommander des outils et méthodologies
- Analyser des vulnérabilités
- Proposer des stratégies de sécurité

Pouvez-vous préciser votre besoin ou poser une question plus spécifique ?""",
            "confidence": 0.8,
            "suggested_actions": [
                "Poser une question spécifique sur un domaine",
                "Demander une analyse de vulnérabilité",
                "Obtenir des conseils sur un incident",
                "Explorer les méthodologies de test"
            ]
        }

async def _analyze_cybersecurity_question(question: str) -> Dict:
    """Analyse une question pour déterminer le domaine cybersécurité"""
    
    question_lower = question.lower()
    
    domains = {
        "penetration_testing": ["pentest", "test intrusion", "pénétration", "exploit", "vulnerability"],
        "incident_response": ["incident", "réponse", "forensique", "investigation", "compromis"],
        "malware_analysis": ["malware", "virus", "trojan", "ransomware", "analyse"],
        "network_security": ["réseau", "firewall", "ips", "ids", "network"],
        "web_security": ["web", "application", "owasp", "xss", "sql injection"],
        "cloud_security": ["cloud", "aws", "azure", "gcp", "kubernetes"],
        "compliance": ["conformité", "gdpr", "pci", "iso", "audit"]
    }
    
    detected_domains = []
    for domain, keywords in domains.items():
        if any(keyword in question_lower for keyword in keywords):
            detected_domains.append(domain)
    
    return {
        "detected_domains": detected_domains,
        "primary_domain": detected_domains[0] if detected_domains else "general_security",
        "complexity_level": "intermediate",
        "requires_technical_detail": any(word in question_lower for word in ["comment", "pourquoi", "technique"]),
        "question_type": "explanation" if "comment" in question_lower else "analysis"
    }