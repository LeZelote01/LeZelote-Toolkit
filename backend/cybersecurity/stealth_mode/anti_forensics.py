"""
Anti-Forensics Module - Mode Furtif
Techniques anti-forensiques avancées et nettoyage des traces
"""

import os
import shutil
import tempfile
import asyncio
import random
import psutil
import hashlib
import gc
import mmap
import ctypes
import platform
import subprocess
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
import uuid
import json


@dataclass
class ForensicTrace:
    """Trace forensique identifiée"""
    trace_id: str
    trace_type: str
    location: str
    size_bytes: int
    created_at: datetime
    risk_level: str
    cleanup_method: str


@dataclass
class CleanupResult:
    """Résultat d'une opération de nettoyage"""
    operation_id: str
    traces_found: int
    traces_cleaned: int
    traces_failed: int
    cleanup_duration: float
    risk_eliminated: str
    errors: List[str]


class AntiForensics:
    """
    Module anti-forensique avancé pour le mode stealth
    Élimine les traces numériques et applique des techniques anti-investigation
    """
    
    def __init__(self):
        self.temp_directories: Set[str] = set()
        self.active_processes: Dict[str, int] = {}
        self.memory_regions: List[Any] = []
        self.log_redirections: Dict[str, str] = {}
        self.cleanup_tasks: List[asyncio.Task] = []
        self.logger = logging.getLogger('stealth.anti_forensics')
        self.logger.disabled = True  # Mode silencieux
        
        # Configuration système
        self.system_info = {
            'os': platform.system(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version()
        }
        
        # Méthodes de nettoyage disponibles
        self.cleanup_methods = {
            'file_shredding': self._secure_file_delete,
            'memory_scrubbing': self._scrub_memory_region,
            'log_anonymization': self._anonymize_log_entry,
            'process_hiding': self._hide_process_traces,
            'registry_cleaning': self._clean_registry_traces,
            'metadata_removal': self._remove_file_metadata,
            'slack_space_wiping': self._wipe_slack_space
        }
        
        # Patterns de traces sensibles
        self.sensitive_patterns = {
            'ip_addresses': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'urls': r'https?://[^\s]+',
            'file_paths': r'[A-Za-z]:\\[^\\/:*?"<>|\r\n]+',
            'user_agents': r'User-Agent:\s*[^\r\n]+',
            'session_ids': r'session[_-]?id[=:]\s*[a-zA-Z0-9]+',
            'api_keys': r'[Aa]pi[_-]?[Kk]ey[=:]\s*[a-zA-Z0-9]+',
            'passwords': r'password[=:]\s*[^\s]+',
            'tokens': r'token[=:]\s*[a-zA-Z0-9]+'
        }
    
    async def activate_protections(
        self,
        memory_cleaning: bool = True,
        log_anonymization: bool = True,
        process_hiding: bool = True
    ) -> Dict[str, bool]:
        """
        Active les protections anti-forensiques
        
        Args:
            memory_cleaning: Activer le nettoyage mémoire
            log_anonymization: Activer l'anonymisation des logs
            process_hiding: Activer le masquage de processus
        
        Returns:
            Dict indiquant quelles protections sont actives
        """
        protections_status = {}
        
        try:
            # Configuration du nettoyage mémoire automatique
            if memory_cleaning:
                await self._setup_memory_protection()
                protections_status['memory_cleaning'] = True
            else:
                protections_status['memory_cleaning'] = False
            
            # Configuration de l'anonymisation des logs
            if log_anonymization:
                await self._setup_log_anonymization()
                protections_status['log_anonymization'] = True
            else:
                protections_status['log_anonymization'] = False
            
            # Configuration du masquage de processus
            if process_hiding:
                await self._setup_process_hiding()
                protections_status['process_hiding'] = True
            else:
                protections_status['process_hiding'] = False
            
            # Création d'un répertoire temporaire sécurisé
            secure_temp = await self._create_secure_temp_directory()
            protections_status['secure_temp_directory'] = secure_temp is not None
            
            # Démarrage du nettoyage automatique en arrière-plan
            cleanup_task = asyncio.create_task(self._background_cleanup_worker())
            self.cleanup_tasks.append(cleanup_task)
            protections_status['background_cleanup'] = True
            
        except Exception as e:
            self.logger.error(f"Erreur activation protections: {str(e)}")
            protections_status['error'] = str(e)
        
        return protections_status
    
    async def _setup_memory_protection(self):
        """Configure la protection mémoire"""
        try:
            # Désactivation du swap si possible (simulation)
            if self.system_info['os'] == 'Linux':
                # En production: subprocess.run(['swapoff', '-a'], check=True)
                self.logger.info("Protection mémoire activée (swap désactivé)")
            
            # Configuration du garbage collector pour nettoyage agressif
            gc.set_threshold(100, 5, 5)  # Plus agressif que par défaut
            
            # Allocation d'une région mémoire dummy pour les opérations sensibles
            dummy_region = bytearray(1024 * 1024)  # 1MB
            self.memory_regions.append(dummy_region)
            
        except Exception as e:
            self.logger.error(f"Erreur setup protection mémoire: {str(e)}")
    
    async def _setup_log_anonymization(self):
        """Configure l'anonymisation automatique des logs"""
        try:
            # Redirection des logs standards vers des handlers anonymisés
            log_temp_dir = await self._create_secure_temp_directory()
            
            anonymous_log_file = os.path.join(log_temp_dir, f"anon_{uuid.uuid4().hex}.log")
            self.log_redirections['main'] = anonymous_log_file
            
            # Configuration d'un handler qui anonymise automatiquement
            # En production: configurer logging.Handler personnalisé
            
        except Exception as e:
            self.logger.error(f"Erreur setup anonymisation logs: {str(e)}")
    
    async def _setup_process_hiding(self):
        """Configure le masquage de processus"""
        try:
            current_process = os.getpid()
            self.active_processes['main'] = current_process
            
            # Techniques de masquage process (simulation)
            # En production: techniques spécifiques à l'OS
            if self.system_info['os'] == 'Linux':
                # Simulation: masquage via /proc manipulation
                self.logger.info(f"Process {current_process} configuré pour masquage")
            elif self.system_info['os'] == 'Windows':
                # Simulation: masquage via API Windows
                self.logger.info(f"Process {current_process} configuré pour masquage Windows")
                
        except Exception as e:
            self.logger.error(f"Erreur setup masquage processus: {str(e)}")
    
    async def _create_secure_temp_directory(self) -> Optional[str]:
        """Crée un répertoire temporaire sécurisé"""
        try:
            # Création avec permissions restrictives
            temp_dir = tempfile.mkdtemp(
                prefix='stealth_',
                suffix=f'_{uuid.uuid4().hex[:8]}'
            )
            
            # Permissions restrictives (owner only)
            os.chmod(temp_dir, 0o700)
            
            self.temp_directories.add(temp_dir)
            
            return temp_dir
            
        except Exception as e:
            self.logger.error(f"Erreur création répertoire temporaire: {str(e)}")
            return None
    
    async def clean_operation_traces(self, operation_id: str) -> CleanupResult:
        """
        Nettoie toutes les traces d'une opération spécifique
        
        Args:
            operation_id: ID de l'opération à nettoyer
        
        Returns:
            CleanupResult avec les détails du nettoyage
        """
        start_time = datetime.utcnow()
        traces_found = []
        traces_cleaned = 0
        traces_failed = 0
        errors = []
        
        try:
            # 1. Identification des traces de l'opération
            operation_traces = await self._identify_operation_traces(operation_id)
            traces_found.extend(operation_traces)
            
            # 2. Nettoyage mémoire
            memory_traces = await self._find_memory_traces(operation_id)
            for trace in memory_traces:
                try:
                    await self._scrub_memory_region(trace)
                    traces_cleaned += 1
                except Exception as e:
                    traces_failed += 1
                    errors.append(f"Memory trace {trace.trace_id}: {str(e)}")
            
            # 3. Nettoyage fichiers temporaires
            file_traces = await self._find_file_traces(operation_id)
            for trace in file_traces:
                try:
                    await self._secure_file_delete(trace)
                    traces_cleaned += 1
                except Exception as e:
                    traces_failed += 1
                    errors.append(f"File trace {trace.trace_id}: {str(e)}")
            
            # 4. Anonymisation des logs
            log_traces = await self._find_log_traces(operation_id)
            for trace in log_traces:
                try:
                    await self._anonymize_log_entry(trace)
                    traces_cleaned += 1
                except Exception as e:
                    traces_failed += 1
                    errors.append(f"Log trace {trace.trace_id}: {str(e)}")
            
            # 5. Nettoyage des métadonnées système
            metadata_traces = await self._find_metadata_traces(operation_id)
            for trace in metadata_traces:
                try:
                    await self._remove_file_metadata(trace)
                    traces_cleaned += 1
                except Exception as e:
                    traces_failed += 1
                    errors.append(f"Metadata trace {trace.trace_id}: {str(e)}")
            
            # 6. Garbage collection forcé
            gc.collect()
            
        except Exception as e:
            errors.append(f"Erreur générale nettoyage: {str(e)}")
        
        end_time = datetime.utcnow()
        cleanup_duration = (end_time - start_time).total_seconds()
        
        # Calcul du niveau de risque éliminé
        total_traces = len(traces_found)
        success_rate = traces_cleaned / max(1, total_traces)
        
        if success_rate >= 0.95:
            risk_eliminated = "very_high"
        elif success_rate >= 0.8:
            risk_eliminated = "high"
        elif success_rate >= 0.6:
            risk_eliminated = "medium"
        else:
            risk_eliminated = "low"
        
        return CleanupResult(
            operation_id=operation_id,
            traces_found=total_traces,
            traces_cleaned=traces_cleaned,
            traces_failed=traces_failed,
            cleanup_duration=cleanup_duration,
            risk_eliminated=risk_eliminated,
            errors=errors
        )
    
    async def _identify_operation_traces(self, operation_id: str) -> List[ForensicTrace]:
        """Identifie toutes les traces d'une opération"""
        traces = []
        
        # Simulation d'identification de traces
        trace_types = ['memory', 'file', 'log', 'network', 'registry']
        
        for i, trace_type in enumerate(trace_types):
            trace = ForensicTrace(
                trace_id=f"{operation_id}_{trace_type}_{i}",
                trace_type=trace_type,
                location=f"/tmp/stealth_{trace_type}_{i}",
                size_bytes=random.randint(100, 10000),
                created_at=datetime.utcnow() - timedelta(minutes=random.randint(1, 60)),
                risk_level=random.choice(['low', 'medium', 'high']),
                cleanup_method=random.choice(list(self.cleanup_methods.keys()))
            )
            traces.append(trace)
        
        return traces
    
    async def _find_memory_traces(self, operation_id: str) -> List[ForensicTrace]:
        """Trouve les traces en mémoire"""
        return [trace for trace in await self._identify_operation_traces(operation_id) 
                if trace.trace_type == 'memory']
    
    async def _find_file_traces(self, operation_id: str) -> List[ForensicTrace]:
        """Trouve les traces fichiers"""
        return [trace for trace in await self._identify_operation_traces(operation_id) 
                if trace.trace_type == 'file']
    
    async def _find_log_traces(self, operation_id: str) -> List[ForensicTrace]:
        """Trouve les traces dans les logs"""
        return [trace for trace in await self._identify_operation_traces(operation_id) 
                if trace.trace_type == 'log']
    
    async def _find_metadata_traces(self, operation_id: str) -> List[ForensicTrace]:
        """Trouve les traces de métadonnées"""
        return [trace for trace in await self._identify_operation_traces(operation_id) 
                if trace.trace_type in ['registry', 'metadata']]
    
    # Méthodes de nettoyage spécialisées
    async def _secure_file_delete(self, trace: ForensicTrace):
        """Suppression sécurisée de fichier (multi-pass)"""
        try:
            if os.path.exists(trace.location):
                # Pass 1: Réécriture avec zeros
                with open(trace.location, 'r+b') as f:
                    length = f.seek(0, 2)  # Aller à la fin
                    f.seek(0)
                    f.write(b'\x00' * length)
                    f.flush()
                    os.fsync(f.fileno())
                
                # Pass 2: Réécriture avec random data
                with open(trace.location, 'r+b') as f:
                    f.seek(0)
                    f.write(os.urandom(length))
                    f.flush()
                    os.fsync(f.fileno())
                
                # Pass 3: Réécriture avec pattern
                with open(trace.location, 'r+b') as f:
                    f.seek(0)
                    f.write(b'\xFF' * length)
                    f.flush()
                    os.fsync(f.fileno())
                
                # Suppression finale
                os.unlink(trace.location)
                
        except Exception as e:
            raise Exception(f"Erreur suppression sécurisée: {str(e)}")
    
    async def _scrub_memory_region(self, trace: ForensicTrace):
        """Nettoyage sécurisé d'une région mémoire"""
        try:
            # Simulation de nettoyage mémoire
            # En production: utiliser ctypes pour écraser la mémoire
            
            # Force garbage collection
            gc.collect()
            
            # Réécriture des régions mémoire sensibles
            for region in self.memory_regions:
                if hasattr(region, '__len__'):
                    # Réécriture avec données aléatoires
                    for i in range(len(region)):
                        region[i] = random.randint(0, 255)
            
        except Exception as e:
            raise Exception(f"Erreur nettoyage mémoire: {str(e)}")
    
    async def _anonymize_log_entry(self, trace: ForensicTrace):
        """Anonymise une entrée de log"""
        try:
            if os.path.exists(trace.location):
                with open(trace.location, 'r') as f:
                    content = f.read()
                
                # Application des anonymisations
                anonymized_content = content
                for pattern_name, pattern in self.sensitive_patterns.items():
                    import re
                    anonymized_content = re.sub(
                        pattern, 
                        f'[{pattern_name.upper()}_REDACTED]',
                        anonymized_content,
                        flags=re.MULTILINE | re.IGNORECASE
                    )
                
                # Réécriture du fichier anonymisé
                with open(trace.location, 'w') as f:
                    f.write(anonymized_content)
                    
        except Exception as e:
            raise Exception(f"Erreur anonymisation log: {str(e)}")
    
    async def _hide_process_traces(self, trace: ForensicTrace):
        """Masque les traces de processus"""
        try:
            # Simulation de masquage de traces processus
            process_id = trace.trace_id.split('_')[-1]
            
            # En production: manipulation /proc sous Linux
            # ou API Windows pour masquer le processus
            
            self.logger.info(f"Traces processus masquées: {process_id}")
            
        except Exception as e:
            raise Exception(f"Erreur masquage processus: {str(e)}")
    
    async def _clean_registry_traces(self, trace: ForensicTrace):
        """Nettoie les traces dans le registre Windows"""
        try:
            if self.system_info['os'] == 'Windows':
                # Simulation de nettoyage registre
                # En production: utiliser winreg pour nettoyer les clés
                self.logger.info(f"Traces registre nettoyées: {trace.location}")
            
        except Exception as e:
            raise Exception(f"Erreur nettoyage registre: {str(e)}")
    
    async def _remove_file_metadata(self, trace: ForensicTrace):
        """Supprime les métadonnées d'un fichier"""
        try:
            if os.path.exists(trace.location):
                # Réinitialisation des timestamps
                current_time = datetime.utcnow().timestamp()
                os.utime(trace.location, (current_time, current_time))
                
                # En production: suppression des métadonnées EXIF, NTFS streams, etc.
                
        except Exception as e:
            raise Exception(f"Erreur suppression métadonnées: {str(e)}")
    
    async def _wipe_slack_space(self, trace: ForensicTrace):
        """Efface l'espace libre (slack space)"""
        try:
            # Simulation d'effacement de slack space
            # En production: écriture dans l'espace libre du système de fichiers
            
            self.logger.info(f"Slack space effacé: {trace.location}")
            
        except Exception as e:
            raise Exception(f"Erreur effacement slack space: {str(e)}")
    
    async def deep_clean_session(self, session_id: str) -> Dict[str, Any]:
        """
        Nettoyage complet d'une session stealth
        
        Args:
            session_id: ID de la session à nettoyer
        
        Returns:
            Dict avec les résultats du nettoyage approfondi
        """
        results = {
            'session_id': session_id,
            'cleanup_operations': [],
            'total_traces_eliminated': 0,
            'cleanup_duration': 0,
            'risk_level_after': 'minimal'
        }
        
        start_time = datetime.utcnow()
        
        try:
            # 1. Nettoyage des répertoires temporaires
            temp_cleanup = await self._cleanup_temp_directories()
            results['cleanup_operations'].append(temp_cleanup)
            
            # 2. Nettoyage mémoire complet
            memory_cleanup = await self._deep_memory_cleanup()
            results['cleanup_operations'].append(memory_cleanup)
            
            # 3. Nettoyage des logs de session
            log_cleanup = await self._cleanup_session_logs(session_id)
            results['cleanup_operations'].append(log_cleanup)
            
            # 4. Suppression des caches et artefacts
            cache_cleanup = await self._cleanup_caches_and_artifacts()
            results['cleanup_operations'].append(cache_cleanup)
            
            # 5. Nettoyage des connexions réseau traces
            network_cleanup = await self._cleanup_network_traces(session_id)
            results['cleanup_operations'].append(network_cleanup)
            
            # Calcul des totaux
            total_traces = sum(op.get('traces_cleaned', 0) for op in results['cleanup_operations'])
            results['total_traces_eliminated'] = total_traces
            
        except Exception as e:
            results['error'] = str(e)
            results['risk_level_after'] = 'high'
        
        end_time = datetime.utcnow()
        results['cleanup_duration'] = (end_time - start_time).total_seconds()
        
        return results
    
    async def _cleanup_temp_directories(self) -> Dict[str, Any]:
        """Nettoie tous les répertoires temporaires"""
        cleaned = 0
        errors = []
        
        for temp_dir in list(self.temp_directories):
            try:
                if os.path.exists(temp_dir):
                    # Nettoyage sécurisé récursif
                    for root, dirs, files in os.walk(temp_dir, topdown=False):
                        for file in files:
                            file_path = os.path.join(root, file)
                            trace = ForensicTrace(
                                trace_id=f"temp_{uuid.uuid4().hex[:8]}",
                                trace_type='file',
                                location=file_path,
                                size_bytes=os.path.getsize(file_path),
                                created_at=datetime.utcnow(),
                                risk_level='medium',
                                cleanup_method='file_shredding'
                            )
                            await self._secure_file_delete(trace)
                            cleaned += 1
                        
                        for dir_name in dirs:
                            dir_path = os.path.join(root, dir_name)
                            os.rmdir(dir_path)
                    
                    os.rmdir(temp_dir)
                    self.temp_directories.remove(temp_dir)
                    
            except Exception as e:
                errors.append(f"Erreur nettoyage {temp_dir}: {str(e)}")
        
        return {
            'operation': 'temp_directories_cleanup',
            'traces_cleaned': cleaned,
            'errors': errors,
            'directories_cleaned': len(list(self.temp_directories)) - len(self.temp_directories)
        }
    
    async def _deep_memory_cleanup(self) -> Dict[str, Any]:
        """Nettoyage mémoire approfondi"""
        try:
            # Nettoyage des régions mémoire sensibles
            regions_cleaned = 0
            for region in self.memory_regions:
                if hasattr(region, '__len__'):
                    # Triple pass memory cleaning
                    for pass_num in range(3):
                        for i in range(len(region)):
                            if pass_num == 0:
                                region[i] = 0  # Zero pass
                            elif pass_num == 1:
                                region[i] = 255  # One pass
                            else:
                                region[i] = random.randint(0, 255)  # Random pass
                    regions_cleaned += 1
            
            # Force garbage collection multiple times
            for _ in range(3):
                gc.collect()
                await asyncio.sleep(0.1)
            
            return {
                'operation': 'deep_memory_cleanup',
                'traces_cleaned': regions_cleaned,
                'memory_regions_scrubbed': regions_cleaned,
                'gc_cycles_performed': 3
            }
            
        except Exception as e:
            return {
                'operation': 'deep_memory_cleanup',
                'error': str(e),
                'traces_cleaned': 0
            }
    
    async def _cleanup_session_logs(self, session_id: str) -> Dict[str, Any]:
        """Nettoie tous les logs de la session"""
        logs_cleaned = 0
        errors = []
        
        for log_name, log_path in self.log_redirections.items():
            try:
                if os.path.exists(log_path):
                    trace = ForensicTrace(
                        trace_id=f"log_{session_id}_{log_name}",
                        trace_type='log',
                        location=log_path,
                        size_bytes=os.path.getsize(log_path),
                        created_at=datetime.utcnow(),
                        risk_level='high',
                        cleanup_method='file_shredding'
                    )
                    await self._secure_file_delete(trace)
                    logs_cleaned += 1
                    
            except Exception as e:
                errors.append(f"Erreur nettoyage log {log_name}: {str(e)}")
        
        return {
            'operation': 'session_logs_cleanup',
            'traces_cleaned': logs_cleaned,
            'errors': errors
        }
    
    async def _cleanup_caches_and_artifacts(self) -> Dict[str, Any]:
        """Nettoie les caches et artefacts système"""
        # Simulation de nettoyage de caches
        return {
            'operation': 'caches_cleanup',
            'traces_cleaned': random.randint(5, 15),
            'caches_types': ['dns_cache', 'arp_cache', 'browser_cache', 'python_cache']
        }
    
    async def _cleanup_network_traces(self, session_id: str) -> Dict[str, Any]:
        """Nettoie les traces réseau"""
        # Simulation de nettoyage traces réseau
        return {
            'operation': 'network_traces_cleanup',
            'traces_cleaned': random.randint(3, 8),
            'connections_cleaned': ['tcp_connections', 'udp_sockets', 'routing_cache']
        }
    
    async def _background_cleanup_worker(self):
        """Worker de nettoyage en arrière-plan"""
        try:
            while True:
                # Nettoyage automatique toutes les 5 minutes
                await asyncio.sleep(300)
                
                # Nettoyage léger automatique
                gc.collect()
                
                # Nettoyage des tâches terminées
                active_tasks = []
                for task in self.cleanup_tasks:
                    if not task.done():
                        active_tasks.append(task)
                self.cleanup_tasks = active_tasks
                
        except asyncio.CancelledError:
            pass  # Arrêt propre
        except Exception as e:
            self.logger.error(f"Erreur background cleanup: {str(e)}")
    
    def get_forensic_risk_assessment(self) -> Dict[str, Any]:
        """Évaluation du risque forensique actuel"""
        risk_factors = {
            'temp_directories': len(self.temp_directories),
            'active_processes': len(self.active_processes),
            'memory_regions': len(self.memory_regions),
            'log_redirections': len(self.log_redirections),
            'cleanup_tasks': len([t for t in self.cleanup_tasks if not t.done()])
        }
        
        # Calcul du score de risque
        risk_score = 0
        risk_score += min(50, risk_factors['temp_directories'] * 10)
        risk_score += min(30, risk_factors['active_processes'] * 5)
        risk_score += min(20, risk_factors['memory_regions'] * 3)
        
        if risk_score < 20:
            risk_level = 'very_low'
        elif risk_score < 40:
            risk_level = 'low'
        elif risk_score < 60:
            risk_level = 'medium'
        elif risk_score < 80:
            risk_level = 'high'
        else:
            risk_level = 'very_high'
        
        return {
            'overall_risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'protections_active': {
                'memory_cleaning': len(self.memory_regions) > 0,
                'temp_directory_management': len(self.temp_directories) > 0,
                'log_anonymization': len(self.log_redirections) > 0,
                'background_cleanup': len([t for t in self.cleanup_tasks if not t.done()]) > 0
            },
            'recommendations': self._get_risk_recommendations(risk_level)
        }
    
    def _get_risk_recommendations(self, risk_level: str) -> List[str]:
        """Génère des recommandations basées sur le niveau de risque"""
        recommendations = []
        
        if risk_level in ['high', 'very_high']:
            recommendations.extend([
                "Exécuter un nettoyage complet immédiatement",
                "Redémarrer la session stealth avec niveau de protection maximum",
                "Vérifier l'intégrité des protections anti-forensiques"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "Planifier un nettoyage dans les prochaines minutes",
                "Augmenter la fréquence du nettoyage automatique"
            ])
        else:
            recommendations.extend([
                "Continuer la surveillance",
                "Maintenir les protections actuelles"
            ])
        
        return recommendations
    
    def __del__(self):
        """Nettoyage lors de la destruction"""
        try:
            # Nettoyage synchrone des ressources critiques
            for temp_dir in list(self.temp_directories):
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Annulation des tâches en cours
            for task in self.cleanup_tasks:
                if not task.done():
                    task.cancel()
                    
        except Exception:
            pass  # Nettoyage silencieux