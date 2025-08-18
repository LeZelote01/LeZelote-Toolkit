#!/usr/bin/env python3
"""
Tests d'Intégration - Base de Données
====================================

Tests d'intégration avec les bases de données SQLite,
la persistence des données entre les sessions et la
cohérence des données entre les modules.

Valide les opérations CRUD, les relations entre tables,
les migrations et la sauvegarde/restauration.
"""

import sys
import os
import pytest
import tempfile
import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.db.sqlite_manager import SQLiteManager
from core.db.models import Project, ScanResult
from core.utils.logging_handler import get_logger
from modules.reconnaissance.network_scanner import NetworkScanner
from modules.vulnerability.web_scanner import WebScanner
from modules.reporting.report_generator import ReportGenerator


class TestDatabaseBasicOperations:
    """Tests des opérations de base de données"""

    @pytest.fixture
    def temp_db_path(self):
        """Fixture pour une base de données temporaire"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def db_manager(self, temp_db_path):
        """Fixture pour le gestionnaire de base de données"""
        manager = SQLiteManager(temp_db_path)
        manager.initialize_database()
        return manager

    def test_database_initialization(self, db_manager):
        """Test de l'initialisation de la base de données"""
        # Vérifier que toutes les tables sont créées
        tables = db_manager.get_table_list()
        expected_tables = ['projects', 'scan_results', 'vulnerabilities', 'hosts', 'reports']
        
        for table in expected_tables:
            assert table in tables

    def test_project_crud_operations(self, db_manager):
        """Test des opérations CRUD pour les projets"""
        # Create
        project_data = {
            'name': 'Test Project Integration',
            'target': '192.168.1.0/24',
            'description': 'Test project for integration testing',
            'created_date': datetime.now().isoformat(),
            'status': 'active'
        }
        
        project_id = db_manager.create_project(project_data)
        assert project_id is not None
        assert isinstance(project_id, str)
        
        # Read
        project = db_manager.get_project(project_id)
        assert project is not None
        assert project['name'] == project_data['name']
        assert project['target'] == project_data['target']
        assert project['status'] == 'active'
        
        # Update
        update_data = {'status': 'completed', 'end_date': datetime.now().isoformat()}
        result = db_manager.update_project(project_id, update_data)
        assert result is True
        
        # Vérifier la mise à jour
        updated_project = db_manager.get_project(project_id)
        assert updated_project['status'] == 'completed'
        assert updated_project['end_date'] is not None
        
        # List all projects
        all_projects = db_manager.list_projects()
        assert len(all_projects) >= 1
        assert any(p['id'] == project_id for p in all_projects)
        
        # Delete
        delete_result = db_manager.delete_project(project_id)
        assert delete_result is True
        
        # Vérifier la suppression
        deleted_project = db_manager.get_project(project_id)
        assert deleted_project is None

    def test_host_and_port_storage(self, db_manager):
        """Test du stockage des hôtes et ports"""
        # Créer un projet
        project_data = {
            'name': 'Host Storage Test',
            'target': '192.168.1.100',
            'status': 'active'
        }
        project_id = db_manager.create_project(project_data)
        
        # Ajouter un hôte avec ports
        host_data = {
            'project_id': project_id,
            'ip_address': '192.168.1.100',
            'hostname': 'test.local',
            'os_family': 'Linux',
            'os_version': 'Ubuntu 20.04',
            'status': 'up',
            'ports': [
                {'port': 22, 'protocol': 'tcp', 'state': 'open', 'service': 'ssh'},
                {'port': 80, 'protocol': 'tcp', 'state': 'open', 'service': 'http'},
                {'port': 443, 'protocol': 'tcp', 'state': 'open', 'service': 'https'}
            ]
        }
        
        host_id = db_manager.create_host(host_data)
        assert host_id is not None
        
        # Récupérer l'hôte
        host = db_manager.get_host(host_id)
        assert host is not None
        assert host['ip_address'] == '192.168.1.100'
        assert host['hostname'] == 'test.local'
        assert len(host['ports']) == 3
        
        # Vérifier les ports
        ports = host['ports']
        port_numbers = [p['port'] for p in ports]
        assert 22 in port_numbers
        assert 80 in port_numbers
        assert 443 in port_numbers

    def test_vulnerability_storage_and_retrieval(self, db_manager):
        """Test du stockage et de la récupération des vulnérabilités"""
        # Créer un projet et un hôte
        project_id = db_manager.create_project({
            'name': 'Vulnerability Test',
            'target': '192.168.1.100',
            'status': 'active'
        })
        
        host_id = db_manager.create_host({
            'project_id': project_id,
            'ip_address': '192.168.1.100',
            'status': 'up'
        })
        
        # Ajouter des vulnérabilités
        vulnerabilities = [
            {
                'project_id': project_id,
                'host_id': host_id,
                'title': 'Cross-Site Scripting (XSS)',
                'description': 'Reflected XSS vulnerability found',
                'severity': 'high',
                'cvss_score': 7.5,
                'cve_id': 'CVE-2023-1234',
                'url': 'http://192.168.1.100/search.php?q=<script>',
                'port': 80,
                'service': 'http',
                'status': 'open'
            },
            {
                'project_id': project_id,
                'host_id': host_id,
                'title': 'SQL Injection',
                'description': 'Boolean-based blind SQL injection',
                'severity': 'critical',
                'cvss_score': 9.0,
                'cve_id': 'CVE-2023-5678',
                'url': 'http://192.168.1.100/login.php',
                'port': 80,
                'service': 'http',
                'status': 'open'
            }
        ]
        
        vuln_ids = []
        for vuln_data in vulnerabilities:
            vuln_id = db_manager.create_vulnerability(vuln_data)
            assert vuln_id is not None
            vuln_ids.append(vuln_id)
        
        # Récupérer les vulnérabilités par projet
        project_vulns = db_manager.get_vulnerabilities_by_project(project_id)
        assert len(project_vulns) == 2
        
        # Récupérer les vulnérabilités par sévérité
        high_vulns = db_manager.get_vulnerabilities_by_severity('high')
        critical_vulns = db_manager.get_vulnerabilities_by_severity('critical')
        
        assert len(high_vulns) >= 1
        assert len(critical_vulns) >= 1
        
        # Vérifier les données spécifiques
        xss_vuln = next((v for v in project_vulns if 'XSS' in v['title']), None)
        assert xss_vuln is not None
        assert xss_vuln['cvss_score'] == 7.5
        assert xss_vuln['cve_id'] == 'CVE-2023-1234'

    def test_scan_result_tracking(self, db_manager):
        """Test du suivi des résultats de scan"""
        # Créer un projet
        project_id = db_manager.create_project({
            'name': 'Scan Tracking Test',
            'target': '192.168.1.0/24',
            'status': 'active'
        })
        
        # Enregistrer des résultats de scan
        scan_results = [
            {
                'project_id': project_id,
                'scan_type': 'nmap_discovery',
                'target': '192.168.1.0/24',
                'start_time': datetime.now().isoformat(),
                'status': 'completed',
                'result_data': json.dumps({
                    'hosts_discovered': 5,
                    'ports_discovered': 25,
                    'services_identified': 12
                }),
                'tool_used': 'nmap',
                'command_line': 'nmap -sn 192.168.1.0/24'
            },
            {
                'project_id': project_id,
                'scan_type': 'web_vulnerability',
                'target': '192.168.1.100',
                'start_time': datetime.now().isoformat(),
                'status': 'completed',
                'result_data': json.dumps({
                    'vulnerabilities_found': 3,
                    'high_risk': 1,
                    'medium_risk': 2
                }),
                'tool_used': 'zaproxy',
                'command_line': 'zap-baseline.py -t http://192.168.1.100'
            }
        ]
        
        scan_ids = []
        for scan_data in scan_results:
            scan_id = db_manager.create_scan_result(scan_data)
            assert scan_id is not None
            scan_ids.append(scan_id)
        
        # Récupérer les résultats par projet
        project_scans = db_manager.get_scan_results_by_project(project_id)
        assert len(project_scans) == 2
        
        # Récupérer par type de scan
        nmap_scans = db_manager.get_scan_results_by_type('nmap_discovery')
        web_scans = db_manager.get_scan_results_by_type('web_vulnerability')
        
        assert len(nmap_scans) >= 1
        assert len(web_scans) >= 1
        
        # Vérifier les données de résultat
        nmap_scan = project_scans[0]
        result_data = json.loads(nmap_scan['result_data'])
        assert 'hosts_discovered' in result_data
        assert result_data['hosts_discovered'] == 5


class TestDatabaseIntegrationWithModules:
    """Tests d'intégration base de données avec les modules"""

    @pytest.fixture
    def temp_db_path(self):
        """Fixture pour une base de données temporaire"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def db_manager(self, temp_db_path):
        """Fixture pour le gestionnaire de base de données"""
        manager = SQLiteManager(temp_db_path)
        manager.initialize_database()
        return manager

    def test_reconnaissance_to_database_integration(self, db_manager):
        """Test d'intégration reconnaissance -> base de données"""
        # Créer un projet
        project_id = db_manager.create_project({
            'name': 'Recon Integration Test',
            'target': '192.168.1.100',
            'status': 'active'
        })
        
        # Mock du scanner réseau
        scanner = NetworkScanner(db_manager)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout=self._get_mock_nmap_output()
            )
            
            # Exécuter le scan
            result = scanner.scan_network('192.168.1.100', project_id)
            
            assert result['success'] is True
            assert 'hosts_discovered' in result
            
            # Vérifier que les données sont en base
            hosts = db_manager.get_hosts_by_project(project_id)
            assert len(hosts) > 0
            
            # Vérifier les détails du premier hôte
            host = hosts[0]
            assert host['ip_address'] == '192.168.1.100'
            assert host['status'] == 'up'
            assert len(host['ports']) > 0
            
            # Vérifier qu'un résultat de scan est enregistré
            scan_results = db_manager.get_scan_results_by_project(project_id)
            assert len(scan_results) > 0
            assert scan_results[0]['scan_type'] == 'network_discovery'

    def test_vulnerability_scanning_integration(self, db_manager):
        """Test d'intégration scan vulnérabilités -> base de données"""
        # Créer un projet avec un hôte
        project_id = db_manager.create_project({
            'name': 'Vuln Integration Test',
            'target': '192.168.1.100',
            'status': 'active'
        })
        
        host_id = db_manager.create_host({
            'project_id': project_id,
            'ip_address': '192.168.1.100',
            'status': 'up',
            'ports': [{'port': 80, 'protocol': 'tcp', 'state': 'open', 'service': 'http'}]
        })
        
        # Mock du scanner de vulnérabilités
        vuln_scanner = WebScanner(db_manager)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout=json.dumps({
                    'vulnerabilities': [
                        {
                            'name': 'Cross-Site Scripting',
                            'severity': 'high',
                            'url': 'http://192.168.1.100/search.php'
                        }
                    ]
                })
            )
            
            # Exécuter le scan de vulnérabilités
            result = vuln_scanner.scan_web_application(
                'http://192.168.1.100', 
                project_id
            )
            
            assert result['success'] is True
            
            # Vérifier les vulnérabilités en base
            vulns = db_manager.get_vulnerabilities_by_project(project_id)
            assert len(vulns) > 0
            
            vuln = vulns[0]
            assert 'Cross-Site Scripting' in vuln['title']
            assert vuln['severity'] == 'high'
            assert vuln['host_id'] == host_id

    def test_report_generation_integration(self, db_manager):
        """Test d'intégration génération de rapports -> base de données"""
        # Créer un projet complet avec données
        project_id = db_manager.create_project({
            'name': 'Report Integration Test',
            'target': '192.168.1.100',
            'status': 'completed'
        })
        
        # Ajouter un hôte
        host_id = db_manager.create_host({
            'project_id': project_id,
            'ip_address': '192.168.1.100',
            'hostname': 'test.local',
            'status': 'up',
            'ports': [
                {'port': 80, 'protocol': 'tcp', 'state': 'open', 'service': 'http'},
                {'port': 443, 'protocol': 'tcp', 'state': 'open', 'service': 'https'}
            ]
        })
        
        # Ajouter des vulnérabilités
        db_manager.create_vulnerability({
            'project_id': project_id,
            'host_id': host_id,
            'title': 'Cross-Site Scripting (XSS)',
            'description': 'Reflected XSS vulnerability',
            'severity': 'high',
            'cvss_score': 7.5,
            'port': 80,
            'status': 'open'
        })
        
        # Générer le rapport
        report_generator = ReportGenerator(db_manager)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            report_config = {
                'project_id': project_id,
                'format': 'html',
                'template': 'pentest_standard',
                'output_dir': temp_dir,
                'include_executive_summary': True,
                'include_technical_details': True
            }
            
            result = report_generator.generate_report(report_config)
            
            assert result['success'] is True
            assert 'report_path' in result
            
            # Vérifier que le rapport est enregistré en base
            report_id = result.get('report_id')
            if report_id:
                report_record = db_manager.get_report(report_id)
                assert report_record is not None
                assert report_record['project_id'] == project_id
                assert report_record['format'] == 'html'
                assert report_record['status'] == 'completed'

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

Service detection performed.
Nmap done: 1 IP address (1 host up) scanned in 2.45 seconds
        '''


class TestDatabasePerformanceAndScaling:
    """Tests de performance et de scalabilité"""

    @pytest.fixture
    def temp_db_path(self):
        """Fixture pour une base de données temporaire"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            temp_path = temp_file.name
        yield temp_path
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def db_manager(self, temp_db_path):
        """Fixture pour le gestionnaire de base de données"""
        manager = SQLiteManager(temp_db_path)
        manager.initialize_database()
        return manager

    def test_bulk_host_insertion(self, db_manager):
        """Test d'insertion en masse d'hôtes"""
        import time
        
        # Créer un projet
        project_id = db_manager.create_project({
            'name': 'Bulk Insert Test',
            'target': '192.168.0.0/16',
            'status': 'active'
        })
        
        # Préparer 1000 hôtes
        hosts_data = []
        for i in range(1000):
            hosts_data.append({
                'project_id': project_id,
                'ip_address': f'192.168.{i//256}.{i%256}',
                'status': 'up' if i % 3 == 0 else 'down',
                'ports': [
                    {'port': 22, 'protocol': 'tcp', 'state': 'open', 'service': 'ssh'}
                ] if i % 3 == 0 else []
            })
        
        # Mesurer le temps d'insertion
        start_time = time.time()
        
        host_ids = db_manager.bulk_create_hosts(hosts_data)
        
        end_time = time.time()
        insertion_time = end_time - start_time
        
        # Validations
        assert len(host_ids) == 1000
        assert insertion_time < 10.0  # Moins de 10 secondes
        
        # Vérifier les données
        all_hosts = db_manager.get_hosts_by_project(project_id)
        assert len(all_hosts) == 1000
        
        # Vérifier les statistiques
        up_hosts = [h for h in all_hosts if h['status'] == 'up']
        assert len(up_hosts) > 300  # Environ 1/3

    def test_complex_queries_performance(self, db_manager):
        """Test de performance des requêtes complexes"""
        import time
        
        # Préparer des données de test
        project_id = db_manager.create_project({
            'name': 'Query Performance Test',
            'target': '192.168.1.0/24',
            'status': 'active'
        })
        
        # Créer 100 hôtes avec vulnérabilités
        for i in range(100):
            host_id = db_manager.create_host({
                'project_id': project_id,
                'ip_address': f'192.168.1.{i}',
                'status': 'up',
                'ports': [
                    {'port': 80, 'protocol': 'tcp', 'state': 'open', 'service': 'http'},
                    {'port': 443, 'protocol': 'tcp', 'state': 'open', 'service': 'https'}
                ]
            })
            
            # Ajouter des vulnérabilités aléatoires
            for j in range(5):  # 5 vulns par hôte
                db_manager.create_vulnerability({
                    'project_id': project_id,
                    'host_id': host_id,
                    'title': f'Vulnerability {j} on Host {i}',
                    'severity': ['low', 'medium', 'high', 'critical'][j % 4],
                    'cvss_score': 3.0 + (j % 4) * 2.0,
                    'port': 80,
                    'status': 'open'
                })
        
        # Test de requêtes complexes
        queries = [
            # Statistiques par projet
            lambda: db_manager.get_project_statistics(project_id),
            
            # Vulnérabilités critiques
            lambda: db_manager.get_vulnerabilities_by_severity('critical'),
            
            # Hôtes avec le plus de vulnérabilités
            lambda: db_manager.get_hosts_with_most_vulnerabilities(project_id, limit=10),
            
            # Recherche de vulnérabilités par mot-clé
            lambda: db_manager.search_vulnerabilities('Vulnerability', project_id)
        ]
        
        for i, query_func in enumerate(queries):
            start_time = time.time()
            result = query_func()
            end_time = time.time()
            
            query_time = end_time - start_time
            
            # Chaque requête doit s'exécuter en moins d'1 seconde
            assert query_time < 1.0, f"Query {i} took {query_time:.2f}s"
            assert result is not None

    def test_database_backup_and_restore(self, db_manager, temp_db_path):
        """Test de sauvegarde et restauration de base de données"""
        # Créer des données de test
        project_id = db_manager.create_project({
            'name': 'Backup Test Project',
            'target': '192.168.1.100',
            'status': 'active'
        })
        
        host_id = db_manager.create_host({
            'project_id': project_id,
            'ip_address': '192.168.1.100',
            'status': 'up'
        })
        
        vuln_id = db_manager.create_vulnerability({
            'project_id': project_id,
            'host_id': host_id,
            'title': 'Test Vulnerability',
            'severity': 'high',
            'status': 'open'
        })
        
        # Créer une sauvegarde
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as backup_file:
            backup_path = backup_file.name
        
        try:
            backup_result = db_manager.backup_database(backup_path)
            assert backup_result['success'] is True
            assert os.path.exists(backup_path)
            
            # Modifier les données originales
            db_manager.update_project(project_id, {'status': 'completed'})
            
            # Restaurer depuis la sauvegarde
            restore_result = db_manager.restore_database(backup_path)
            assert restore_result['success'] is True
            
            # Vérifier la restauration
            restored_project = db_manager.get_project(project_id)
            assert restored_project['status'] == 'active'  # État avant modification
            
        finally:
            if os.path.exists(backup_path):
                os.unlink(backup_path)


class TestDatabaseMigrationAndUpgrade:
    """Tests de migration et mise à niveau"""

    def test_schema_migration(self):
        """Test de migration de schéma"""
        # Créer une ancienne version de DB
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_file:
            old_db_path = temp_file.name
        
        try:
            # Créer une DB avec ancien schéma
            conn = sqlite3.connect(old_db_path)
            cursor = conn.cursor()
            
            # Ancien schéma simplifié
            cursor.execute('''
                CREATE TABLE projects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    target TEXT NOT NULL,
                    created_date TEXT
                )
            ''')
            
            # Insérer des données test
            cursor.execute(
                "INSERT INTO projects (id, name, target, created_date) VALUES (?, ?, ?, ?)",
                ('test-id', 'Test Project', '192.168.1.100', '2023-01-01T00:00:00')
            )
            
            conn.commit()
            conn.close()
            
            # Effectuer la migration
            db_manager = SQLiteManager(old_db_path)
            migration_result = db_manager.migrate_database()
            
            assert migration_result['success'] is True
            assert 'migrations_applied' in migration_result
            
            # Vérifier que les nouvelles colonnes existent
            migrated_project = db_manager.get_project('test-id')
            assert migrated_project is not None
            assert migrated_project['name'] == 'Test Project'
            
            # Vérifier les nouvelles tables
            tables = db_manager.get_table_list()
            expected_new_tables = ['vulnerabilities', 'hosts', 'reports']
            for table in expected_new_tables:
                assert table in tables
                
        finally:
            if os.path.exists(old_db_path):
                os.unlink(old_db_path)


if __name__ == "__main__":
    # Exécution des tests
    pytest.main([__file__, "-v"])