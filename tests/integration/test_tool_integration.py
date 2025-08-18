#!/usr/bin/env python3
"""
Tests d'Intégration - Outils Externes
====================================

Tests d'intégration avec les outils de sécurité externes
comme Nmap, Metasploit, ZAP, SQLMap, etc.

Valide la communication, le parsing des résultats et la
gestion des erreurs avec tous les outils intégrés.
"""

import sys
import os
import pytest
import tempfile
import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.api.nmap_api import NmapAPI
from core.api.metasploit_api import MetasploitAPI
from core.api.zap_api import ZapAPI
from core.api.nessus_api import NessusAPI
from core.api.shodan_api import ShodanAPI
from core.api.cloud_api import CloudAPI
from core.utils.logging_handler import get_logger


class TestNmapIntegration:
    """Tests d'intégration avec Nmap"""

    @pytest.fixture
    def nmap_api(self):
        """Fixture pour l'API Nmap"""
        return NmapAPI()

    def test_nmap_basic_scan(self, nmap_api):
        """Test d'un scan Nmap basique"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout=self._get_nmap_xml_output()
            )
            
            result = nmap_api.scan_host('192.168.1.100')
            
            assert result['success'] is True
            assert 'hosts' in result
            assert len(result['hosts']) > 0
            
            host = result['hosts'][0]
            assert host['ip'] == '192.168.1.100'
            assert 'ports' in host
            assert len(host['ports']) > 0

    def test_nmap_service_detection(self, nmap_api):
        """Test de la détection de services Nmap"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout=self._get_nmap_service_xml()
            )
            
            result = nmap_api.scan_services('192.168.1.100', [80, 443, 22])
            
            assert result['success'] is True
            assert 'services' in result
            
            services = result['services']
            assert '80' in services
            assert services['80']['name'] == 'http'
            assert services['80']['version'] is not None

    def test_nmap_vulnerability_scan(self, nmap_api):
        """Test du scan de vulnérabilités Nmap"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout=self._get_nmap_vuln_xml()
            )
            
            result = nmap_api.vulnerability_scan('192.168.1.100')
            
            assert result['success'] is True
            assert 'vulnerabilities' in result
            assert len(result['vulnerabilities']) > 0
            
            vuln = result['vulnerabilities'][0]
            assert 'cve' in vuln
            assert 'severity' in vuln

    def test_nmap_error_handling(self, nmap_api):
        """Test de la gestion d'erreurs Nmap"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stderr='Host seems down'
            )
            
            result = nmap_api.scan_host('999.999.999.999')
            
            assert result['success'] is False
            assert 'error' in result
            assert 'Host seems down' in result['error']

    def _get_nmap_xml_output(self):
        """Retourne un XML Nmap mocké"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<nmaprun>
    <host>
        <address addr="192.168.1.100" addrtype="ipv4"/>
        <status state="up"/>
        <ports>
            <port protocol="tcp" portid="22">
                <state state="open"/>
                <service name="ssh" product="OpenSSH" version="8.2p1"/>
            </port>
            <port protocol="tcp" portid="80">
                <state state="open"/>
                <service name="http" product="Apache" version="2.4.41"/>
            </port>
        </ports>
    </host>
</nmaprun>'''

    def _get_nmap_service_xml(self):
        """Retourne un XML de services Nmap"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<nmaprun>
    <host>
        <address addr="192.168.1.100" addrtype="ipv4"/>
        <ports>
            <port protocol="tcp" portid="80">
                <state state="open"/>
                <service name="http" product="Apache httpd" version="2.4.41" extrainfo="(Ubuntu)"/>
            </port>
        </ports>
    </host>
</nmaprun>'''

    def _get_nmap_vuln_xml(self):
        """Retourne un XML de vulnérabilités Nmap"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<nmaprun>
    <host>
        <address addr="192.168.1.100" addrtype="ipv4"/>
        <hostscript>
            <script id="http-vuln-cve2017-5638" output="VULNERABLE">
                <elem key="CVE">CVE-2017-5638</elem>
                <elem key="severity">HIGH</elem>
            </script>
        </hostscript>
    </host>
</nmaprun>'''


class TestMetasploitIntegration:
    """Tests d'intégration avec Metasploit"""

    @pytest.fixture
    def msf_api(self):
        """Fixture pour l'API Metasploit"""
        return MetasploitAPI()

    def test_metasploit_connection(self, msf_api):
        """Test de connexion à Metasploit"""
        with patch('requests.post') as mock_post:
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {'result': 'success', 'token': 'test_token_123'}
            )
            
            result = msf_api.connect('127.0.0.1', 55553, 'msf', 'msf_password')
            
            assert result['success'] is True
            assert 'token' in result
            assert result['token'] == 'test_token_123'

    def test_metasploit_module_search(self, msf_api):
        """Test de recherche de modules Metasploit"""
        with patch('requests.post') as mock_post:
            # Mock de la connexion
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {'result': 'success', 'token': 'test_token'}
            )
            
            msf_api.connect('127.0.0.1', 55553, 'msf', 'msf_password')
            
            # Mock de la recherche de modules
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {
                    'modules': [
                        {
                            'fullname': 'exploit/linux/http/apache_struts_rce',
                            'name': 'Apache Struts RCE',
                            'rank': 'excellent'
                        }
                    ]
                }
            )
            
            result = msf_api.search_exploits('apache struts')
            
            assert result['success'] is True
            assert 'modules' in result
            assert len(result['modules']) > 0

    def test_metasploit_exploit_execution(self, msf_api):
        """Test d'exécution d'exploit Metasploit"""
        with patch('requests.post') as mock_post:
            # Mock connexion et configuration
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {'result': 'success', 'job_id': 1}
            )
            
            msf_api.connect('127.0.0.1', 55553, 'msf', 'msf_password')
            
            # Configuration de l'exploit
            exploit_config = {
                'module': 'exploit/linux/http/apache_struts_rce',
                'RHOSTS': '192.168.1.100',
                'RPORT': '80',
                'payload': 'linux/x64/meterpreter/reverse_tcp',
                'LHOST': '192.168.1.50',
                'LPORT': '4444'
            }
            
            result = msf_api.execute_exploit(exploit_config)
            
            assert result['success'] is True
            assert 'job_id' in result

    def test_metasploit_session_management(self, msf_api):
        """Test de gestion des sessions Metasploit"""
        with patch('requests.post') as mock_post:
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {
                    'sessions': {
                        '1': {
                            'type': 'meterpreter',
                            'tunnel_local': '192.168.1.50:4444',
                            'tunnel_peer': '192.168.1.100:35678',
                            'via_exploit': 'exploit/linux/http/apache_struts_rce'
                        }
                    }
                }
            )
            
            msf_api.connect('127.0.0.1', 55553, 'msf', 'msf_password')
            
            result = msf_api.list_sessions()
            
            assert result['success'] is True
            assert 'sessions' in result
            assert '1' in result['sessions']


class TestZAPIntegration:
    """Tests d'intégration avec OWASP ZAP"""

    @pytest.fixture
    def zap_api(self):
        """Fixture pour l'API ZAP"""
        return ZapAPI()

    def test_zap_spider_scan(self, zap_api):
        """Test du spider ZAP"""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: {'scan': '1'}
            )
            
            result = zap_api.spider_scan('http://testphp.vulnweb.com')
            
            assert result['success'] is True
            assert 'scan_id' in result

    def test_zap_active_scan(self, zap_api):
        """Test du scan actif ZAP"""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: {'scan': '2'}
            )
            
            result = zap_api.active_scan('http://testphp.vulnweb.com')
            
            assert result['success'] is True
            assert 'scan_id' in result

    def test_zap_vulnerability_report(self, zap_api):
        """Test du rapport de vulnérabilités ZAP"""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: {
                    'alerts': [
                        {
                            'alert': 'Cross Site Scripting (Reflected)',
                            'risk': 'High',
                            'confidence': 'Medium',
                            'url': 'http://testphp.vulnweb.com/search.php?test=<script>'
                        }
                    ]
                }
            )
            
            result = zap_api.get_alerts('http://testphp.vulnweb.com')
            
            assert result['success'] is True
            assert 'vulnerabilities' in result
            assert len(result['vulnerabilities']) > 0


class TestNessusIntegration:
    """Tests d'intégration avec Nessus"""

    @pytest.fixture
    def nessus_api(self):
        """Fixture pour l'API Nessus"""
        return NessusAPI()

    def test_nessus_authentication(self, nessus_api):
        """Test d'authentification Nessus"""
        with patch('requests.post') as mock_post:
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {'token': 'nessus_token_123'}
            )
            
            result = nessus_api.authenticate('admin', 'password')
            
            assert result['success'] is True
            assert 'token' in result

    def test_nessus_scan_creation(self, nessus_api):
        """Test de création de scan Nessus"""
        with patch('requests.post') as mock_post:
            # Mock authentification
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {'token': 'nessus_token'}
            )
            
            nessus_api.authenticate('admin', 'password')
            
            # Mock création de scan
            mock_post.return_value = Mock(
                status_code=200,
                json=lambda: {'scan': {'id': 123}}
            )
            
            scan_config = {
                'name': 'Integration Test Scan',
                'targets': '192.168.1.100',
                'template': 'basic'
            }
            
            result = nessus_api.create_scan(scan_config)
            
            assert result['success'] is True
            assert 'scan_id' in result

    def test_nessus_scan_results(self, nessus_api):
        """Test de récupération des résultats Nessus"""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: {
                    'vulnerabilities': [
                        {
                            'plugin_id': '11219',
                            'plugin_name': 'Nessus SYN scanner',
                            'severity': 0
                        }
                    ]
                }
            )
            
            nessus_api.token = 'nessus_token'
            result = nessus_api.get_scan_results(123)
            
            assert result['success'] is True
            assert 'vulnerabilities' in result


class TestShodanIntegration:
    """Tests d'intégration avec Shodan"""

    @pytest.fixture
    def shodan_api(self):
        """Fixture pour l'API Shodan"""
        return ShodanAPI(api_key='test_api_key_12345')

    def test_shodan_host_lookup(self, shodan_api):
        """Test de lookup d'hôte Shodan"""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: {
                    'ip_str': '192.168.1.100',
                    'ports': [22, 80, 443],
                    'vulns': ['CVE-2017-5638'],
                    'org': 'Test Organization'
                }
            )
            
            result = shodan_api.host_lookup('192.168.1.100')
            
            assert result['success'] is True
            assert 'host_info' in result
            assert result['host_info']['ip'] == '192.168.1.100'

    def test_shodan_search(self, shodan_api):
        """Test de recherche Shodan"""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: {
                    'matches': [
                        {
                            'ip_str': '192.168.1.100',
                            'port': 80,
                            'product': 'Apache httpd'
                        }
                    ],
                    'total': 1
                }
            )
            
            result = shodan_api.search('apache')
            
            assert result['success'] is True
            assert 'results' in result
            assert len(result['results']) > 0


class TestCloudAPIIntegration:
    """Tests d'intégration avec les APIs Cloud"""

    @pytest.fixture
    def cloud_api(self):
        """Fixture pour l'API Cloud"""
        return CloudAPI()

    def test_aws_enumeration(self, cloud_api):
        """Test d'énumération AWS"""
        with patch('boto3.client') as mock_boto3:
            mock_client = Mock()
            mock_client.list_buckets.return_value = {
                'Buckets': [
                    {'Name': 'test-bucket-1'},
                    {'Name': 'test-bucket-2'}
                ]
            }
            mock_boto3.return_value = mock_client
            
            credentials = {
                'access_key': 'test_key',
                'secret_key': 'test_secret',
                'region': 'us-east-1'
            }
            
            result = cloud_api.enumerate_aws_resources(credentials)
            
            assert result['success'] is True
            assert 'buckets' in result
            assert len(result['buckets']) == 2

    def test_azure_enumeration(self, cloud_api):
        """Test d'énumération Azure"""
        with patch('azure.mgmt.storage.StorageManagementClient') as mock_azure:
            mock_client = Mock()
            mock_client.storage_accounts.list.return_value = [
                Mock(name='teststorage1'),
                Mock(name='teststorage2')
            ]
            mock_azure.return_value = mock_client
            
            credentials = {
                'subscription_id': 'test_subscription',
                'tenant_id': 'test_tenant',
                'client_id': 'test_client',
                'client_secret': 'test_secret'
            }
            
            result = cloud_api.enumerate_azure_resources(credentials)
            
            assert result['success'] is True
            assert 'storage_accounts' in result


class TestToolChaining:
    """Tests d'intégration en chaîne des outils"""

    def test_nmap_to_nessus_workflow(self):
        """Test du workflow Nmap -> Nessus"""
        nmap_api = NmapAPI()
        nessus_api = NessusAPI()
        
        with patch('subprocess.run') as mock_nmap, \
             patch('requests.post') as mock_nessus_post, \
             patch('requests.get') as mock_nessus_get:
            
            # Mock Nmap scan
            mock_nmap.return_value = Mock(
                returncode=0,
                stdout=self._get_nmap_xml_with_ports()
            )
            
            # Mock Nessus auth
            mock_nessus_post.return_value = Mock(
                status_code=200,
                json=lambda: {'token': 'nessus_token'}
            )
            
            # Étape 1: Scan Nmap
            nmap_result = nmap_api.scan_host('192.168.1.100')
            assert nmap_result['success'] is True
            
            discovered_ports = nmap_result['hosts'][0]['ports']
            
            # Étape 2: Authentification Nessus
            auth_result = nessus_api.authenticate('admin', 'password')
            assert auth_result['success'] is True
            
            # Mock Nessus scan creation
            mock_nessus_post.return_value = Mock(
                status_code=200,
                json=lambda: {'scan': {'id': 123}}
            )
            
            # Étape 3: Scan Nessus ciblé sur les ports découverts
            scan_config = {
                'name': 'Targeted Scan from Nmap',
                'targets': '192.168.1.100',
                'ports': ','.join([str(p['port']) for p in discovered_ports])
            }
            
            nessus_result = nessus_api.create_scan(scan_config)
            assert nessus_result['success'] is True
            
            # Validation de l'intégration
            assert len(discovered_ports) > 0
            assert nessus_result['scan_id'] == 123

    def test_shodan_to_zap_workflow(self):
        """Test du workflow Shodan -> ZAP"""
        shodan_api = ShodanAPI()
        zap_api = ZapAPI()
        
        with patch('requests.get') as mock_get:
            # Mock Shodan lookup
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: {
                    'ip_str': '192.168.1.100',
                    'ports': [80, 443],
                    'data': [
                        {'port': 80, 'product': 'Apache httpd'},
                        {'port': 443, 'product': 'Apache httpd'}
                    ]
                }
            )
            
            # Étape 1: Lookup Shodan
            shodan_result = shodan_api.host_lookup('192.168.1.100')
            assert shodan_result['success'] is True
            
            web_ports = [port for port in shodan_result['host_info']['ports'] 
                        if port in [80, 443, 8080, 8443]]
            
            # Mock ZAP scan
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: {'scan': '1'}
            )
            
            # Étape 2: Scan ZAP pour chaque port web découvert
            zap_results = []
            for port in web_ports:
                protocol = 'https' if port in [443, 8443] else 'http'
                url = f"{protocol}://192.168.1.100:{port}"
                
                zap_result = zap_api.spider_scan(url)
                assert zap_result['success'] is True
                zap_results.append(zap_result)
            
            # Validation
            assert len(zap_results) == len(web_ports)
            assert all(r['success'] for r in zap_results)

    def _get_nmap_xml_with_ports(self):
        """Retourne un XML Nmap avec plusieurs ports"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<nmaprun>
    <host>
        <address addr="192.168.1.100" addrtype="ipv4"/>
        <status state="up"/>
        <ports>
            <port protocol="tcp" portid="22">
                <state state="open"/>
                <service name="ssh" product="OpenSSH" version="8.2p1"/>
            </port>
            <port protocol="tcp" portid="80">
                <state state="open"/>
                <service name="http" product="Apache" version="2.4.41"/>
            </port>
            <port protocol="tcp" portid="443">
                <state state="open"/>
                <service name="https" product="Apache" version="2.4.41"/>
            </port>
        </ports>
    </host>
</nmaprun>'''


if __name__ == "__main__":
    # Exécution des tests
    pytest.main([__file__, "-v"])