"""
Conversational AI - Extension assistant CyberSec Toolkit Pro 2025 PORTABLE
Sprint 1.5 - IA conversationnelle avancée pour interactions naturelles
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
from fastapi import HTTPException
from pydantic import BaseModel, Field

# Intégration Emergent LLM
try:
    from emergentintegrations import EmergentLLM
except ImportError:
    print("⚠️ EmergentLLM non disponible pour Conversational AI - Mode fallback activé")
    EmergentLLM = None

from backend.config import settings
from backend.database import get_collection

# Modèles de données Conversational AI
class ConversationContext(BaseModel):
    user_id: str = Field(..., description="ID utilisateur")
    session_id: str = Field(..., description="ID de session")
    conversation_type: str = Field("general", description="Type de conversation: general, support, training, consultation")
    user_profile: Optional[Dict[str, Any]] = Field(None, description="Profil utilisateur")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Préférences utilisateur")

class ConversationMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID unique du message")
    content: str = Field(..., description="Contenu du message")
    message_type: str = Field("text", description="Type de message: text, command, query, help")
    context: Optional[ConversationContext] = Field(None, description="Contexte de la conversation")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="Fichiers ou données attachés")
    
class ConversationResponse(BaseModel):
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID de la réponse")
    content: str = Field(..., description="Contenu de la réponse")
    response_type: str = Field("answer", description="Type de réponse: answer, question, suggestion, command")
    confidence: float = Field(..., description="Niveau de confiance (0-1)")
    suggested_actions: Optional[List[str]] = Field(None, description="Actions suggérées")
    follow_up_questions: Optional[List[str]] = Field(None, description="Questions de suivi")
    context_updated: bool = Field(False, description="Contexte mis à jour")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversationFlow(BaseModel):
    flow_id: str = Field(..., description="ID du flux de conversation")
    flow_name: str = Field(..., description="Nom du flux")
    description: str = Field(..., description="Description du flux")
    triggers: List[str] = Field(..., description="Mots-clés ou phrases de déclenchement")
    steps: List[Dict[str, Any]] = Field(..., description="Étapes du flux conversationnel")
    is_active: bool = Field(True, description="Flux actif")

class ConversationalAIService:
    """Service IA Conversationnelle - Interactions naturelles avancées"""
    
    def __init__(self):
        self.llm_client = None
        self.conversation_flows = self._initialize_conversation_flows()
        self.active_conversations = {}  # Sessions actives
        self.conversation_history = {}  # Historique par utilisateur
        self.user_profiles = {}  # Profils utilisateur
        self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialise le client LLM pour Conversational AI"""
        try:
            if EmergentLLM and settings.emergent_llm_key:
                self.llm_client = EmergentLLM(
                    api_key=settings.emergent_llm_key,
                    default_provider=settings.default_llm_provider,
                    default_model=settings.default_llm_model
                )
                print("✅ Conversational AI initialisé avec Emergent LLM")
            else:
                print("⚠️ Conversational AI - Mode simulation activé")
        except Exception as e:
            print(f"❌ Erreur initialisation Conversational AI LLM: {e}")
    
    def _initialize_conversation_flows(self) -> Dict[str, ConversationFlow]:
        """Initialise les flux de conversation prédéfinis"""
        flows = {}
        
        # Flux 1: Onboarding Sécurité
        flows["security_onboarding"] = ConversationFlow(
            flow_id="security_onboarding",
            flow_name="Onboarding Sécurité",
            description="Guide l'utilisateur à travers les fonctionnalités de sécurité",
            triggers=["aide", "help", "commencer", "guide", "onboarding"],
            steps=[
                {
                    "step": "welcome",
                    "message": "👋 Bienvenue dans CyberSec Toolkit Pro 2025! Je suis votre assistant IA spécialisé en cybersécurité. Comment puis-je vous aider aujourd'hui?",
                    "options": ["Découvrir les services", "Faire un audit", "Configurer la sécurité", "Formation"]
                },
                {
                    "step": "capability_intro",
                    "message": "🛡️ Je peux vous aider avec 35 services cybersécurité intégrés. Voulez-vous une démonstration spécifique?",
                    "next_flows": ["pentest_demo", "incident_response_demo", "compliance_demo"]
                }
            ]
        )
        
        # Flux 2: Démonstration Pentest
        flows["pentest_demo"] = ConversationFlow(
            flow_id="pentest_demo",
            flow_name="Démonstration Pentesting",
            description="Démontre les capacités de tests de pénétration",
            triggers=["pentest", "test pénétration", "audit sécurité", "vulnérabilités"],
            steps=[
                {
                    "step": "pentest_intro",
                    "message": "🎯 Notre module Pentesting OWASP Top 10 peut analyser vos systèmes. Avez-vous une cible spécifique à tester?",
                    "collect_input": "target_system"
                },
                {
                    "step": "scan_options",
                    "message": "📊 Quel type de scan souhaitez-vous? 1) Scan rapide 2) Audit complet 3) Test personnalisé",
                    "collect_input": "scan_type"
                },
                {
                    "step": "execute_scan",
                    "message": "⚡ Lancement du scan... Cela peut prendre quelques minutes.",
                    "action": "trigger_pentest_scan"
                }
            ]
        )
        
        # Flux 3: Formation Sécurité Interactive
        flows["security_training"] = ConversationFlow(
            flow_id="security_training",
            flow_name="Formation Sécurité Interactive",
            description="Formation personnalisée en cybersécurité",
            triggers=["formation", "apprendre", "training", "cours", "éducation"],
            steps=[
                {
                    "step": "assess_level",
                    "message": "📚 Quel est votre niveau en cybersécurité? 1) Débutant 2) Intermédiaire 3) Avancé",
                    "collect_input": "security_level"
                },
                {
                    "step": "topic_selection",
                    "message": "🎯 Sur quoi voulez-vous vous former? OWASP, Incident Response, Compliance, Threat Intelligence?",
                    "collect_input": "training_topic"
                },
                {
                    "step": "personalized_content",
                    "message": "📖 Voici un programme de formation personnalisé...",
                    "action": "generate_training_content"
                }
            ]
        )
        
        # Flux 4: Support Technique
        flows["technical_support"] = ConversationFlow(
            flow_id="technical_support",
            flow_name="Support Technique",
            description="Assistance technique pour les problèmes",
            triggers=["problème", "erreur", "bug", "support", "aide technique"],
            steps=[
                {
                    "step": "problem_identification",
                    "message": "🔧 Décrivez le problème que vous rencontrez. Je vais vous aider à le résoudre.",
                    "collect_input": "problem_description"
                },
                {
                    "step": "diagnostic",
                    "message": "🔍 Analysons ce problème ensemble...",
                    "action": "analyze_problem"
                },
                {
                    "step": "solution",
                    "message": "💡 Voici la solution recommandée...",
                    "action": "provide_solution"
                }
            ]
        )
        
        return flows
    
    async def process_message(self, message: ConversationMessage) -> ConversationResponse:
        """Traite un message conversationnel"""
        try:
            print(f"💬 Conversational AI - Traitement message: {message.content[:50]}...")
            
            # Analyse du contexte
            context = message.context or ConversationContext(
                user_id="anonymous",
                session_id=str(uuid.uuid4())
            )
            
            # Mise à jour du profil utilisateur
            await self._update_user_profile(context.user_id, message)
            
            # Détection du type de conversation
            conversation_type = await self._detect_conversation_type(message.content)
            
            # Vérification des flux conversationnels
            active_flow = await self._check_conversation_flows(message, context)
            
            if active_flow:
                # Traitement via flux conversationnel
                response = await self._process_conversation_flow(message, context, active_flow)
            else:
                # Traitement conversationnel libre
                response = await self._process_free_conversation(message, context)
            
            # Sauvegarde de la conversation
            await self._save_conversation_turn(context.user_id, context.session_id, message, response)
            
            return response
            
        except Exception as e:
            print(f"❌ Erreur traitement conversationnel: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur Conversational AI: {str(e)}")
    
    async def _detect_conversation_type(self, message_content: str) -> str:
        """Détecte le type de conversation basé sur le contenu"""
        content_lower = message_content.lower()
        
        # Mots-clés pour les différents types
        if any(word in content_lower for word in ["aide", "help", "comment", "guide"]):
            return "support"
        elif any(word in content_lower for word in ["apprendre", "formation", "cours", "expliquer"]):
            return "training"
        elif any(word in content_lower for word in ["scan", "audit", "pentest", "vulnérabilité"]):
            return "consultation"
        elif any(word in content_lower for word in ["problème", "erreur", "bug", "marche pas"]):
            return "troubleshooting"
        else:
            return "general"
    
    async def _check_conversation_flows(self, message: ConversationMessage, context: ConversationContext) -> Optional[str]:
        """Vérifie si le message déclenche un flux conversationnel"""
        content_lower = message.content.lower()
        
        for flow_id, flow in self.conversation_flows.items():
            for trigger in flow.triggers:
                if trigger.lower() in content_lower:
                    return flow_id
        
        # Vérifier si l'utilisateur est dans un flux actif
        session_key = f"{context.user_id}_{context.session_id}"
        if session_key in self.active_conversations:
            return self.active_conversations[session_key].get("active_flow")
        
        return None
    
    async def _process_conversation_flow(self, message: ConversationMessage, 
                                       context: ConversationContext, flow_id: str) -> ConversationResponse:
        """Traite un message dans le cadre d'un flux conversationnel"""
        flow = self.conversation_flows[flow_id]
        session_key = f"{context.user_id}_{context.session_id}"
        
        # Récupérer ou initialiser l'état du flux
        if session_key not in self.active_conversations:
            self.active_conversations[session_key] = {
                "active_flow": flow_id,
                "current_step": 0,
                "flow_data": {},
                "started_at": datetime.now(timezone.utc)
            }
        
        conversation_state = self.active_conversations[session_key]
        current_step_index = conversation_state["current_step"]
        
        if current_step_index >= len(flow.steps):
            # Flux terminé
            del self.active_conversations[session_key]
            return ConversationResponse(
                content="✅ Flux de conversation terminé. Comment puis-je vous aider d'autre?",
                response_type="completion",
                confidence=0.9
            )
        
        current_step = flow.steps[current_step_index]
        
        # Traitement selon le type d'étape
        if "collect_input" in current_step:
            # Collecter l'entrée utilisateur
            input_key = current_step["collect_input"]
            conversation_state["flow_data"][input_key] = message.content
            
            # Passer à l'étape suivante
            conversation_state["current_step"] += 1
            
            if conversation_state["current_step"] < len(flow.steps):
                next_step = flow.steps[conversation_state["current_step"]]
                response_content = next_step["message"]
            else:
                response_content = "✅ Merci pour ces informations. Je traite votre demande..."
                # Déclencher l'action finale si définie
                if "action" in current_step:
                    action_result = await self._execute_flow_action(current_step["action"], conversation_state["flow_data"])
                    response_content += f"\n\n{action_result}"
        
        elif "action" in current_step:
            # Exécuter une action
            action_result = await self._execute_flow_action(current_step["action"], conversation_state["flow_data"])
            response_content = current_step["message"] + f"\n\n{action_result}"
            conversation_state["current_step"] += 1
        
        else:
            # Message simple
            response_content = current_step["message"]
            conversation_state["current_step"] += 1
        
        # Générer les actions suggérées
        suggested_actions = current_step.get("options", [])
        follow_up = current_step.get("next_flows", [])
        
        return ConversationResponse(
            content=response_content,
            response_type="flow_step",
            confidence=0.9,
            suggested_actions=suggested_actions,
            follow_up_questions=[f"Voulez-vous en savoir plus sur {flow}?" for flow in follow_up[:3]],
            context_updated=True
        )
    
    async def _process_free_conversation(self, message: ConversationMessage, 
                                       context: ConversationContext) -> ConversationResponse:
        """Traite une conversation libre (sans flux défini)"""
        if self.llm_client:
            return await self._process_llm_conversation(message, context)
        else:
            return await self._process_rule_based_conversation(message, context)
    
    async def _process_llm_conversation(self, message: ConversationMessage, 
                                      context: ConversationContext) -> ConversationResponse:
        """Traite la conversation via LLM"""
        try:
            # Construire le contexte pour le LLM
            system_prompt = self._build_conversation_system_prompt(context)
            conversation_history = await self._get_conversation_history(context.user_id, context.session_id)
            
            # Préparer les messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Ajouter l'historique récent
            for hist_msg in conversation_history[-5:]:  # Derniers 5 échanges
                messages.append({"role": "user", "content": hist_msg.get("user_message", "")})
                messages.append({"role": "assistant", "content": hist_msg.get("assistant_response", "")})
            
            # Ajouter le message actuel
            messages.append({"role": "user", "content": message.content})
            
            # Appel LLM
            response = await asyncio.to_thread(
                self.llm_client.chat.completions.create,
                model=settings.default_llm_model,
                messages=messages,
                max_tokens=1200,
                temperature=0.7
            )
            
            response_content = response.choices[0].message.content
            
            # Analyser la réponse pour extraire les actions suggérées
            suggested_actions = self._extract_suggested_actions(response_content)
            follow_up_questions = self._extract_follow_up_questions(response_content)
            
            return ConversationResponse(
                content=response_content,
                response_type="llm_response",
                confidence=0.85,
                suggested_actions=suggested_actions,
                follow_up_questions=follow_up_questions
            )
            
        except Exception as e:
            print(f"⚠️ Erreur LLM conversationnel: {e}")
            return await self._process_rule_based_conversation(message, context)
    
    async def _process_rule_based_conversation(self, message: ConversationMessage, 
                                             context: ConversationContext) -> ConversationResponse:
        """Traite la conversation avec des règles prédéfinies"""
        content_lower = message.content.lower()
        
        # Patterns de réponse basés sur des règles
        if any(word in content_lower for word in ["bonjour", "salut", "hello", "hi"]):
            response_content = """👋 **Bonjour et bienvenue dans CyberSec Toolkit Pro 2025 !**

Je suis votre assistant IA conversationnel spécialisé en cybersécurité. Je peux vous aider avec :

🛡️ **Services disponibles :**
• Tests de pénétration automatisés
• Analyse de conformité (ISO 27001, GDPR, NIST)
• Réponse aux incidents en temps réel
• Formation cybersécurité interactive
• Audit de sécurité complet

💬 **Comment puis-je vous aider aujourd'hui ?**
Dites-moi simplement ce dont vous avez besoin !"""
            
            suggested_actions = ["Faire un scan de sécurité", "Formation OWASP", "Aide technique", "Démonstration"]
            
        elif any(word in content_lower for word in ["services", "fonctionnalités", "capacités"]):
            response_content = """🚀 **CyberSec Toolkit Pro 2025 - 35 Services Intégrés**

**🛡️ Services Cybersécurité (11 opérationnels) :**
✅ Assistant IA Expert • ✅ Pentesting OWASP • ✅ Incident Response
✅ Digital Forensics • ✅ Compliance • ✅ Vulnerability Management
✅ Monitoring 24/7 • ✅ Threat Intelligence • ✅ Red/Blue Team • ✅ Audit

**🧠 Services IA (6 en développement Sprint 1.5) :**
🔄 Cyber AI • 🔄 Predictive AI • 🔄 Automation AI
🔄 Conversational AI • 🔄 Business AI • 🔄 Code Analysis AI

**💼 Services Business (5 planifiés) :**
📋 CRM • 📋 Billing • 📋 Analytics • 📋 Planning • 📋 Training

Sur quoi souhaitez-vous plus d'informations ?"""
            
            suggested_actions = ["Tester un service", "Voir les démos", "Documentation technique"]
            
        elif any(word in content_lower for word in ["aide", "help", "comment"]):
            response_content = """❓ **Centre d'Aide CyberSec Toolkit Pro 2025**

Je peux vous assister sur :

**🔧 Utilisation des outils :**
• Configuration et paramétrage
• Lancement d'analyses et scans
• Interprétation des résultats

**📚 Formation et guidance :**
• Meilleures pratiques cybersécurité
• Explication des concepts techniques
• Recommandations personnalisées

**🚨 Support technique :**
• Résolution de problèmes
• Optimisation des performances
• Questions sur les fonctionnalités

Quelle est votre question spécifique ?"""
            
            suggested_actions = ["Problème technique", "Formation OWASP", "Configuration", "Démonstration"]
            
        elif any(word in content_lower for word in ["pentest", "audit", "scan", "vulnérabilité"]):
            response_content = """🎯 **Module Pentesting & Audit OWASP Top 10**

Notre scanner professionnel peut analyser :

**🌐 Applications Web :**
• Injection SQL, XSS, CSRF
• Broken Authentication
• Security Misconfigurations
• Vulnerable Components

**🔍 Infrastructure :**
• Scan de ports avancé
• Énumération services
• Tests configuration SSL/TLS
• Headers de sécurité

**📊 Génération de rapports :**
• PDF professionnel avec scoring CVSS
• Recommandations priorisées
• Plan de remédiation détaillé

Voulez-vous lancer un scan de démonstration ?"""
            
            suggested_actions = ["Lancer scan démo", "Plus d'infos OWASP", "Voir exemple rapport"]
            
        else:
            # Réponse générique
            response_content = f"""💭 **Réponse à votre message :**

J'ai bien reçu votre message : "{message.content[:100]}{'...' if len(message.content) > 100 else ''}"

En tant qu'assistant IA cybersécurité, je peux vous aider avec :
• **Analyses techniques** - Scans, audits, tests
• **Conseils experts** - Recommandations sécurité
• **Formation** - Explications et guides
• **Support** - Assistance technique

Pouvez-vous être plus précis sur votre besoin ?"""
            
            suggested_actions = ["Préciser ma demande", "Voir les services", "Aide générale"]
        
        return ConversationResponse(
            content=response_content,
            response_type="rule_based",
            confidence=0.7,
            suggested_actions=suggested_actions,
            follow_up_questions=["Avez-vous d'autres questions?", "Voulez-vous une démonstration?"]
        )
    
    def _build_conversation_system_prompt(self, context: ConversationContext) -> str:
        """Construit le prompt système pour la conversation"""
        base_prompt = """Tu es un assistant IA conversationnel expert en cybersécurité pour CyberSec Toolkit Pro 2025.

🎯 TON RÔLE:
- Assistant conversationnel naturel et engageant
- Expert cybersécurité avec 15+ ans d'expérience
- Guide l'utilisateur à travers les 35 services intégrés
- Fournit des réponses personnalisées et actionnables

💬 STYLE CONVERSATIONNEL:
- Naturel et professionnel
- Utilise des emojis appropriés
- Questions de suivi pertinentes  
- Suggestions d'actions concrètes
- Adapté au niveau technique de l'utilisateur

🛡️ SPÉCIALITÉS:
- Tous les services CyberSec Toolkit Pro 2025
- Formation interactive cybersécurité
- Support technique personnalisé
- Démonstrations guidées
- Conseils stratégiques sécurité"""
        
        # Personnalisation selon le contexte
        if context.conversation_type == "training":
            base_prompt += "\n\n🎓 MODE FORMATION: Privilégie l'apprentissage progressif et les explications pédagogiques."
        elif context.conversation_type == "support":
            base_prompt += "\n\n🔧 MODE SUPPORT: Focus sur la résolution rapide et efficace des problèmes."
        elif context.conversation_type == "consultation":
            base_prompt += "\n\n💼 MODE CONSULTATION: Approche stratégique et recommandations expertes."
        
        return base_prompt

    async def _update_user_profile(self, user_id: str, message: ConversationMessage) -> None:
        try:
            self.user_profiles.setdefault(user_id, {"messages": 0, "last_interaction": datetime.now(timezone.utc).isoformat()})
            self.user_profiles[user_id]["messages"] += 1
            self.user_profiles[user_id]["last_interaction"] = datetime.now(timezone.utc).isoformat()
        except Exception:
            pass

    async def _get_conversation_history(self, user_id: str, session_id: str) -> List[Dict[str, Any]]:
        try:
            key = f"{user_id}_{session_id}"
            return self.conversation_history.get(key, [])
        except Exception:
            return []

    async def _save_conversation_turn(self, user_id: str, session_id: str, message: ConversationMessage, response: ConversationResponse) -> None:
        try:
            key = f"{user_id}_{session_id}"
            self.conversation_history.setdefault(key, [])
            self.conversation_history[key].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_message": message.content,
                "assistant_response": response.content,
                "response_type": response.response_type
            })
        except Exception:
            pass

    async def _execute_flow_action(self, action: str, data: Dict[str, Any]) -> str:
        try:
            if action == "trigger_pentest_scan":
                return "Scan de démonstration lancé. Vous recevrez un rapport synthétique."
            elif action == "generate_training_content":
                level = data.get("security_level", "intermédiaire")
                topic = data.get("training_topic", "OWASP")
                return f"Contenu de formation {level} généré pour le sujet {topic}."
            elif action == "analyze_problem":
                return "Diagnostic initial effectué. Probable problème de configuration."
            elif action == "provide_solution":
                return "Solution proposée: redémarrer le service et appliquer le patch de sécurité KB-2025-07."
            return "Action exécutée."
        except Exception:
            return "Action traitée."

    def _extract_suggested_actions(self, text: str) -> List[str]:
        try:
            actions = []
            for key in ["scan", "audit", "configuration", "formation", "support"]:
                if key in text.lower():
                    actions.append(key)
            return actions[:5] or ["continuer"]
        except Exception:
            return ["continuer"]

    def _extract_follow_up_questions(self, text: str) -> List[str]:
        try:
            qs = []
            if len(text) > 60:
                qs.append("Souhaitez-vous plus de détails ?")
            qs.append("Voulez-vous une démonstration ?")
            return qs[:3]
        except Exception:
            return ["Voulez-vous une démonstration ?"]


# Instance globale du service Conversational AI
conversational_ai_service = ConversationalAIService()