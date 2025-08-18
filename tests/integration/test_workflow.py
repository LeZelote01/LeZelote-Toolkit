#!/usr/bin/env python3
"""
Tests d'Intégration - Workflow Complet
=====================================

Tests du workflow complet de pentesting depuis la reconnaissance
jusqu'au reporting, en passant par la détection de vulnérabilités
et l'exploitation.

Ces tests valident l'intégration entre tous les modules principaux
et la cohérence des données entre les phases.
"""

import sys
import os
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.engine.orchestrator import PentestOrchestrator
from core.utils.logging_handler import get_logger
from modules.reconnaissance.network_scanner import NetworkScanner
from modules.vulnerability.web_scanner import WebScanner
from modules.exploitation.web_exploit import WebExploitationEngine
from modules.reporting.report_generator import ReportGenerator


@pytest.fixture
def orchestrator():
    """Fixture pour l'orchestrateur de pentest"""
    return PentestOrchestrator(target="192.168.1.100", profile="test")

@pytest.fixture
def temp_project_dir():
    """Fixture pour un dossier de projet temporaire"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_target():
    """Fixture pour une cible de test"""
    return {
        'ip': '192.168.1.100',
        'hostname': 'test-target.local',
        'ports': [22, 80, 443, 3389],
        'services': {
            22: 'ssh',
            80: 'http',
            443: 'https',
            3389: 'rdp'
        }
    }


class TestWorkflowIntegration:
    """Tests d'intégration du workflow complet"""

    def test_full_pentest_workflow(self, orchestrator, temp_project_dir, mock_target):
        """Test du workflow complet de pentest"""
        logger = get_logger(__name__)
        
        # Configuration du projet
        project_config = {
            'name': 'integration_test_project',
            'target': mock_target['ip'],
            'profile': 'comprehensive',
            'output_dir': temp_project_dir,
            'phases': ['reconnaissance', 'vulnerability', 'exploitation', 'reporting']
        }
        
        # Mock des outils externes et vérification de consentement
        with patch('core.api.nmap_api.subprocess.run') as mock_nmap, \
             patch('core.security.consent_manager.ConsentManager.verify_consent') as mock_consent:
            
            # Configuration des mocks
            mock_nmap.return_value = Mock(
                returncode=0,
                stdout=self._get_mock_nmap_output()
            )
            
            # Mock du consentement pour les tests
            mock_consent.return_value = True
            
            # Initialisation du projet
            result = orchestrator.initialize_project(project_config)
            assert result['success'] is True
            assert 'project_id' in result
            
            project_id = result['project_id']
            
            # Exécution du workflow complet
            logger.info("Démarrage du workflow complet")
            
            # Exécution du workflow
            workflow_result = orchestrator.run_workflow()
            
            # Vérifications du résultat
            assert workflow_result is not None
            assert 'start_time' in workflow_result
            assert workflow_result.get('state') in ['complete', 'paused', 'running']
            
        logger.info("Workflow complet testé avec succès")

    def test_workflow_with_errors(self, orchestrator, temp_project_dir):
        """Test du workflow avec gestion d'erreurs"""
        project_config = {
            'name': 'error_test_project',
            'target': '999.999.999.999',  # IP invalide
            'profile': 'quick',
            'output_dir': temp_project_dir,
            'phases': ['reconnaissance']
        }
        
        # Mock d'un échec de scan et vérification de consentement
        with patch('core.api.nmap_api.subprocess.run') as mock_nmap, \
             patch('core.security.consent_manager.ConsentManager.verify_consent') as mock_consent:
            mock_nmap.return_value = Mock(
                returncode=1,
                stderr='Host seems down'
            )
            
            # Mock du consentement pour les tests
            mock_consent.return_value = True
            
            result = orchestrator.initialize_project(project_config)
            assert result['success'] is True
            
            # Tentative d'exécution du workflow avec une cible invalide
            try:
                workflow_result = orchestrator.run_workflow()
                # Le workflow devrait échouer ou retourner un état d'erreur
                assert workflow_result.get('state') in ['failed', 'error']
            except Exception as e:
                # Une exception est attendue avec une cible invalide
                assert 'failed' in str(e).lower() or 'error' in str(e).lower() or 'host' in str(e).lower()

    def test_workflow_data_continuity(self, orchestrator, temp_project_dir, mock_target):
        """Test de la continuité des données entre les phases"""
        project_config = {
            'name': 'continuity_test_project',
            'target': mock_target['ip'],
            'profile': 'standard',
            'output_dir': temp_project_dir
        }
        
        with patch('core.api.nmap_api.subprocess.run') as mock_nmap, \
             patch('core.security.consent_manager.ConsentManager.verify_consent') as mock_consent:
            mock_nmap.return_value = Mock(
                returncode=0,
                stdout=self._get_mock_nmap_output()
            )
            
            # Mock du consentement pour les tests
            mock_consent.return_value = True
            
            # Initialisation
            result = orchestrator.initialize_project(project_config)
            project_id = result['project_id']
            
            # Phase reconnaissance
            recon_result = orchestrator.execute_phase('reconnaissance', project_id, {
                'target': mock_target['ip']
            })
            
            # Vérification de la persistance des données
            project_data = orchestrator.get_project_data(project_id)
            assert 'reconnaissance' in project_data['phases']
            assert 'hosts_discovered' in project_data['phases']['reconnaissance']
            
            # Validation que les données sont bien stockées
            stored_hosts = project_data['phases']['reconnaissance']['hosts_discovered']
            assert len(stored_hosts) == len(recon_result['hosts_discovered'])
            
            # Test de récupération des données pour phase suivante
            for i, host in enumerate(stored_hosts):
                assert host['ip'] == recon_result['hosts_discovered'][i]['ip']
                assert host['ports'] == recon_result['hosts_discovered'][i]['ports']

    def test_concurrent_workflow_execution(self, orchestrator, temp_project_dir):
        """Test de l'exécution concurrente de workflows"""
        import asyncio
        import concurrent.futures
        
        async def run_parallel_projects():
            """Exécute plusieurs projets en parallèle"""
            projects = []
            
            for i in range(3):
                project_config = {
                    'name': f'parallel_test_project_{i}',
                    'target': f'192.168.1.{100 + i}',
                    'profile': 'quick',
                    'output_dir': temp_project_dir
                }
                projects.append(project_config)
            
            with patch('core.api.nmap_api.subprocess.run') as mock_nmap, \
                 patch('core.security.consent_manager.ConsentManager.verify_consent') as mock_consent:
                mock_nmap.return_value = Mock(
                    returncode=0,
                    stdout=self._get_mock_nmap_output()
                )
                
                # Mock du consentement pour les tests
                mock_consent.return_value = True
                
                # Exécution parallèle
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    futures = []
                    
                    for project_config in projects:
                        future = executor.submit(self._run_single_project, orchestrator, project_config)
                        futures.append(future)
                    
                    # Récupération des résultats
                    results = []
                    for future in concurrent.futures.as_completed(futures):
                        result = future.result()
                        results.append(result)
                        assert result['success'] is True
                    
                    # Validation que tous les projets ont réussi
                    assert len(results) == 3
                    
                    # Validation de l'unicité des project_ids
                    project_ids = [r['project_id'] for r in results]
                    assert len(set(project_ids)) == 3

        # Exécution du test asynchrone
        asyncio.run(run_parallel_projects())

    def test_workflow_recovery_and_resume(self, orchestrator, temp_project_dir, mock_target):
        """Test de récupération et reprise après interruption"""
        project_config = {
            'name': 'recovery_test_project',
            'target': mock_target['ip'],
            'profile': 'comprehensive',
            'output_dir': temp_project_dir,
            'phases': ['reconnaissance', 'vulnerability']
        }
        
        with patch('core.api.nmap_api.subprocess.run') as mock_nmap, \
             patch('core.security.consent_manager.ConsentManager.verify_consent') as mock_consent:
            mock_nmap.return_value = Mock(
                returncode=0,
                stdout=self._get_mock_nmap_output()
            )
            
            # Mock du consentement pour les tests
            mock_consent.return_value = True
            
            # Initialisation et première phase
            result = orchestrator.initialize_project(project_config)
            project_id = result['project_id']
            
            # Exécution de la reconnaissance
            recon_result = orchestrator.execute_phase('reconnaissance', project_id, {
                'target': mock_target['ip']
            })
            assert recon_result['success'] is True
            
            # Simulation d'une interruption - sauvegarde de l'état
            state = orchestrator.save_project_state(project_id)
            assert state is not None
            
            # Création d'un nouvel orchestrateur (simulation redémarrage)
            new_orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
            
            # Restauration de l'état
            restore_result = new_orchestrator.restore_project_state(project_id, state)
            assert restore_result['success'] is True
            
            # Vérification que les données sont bien restaurées
            restored_data = new_orchestrator.get_project_data(project_id)
            assert 'reconnaissance' in restored_data['phases']
            
            # Reprise du workflow à partir de la phase vulnérabilité
            with patch('modules.vulnerability.web_scanner.subprocess.run') as mock_zap:
                mock_zap.return_value = Mock(
                    returncode=0,
                    stdout='{"vulnerabilities": [{"type": "sql_injection"}]}'
                )
                
                vuln_result = new_orchestrator.execute_phase('vulnerability', project_id, {
                    'targets': restored_data['phases']['reconnaissance']['hosts_discovered']
                })
                
                assert vuln_result['success'] is True

    def _run_single_project(self, orchestrator, project_config):
        """Exécute un seul projet (helper pour tests parallèles)"""
        result = orchestrator.initialize_project(project_config)
        if not result['success']:
            return result
            
        project_id = result['project_id']
        
        recon_result = orchestrator.execute_phase('reconnaissance', project_id, {
            'target': project_config['target']
        })
        
        return {
            'success': recon_result['success'],
            'project_id': project_id
        }

    def _get_mock_nmap_output(self):
        """Retourne un output Nmap mocké"""
        return '''
# Nmap 7.94 scan initiated
Nmap scan report for 192.168.1.100
Host is up (0.00012s latency).
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5
80/tcp   open  http    Apache httpd 2.4.41 ((Ubuntu))
443/tcp  open  https   Apache httpd 2.4.41 ((Ubuntu))
21/tcp   open  ftp     vsftpd 3.0.3
MAC Address: 00:0C:29:XX:XX:XX (VMware)

Service detection performed. Please report any incorrect results.
Nmap done: 1 IP address (1 host up) scanned in 2.45 seconds
        '''


class TestWorkflowPerformance:
    """Tests de performance du workflow"""

    def test_workflow_execution_time(self, orchestrator, temp_project_dir):
        """Test du temps d'exécution du workflow"""
        import time
        
        project_config = {
            'name': 'performance_test_project',
            'target': '192.168.1.100',
            'profile': 'quick',
            'output_dir': temp_project_dir
        }
        
        with patch('core.api.nmap_api.subprocess.run') as mock_nmap, \
             patch('core.security.consent_manager.ConsentManager.verify_consent') as mock_consent:
            mock_nmap.return_value = Mock(
                returncode=0,
                stdout=self._get_mock_nmap_output()
            )
            
            # Mock du consentement pour les tests
            mock_consent.return_value = True
            
            start_time = time.time()
            
            # Workflow complet
            result = orchestrator.initialize_project(project_config)
            project_id = result['project_id']
            
            recon_result = orchestrator.execute_phase('reconnaissance', project_id, {
                'target': '192.168.1.100'
            })
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Validation des performances (< 5 secondes pour un test simple)
            assert execution_time < 5.0
            assert recon_result['success'] is True

    def test_workflow_memory_usage(self, orchestrator, temp_project_dir):
        """Test de l'utilisation mémoire du workflow"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        project_config = {
            'name': 'memory_test_project',
            'target': '192.168.1.100',
            'profile': 'quick',
            'output_dir': temp_project_dir
        }
        
        with patch('core.api.nmap_api.subprocess.run') as mock_nmap, \
             patch('core.security.consent_manager.ConsentManager.verify_consent') as mock_consent:
            mock_nmap.return_value = Mock(
                returncode=0,
                stdout=self._get_mock_nmap_output()
            )
            
            # Mock du consentement pour les tests
            mock_consent.return_value = True
            
            # Exécution du workflow
            result = orchestrator.initialize_project(project_config)
            project_id = result['project_id']
            
            recon_result = orchestrator.execute_phase('reconnaissance', project_id, {
                'target': '192.168.1.100'
            })
            
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Validation que l'augmentation mémoire reste raisonnable (< 100MB)
            assert memory_increase < 100 * 1024 * 1024  # 100MB
            assert recon_result['success'] is True

    def _get_mock_nmap_output(self):
        """Retourne un output Nmap mocké"""
        return '''
# Nmap 7.94 scan initiated
Nmap scan report for 192.168.1.100
Host is up (0.00012s latency).
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5
80/tcp   open  http    Apache httpd 2.4.41 ((Ubuntu))
443/tcp  open  https   Apache httpd 2.4.41 ((Ubuntu))
21/tcp   open  ftp     vsftpd 3.0.3

Service detection performed. Please report any incorrect results.
Nmap done: 1 IP address (1 host up) scanned in 2.45 seconds
        '''


if __name__ == "__main__":
    # Exécution des tests
    pytest.main([__file__, "-v"])