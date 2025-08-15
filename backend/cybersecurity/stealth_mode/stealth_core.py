"""
Stealth Core - Module central du mode furtif
Coordination de toutes les fonctionnalités de stealth
"""

import asyncio
import logging
import uuid
import json
import os
import tempfile
import shutil
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from .network_obfuscation import NetworkObfuscator
from .signature_evasion import SignatureEvasion
from .anti_forensics import AntiForensics

# Configuration des logs pour le mode stealth
stealth_logger = logging.getLogger('stealth_mode')
stealth_logger.setLevel(logging.WARNING)  # Minimal logging par défaut


class StealthLevel(Enum):
    """Niveaux de furtivité"""
    LOW = "low"           # Obfuscation basique
    MEDIUM = "medium"     # Obfuscation avancée + anti-forensics
    HIGH = "high"         # Obfuscation maximale + évasion complète
    GHOST = "ghost"       # Mode fantôme - indétectable total


@dataclass
class StealthConfig:
    """Configuration du mode stealth"""
    level: StealthLevel = StealthLevel.MEDIUM
    tor_enabled: bool = True
    vpn_chaining: bool = False
    signature_evasion: bool = True
    anti_forensics: bool = True
    decoy_traffic: bool = False
    mac_spoofing: bool = False
    process_hiding: bool = True
    memory_cleaning: bool = True
    log_anonymization: bool = True
    dns_over_https: bool = True
    proxy_chains: Optional[List[str]] = None
    custom_user_agents: Optional[List[str]] = None
    timing_variation_range: tuple = (1, 30)  # secondes


@dataclass
class StealthSession:
    """Session stealth active"""
    session_id: str
    level: StealthLevel
    start_time: datetime
    config: StealthConfig
    active_operations: List[str]
    network_identity: Dict[str, Any]
    forensic_protection: Dict[str, bool]


class StealthCore:
    """
    Classe principale du module Stealth Mode
    Coordonne toutes les fonctionnalités d'anonymat et d'indétectabilité
    """
    
    def __init__(self):
        self.sessions: Dict[str, StealthSession] = {}
        self.network_obfuscator = NetworkObfuscator()
        self.signature_evasion = SignatureEvasion()
        self.anti_forensics = AntiForensics()
        self.temp_dir = None
        self.original_config_backup = {}
        self._initialize_stealth_environment()
    
    def _initialize_stealth_environment(self):
        """Initialise l'environnement stealth"""
        # Création d'un répertoire temporaire sécurisé
        self.temp_dir = tempfile.mkdtemp(prefix='stealth_', suffix='_tmp')
        
        # Configuration des logs minimaux
        logging.getLogger('stealth_mode').disabled = True
        
        # Backup de la configuration originale
        self.original_config_backup = {
            'temp_dir': self.temp_dir,
            'log_level': logging.root.level,
            'initialized_at': datetime.utcnow().isoformat()
        }
    
    async def create_stealth_session(
        self, 
        config: Optional[StealthConfig] = None
    ) -> str:
        """
        Crée une nouvelle session stealth
        
        Args:
            config: Configuration stealth (utilise config par défaut si None)
        
        Returns:
            str: ID de la session créée
        """
        if config is None:
            config = StealthConfig()
        
        session_id = str(uuid.uuid4())
        
        # Initialisation des composants selon la configuration
        network_identity = await self.network_obfuscator.initialize_identity(
            tor_enabled=config.tor_enabled,
            vpn_chaining=config.vpn_chaining,
            mac_spoofing=config.mac_spoofing
        )
        
        # Configuration de l'évasion de signature
        await self.signature_evasion.configure(
            user_agents=config.custom_user_agents,
            timing_range=config.timing_variation_range,
            enabled=config.signature_evasion
        )
        
        # Activation des protections anti-forensiques
        forensic_protection = await self.anti_forensics.activate_protections(
            memory_cleaning=config.memory_cleaning,
            log_anonymization=config.log_anonymization,
            process_hiding=config.process_hiding
        )
        
        session = StealthSession(
            session_id=session_id,
            level=config.level,
            start_time=datetime.utcnow(),
            config=config,
            active_operations=[],
            network_identity=network_identity,
            forensic_protection=forensic_protection
        )
        
        self.sessions[session_id] = session
        
        stealth_logger.info(f"Session stealth créée: {session_id} (Niveau: {config.level.value})")
        
        return session_id
    
    async def execute_stealth_operation(
        self, 
        session_id: str, 
        operation_type: str, 
        target: str, 
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Exécute une opération en mode stealth
        
        Args:
            session_id: ID de la session stealth
            operation_type: Type d'opération (scan, test, etc.)
            target: Cible de l'opération
            params: Paramètres spécifiques à l'opération
        
        Returns:
            Dict contenant les résultats de l'opération
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session stealth non trouvée: {session_id}")
        
        session = self.sessions[session_id]
        operation_id = str(uuid.uuid4())
        
        session.active_operations.append(operation_id)
        
        try:
            # Application de l'obfuscation réseau
            obfuscated_connection = await self.network_obfuscator.create_obfuscated_connection(
                target=target,
                session_config=session.config
            )
            
            # Application de l'évasion de signature
            evasion_params = await self.signature_evasion.generate_evasion_parameters(
                operation_type=operation_type,
                target=target
            )
            
            # Génération de trafic decoy si activé
            if session.config.decoy_traffic:
                await self.network_obfuscator.generate_decoy_traffic(
                    target_pattern=target,
                    duration_seconds=30
                )
            
            # Simulation d'exécution de l'opération avec les paramètres stealth
            operation_result = await self._simulate_stealth_operation(
                operation_type=operation_type,
                target=target,
                connection=obfuscated_connection,
                evasion_params=evasion_params,
                params=params or {}
            )
            
            # Nettoyage anti-forensique immédiat
            await self.anti_forensics.clean_operation_traces(operation_id)
            
            return {
                'operation_id': operation_id,
                'session_id': session_id,
                'status': 'completed',
                'stealth_level': session.level.value,
                'network_identity': session.network_identity,
                'evasion_applied': evasion_params,
                'results': operation_result,
                'timestamp': datetime.utcnow().isoformat(),
                'detection_risk': self._calculate_detection_risk(session, operation_result)
            }
            
        except Exception as e:
            stealth_logger.error(f"Erreur dans opération stealth {operation_id}: {str(e)}")
            return {
                'operation_id': operation_id,
                'session_id': session_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        finally:
            if operation_id in session.active_operations:
                session.active_operations.remove(operation_id)
    
    async def _simulate_stealth_operation(
        self,
        operation_type: str,
        target: str,
        connection: Dict[str, Any],
        evasion_params: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simule l'exécution d'une opération stealth"""
        
        # Simulation d'un délai variable pour éviter la détection
        delay = evasion_params.get('timing_delay', 2)
        await asyncio.sleep(delay)
        
        # Résultat simulé basé sur le type d'opération
        operation_results = {
            'port_scan': {
                'ports_found': ['80', '443', '8080'],
                'os_detection': 'Linux Ubuntu 20.04',
                'services': ['nginx', 'ssh', 'http']
            },
            'vulnerability_scan': {
                'vulnerabilities': [
                    {'cve': 'CVE-2023-1234', 'severity': 'medium', 'service': 'nginx'},
                    {'cve': 'CVE-2023-5678', 'severity': 'low', 'service': 'ssh'}
                ],
                'risk_score': 6.5
            },
            'web_crawl': {
                'pages_found': 15,
                'forms_detected': 3,
                'potential_entry_points': ['login.php', 'admin/', 'api/v1/']
            }
        }
        
        return {
            'target': target,
            'operation_type': operation_type,
            'connection_info': connection,
            'evasion_applied': evasion_params,
            'data': operation_results.get(operation_type, {'status': 'completed'}),
            'stealth_indicators': {
                'signature_randomized': True,
                'timing_varied': True,
                'source_obfuscated': True,
                'traces_cleaned': True
            }
        }
    
    def _calculate_detection_risk(self, session: StealthSession, operation_result: Dict[str, Any]) -> str:
        """Calcule le risque de détection basé sur la configuration et les résultats"""
        risk_score = 0
        
        # Facteurs de réduction du risque
        if session.config.tor_enabled:
            risk_score -= 30
        if session.config.vpn_chaining:
            risk_score -= 20
        if session.config.signature_evasion:
            risk_score -= 25
        if session.config.decoy_traffic:
            risk_score -= 15
        if session.config.anti_forensics:
            risk_score -= 10
        
        # Facteurs d'augmentation du risque
        if len(session.active_operations) > 5:
            risk_score += 20
        if 'error' in operation_result:
            risk_score += 15
        
        # Normalisation
        risk_score = max(0, min(100, risk_score + 50))  # Base de 50
        
        if risk_score < 20:
            return 'very_low'
        elif risk_score < 40:
            return 'low'
        elif risk_score < 60:
            return 'medium'
        elif risk_score < 80:
            return 'high'
        else:
            return 'very_high'
    
    async def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Récupère le statut d'une session stealth"""
        if session_id not in self.sessions:
            return {'error': 'Session non trouvée'}
        
        session = self.sessions[session_id]
        
        # Conversion manuelle pour éviter les problèmes de sérialisation
        config_dict = asdict(session.config)
        config_dict['level'] = session.config.level.value  # Convertir enum en string
        
        return {
            'session_id': session.session_id,
            'level': session.level.value,
            'start_time': session.start_time.isoformat(),
            'duration': str(datetime.utcnow() - session.start_time),
            'active_operations': len(session.active_operations),
            'network_identity': session.network_identity,
            'forensic_protection': session.forensic_protection,
            'config': config_dict
        }
    
    async def terminate_stealth_session(self, session_id: str) -> Dict[str, str]:
        """Termine une session stealth et nettoie toutes les traces"""
        if session_id not in self.sessions:
            return {'error': 'Session non trouvée'}
        
        session = self.sessions[session_id]
        
        try:
            # Nettoyage de toutes les opérations actives
            for operation_id in session.active_operations:
                await self.anti_forensics.clean_operation_traces(operation_id)
            
            # Restauration de l'identité réseau originale
            await self.network_obfuscator.restore_original_identity()
            
            # Nettoyage final de la session
            await self.anti_forensics.deep_clean_session(session_id)
            
            # Suppression de la session
            del self.sessions[session_id]
            
            return {
                'status': 'terminated',
                'session_id': session_id,
                'message': 'Session stealth terminée et traces nettoyées'
            }
            
        except Exception as e:
            stealth_logger.error(f"Erreur lors de la terminaison de la session {session_id}: {str(e)}")
            return {'error': f'Erreur lors de la terminaison: {str(e)}'}
    
    def get_stealth_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques globales du mode stealth"""
        active_sessions = len(self.sessions)
        total_operations = sum(len(s.active_operations) for s in self.sessions.values())
        
        levels_distribution = {}
        for session in self.sessions.values():
            level = session.level.value
            levels_distribution[level] = levels_distribution.get(level, 0) + 1
        
        return {
            'active_sessions': active_sessions,
            'total_active_operations': total_operations,
            'levels_distribution': levels_distribution,
            'components_status': {
                'network_obfuscator': 'active',
                'signature_evasion': 'active', 
                'anti_forensics': 'active'
            },
            'temp_directory': self.temp_dir,
            'uptime': str(datetime.utcnow() - datetime.fromisoformat(
                self.original_config_backup['initialized_at']
            ))
        }
    
    def __del__(self):
        """Nettoyage lors de la destruction de l'objet"""
        if hasattr(self, 'temp_dir') and self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass  # Nettoyage silencieux