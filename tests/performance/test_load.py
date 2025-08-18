#!/usr/bin/env python3
"""
Tests de Performance - Charge
=============================

Tests de charge pour valider les performances
du système sous différentes conditions de charge.

Teste la capacité du système à traiter plusieurs
requêtes simultanées et à gérer la montée en charge.
"""

import sys
import os
import pytest
import time
import threading
import concurrent.futures
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.engine.orchestrator import PentestOrchestrator
from core.utils.logging_handler import get_logger
from modules.reconnaissance.network_scanner import NetworkScanner


class TestLoadPerformance:
    """Tests de performance sous charge"""

    @pytest.fixture
    def orchestrator(self):
        """Fixture pour l'orchestrateur"""
        return PentestOrchestrator(target="192.168.1.100", profile="test")

    def test_concurrent_project_creation(self, orchestrator):
        """Test de création concurrente de projets"""
        import time
        import threading
        
        num_projects = 50
        results = []
        errors = []
        
        def create_project(project_id):
            """Créer un projet"""
            try:
                project_config = {
                    'name': f'Load Test Project {project_id}',
                    'target': f'192.168.1.{project_id % 255}',
                    'output_dir': '/tmp'
                }
                
                start_time = time.time()
                result = orchestrator.initialize_project(project_config)
                end_time = time.time()
                
                results.append({
                    'project_id': result.get('project_id'),
                    'success': result.get('success', False),
                    'creation_time': end_time - start_time,
                    'thread_id': threading.current_thread().ident
                })
                
            except Exception as e:
                errors.append({
                    'project_id': project_id,
                    'error': str(e),
                    'thread_id': threading.current_thread().ident
                })
        
        # Lancement concurrent
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_project, i) for i in range(num_projects)]
            concurrent.futures.wait(futures)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Validations
        assert len(errors) == 0, f"Erreurs dans la création: {errors}"
        assert len(results) == num_projects
        assert all(r['success'] for r in results)
        
        # Performance validations
        avg_creation_time = sum(r['creation_time'] for r in results) / len(results)
        assert avg_creation_time < 1.0, f"Temps moyen trop élevé: {avg_creation_time:.2f}s"
        assert total_time < 30.0, f"Temps total trop élevé: {total_time:.2f}s"
        
        # Validation de l'unicité des IDs
        project_ids = [r['project_id'] for r in results]
        assert len(set(project_ids)) == num_projects, "IDs de projets non uniques"

    def test_parallel_scanning_load(self):
        """Test de charge avec scans parallèles"""
        num_scans = 20
        scanner = NetworkScanner()
        
        results = []
        errors = []
        
        def perform_scan(target_ip):
            """Effectuer un scan"""
            try:
                with patch('subprocess.run') as mock_run:
                    mock_run.return_value = Mock(
                        returncode=0,
                        stdout=f'''
# Nmap scan for {target_ip}
Nmap scan report for {target_ip}
Host is up (0.001s latency).
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
443/tcp  open  https
                        '''
                    )
                    
                    start_time = time.time()
                    result = scanner.scan_host(target_ip)
                    end_time = time.time()
                    
                    results.append({
                        'target': target_ip,
                        'success': result.get('success', False),
                        'scan_time': end_time - start_time,
                        'hosts_found': len(result.get('hosts', [])),
                        'thread_id': threading.current_thread().ident
                    })
                    
            except Exception as e:
                errors.append({
                    'target': target_ip,
                    'error': str(e),
                    'thread_id': threading.current_thread().ident
                })
        
        # Préparer les cibles
        targets = [f'192.168.1.{i}' for i in range(1, num_scans + 1)]
        
        # Lancement concurrent
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(perform_scan, target) for target in targets]
            concurrent.futures.wait(futures)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Validations
        assert len(errors) == 0, f"Erreurs dans les scans: {errors}"
        assert len(results) == num_scans
        assert all(r['success'] for r in results)
        
        # Performance validations
        avg_scan_time = sum(r['scan_time'] for r in results) / len(results)
        assert avg_scan_time < 2.0, f"Temps moyen de scan trop élevé: {avg_scan_time:.2f}s"
        assert total_time < 60.0, f"Temps total trop élevé: {total_time:.2f}s"

    def test_high_frequency_requests(self, orchestrator):
        """Test de requêtes haute fréquence"""
        num_requests = 200
        request_interval = 0.01  # 100 requêtes par seconde
        
        results = []
        errors = []
        
        def make_request(request_id):
            """Faire une requête simple"""
            try:
                start_time = time.time()
                
                # Simulation d'une requête de status
                project_config = {
                    'name': f'Quick Request {request_id}',
                    'target': '192.168.1.1',
                    'output_dir': '/tmp'
                }
                
                result = orchestrator.initialize_project(project_config)
                
                end_time = time.time()
                
                results.append({
                    'request_id': request_id,
                    'success': result.get('success', False),
                    'response_time': end_time - start_time,
                    'timestamp': end_time
                })
                
            except Exception as e:
                errors.append({
                    'request_id': request_id,
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        # Lancement haute fréquence
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i in range(num_requests):
                future = executor.submit(make_request, i)
                futures.append(future)
                time.sleep(request_interval)
            
            concurrent.futures.wait(futures)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Validations
        success_rate = len(results) / num_requests * 100
        error_rate = len(errors) / num_requests * 100
        
        assert success_rate >= 95.0, f"Taux de succès trop bas: {success_rate:.1f}%"
        assert error_rate <= 5.0, f"Taux d'erreur trop élevé: {error_rate:.1f}%"
        
        # Performance validations
        if results:
            avg_response_time = sum(r['response_time'] for r in results) / len(results)
            max_response_time = max(r['response_time'] for r in results)
            
            assert avg_response_time < 0.5, f"Temps de réponse moyen trop élevé: {avg_response_time:.3f}s"
            assert max_response_time < 2.0, f"Temps de réponse max trop élevé: {max_response_time:.3f}s"

    def test_load_with_resource_constraints(self, orchestrator):
        """Test de charge avec contraintes de ressources"""
        import psutil
        import os
        
        # Obtenir les ressources initiales
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        initial_cpu_times = process.cpu_times()
        
        num_operations = 100
        results = []
        
        def resource_intensive_operation(op_id):
            """Opération consommatrice de ressources"""
            try:
                # Simulation d'opération intensive
                project_config = {
                    'name': f'Resource Test {op_id}',
                    'target': f'192.168.{op_id % 255}.0/24',
                    'output_dir': '/tmp'
                }
                
                start_time = time.time()
                result = orchestrator.initialize_project(project_config)
                end_time = time.time()
                
                # Mesurer l'utilisation des ressources
                current_memory = process.memory_info().rss
                memory_usage = current_memory - initial_memory
                
                results.append({
                    'operation_id': op_id,
                    'success': result.get('success', False),
                    'execution_time': end_time - start_time,
                    'memory_usage': memory_usage,
                    'timestamp': end_time
                })
                
                return True
                
            except Exception as e:
                print(f"Erreur opération {op_id}: {e}")
                return False
        
        # Exécution avec limitation de threads pour simuler contraintes
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(resource_intensive_operation, i) for i in range(num_operations)]
            completed = concurrent.futures.as_completed(futures)
            
            success_count = sum(1 for future in completed if future.result())
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Validations
        success_rate = success_count / num_operations * 100
        assert success_rate >= 90.0, f"Taux de succès sous contraintes trop bas: {success_rate:.1f}%"
        
        # Validation mémoire
        final_memory = process.memory_info().rss
        total_memory_increase = final_memory - initial_memory
        
        # La consommation mémoire ne doit pas être excessive (< 200MB)
        assert total_memory_increase < 200 * 1024 * 1024, f"Consommation mémoire excessive: {total_memory_increase / 1024 / 1024:.1f}MB"

    def test_sustained_load_over_time(self, orchestrator):
        """Test de charge soutenue dans le temps"""
        duration_seconds = 60  # 1 minute de test
        operations_per_second = 5
        
        results = []
        errors = []
        start_test_time = time.time()
        
        def continuous_operations():
            """Opérations continues"""
            operation_count = 0
            
            while time.time() - start_test_time < duration_seconds:
                try:
                    operation_start = time.time()
                    
                    project_config = {
                        'name': f'Sustained Test {operation_count}',
                        'target': f'192.168.1.{(operation_count % 254) + 1}',
                        'output_dir': '/tmp'
                    }
                    
                    result = orchestrator.initialize_project(project_config)
                    
                    operation_end = time.time()
                    
                    results.append({
                        'operation_id': operation_count,
                        'success': result.get('success', False),
                        'operation_time': operation_end - operation_start,
                        'timestamp': operation_end
                    })
                    
                    operation_count += 1
                    
                    # Contrôler la fréquence
                    time.sleep(1.0 / operations_per_second)
                    
                except Exception as e:
                    errors.append({
                        'operation_id': operation_count,
                        'error': str(e),
                        'timestamp': time.time()
                    })
                    operation_count += 1
        
        # Lancer le test de charge soutenue
        continuous_operations()
        
        end_test_time = time.time()
        actual_duration = end_test_time - start_test_time
        
        # Validations
        expected_operations = duration_seconds * operations_per_second
        actual_operations = len(results) + len(errors)
        
        # Tolérance de 10% sur le nombre d'opérations
        assert actual_operations >= expected_operations * 0.9, f"Pas assez d'opérations: {actual_operations}/{expected_operations}"
        
        # Taux de succès
        if actual_operations > 0:
            success_rate = len(results) / actual_operations * 100
            assert success_rate >= 95.0, f"Taux de succès en charge soutenue trop bas: {success_rate:.1f}%"
        
        # Performance dans le temps
        if results:
            # Analyser la dégradation dans le temps
            time_buckets = {}
            for result in results:
                bucket = int((result['timestamp'] - start_test_time) // 10)  # Buckets de 10s
                if bucket not in time_buckets:
                    time_buckets[bucket] = []
                time_buckets[bucket].append(result['operation_time'])
            
            # Vérifier que les performances ne se dégradent pas significativement
            if len(time_buckets) > 1:
                first_bucket_avg = sum(time_buckets[0]) / len(time_buckets[0])
                last_bucket = max(time_buckets.keys())
                last_bucket_avg = sum(time_buckets[last_bucket]) / len(time_buckets[last_bucket])
                
                # La dégradation ne doit pas dépasser 50%
                degradation = (last_bucket_avg - first_bucket_avg) / first_bucket_avg * 100
                assert degradation <= 50.0, f"Dégradation de performance trop importante: {degradation:.1f}%"


class TestDatabaseLoadPerformance:
    """Tests de performance de base de données sous charge"""

    def test_bulk_database_operations(self):
        """Test d'opérations de base de données en masse"""
        from core.db.sqlite_manager import SQLiteManager
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            db_path = temp_file.name
        
        try:
            db_manager = SQLiteManager(db_path)
            db_manager.initialize_database()
            
            num_records = 1000
            
            # Test d'insertion en masse
            start_time = time.time()
            
            project_data_list = []
            for i in range(num_records):
                project_data = {
                    'name': f'Bulk Project {i}',
                    'target': f'192.168.{i // 256}.{i % 256}',
                    'description': f'Test project for bulk operations {i}',
                    'status': 'active'
                }
                project_data_list.append(project_data)
            
            # Insertion avec transactions
            project_ids = []
            for project_data in project_data_list:
                project_id = db_manager.create_project(project_data)
                project_ids.append(project_id)
            
            insertion_time = time.time() - start_time
            
            # Validation des insertions
            assert len(project_ids) == num_records
            assert insertion_time < 30.0, f"Insertion trop lente: {insertion_time:.2f}s pour {num_records} enregistrements"
            
            # Test de lecture en masse
            start_time = time.time()
            
            all_projects = db_manager.list_projects()
            
            read_time = time.time() - start_time
            
            # Validations de lecture
            assert len(all_projects) >= num_records
            assert read_time < 5.0, f"Lecture trop lente: {read_time:.2f}s pour {len(all_projects)} enregistrements"
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_concurrent_database_access(self):
        """Test d'accès concurrent à la base de données"""
        from core.db.sqlite_manager import SQLiteManager
        import tempfile
        import threading
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            db_path = temp_file.name
        
        try:
            # Initialiser la base
            db_manager = SQLiteManager(db_path)
            db_manager.initialize_database()
            
            num_threads = 10
            operations_per_thread = 50
            results = []
            errors = []
            
            def database_operations(thread_id):
                """Opérations de base de données par thread"""
                thread_db = SQLiteManager(db_path)
                
                for i in range(operations_per_thread):
                    try:
                        # Créer un projet
                        project_data = {
                            'name': f'Thread {thread_id} Project {i}',
                            'target': f'192.168.{thread_id}.{i}',
                            'status': 'active'
                        }
                        
                        start_time = time.time()
                        project_id = thread_db.create_project(project_data)
                        
                        # Lire le projet
                        project = thread_db.get_project(project_id)
                        
                        # Mettre à jour le projet
                        thread_db.update_project(project_id, {'status': 'updated'})
                        
                        end_time = time.time()
                        
                        results.append({
                            'thread_id': thread_id,
                            'operation_id': i,
                            'project_id': project_id,
                            'operation_time': end_time - start_time,
                            'success': True
                        })
                        
                    except Exception as e:
                        errors.append({
                            'thread_id': thread_id,
                            'operation_id': i,
                            'error': str(e)
                        })
            
            # Lancer les threads concurrents
            start_time = time.time()
            
            threads = []
            for thread_id in range(num_threads):
                thread = threading.Thread(target=database_operations, args=(thread_id,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Validations
            expected_operations = num_threads * operations_per_thread
            success_count = len(results)
            error_count = len(errors)
            
            success_rate = success_count / expected_operations * 100
            assert success_rate >= 95.0, f"Taux de succès concurrent trop bas: {success_rate:.1f}%"
            
            if results:
                avg_operation_time = sum(r['operation_time'] for r in results) / len(results)
                assert avg_operation_time < 1.0, f"Temps d'opération moyen trop élevé: {avg_operation_time:.3f}s"
            
            print(f"Opérations concurrentes: {success_count}/{expected_operations} réussies en {total_time:.2f}s")
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


if __name__ == "__main__":
    # Exécution des tests
    pytest.main([__file__, "-v"])