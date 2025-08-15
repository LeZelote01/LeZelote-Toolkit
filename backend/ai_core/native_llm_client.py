"""
Client LLM natif pour utiliser directement OpenAI ou Anthropic
Alternative à emergentintegrations pour les clés API personnelles
"""
import os
from typing import Optional, Dict, Any, List
from backend.config import settings

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False


class NativeLLMClient:
    """Client LLM natif pour OpenAI et Anthropic"""
    
    def __init__(self):
        self.provider = settings.default_llm_provider
        self.model = settings.default_llm_model
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialise le client selon le provider configuré"""
        try:
            if self.provider == "openai" and settings.openai_api_key and OPENAI_AVAILABLE:
                self.client = openai.OpenAI(api_key=settings.openai_api_key)
                print(f"✅ Client OpenAI initialisé avec modèle {self.model}")
                
            elif self.provider == "anthropic" and settings.anthropic_api_key and ANTHROPIC_AVAILABLE:
                self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
                print(f"✅ Client Anthropic initialisé avec modèle {self.model}")
                
            elif self.provider == "google" and settings.google_ai_api_key and GOOGLE_AI_AVAILABLE:
                genai.configure(api_key=settings.google_ai_api_key)
                self.client = genai.GenerativeModel(self.model)
                print(f"✅ Client Google AI initialisé avec modèle {self.model}")
                
            else:
                print(f"⚠️ Provider {self.provider} non configuré ou clé manquante")
                
        except Exception as e:
            print(f"❌ Erreur initialisation client LLM natif: {e}")
    
    def is_configured(self) -> bool:
        """Vérifie si le client est correctement configuré"""
        return self.client is not None
    
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Génère une réponse avec le LLM configuré"""
        if not self.client:
            return self._get_fallback_response(prompt)
        
        try:
            if self.provider == "openai":
                return await self._openai_generate(prompt, context)
            elif self.provider == "anthropic":
                return await self._anthropic_generate(prompt, context)
            elif self.provider == "google":
                return await self._google_generate(prompt, context)
            else:
                return self._get_fallback_response(prompt)
                
        except Exception as e:
            print(f"❌ Erreur génération réponse: {e}")
            return self._get_fallback_response(prompt)
    
    async def _openai_generate(self, prompt: str, context: Optional[str] = None) -> str:
        """Génère une réponse avec OpenAI"""
        messages = [
            {"role": "system", "content": "Tu es un expert en cybersécurité qui aide avec le CyberSec Toolkit Pro 2025."}
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Contexte: {context}"})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    async def _anthropic_generate(self, prompt: str, context: Optional[str] = None) -> str:
        """Génère une réponse avec Anthropic"""
        system_prompt = "Tu es un expert en cybersécurité qui aide avec le CyberSec Toolkit Pro 2025."
        
        if context:
            system_prompt += f" Contexte: {context}"
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.content[0].text
    
    async def _google_generate(self, prompt: str, context: Optional[str] = None) -> str:
        """Génère une réponse avec Google AI"""
        system_prompt = "Tu es un expert en cybersécurité qui aide avec le CyberSec Toolkit Pro 2025."
        
        if context:
            system_prompt += f" Contexte: {context}"
        
        full_prompt = f"{system_prompt}\n\nUtilisateur: {prompt}"
        
        response = self.client.generate_content(full_prompt)
        return response.text
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Réponse de fallback si pas de LLM configuré"""
        return f"""🛡️ **CyberSec Toolkit Pro 2025 - Mode Simulation**

Votre demande: {prompt[:100]}...

Je fonctionne actuellement en mode simulation car aucune clé API n'est configurée.

**Pour activer l'IA, configurez une de ces options :**

1. **OpenAI** : Ajoutez `OPENAI_API_KEY=sk-...` dans le fichier `.env`
2. **Anthropic** : Ajoutez `ANTHROPIC_API_KEY=sk-ant-...` dans le fichier `.env`  
3. **Emergent** : Ajoutez `EMERGENT_LLM_KEY=sk-emergent-...` dans le fichier `.env`

Une fois configuré, redémarrez l'application pour activer l'IA complète.

**Services disponibles sans IA :**
- Tous les outils de scan et audit
- Génération de rapports
- Base de données des vulnérabilités
- Framework de conformité
"""


# Instance globale
native_llm_client = NativeLLMClient()