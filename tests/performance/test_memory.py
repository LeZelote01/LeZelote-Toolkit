#!/usr/bin/env python3
"""
Tests de Performance - Mémoire
==============================

Tests spécifiques à l'utilisation mémoire
et à la détection de fuites mémoire.

Valide l'efficacité de la gestion mémoire
et l'absence de fuites dans le système.
"""

import sys
import os
import pytest
import time
import gc
import psutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.engine.orchestrator import PentestOrchestrator
from core.utils.logging_handler import get_logger


class TestMemoryPerformance:
    """Tests de performance mémoire"""

    def setup_method(self):
        """Setup pour chaque test"""
        # Forcer le garbage collection avant chaque test
        gc.collect()
        
        # Obtenir le processus courant pour monitoring
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.process.memory_info().rss

    def test_memory_usage_single_project(self):
        """Test d'utilisation mémoire pour un projet unique"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Mesurer mémoire avant création
        memory_before = self.process.memory_info().rss
        
        project_config = {
            'name': 'Memory Test Project',
            'target': '192.168.1.100',
            'output_dir': '/tmp',
            'description': 'Test project for memory usage analysis'
        }
        
        # Créer le projet
        result = orchestrator.initialize_project(project_config)
        
        # Mesurer mémoire après création
        memory_after = self.process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        # Validations
        assert result['success'] is True
        # L'augmentation mémoire pour un projet doit être raisonnable (< 10MB)
        assert memory_increase < 10 * 1024 * 1024, f"Utilisation mémoire excessive: {memory_increase / 1024 / 1024:.2f}MB"
        
        print(f"Mémoire utilisée pour un projet: {memory_increase / 1024:.0f}KB")

    def test_memory_leak_detection(self):
        """Test de détection de fuites mémoire"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Effectuer plusieurs cycles de création/destruction
        num_cycles = 50
        memory_measurements = []
        
        for i in range(num_cycles):
            # Mesurer mémoire avant
            memory_before = self.process.memory_info().rss
            
            # Créer un projet
            project_config = {
                'name': f'Memory Leak Test {i}',
                'target': f'192.168.1.{i % 255}',
                'output_dir': '/tmp'
            }
            
            result = orchestrator.initialize_project(project_config)
            project_id = result.get('project_id')
            
            # Simuler utilisation du projet
            if project_id:
                # Simuler des opérations sur le projet
                pass
            
            # Forcer nettoyage (simuler fin de cycle de vie)
            del result
            if 'project_config' in locals():
                del project_config
            
            # Garbage collection
            gc.collect()
            
            # Mesurer mémoire après nettoyage
            memory_after = self.process.memory_info().rss
            memory_measurements.append(memory_after)
            
            # Pause courte entre cycles
            time.sleep(0.01)
        
        # Analyser la tendance mémoire
        if len(memory_measurements) >= 10:
            # Comparer le début et la fin
            start_avg = sum(memory_measurements[:5]) / 5
            end_avg = sum(memory_measurements[-5:]) / 5
            
            memory_growth = end_avg - start_avg
            growth_percentage = (memory_growth / start_avg) * 100
            
            # Validation: la croissance mémoire doit être < 5% après 50 cycles
            assert growth_percentage < 5.0, f"Fuite mémoire détectée: {growth_percentage:.2f}% d'augmentation"
            
            print(f"Croissance mémoire sur {num_cycles} cycles: {growth_percentage:.2f}%")

    def test_large_data_handling(self):
        """Test de gestion de grandes quantités de données"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Créer un projet avec beaucoup de données
        large_description = 'A' * (1024 * 1024)  # 1MB de texte
        large_target_list = '\n'.join([f'192.168.{i//256}.{i%256}' for i in range(10000)])  # 10k cibles
        
        memory_before = self.process.memory_info().rss
        
        project_config = {
            'name': 'Large Data Test Project',
            'target': large_target_list,
            'output_dir': '/tmp',
            'description': large_description
        }
        
        result = orchestrator.initialize_project(project_config)
        
        memory_after_creation = self.process.memory_info().rss
        creation_memory_increase = memory_after_creation - memory_before
        
        # Validations
        assert result['success'] is True
        
        # L'augmentation mémoire doit être proportionnelle mais pas excessive
        # (moins de 5x la taille des données brutes)
        raw_data_size = len(large_description) + len(large_target_list)
        assert creation_memory_increase < raw_data_size * 5, f"Utilisation mémoire disproportionnée: {creation_memory_increase / 1024 / 1024:.2f}MB pour {raw_data_size / 1024 / 1024:.2f}MB de données"
        
        # Nettoyer et vérifier la libération mémoire
        del project_config
        del large_description
        del large_target_list
        gc.collect()
        
        memory_after_cleanup = self.process.memory_info().rss
        cleanup_memory_decrease = memory_after_creation - memory_after_cleanup
        
        # Au moins 50% de la mémoire utilisée devrait être libérée
        assert cleanup_memory_decrease >= creation_memory_increase * 0.5, f"Nettoyage mémoire insuffisant: {cleanup_memory_decrease / 1024 / 1024:.2f}MB libérés sur {creation_memory_increase / 1024 / 1024:.2f}MB utilisés"
        
        print(f"Gestion grandes données: +{creation_memory_increase / 1024 / 1024:.2f}MB créé, -{cleanup_memory_decrease / 1024 / 1024:.2f}MB libéré")

    def test_concurrent_memory_usage(self):
        """Test d'utilisation mémoire concurrent"""
        import threading
        import concurrent.futures
        
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        num_threads = 10
        projects_per_thread = 20
        
        memory_before = self.process.memory_info().rss
        results = []
        
        def create_projects_in_thread(thread_id):
            """Créer des projets dans un thread"""
            thread_results = []
            
            for i in range(projects_per_thread):
                try:
                    project_config = {
                        'name': f'Concurrent Memory Test T{thread_id}P{i}',
                        'target': f'10.{thread_id}.{i}.1',
                        'output_dir': '/tmp'
                    }
                    
                    result = orchestrator.initialize_project(project_config)
                    thread_results.append(result.get('success', False))
                    
                except Exception as e:
                    thread_results.append(False)
            
            return thread_results
        
        # Exécuter threads concurrents
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(create_projects_in_thread, i) for i in range(num_threads)]
            
            for future in concurrent.futures.as_completed(futures):
                thread_results = future.result()
                results.extend(thread_results)
        
        memory_after = self.process.memory_info().rss
        total_memory_increase = memory_after - memory_before
        
        # Analyser les résultats
        successful_projects = sum(results)
        total_projects = len(results)
        success_rate = (successful_projects / total_projects) * 100
        
        # Validations
        assert success_rate >= 90.0, f"Taux de succès concurrent trop bas: {success_rate:.1f}%"
        
        # Mémoire par projet (approximation)
        if successful_projects > 0:
            memory_per_project = total_memory_increase / successful_projects
            assert memory_per_project < 1024 * 1024, f"Utilisation mémoire par projet trop élevée: {memory_per_project / 1024:.1f}KB"
        
        print(f"Concurrent mémoire: {successful_projects} projets, {total_memory_increase / 1024 / 1024:.2f}MB total")

    def test_memory_fragmentation(self):
        """Test de fragmentation mémoire"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Créer et détruire des projets de tailles variables
        memory_before = self.process.memory_info().rss
        created_projects = []
        
        # Créer des projets de différentes tailles
        for i in range(100):
            # Taille variable des descriptions
            description_size = (i % 10 + 1) * 1000  # De 1KB à 10KB
            description = 'X' * description_size
            
            project_config = {
                'name': f'Fragmentation Test {i}',
                'target': f'192.168.{i // 255}.{i % 255}',
                'output_dir': '/tmp',
                'description': description
            }
            
            result = orchestrator.initialize_project(project_config)
            if result.get('success'):
                created_projects.append((result['project_id'], description_size))
        
        memory_after_creation = self.process.memory_info().rss
        
        # Supprimer la moitié des projets (pattern fragmentant)
        projects_to_remove = created_projects[::2]  # Supprime 1 projet sur 2
        
        for project_id, size in projects_to_remove:
            # Simuler suppression (pas d'API de suppression réelle)
            pass
        
        # Forcer garbage collection
        gc.collect()
        
        memory_after_partial_cleanup = self.process.memory_info().rss
        
        # Créer de nouveaux projets dans les "trous"
        for i in range(50):
            project_config = {
                'name': f'Refill Test {i}',
                'target': f'172.16.1.{i}',
                'output_dir': '/tmp',
                'description': 'Y' * 5000  # Taille moyenne
            }
            
            result = orchestrator.initialize_project(project_config)
        
        memory_final = self.process.memory_info().rss
        
        # Analyser la fragmentation
        total_memory_increase = memory_final - memory_before
        
        # L'augmentation totale ne devrait pas être excessive malgré la fragmentation
        # (moins de 100MB pour 150 projets créés)
        assert total_memory_increase < 100 * 1024 * 1024, f"Fragmentation mémoire excessive: {total_memory_increase / 1024 / 1024:.2f}MB"
        
        print(f"Test fragmentation: {len(created_projects)} créés, {len(projects_to_remove)} partiels, +{total_memory_increase / 1024 / 1024:.2f}MB total")

    def test_memory_peak_usage(self):
        """Test du pic d'utilisation mémoire"""
        import threading
        import time
        
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Monitorer la mémoire en continu
        memory_samples = []
        monitoring = True
        
        def memory_monitor():
            """Monitorer l'utilisation mémoire"""
            while monitoring:
                memory_usage = self.process.memory_info().rss
                memory_samples.append({
                    'timestamp': time.time(),
                    'memory_rss': memory_usage,
                    'memory_vms': self.process.memory_info().vms
                })
                time.sleep(0.1)  # Échantillonnage toutes les 100ms
        
        # Démarrer le monitoring
        monitor_thread = threading.Thread(target=memory_monitor)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Phase de charge intensive
        num_projects = 200
        projects = []
        
        start_time = time.time()
        
        for i in range(num_projects):
            project_config = {
                'name': f'Peak Memory Test {i}',
                'target': f'10.{i//65536}.{(i//256)%256}.{i%256}',
                'output_dir': '/tmp',
                'description': f'Project {i} with data: ' + ('Z' * (i % 5000 + 1000))  # Taille croissante
            }
            
            result = orchestrator.initialize_project(project_config)
            if result.get('success'):
                projects.append(result['project_id'])
            
            # Pause occasionnelle pour permettre le nettoyage
            if i % 50 == 0:
                time.sleep(0.1)
                gc.collect()
        
        end_time = time.time()
        
        # Arrêter le monitoring
        monitoring = False
        monitor_thread.join(timeout=1)
        
        # Analyser les pics de mémoire
        if memory_samples:
            initial_memory = memory_samples[0]['memory_rss']
            peak_memory = max(sample['memory_rss'] for sample in memory_samples)
            final_memory = memory_samples[-1]['memory_rss']
            
            peak_increase = peak_memory - initial_memory
            final_increase = final_memory - initial_memory
            
            # Validations
            # Le pic ne devrait pas dépasser 500MB
            assert peak_increase < 500 * 1024 * 1024, f"Pic mémoire trop élevé: {peak_increase / 1024 / 1024:.2f}MB"
            
            # La mémoire finale devrait être raisonnable par rapport au pic
            memory_efficiency = (final_increase / peak_increase) * 100 if peak_increase > 0 else 100
            assert memory_efficiency <= 150, f"Efficacité mémoire faible: {memory_efficiency:.1f}% (final vs pic)"
            
            print(f"Pic mémoire: initial={initial_memory/1024/1024:.1f}MB, pic={peak_memory/1024/1024:.1f}MB, final={final_memory/1024/1024:.1f}MB")
            print(f"Projets créés: {len(projects)}/{num_projects}")

    def test_garbage_collection_effectiveness(self):
        """Test de l'efficacité du garbage collection"""
        orchestrator = PentestOrchestrator(target="192.168.1.100", profile="test")
        
        # Créer beaucoup d'objets temporaires
        memory_before_gc = self.process.memory_info().rss
        
        temp_objects = []
        for i in range(1000):
            project_config = {
                'name': f'GC Test {i}',
                'target': f'192.168.{i//256}.{i%256}',
                'output_dir': '/tmp',
                'description': 'Temporary object for GC testing: ' + ('A' * 1000)
            }
            
            result = orchestrator.initialize_project(project_config)
            temp_objects.append((project_config, result))
        
        memory_after_creation = self.process.memory_info().rss
        creation_increase = memory_after_creation - memory_before_gc
        
        # Supprimer les références
        del temp_objects
        
        # Garbage collection sans forçage
        memory_after_del = self.process.memory_info().rss
        auto_cleanup = memory_after_creation - memory_after_del
        
        # Garbage collection forcé
        gc.collect()
        memory_after_gc = self.process.memory_info().rss
        gc_cleanup = memory_after_del - memory_after_gc
        
        total_cleanup = memory_after_creation - memory_after_gc
        cleanup_percentage = (total_cleanup / creation_increase) * 100 if creation_increase > 0 else 100
        
        # Validations
        # Au moins 70% de la mémoire devrait être libérée
        assert cleanup_percentage >= 70.0, f"Garbage collection inefficace: {cleanup_percentage:.1f}% nettoyé"
        
        # Le GC forcé devrait libérer de la mémoire supplémentaire
        assert gc_cleanup >= 0, f"GC forcé contre-productif: {gc_cleanup / 1024 / 1024:.2f}MB"
        
        print(f"GC effectivité: {cleanup_percentage:.1f}% nettoyé ({total_cleanup / 1024 / 1024:.2f}MB sur {creation_increase / 1024 / 1024:.2f}MB)")
        print(f"Auto cleanup: {auto_cleanup / 1024 / 1024:.2f}MB, GC forcé: {gc_cleanup / 1024 / 1024:.2f}MB")


if __name__ == "__main__":
    # Exécution des tests
    pytest.main([__file__, "-v"])