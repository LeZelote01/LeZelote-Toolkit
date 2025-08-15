"""
Signature Evasion Module - Mode Furtif
Techniques d'évasion des signatures de sécurité et de détection
"""

import asyncio
import random
import string
import base64
import hashlib
import time
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid
import logging


@dataclass
class EvasionProfile:
    """Profil d'évasion personnalisé"""
    name: str
    user_agents: List[str]
    timing_patterns: Dict[str, Tuple[float, float]]  # min, max delays
    payload_transformations: List[str]
    header_randomization: bool
    request_chunking: bool
    encoding_techniques: List[str]
    signature_mutations: Dict[str, str]


class SignatureEvasion:
    """
    Gestionnaire d'évasion de signatures pour le mode stealth
    Implemente techniques avancées pour éviter la détection
    """
    
    def __init__(self):
        self.active_profile: Optional[EvasionProfile] = None
        self.mutation_cache: Dict[str, str] = {}
        self.timing_patterns: Dict[str, float] = {}
        self.logger = logging.getLogger('stealth.signature_evasion')
        self.logger.disabled = True  # Mode silencieux
        
        # Profils d'évasion prédéfinis
        self.builtin_profiles = self._initialize_builtin_profiles()
        
        # Patterns de détection communs à éviter
        self.detection_patterns = {
            'nmap': [r'nmap', r'Nmap', r'NmAp'],
            'nikto': [r'nikto', r'Nikto'],
            'sqlmap': [r'sqlmap', r'SqlMap'],
            'burp': [r'burp', r'Burp Suite'],
            'dirb': [r'dirb', r'DIRB'],
            'gobuster': [r'gobuster', r'GoBuster'],
            'ffuf': [r'ffuf', r'Fuzz Faster']
        }
        
        # Techniques d'encodage disponibles
        self.encoding_techniques = {
            'base64': self._base64_encode,
            'url': self._url_encode,
            'hex': self._hex_encode,
            'unicode': self._unicode_encode,
            'double_url': self._double_url_encode,
            'mixed_case': self._mixed_case_encode,
            'comment_injection': self._comment_injection_encode
        }
    
    def _initialize_builtin_profiles(self) -> Dict[str, EvasionProfile]:
        """Initialise les profils d'évasion prédéfinis"""
        profiles = {}
        
        # Profil Browser Standard
        profiles['browser_standard'] = EvasionProfile(
            name="Browser Standard",
            user_agents=[
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
            ],
            timing_patterns={
                'scan': (2.0, 8.0),
                'request': (0.5, 3.0),
                'burst': (10.0, 30.0)
            },
            payload_transformations=['mixed_case', 'comment_injection'],
            header_randomization=True,
            request_chunking=False,
            encoding_techniques=['url', 'unicode'],
            signature_mutations={'nmap': 'custom_scanner', 'sqlmap': 'custom_tester'}
        )
        
        # Profil Mobile
        profiles['mobile'] = EvasionProfile(
            name="Mobile Browser",
            user_agents=[
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
                "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
            ],
            timing_patterns={
                'scan': (3.0, 12.0),
                'request': (1.0, 5.0),
                'burst': (15.0, 45.0)
            },
            payload_transformations=['base64', 'hex'],
            header_randomization=True,
            request_chunking=True,
            encoding_techniques=['base64', 'url', 'double_url'],
            signature_mutations={'nikto': 'mobile_scanner', 'dirb': 'mobile_crawler'}
        )
        
        # Profil API Client
        profiles['api_client'] = EvasionProfile(
            name="API Client", 
            user_agents=[
                "PostmanRuntime/7.36.0",
                "curl/8.4.0",
                "HTTPie/3.2.2",
                "Insomnia/8.4.5",
                "RestClient/1.0"
            ],
            timing_patterns={
                'scan': (1.0, 4.0),
                'request': (0.2, 1.5),
                'burst': (5.0, 15.0)
            },
            payload_transformations=['base64', 'hex', 'unicode'],
            header_randomization=False,
            request_chunking=True,
            encoding_techniques=['base64', 'hex', 'unicode'],
            signature_mutations={'burp': 'api_client', 'ffuf': 'api_fuzzer'}
        )
        
        # Profil Stealth Maximum
        profiles['stealth_max'] = EvasionProfile(
            name="Maximum Stealth",
            user_agents=[
                "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
            ],
            timing_patterns={
                'scan': (5.0, 20.0),
                'request': (2.0, 8.0),  
                'burst': (30.0, 120.0)
            },
            payload_transformations=['all'],
            header_randomization=True,
            request_chunking=True,
            encoding_techniques=['base64', 'hex', 'unicode', 'double_url', 'mixed_case'],
            signature_mutations={'all': 'custom_tool_v1.0'}
        )
        
        return profiles
    
    async def configure(
        self, 
        profile_name: str = 'browser_standard',
        user_agents: Optional[List[str]] = None,
        timing_range: Optional[Tuple[float, float]] = None,
        enabled: bool = True
    ):
        """
        Configure le module d'évasion de signatures
        
        Args:
            profile_name: Nom du profil à utiliser
            user_agents: Liste custom d'user agents
            timing_range: Range de délais personnalisé (min, max)
            enabled: Activer/désactiver l'évasion
        """
        if not enabled:
            self.active_profile = None
            return
        
        # Sélection du profil
        if profile_name in self.builtin_profiles:
            self.active_profile = self.builtin_profiles[profile_name]
        else:
            # Profil par défaut si non trouvé
            self.active_profile = self.builtin_profiles['browser_standard']
        
        # Override avec paramètres custom
        if user_agents:
            self.active_profile.user_agents = user_agents
            
        if timing_range:
            for pattern_type in self.active_profile.timing_patterns:
                self.active_profile.timing_patterns[pattern_type] = timing_range
        
        self.logger.info(f"Profil d'évasion configuré: {self.active_profile.name}")
    
    async def generate_evasion_parameters(
        self,
        operation_type: str,
        target: str,
        payload: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère les paramètres d'évasion pour une opération
        
        Args:
            operation_type: Type d'opération (scan, test, etc.)
            target: Cible de l'opération
            payload: Payload optionnel à transformer
        
        Returns:
            Dict avec les paramètres d'évasion générés
        """
        if not self.active_profile:
            return {'evasion_disabled': True}
        
        # User-Agent aléatoire du profil
        user_agent = random.choice(self.active_profile.user_agents)
        
        # Délai timing basé sur l'opération
        timing_key = operation_type if operation_type in self.active_profile.timing_patterns else 'request'
        timing_range = self.active_profile.timing_patterns[timing_key]
        timing_delay = random.uniform(timing_range[0], timing_range[1])
        
        # Headers personnalisés avec randomisation
        headers = await self._generate_evasion_headers(user_agent, target)
        
        # Transformation du payload si fourni
        transformed_payload = payload
        if payload and self.active_profile.payload_transformations:
            transformed_payload = await self._transform_payload(payload)
        
        # Génération d'un ID de session unique
        session_fingerprint = self._generate_session_fingerprint()
        
        return {
            'user_agent': user_agent,
            'timing_delay': timing_delay,
            'headers': headers,
            'transformed_payload': transformed_payload,
            'original_payload': payload,
            'session_fingerprint': session_fingerprint,
            'profile_used': self.active_profile.name,
            'evasion_techniques': {
                'header_randomization': self.active_profile.header_randomization,
                'request_chunking': self.active_profile.request_chunking,
                'payload_transformation': bool(transformed_payload != payload),
                'timing_variation': True
            }
        }
    
    async def _generate_evasion_headers(self, user_agent: str, target: str) -> Dict[str, str]:
        """Génère des headers HTTP d'évasion"""
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice([
                'en-US,en;q=0.5',
                'fr-FR,fr;q=0.9,en;q=0.8', 
                'es-ES,es;q=0.9,en;q=0.8',
                'de-DE,de;q=0.9,en;q=0.8'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        if self.active_profile.header_randomization:
            # Ajout d'headers aléatoires pour brouiller les pistes
            optional_headers = {
                'Cache-Control': random.choice(['no-cache', 'max-age=0', 'no-store']),
                'Pragma': 'no-cache',
                'Sec-Fetch-Dest': random.choice(['document', 'empty', 'script']),
                'Sec-Fetch-Mode': random.choice(['navigate', 'cors', 'no-cors']),
                'Sec-Fetch-Site': random.choice(['none', 'same-origin', 'cross-site']),
                'DNT': '1'
            }
            
            # Ajout aléatoire de certains headers
            for header, value in optional_headers.items():
                if random.choice([True, False]):  # 50% de chance
                    headers[header] = value
            
            # Referer aléatoire basé sur la cible
            if random.choice([True, False]) and 'http' in target:
                base_domain = target.split('/')[2] if '/' in target else target
                headers['Referer'] = f"https://{base_domain}/"
        
        return headers
    
    async def _transform_payload(self, payload: str) -> str:
        """Transforme un payload pour éviter la détection"""
        transformed = payload
        
        # Application des transformations configurées
        for transform in self.active_profile.payload_transformations:
            if transform == 'all':
                # Application de toutes les transformations disponibles
                for technique in random.sample(list(self.encoding_techniques.keys()), 2):
                    if technique in self.encoding_techniques:
                        transformed = self.encoding_techniques[technique](transformed)
            elif transform in self.encoding_techniques:
                transformed = self.encoding_techniques[transform](transformed)
        
        # Application des mutations de signatures
        transformed = await self._apply_signature_mutations(transformed)
        
        return transformed
    
    async def _apply_signature_mutations(self, payload: str) -> str:
        """Applique des mutations pour éviter les signatures connues"""
        mutated = payload
        
        # Mutations spécifiques aux outils détectés
        for tool, patterns in self.detection_patterns.items():
            for pattern in patterns:
                if re.search(pattern, mutated, re.IGNORECASE):
                    if tool in self.active_profile.signature_mutations:
                        replacement = self.active_profile.signature_mutations[tool]
                    elif 'all' in self.active_profile.signature_mutations:
                        replacement = self.active_profile.signature_mutations['all']
                    else:
                        replacement = self._generate_random_replacement(pattern)
                    
                    mutated = re.sub(pattern, replacement, mutated, flags=re.IGNORECASE)
        
        # Mutations générales (casse, espaces, caractères)
        if random.choice([True, False]):
            mutated = self._apply_general_mutations(mutated)
        
        return mutated
    
    def _generate_random_replacement(self, pattern: str) -> str:
        """Génère un remplacement aléatoire pour un pattern détecté"""
        replacements = [
            'custom_tool',
            'security_scanner',
            'webapp_tester',
            'vuln_checker',
            'sec_audit',
            'penetest_tool',
            'compliance_check'
        ]
        
        return random.choice(replacements)
    
    def _apply_general_mutations(self, text: str) -> str:
        """Applique des mutations générales au texte"""
        mutated = text
        
        mutations = [
            # Injection de commentaires HTML
            lambda t: t.replace(' ', '<!-- comment --> '),
            # Changement de casse aléatoire
            lambda t: ''.join(random.choice([c.upper(), c.lower()]) for c in t),
            # Injection de caractères invisibles
            lambda t: t.replace(' ', '\u200b '),  # Zero-width space
            # Injection de caractères d'échappement
            lambda t: t.replace('"', '\\"').replace("'", "\\'")
        ]
        
        # Application d'une mutation aléatoire
        mutation = random.choice(mutations)
        try:
            mutated = mutation(mutated)
        except Exception:
            pass  # Garde l'original si mutation échoue
        
        return mutated
    
    def _generate_session_fingerprint(self) -> str:
        """Génère un fingerprint unique pour la session"""
        timestamp = str(int(time.time()))
        random_data = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        
        fingerprint_data = f"{timestamp}-{random_data}-{self.active_profile.name}"
        
        return hashlib.md5(fingerprint_data.encode()).hexdigest()[:16]
    
    # Techniques d'encodage
    def _base64_encode(self, text: str) -> str:
        """Encodage Base64"""
        try:
            return base64.b64encode(text.encode()).decode()
        except Exception:
            return text
    
    def _url_encode(self, text: str) -> str:
        """Encodage URL"""
        import urllib.parse
        try:
            return urllib.parse.quote(text)
        except Exception:
            return text
    
    def _hex_encode(self, text: str) -> str:
        """Encodage Hexadécimal"""
        try:
            return ''.join(f'%{ord(c):02x}' for c in text)
        except Exception:
            return text
    
    def _unicode_encode(self, text: str) -> str:
        """Encodage Unicode"""
        try:
            return ''.join(f'\\u{ord(c):04x}' for c in text if ord(c) > 127) + \
                   ''.join(c for c in text if ord(c) <= 127)
        except Exception:
            return text
    
    def _double_url_encode(self, text: str) -> str:
        """Double encodage URL"""
        try:
            import urllib.parse
            encoded_once = urllib.parse.quote(text)
            return urllib.parse.quote(encoded_once)
        except Exception:
            return text
    
    def _mixed_case_encode(self, text: str) -> str:
        """Encodage avec casse mixte"""
        try:
            return ''.join(random.choice([c.upper(), c.lower()]) for c in text)
        except Exception:
            return text
    
    def _comment_injection_encode(self, text: str) -> str:
        """Injection de commentaires pour obfusquer"""
        try:
            comments = ['/*comment*/', '<!--comment-->', '//comment\\n']
            comment = random.choice(comments)
            # Injection de commentaires à intervalles aléatoires
            words = text.split(' ')
            result = []
            for i, word in enumerate(words):
                result.append(word)
                if i > 0 and i % random.randint(2, 5) == 0:
                    result.append(comment)
            return ' '.join(result)
        except Exception:
            return text
    
    async def evade_waf_detection(
        self, 
        payload: str, 
        waf_type: str = 'generic'
    ) -> Dict[str, Any]:
        """
        Techniques spécifiques d'évasion WAF
        
        Args:
            payload: Payload à transformer
            waf_type: Type de WAF (cloudflare, aws, generic, etc.)
        
        Returns:
            Dict avec payloads transformés pour évasion WAF
        """
        waf_evasion_techniques = {
            'cloudflare': [
                self._cloudflare_evasion,
                self._generic_waf_evasion
            ],
            'aws': [
                self._aws_waf_evasion,
                self._generic_waf_evasion
            ],
            'generic': [
                self._generic_waf_evasion
            ]
        }
        
        techniques = waf_evasion_techniques.get(waf_type, waf_evasion_techniques['generic'])
        
        evaded_payloads = []
        for technique in techniques:
            try:
                evaded = technique(payload)
                evaded_payloads.append(evaded)
            except Exception as e:
                self.logger.error(f"Erreur technique évasion WAF: {str(e)}")
        
        return {
            'original_payload': payload,
            'waf_type': waf_type,
            'evaded_payloads': evaded_payloads,
            'techniques_applied': len(evaded_payloads),
            'success_probability': min(95, len(evaded_payloads) * 30)  # Estimation
        }
    
    def _cloudflare_evasion(self, payload: str) -> str:
        """Techniques spécifiques Cloudflare"""
        # Cloudflare contournement par fragmentation
        evaded = payload.replace('UNION', 'UN/**/ION')
        evaded = evaded.replace('SELECT', 'SE/**/LECT')
        evaded = evaded.replace('<script>', '<scr/**/ipt>')
        return evaded
    
    def _aws_waf_evasion(self, payload: str) -> str:
        """Techniques spécifiques AWS WAF"""
        # AWS WAF contournement par encodage multiple
        evaded = self._double_url_encode(payload)
        evaded = evaded.replace(' ', '%20')
        return evaded
    
    def _generic_waf_evasion(self, payload: str) -> str:
        """Techniques génériques d'évasion WAF"""
        # Combinaison de techniques génériques
        evaded = payload
        evaded = evaded.replace(' ', '/**/')  # Commentaires SQL
        evaded = evaded.replace('=', '/*!00000=*/')  # Commentaires MySQL
        evaded = self._mixed_case_encode(evaded)
        return evaded
    
    def get_active_profile_info(self) -> Dict[str, Any]:
        """Retourne les informations sur le profil actif"""
        if not self.active_profile:
            return {'status': 'no_active_profile'}
        
        return {
            'profile_name': self.active_profile.name,
            'user_agents_count': len(self.active_profile.user_agents),
            'timing_patterns': dict(self.active_profile.timing_patterns),
            'transformations_enabled': self.active_profile.payload_transformations,
            'techniques_available': list(self.encoding_techniques.keys()),
            'header_randomization': self.active_profile.header_randomization,
            'request_chunking': self.active_profile.request_chunking,
            'signature_mutations': dict(self.active_profile.signature_mutations)
        }
    
    def get_evasion_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques d'utilisation du module"""
        return {
            'profiles_available': list(self.builtin_profiles.keys()),
            'active_profile': self.active_profile.name if self.active_profile else None,
            'detection_patterns_tracked': list(self.detection_patterns.keys()),
            'encoding_techniques_available': list(self.encoding_techniques.keys()),
            'mutation_cache_size': len(self.mutation_cache),
            'timing_patterns_cached': len(self.timing_patterns)
        }