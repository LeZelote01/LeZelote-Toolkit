#!/usr/bin/env python3
"""
Tests de Performance - Stress
=============================

Tests de stress pour valider la robustesse
du système sous des conditions extrêmes.

Teste les limites du système et sa capacité
de récupération après des charges extrêmes.
"""

import sys
import os
import pytest
import time
import threading
import multiprocessing
import psutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.engine.orchestrator import PentestOrchestrator
from core.utils.logging_handler import get_logger


class TestStressPerformance:
    """Tests de stress système"""

    def test_memory_stress(self):
        """Test de stress mémoire"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Mesurer la mémoire initiale
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Créer de nombreux projets pour stresser la mémoire
        num_projects = 500
        project_ids = []
        
        start_time = time.time()
        
        try:
            for i in range(num_projects):
                project_config = {
                    'name': f'Memory Stress Project {i}',
                    'target': f'10.{i//256}.{(i//256)%256}.{i%256}',
                    'output_dir': '/tmp',
                    'description': 'A' * 1000  # Description longue pour consommer mémoire
                }
                
                result = orchestrator.initialize_project(project_config)
                if result.get('success'):
                    project_ids.append(result['project_id'])
                
                # Mesurer la mémoire toutes les 50 itérations
                if i % 50 == 0:
                    current_memory = process.memory_info().rss
                    memory_increase = current_memory - initial_memory
                    
                    # Vérifier que la croissance mémoire reste raisonnable
                    # (moins de 500MB pour 500 projets)
                    if memory_increase > 500 * 1024 * 1024:
                        pytest.fail(f"Consommation mémoire excessive: {memory_increase / 1024 / 1024:.1f}MB après {i+1} projets")
        
        except Exception as e:
            pytest.fail(f"Échec du test de stress mémoire: {str(e)}")
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # Mesurer la mémoire finale
        final_memory = process.memory_info().rss
        total_memory_increase = final_memory - initial_memory
        
        # Validations
        assert len(project_ids) >= num_projects * 0.9, f"Trop d'échecs de création: {len(project_ids)}/{num_projects}"
        assert creation_time < 120.0, f"Création trop lente: {creation_time:.2f}s"
        assert total_memory_increase < 500 * 1024 * 1024, f"Fuite mémoire: {total_memory_increase / 1024 / 1024:.1f}MB"
        
        print(f"Stress mémoire: {len(project_ids)} projets créés en {creation_time:.2f}s, +{total_memory_increase / 1024 / 1024:.1f}MB")

    def test_cpu_stress(self):
        """Test de stress CPU"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Mesurer CPU initial
        process = psutil.Process(os.getpid())
        initial_cpu_times = process.cpu_times()
        
        num_operations = 200
        results = []
        
        def cpu_intensive_operation(op_id):
            """Opération intensive CPU"""
            try:
                # Simulation d'opérations CPU intensives
                start_time = time.time()
                
                # Créer un projet avec beaucoup de calculs
                project_config = {
                    'name': f'CPU Stress {op_id}',
                    'target': f'192.168.{op_id % 256}.0/24',
                    'output_dir': '/tmp'
                }
                
                result = orchestrator.initialize_project(project_config)
                
                # Simulation de calculs additionnels
                for _ in range(1000):
                    dummy = sum(range(100))
                
                end_time = time.time()
                
                return {
                    'operation_id': op_id,
                    'success': result.get('success', False),
                    'execution_time': end_time - start_time,
                    'cpu_intensive': True
                }
                
            except Exception as e:
                return {
                    'operation_id': op_id,
                    'success': False,
                    'error': str(e)
                }
        
        # Utiliser tous les cœurs disponibles
        num_cores = multiprocessing.cpu_count()
        
        start_time = time.time()
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores * 2) as executor:
            futures = [executor.submit(cpu_intensive_operation, i) for i in range(num_operations)]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyser les résultats
        successful_operations = [r for r in results if r.get('success', False)]
        failed_operations = [r for r in results if not r.get('success', False)]
        
        # Validations
        success_rate = len(successful_operations) / len(results) * 100
        assert success_rate >= 90.0, f"Taux de succès sous stress CPU trop bas: {success_rate:.1f}%"
        
        if successful_operations:
            avg_execution_time = sum(r['execution_time'] for r in successful_operations) / len(successful_operations)
            max_execution_time = max(r['execution_time'] for r in successful_operations)
            
            # Sous stress CPU, les temps peuvent être plus élevés
            assert avg_execution_time < 5.0, f"Temps d'exécution moyen trop élevé: {avg_execution_time:.2f}s"
            assert max_execution_time < 10.0, f"Temps d'exécution max trop élevé: {max_execution_time:.2f}s"
        
        print(f"Stress CPU: {len(successful_operations)}/{len(results)} succès en {total_time:.2f}s")

    def test_thread_exhaustion(self):
        """Test d'épuisement de threads"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Créer un grand nombre de threads simultanément
        num_threads = 100
        results = []
        errors = []
        
        def thread_operation(thread_id):
            """Opération par thread"""
            try:
                project_config = {
                    'name': f'Thread Exhaustion {thread_id}',
                    'target': f'192.168.1.{thread_id % 255}',
                    'output_dir': '/tmp'
                }
                
                start_time = time.time()
                result = orchestrator.initialize_project(project_config)
                end_time = time.time()
                
                # Simulation d'attente pour maintenir le thread
                time.sleep(0.5)
                
                results.append({
                    'thread_id': thread_id,
                    'success': result.get('success', False),
                    'execution_time': end_time - start_time,
                    'project_id': result.get('project_id')
                })
                
            except Exception as e:
                errors.append({
                    'thread_id': thread_id,
                    'error': str(e)
                })
        
        # Lancer tous les threads
        threads = []
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(target=thread_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Attendre tous les threads
        for thread in threads:
            thread.join(timeout=30)  # Timeout de sécurité
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyser les résultats
        active_threads = threading.active_count()
        
        # Validations
        success_rate = len(results) / num_threads * 100
        error_rate = len(errors) / num_threads * 100
        
        assert success_rate >= 80.0, f"Taux de succès avec {num_threads} threads trop bas: {success_rate:.1f}%"
        assert error_rate <= 20.0, f"Taux d'erreur avec {num_threads} threads trop élevé: {error_rate:.1f}%"
        assert total_time < 60.0, f"Temps d'exécution avec threads trop long: {total_time:.2f}s"
        
        print(f"Thread exhaustion: {len(results)} succès, {len(errors)} erreurs en {total_time:.2f}s")

    def test_disk_io_stress(self):
        """Test de stress I/O disque"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        import tempfile
        import shutil
        
        # Créer un dossier temporaire
        temp_dir = tempfile.mkdtemp(prefix='pentest_stress_')
        
        try:
            num_projects = 100
            results = []
            
            start_time = time.time()
            
            for i in range(num_projects):
                project_config = {
                    'name': f'Disk IO Stress Project {i}',
                    'target': f'192.168.{i // 256}.{i % 256}',
                    'output_dir': temp_dir,
                    'description': 'X' * 10000  # Description très longue
                }
                
                operation_start = time.time()
                result = orchestrator.initialize_project(project_config)
                operation_end = time.time()
                
                # Simuler écriture de fichiers
                if result.get('success'):
                    project_id = result['project_id']
                    project_dir = os.path.join(temp_dir, project_id)
                    os.makedirs(project_dir, exist_ok=True)
                    
                    # Créer plusieurs fichiers pour stresser I/O
                    for j in range(10):
                        file_path = os.path.join(project_dir, f'data_{j}.txt')
                        with open(file_path, 'w') as f:
                            f.write('A' * 1000)  # 1KB par fichier
                
                results.append({
                    'project_id': i,
                    'success': result.get('success', False),
                    'io_time': operation_end - operation_start,
                    'project_path': project_dir if result.get('success') else None
                })
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Vérifier l'usage disque
            total_size = 0
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except:
                        pass
            
            # Validations
            successful_projects = [r for r in results if r['success']]
            success_rate = len(successful_projects) / num_projects * 100
            
            assert success_rate >= 95.0, f"Taux de succès I/O trop bas: {success_rate:.1f}%"
            
            if successful_projects:
                avg_io_time = sum(r['io_time'] for r in successful_projects) / len(successful_projects)
                max_io_time = max(r['io_time'] for r in successful_projects)
                
                assert avg_io_time < 2.0, f"Temps I/O moyen trop élevé: {avg_io_time:.2f}s"
                assert max_io_time < 5.0, f"Temps I/O max trop élevé: {max_io_time:.2f}s"
            
            print(f"Stress I/O: {len(successful_projects)} projets, {total_size / 1024 / 1024:.1f}MB en {total_time:.2f}s")
            
        finally:
            # Nettoyer
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

    def test_recovery_after_stress(self):
        """Test de récupération après stress"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Phase 1: Stress intensif
        print("Phase 1: Stress intensif")
        stress_operations = 200
        
        start_stress = time.time()
        stress_results = []
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            def stress_operation(op_id):
                try:
                    project_config = {
                        'name': f'Stress Recovery Test {op_id}',
                        'target': f'10.0.{op_id // 256}.{op_id % 256}',
                        'output_dir': '/tmp'
                    }
                    
                    result = orchestrator.initialize_project(project_config)
                    return result.get('success', False)
                except:
                    return False
            
            futures = [executor.submit(stress_operation, i) for i in range(stress_operations)]
            stress_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_stress = time.time()
        stress_time = end_stress - start_stress
        stress_success_rate = sum(stress_results) / len(stress_results) * 100
        
        print(f"Stress terminé: {stress_success_rate:.1f}% succès en {stress_time:.2f}s")
        
        # Phase 2: Période de récupération
        print("Phase 2: Période de récupération")
        recovery_time = 10  # 10 secondes de pause
        time.sleep(recovery_time)
        
        # Phase 3: Test de fonctionnement normal après stress
        print("Phase 3: Test post-stress")
        post_stress_operations = 20
        
        start_post_stress = time.time()
        post_stress_results = []
        
        for i in range(post_stress_operations):
            try:
                project_config = {
                    'name': f'Post Stress Test {i}',
                    'target': f'192.168.100.{i}',
                    'output_dir': '/tmp'
                }
                
                operation_start = time.time()
                result = orchestrator.initialize_project(project_config)
                operation_end = time.time()
                
                post_stress_results.append({
                    'success': result.get('success', False),
                    'response_time': operation_end - operation_start
                })
                
            except Exception as e:
                post_stress_results.append({
                    'success': False,
                    'error': str(e)
                })
        
        end_post_stress = time.time()
        post_stress_time = end_post_stress - start_post_stress
        
        # Analyse des résultats post-stress
        successful_post_stress = [r for r in post_stress_results if r.get('success', False)]
        post_stress_success_rate = len(successful_post_stress) / len(post_stress_results) * 100
        
        # Validations de récupération
        assert post_stress_success_rate >= 95.0, f"Récupération insuffisante: {post_stress_success_rate:.1f}% succès après stress"
        
        if successful_post_stress:
            avg_post_stress_time = sum(r['response_time'] for r in successful_post_stress) / len(successful_post_stress)
            assert avg_post_stress_time < 1.0, f"Performance non récupérée: {avg_post_stress_time:.2f}s temps moyen"
        
        print(f"Récupération: {post_stress_success_rate:.1f}% succès, temps moyen: {avg_post_stress_time:.3f}s")

    def test_resource_exhaustion_boundaries(self):
        """Test des limites d'épuisement des ressources"""
        import gc
        import resource
        
        # Mesurer les limites système
        max_memory = resource.getrlimit(resource.RLIMIT_AS)[0]  # Limite mémoire virtuelle
        max_files = resource.getrlimit(resource.RLIMIT_NOFILE)[0]  # Limite fichiers ouverts
        
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Test d'approche des limites
        operations = []
        current_memory = psutil.Process(os.getpid()).memory_info().rss
        
        project_count = 0
        try:
            while project_count < 1000:  # Limite de sécurité
                project_config = {
                    'name': f'Boundary Test {project_count}',
                    'target': f'172.16.{project_count // 256}.{project_count % 256}',
                    'output_dir': '/tmp'
                }
                
                result = orchestrator.initialize_project(project_config)
                
                if result.get('success'):
                    operations.append(result['project_id'])
                    project_count += 1
                    
                    # Vérifier l'usage mémoire
                    new_memory = psutil.Process(os.getpid()).memory_info().rss
                    memory_increase = new_memory - current_memory
                    
                    # Si la mémoire augmente trop, arrêter le test
                    if memory_increase > 800 * 1024 * 1024:  # 800MB
                        print(f"Limite mémoire atteinte après {project_count} projets")
                        break
                else:
                    # Si les créations échouent, on atteint probablement une limite
                    print(f"Limite de création atteinte après {project_count} projets")
                    break
                
                # Forcer le garbage collection périodiquement
                if project_count % 100 == 0:
                    gc.collect()
        
        except Exception as e:
            print(f"Exception à la limite après {project_count} projets: {e}")
        
        # Validations
        assert project_count >= 100, f"Limite trop basse: seulement {project_count} projets créés"
        
        # Test de nettoyage et récupération
        operations.clear()
        gc.collect()
        
        # Vérifier la récupération
        recovery_test_config = {
            'name': 'Recovery After Exhaustion',
            'target': '192.168.1.1',
            'output_dir': '/tmp'
        }
        
        recovery_result = orchestrator.initialize_project(recovery_test_config)
        assert recovery_result.get('success', False), "Système non récupéré après épuisement des ressources"
        
        print(f"Limites testées: {project_count} projets créés, récupération réussie")


if __name__ == "__main__":
    # Exécution des tests
    pytest.main([__file__, "-v"])