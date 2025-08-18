#!/usr/bin/env python3
"""
Tests de Performance - Scalabilité
==================================

Tests de scalabilité pour valider la capacité
du système à monter en charge efficacement.

Teste l'évolution des performances avec
l'augmentation de la charge de travail.
"""

import sys
import os
import pytest
import time
import threading
import multiprocessing
from pathlib import Path
from unittest.mock import Mock, patch
import concurrent.futures

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.engine.orchestrator import PentestOrchestrator
from core.utils.logging_handler import get_logger


class TestScalabilityPerformance:
    """Tests de scalabilité système"""

    def test_horizontal_scalability(self):
        """Test de scalabilité horizontale (plus d'utilisateurs)"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Tester différents niveaux de charge
        load_levels = [1, 5, 10, 20, 50]
        results = {}
        
        for num_users in load_levels:
            print(f"Testing avec {num_users} utilisateurs simultanés")
            
            operations_per_user = 10
            user_results = []
            
            def simulate_user(user_id):
                """Simuler un utilisateur"""
                user_operations = []
                
                for op in range(operations_per_user):
                    try:
                        start_time = time.time()
                        
                        project_config = {
                            'name': f'User{user_id}_Op{op}',
                            'target': f'192.168.{user_id}.{op}',
                            'output_dir': '/tmp'
                        }
                        
                        result = orchestrator.initialize_project(project_config)
                        
                        end_time = time.time()
                        
                        user_operations.append({
                            'user_id': user_id,
                            'operation_id': op,
                            'success': result.get('success', False),
                            'response_time': end_time - start_time,
                            'timestamp': end_time
                        })
                        
                    except Exception as e:
                        user_operations.append({
                            'user_id': user_id,
                            'operation_id': op,
                            'success': False,
                            'error': str(e),
                            'timestamp': time.time()
                        })
                
                return user_operations
            
            # Lancer les utilisateurs simultanés
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = [executor.submit(simulate_user, i) for i in range(num_users)]
                
                all_operations = []
                for future in concurrent.futures.as_completed(futures):
                    user_ops = future.result()
                    all_operations.extend(user_ops)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyser les résultats
            successful_ops = [op for op in all_operations if op.get('success', False)]
            failed_ops = [op for op in all_operations if not op.get('success', False)]
            
            # Calculer métriques
            success_rate = len(successful_ops) / len(all_operations) * 100 if all_operations else 0
            throughput = len(successful_ops) / total_time if total_time > 0 else 0
            
            avg_response_time = 0
            if successful_ops:
                avg_response_time = sum(op['response_time'] for op in successful_ops) / len(successful_ops)
            
            results[num_users] = {
                'success_rate': success_rate,
                'throughput': throughput,
                'avg_response_time': avg_response_time,
                'total_operations': len(all_operations),
                'successful_operations': len(successful_ops),
                'total_time': total_time
            }
            
            print(f"{num_users} utilisateurs: {success_rate:.1f}% succès, {throughput:.2f} ops/s, {avg_response_time:.3f}s moyen")
        
        # Validations de scalabilité
        # Le taux de succès ne doit pas trop diminuer
        baseline_success = results[1]['success_rate']
        max_load_success = results[max(load_levels)]['success_rate']
        success_degradation = baseline_success - max_load_success
        
        assert success_degradation <= 10.0, f"Dégradation du taux de succès trop importante: {success_degradation:.1f}%"
        
        # Le throughput doit augmenter avec la charge (jusqu'à un certain point)
        throughputs = [results[level]['throughput'] for level in load_levels]
        assert max(throughputs) > throughputs[0], "Aucune amélioration de throughput avec l'augmentation de charge"
        
        return results

    def test_vertical_scalability(self):
        """Test de scalabilité verticale (plus de ressources par opération)"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Tester différentes tailles de charge de travail
        workload_sizes = [1, 10, 50, 100, 500]  # Nombre de cibles par projet
        results = {}
        
        for workload_size in workload_sizes:
            print(f"Testing avec workload de {workload_size} cibles")
            
            # Créer une liste de cibles proportionnelle
            targets = []
            for i in range(workload_size):
                targets.append(f'192.168.{i//256}.{i%256}')
            
            target_string = '\n'.join(targets)
            description = f'Large workload test with {workload_size} targets: ' + ('X' * workload_size * 10)
            
            try:
                start_time = time.time()
                
                project_config = {
                    'name': f'Vertical Scale Test {workload_size}',
                    'target': target_string,
                    'output_dir': '/tmp',
                    'description': description
                }
                
                result = orchestrator.initialize_project(project_config)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                results[workload_size] = {
                    'success': result.get('success', False),
                    'processing_time': processing_time,
                    'targets_per_second': workload_size / processing_time if processing_time > 0 else 0,
                    'memory_per_target': 0  # Sera calculé si nécessaire
                }
                
                print(f"{workload_size} cibles: {processing_time:.2f}s ({workload_size / processing_time:.2f} cibles/s)")
                
            except Exception as e:
                results[workload_size] = {
                    'success': False,
                    'error': str(e),
                    'processing_time': float('inf')
                }
                print(f"{workload_size} cibles: ÉCHEC - {str(e)}")
        
        # Validations de scalabilité verticale
        successful_results = {k: v for k, v in results.items() if v.get('success', False)}
        
        assert len(successful_results) >= len(workload_sizes) * 0.8, "Trop d'échecs dans la scalabilité verticale"
        
        # Vérifier que le système peut gérer des charges importantes
        max_successful_workload = max(successful_results.keys()) if successful_results else 0
        assert max_successful_workload >= 100, f"Scalabilité verticale limitée: max {max_successful_workload} cibles"
        
        # Analyser l'efficacité (temps par cible ne doit pas augmenter exponentiellement)
        if len(successful_results) >= 2:
            times_per_target = [(v['processing_time'] / k) for k, v in successful_results.items()]
            efficiency_degradation = (max(times_per_target) - min(times_per_target)) / min(times_per_target) * 100
            
            assert efficiency_degradation <= 200.0, f"Dégradation d'efficacité trop importante: {efficiency_degradation:.1f}%"
        
        return results

    def test_temporal_scalability(self):
        """Test de scalabilité temporelle (performance dans le temps)"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Test sur plusieurs périodes
        test_duration = 120  # 2 minutes
        measurement_interval = 10  # Mesure toutes les 10 secondes
        operations_per_interval = 20
        
        results = []
        start_test = time.time()
        
        while time.time() - start_test < test_duration:
            interval_start = time.time()
            interval_results = []
            
            # Effectuer des opérations pendant l'intervalle
            for i in range(operations_per_interval):
                try:
                    op_start = time.time()
                    
                    project_config = {
                        'name': f'Temporal Test {int(time.time())}_{i}',
                        'target': f'10.0.{int(time.time()) % 256}.{i}',
                        'output_dir': '/tmp'
                    }
                    
                    result = orchestrator.initialize_project(project_config)
                    
                    op_end = time.time()
                    
                    interval_results.append({
                        'success': result.get('success', False),
                        'response_time': op_end - op_start,
                        'timestamp': op_end
                    })
                    
                except Exception as e:
                    interval_results.append({
                        'success': False,
                        'error': str(e),
                        'timestamp': time.time()
                    })
            
            interval_end = time.time()
            
            # Calculer métriques pour cet intervalle
            successful_ops = [r for r in interval_results if r.get('success', False)]
            interval_duration = interval_end - interval_start
            
            interval_metrics = {
                'timestamp': interval_start,
                'duration': interval_duration,
                'total_operations': len(interval_results),
                'successful_operations': len(successful_ops),
                'success_rate': len(successful_ops) / len(interval_results) * 100 if interval_results else 0,
                'throughput': len(successful_ops) / interval_duration if interval_duration > 0 else 0,
                'avg_response_time': sum(r['response_time'] for r in successful_ops) / len(successful_ops) if successful_ops else 0
            }
            
            results.append(interval_metrics)
            
            print(f"Intervalle {len(results)}: {interval_metrics['success_rate']:.1f}% succès, {interval_metrics['throughput']:.2f} ops/s")
            
            # Attendre le prochain intervalle
            time.sleep(max(0, measurement_interval - interval_duration))
        
        # Analyser la stabilité temporelle
        if len(results) >= 3:
            # Comparer début, milieu et fin
            first_third = results[:len(results)//3]
            last_third = results[-len(results)//3:]
            
            avg_success_start = sum(r['success_rate'] for r in first_third) / len(first_third)
            avg_success_end = sum(r['success_rate'] for r in last_third) / len(last_third)
            
            avg_throughput_start = sum(r['throughput'] for r in first_third) / len(first_third)
            avg_throughput_end = sum(r['throughput'] for r in last_third) / len(last_third)
            
            # Validations de stabilité
            success_degradation = avg_success_start - avg_success_end
            throughput_degradation = (avg_throughput_start - avg_throughput_end) / avg_throughput_start * 100 if avg_throughput_start > 0 else 0
            
            assert success_degradation <= 5.0, f"Dégradation temporelle du taux de succès: {success_degradation:.1f}%"
            assert abs(throughput_degradation) <= 20.0, f"Dégradation temporelle du throughput: {throughput_degradation:.1f}%"
            
            print(f"Stabilité temporelle: succès {avg_success_start:.1f}% -> {avg_success_end:.1f}%, throughput {avg_throughput_start:.2f} -> {avg_throughput_end:.2f}")
        
        return results

    def test_resource_efficiency_scaling(self):
        """Test d'efficacité des ressources avec l'augmentation de charge"""
        import psutil
        
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        process = psutil.Process(os.getpid())
        
        # Tester différents niveaux de charge
        load_levels = [10, 50, 100, 200]
        efficiency_results = {}
        
        for load_level in load_levels:
            # Mesurer ressources avant
            cpu_before = process.cpu_percent()
            memory_before = process.memory_info().rss
            
            start_time = time.time()
            
            # Générer la charge
            successful_operations = 0
            
            for i in range(load_level):
                try:
                    project_config = {
                        'name': f'Efficiency Test L{load_level}_Op{i}',
                        'target': f'172.16.{i//256}.{i%256}',
                        'output_dir': '/tmp'
                    }
                    
                    result = orchestrator.initialize_project(project_config)
                    if result.get('success', False):
                        successful_operations += 1
                        
                except Exception:
                    pass
            
            end_time = time.time()
            
            # Mesurer ressources après
            cpu_after = process.cpu_percent()
            memory_after = process.memory_info().rss
            
            total_time = end_time - start_time
            memory_increase = memory_after - memory_before
            
            # Calculer efficacité
            ops_per_second = successful_operations / total_time if total_time > 0 else 0
            memory_per_op = memory_increase / successful_operations if successful_operations > 0 else float('inf')
            cpu_efficiency = successful_operations / (cpu_after + 1) if cpu_after >= 0 else 0  # +1 pour éviter division par 0
            
            efficiency_results[load_level] = {
                'successful_operations': successful_operations,
                'total_time': total_time,
                'ops_per_second': ops_per_second,
                'memory_increase': memory_increase,
                'memory_per_op': memory_per_op,
                'cpu_usage': cpu_after,
                'cpu_efficiency': cpu_efficiency
            }
            
            print(f"Load {load_level}: {successful_operations} ops en {total_time:.2f}s, +{memory_increase/1024/1024:.1f}MB")
        
        # Analyser l'efficacité des ressources
        if len(efficiency_results) >= 2:
            loads = sorted(efficiency_results.keys())
            
            # L'efficacité mémoire ne doit pas se dégrader exponentiellement
            memory_efficiencies = [efficiency_results[load]['memory_per_op'] for load in loads]
            memory_efficiency_ratio = max(memory_efficiencies) / min(memory_efficiencies) if min(memory_efficiencies) > 0 else float('inf')
            
            assert memory_efficiency_ratio <= 5.0, f"Dégradation d'efficacité mémoire trop importante: {memory_efficiency_ratio:.2f}x"
            
            # Le throughput doit augmenter de manière cohérente
            throughputs = [efficiency_results[load]['ops_per_second'] for load in loads]
            throughput_improvement = max(throughputs) / throughputs[0] if throughputs[0] > 0 else 0
            
            assert throughput_improvement >= 1.5, f"Amélioration de throughput insuffisante: {throughput_improvement:.2f}x"
        
        return efficiency_results

    def test_concurrent_module_scalability(self):
        """Test de scalabilité avec modules concurrents"""
        from modules.reconnaissance.network_scanner import NetworkScanner
        from core.db.sqlite_manager import SQLiteManager
        import tempfile
        
        # Simuler plusieurs modules travaillant en parallèle
        num_scanners = 5
        scans_per_scanner = 20
        
        # Base de données temporaire
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            db_path = temp_file.name
        
        try:
            db_manager = SQLiteManager(db_path)
            db_manager.initialize_database()
            
            def scanner_worker(scanner_id):
                """Worker pour un scanner"""
                scanner = NetworkScanner(db_manager)
                results = []
                
                for i in range(scans_per_scanner):
                    try:
                        with patch('subprocess.run') as mock_run:
                            mock_run.return_value = Mock(
                                returncode=0,
                                stdout=f'Host {scanner_id}.{i} is up\nPort 80/tcp open'
                            )
                            
                            start_time = time.time()
                            target = f'10.{scanner_id}.1.{i}'
                            result = scanner.scan_host(target)
                            end_time = time.time()
                            
                            results.append({
                                'scanner_id': scanner_id,
                                'scan_id': i,
                                'success': result.get('success', False),
                                'scan_time': end_time - start_time,
                                'target': target
                            })
                            
                    except Exception as e:
                        results.append({
                            'scanner_id': scanner_id,
                            'scan_id': i,
                            'success': False,
                            'error': str(e)
                        })
                
                return results
            
            # Lancer scanners concurrents
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_scanners) as executor:
                futures = [executor.submit(scanner_worker, i) for i in range(num_scanners)]
                
                all_results = []
                for future in concurrent.futures.as_completed(futures):
                    scanner_results = future.result()
                    all_results.extend(scanner_results)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyser résultats
            successful_scans = [r for r in all_results if r.get('success', False)]
            total_scans = len(all_results)
            
            success_rate = len(successful_scans) / total_scans * 100 if total_scans > 0 else 0
            scan_throughput = len(successful_scans) / total_time if total_time > 0 else 0
            
            # Validations
            assert success_rate >= 90.0, f"Taux de succès modules concurrents trop bas: {success_rate:.1f}%"
            
            expected_throughput = num_scanners * 2  # Au moins 2 scans par seconde par scanner
            assert scan_throughput >= expected_throughput * 0.5, f"Throughput modules concurrents trop bas: {scan_throughput:.2f} < {expected_throughput * 0.5}"
            
            print(f"Modules concurrents: {len(successful_scans)}/{total_scans} scans réussis en {total_time:.2f}s ({scan_throughput:.2f} scans/s)")
            
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

    def test_data_volume_scalability(self):
        """Test de scalabilité avec volumes de données croissants"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Tester différents volumes de données
        data_volumes = [
            ('small', 1024, 10),           # 1KB, 10 projets
            ('medium', 10240, 25),         # 10KB, 25 projets  
            ('large', 102400, 50),         # 100KB, 50 projets
            ('xlarge', 1024000, 75)        # 1MB, 75 projets
        ]
        
        volume_results = {}
        
        for volume_name, data_size, num_projects in data_volumes:
            print(f"Testing volume {volume_name}: {data_size} bytes x {num_projects} projets")
            
            # Générer données de test
            test_data = 'D' * data_size
            
            start_time = time.time()
            successful_projects = 0
            
            for i in range(num_projects):
                try:
                    project_config = {
                        'name': f'Volume Test {volume_name} {i}',
                        'target': f'192.168.{i//256}.{i%256}',
                        'output_dir': '/tmp',
                        'description': f'Project {i}: {test_data}'
                    }
                    
                    result = orchestrator.initialize_project(project_config)
                    if result.get('success', False):
                        successful_projects += 1
                        
                except Exception as e:
                    pass  # Compter seulement les succès
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Calculer métriques
            success_rate = successful_projects / num_projects * 100
            data_throughput = (successful_projects * data_size) / total_time if total_time > 0 else 0  # bytes/sec
            projects_per_second = successful_projects / total_time if total_time > 0 else 0
            
            volume_results[volume_name] = {
                'data_size': data_size,
                'num_projects': num_projects,
                'successful_projects': successful_projects,
                'success_rate': success_rate,
                'total_time': total_time,
                'data_throughput': data_throughput,
                'projects_per_second': projects_per_second
            }
            
            print(f"{volume_name}: {success_rate:.1f}% succès, {data_throughput / 1024:.1f} KB/s")
        
        # Validations de scalabilité des données
        # Le système doit pouvoir traiter au moins les volumes medium
        medium_result = volume_results.get('medium', {})
        assert medium_result.get('success_rate', 0) >= 90.0, f"Scalabilité données insuffisante pour volume medium: {medium_result.get('success_rate', 0):.1f}%"
        
        # Le throughput ne doit pas s'effondrer avec l'augmentation du volume
        if 'small' in volume_results and 'large' in volume_results:
            small_throughput = volume_results['small']['projects_per_second']
            large_throughput = volume_results['large']['projects_per_second']
            
            if small_throughput > 0:
                throughput_ratio = large_throughput / small_throughput
                assert throughput_ratio >= 0.2, f"Dégradation throughput trop importante avec volume: {throughput_ratio:.2f}x"
        
        return volume_results


if __name__ == "__main__":
    # Exécution des tests
    pytest.main([__file__, "-v"])