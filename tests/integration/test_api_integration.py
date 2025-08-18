#!/usr/bin/env python3
"""
Tests d'Intégration - APIs Externes
==================================

Tests d'intégration avec les APIs externes comme Shodan,
les services cloud (AWS, Azure, GCP) et autres APIs
de renseignement sur les menaces.

Valide l'authentification, les appels d'API, le parsing
des réponses et la gestion des erreurs réseau.
"""

import sys
import os
import pytest
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.api.shodan_api import ShodanAPI
from core.api.cloud_api import CloudAPI
from core.utils.logging_handler import get_logger


class TestShodanAPIIntegration:
    """Tests d'intégration avec l'API Shodan"""

    @pytest.fixture
    def shodan_api(self):
        """Fixture pour l'API Shodan"""
        return ShodanAPI(api_key='test_api_key_12345')

    def test_shodan_host_lookup_integration(self, shodan_api):
        """Test d'intégration lookup d'hôte Shodan"""
        with patch('requests.get') as mock_get:
            # Mock de la réponse Shodan
            mock_response = {
                'ip_str': '8.8.8.8',
                'country_name': 'United States',
                'city': 'Mountain View',
                'org': 'Google LLC',
                'isp': 'Google LLC',
                'ports': [53, 443],
                'hostnames': ['dns.google'],
                'vulns': ['CVE-2016-6210'],
                'data': [
                    {
                        'port': 53,
                        'product': 'Google DNS',
                        'version': '2.0',
                        'transport': 'udp'
                    },
                    {
                        'port': 443,
                        'product': 'gws',
                        'ssl': {
                            'cert': {
                                'subject': {
                                    'CN': '*.google.com'
                                },
                                'issuer': {
                                    'CN': 'GTS CA 1C3'
                                }
                            }
                        }
                    }
                ]
            }
            
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: mock_response
            )
            
            # Test de lookup
            result = shodan_api.host_lookup('8.8.8.8')
            
            assert result['success'] is True
            assert 'host_info' in result
            
            host_info = result['host_info']
            assert host_info['ip'] == '8.8.8.8'
            assert host_info['country'] == 'United States'
            assert host_info['organization'] == 'Google LLC'
            assert 53 in host_info['ports']
            assert 443 in host_info['ports']
            assert len(host_info['vulnerabilities']) > 0
            
            # Vérifier les services détaillés
            assert 'services' in host_info
            services = host_info['services']
            assert len(services) == 2
            
            dns_service = next((s for s in services if s['port'] == 53), None)
            assert dns_service is not None
            assert dns_service['product'] == 'Google DNS'

    def test_shodan_search_integration(self, shodan_api):
        """Test d'intégration recherche Shodan"""
        with patch('requests.get') as mock_get:
            mock_response = {
                'matches': [
                    {
                        'ip_str': '192.168.1.100',
                        'port': 80,
                        'product': 'Apache httpd',
                        'version': '2.4.41',
                        'location': {
                            'country_name': 'United States',
                            'city': 'New York'
                        },
                        'org': 'Test Organization',
                        'data': 'HTTP/1.1 200 OK\\r\\nServer: Apache/2.4.41'
                    },
                    {
                        'ip_str': '192.168.1.101',
                        'port': 80,
                        'product': 'nginx',
                        'version': '1.18.0',
                        'location': {
                            'country_name': 'United States',
                            'city': 'San Francisco'
                        },
                        'org': 'Another Organization'
                    }
                ],
                'total': 2,
                'facets': {
                    'country': [
                        {'value': 'US', 'count': 2}
                    ]
                }
            }
            
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: mock_response
            )
            
            # Test de recherche
            result = shodan_api.search('apache', limit=2)
            
            assert result['success'] is True
            assert 'results' in result
            assert 'statistics' in result
            
            results = result['results']
            assert len(results) == 2
            
            # Vérifier le premier résultat
            apache_result = results[0]
            assert apache_result['ip'] == '192.168.1.100'
            assert apache_result['port'] == 80
            assert apache_result['product'] == 'Apache httpd'
            assert apache_result['version'] == '2.4.41'
            
            # Vérifier les statistiques
            stats = result['statistics']
            assert stats['total_results'] == 2
            assert 'country_distribution' in stats

    def test_shodan_api_rate_limiting(self, shodan_api):
        """Test de la gestion des limites de taux API Shodan"""
        with patch('requests.get') as mock_get:
            # Simuler une réponse de rate limiting
            mock_get.return_value = Mock(
                status_code=429,
                json=lambda: {'error': 'Request rate limit exceeded'},
                headers={'X-Rate-Limit-Reset': str(int(time.time()) + 60)}
            )
            
            result = shodan_api.host_lookup('8.8.8.8')
            
            assert result['success'] is False
            assert 'rate_limit' in result['error'].lower()
            assert 'retry_after' in result

    def test_shodan_api_authentication_error(self, shodan_api):
        """Test de gestion d'erreur d'authentification"""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=401,
                json=lambda: {'error': 'Invalid API key'}
            )
            
            result = shodan_api.host_lookup('8.8.8.8')
            
            assert result['success'] is False
            assert 'authentication' in result['error'].lower() or 'api key' in result['error'].lower()

    def test_shodan_bulk_host_lookup(self, shodan_api):
        """Test de lookup en masse d'hôtes"""
        hosts = ['8.8.8.8', '1.1.1.1', '208.67.222.222']
        
        with patch('requests.get') as mock_get:
            # Mock différentes réponses pour chaque hôte
            responses = [
                {'ip_str': '8.8.8.8', 'org': 'Google LLC', 'ports': [53, 443]},
                {'ip_str': '1.1.1.1', 'org': 'Cloudflare Inc.', 'ports': [53, 80, 443]},
                {'ip_str': '208.67.222.222', 'org': 'OpenDNS LLC', 'ports': [53, 443]}
            ]
            
            mock_get.side_effect = [
                Mock(status_code=200, json=lambda r=resp: r) for resp in responses
            ]
            
            result = shodan_api.bulk_host_lookup(hosts)
            
            assert result['success'] is True
            assert 'hosts' in result
            assert len(result['hosts']) == 3
            
            # Vérifier que tous les hôtes sont présents
            returned_ips = [h['ip'] for h in result['hosts']]
            for ip in hosts:
                assert ip in returned_ips


class TestCloudAPIIntegration:
    """Tests d'intégration avec les APIs Cloud"""

    @pytest.fixture
    def cloud_api(self):
        """Fixture pour l'API Cloud"""
        return CloudAPI()

    def test_aws_s3_enumeration(self, cloud_api):
        """Test d'énumération des buckets S3 AWS"""
        with patch('boto3.client') as mock_boto3:
            mock_s3_client = Mock()
            mock_s3_client.list_buckets.return_value = {
                'Buckets': [
                    {
                        'Name': 'example-bucket-1',
                        'CreationDate': '2023-01-01T00:00:00Z'
                    },
                    {
                        'Name': 'example-bucket-2',
                        'CreationDate': '2023-02-01T00:00:00Z'
                    }
                ]
            }
            
            # Mock pour les permissions de buckets
            mock_s3_client.get_bucket_acl.side_effect = [
                {
                    'Grants': [
                        {
                            'Grantee': {'Type': 'Group', 'URI': 'http://acs.amazonaws.com/groups/global/AllUsers'},
                            'Permission': 'READ'
                        }
                    ]
                },
                Exception('Access Denied')  # Bucket privé
            ]
            
            mock_boto3.return_value = mock_s3_client
            
            aws_credentials = {
                'access_key_id': 'AKIAIOSFODNN7EXAMPLE',
                'secret_access_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
                'region_name': 'us-east-1'
            }
            
            result = cloud_api.enumerate_aws_s3_buckets(aws_credentials)
            
            assert result['success'] is True
            assert 'buckets' in result
            assert len(result['buckets']) == 2
            
            # Vérifier les détails des buckets
            buckets = result['buckets']
            bucket1 = next((b for b in buckets if b['name'] == 'example-bucket-1'), None)
            assert bucket1 is not None
            assert bucket1['public_read'] is True
            
            bucket2 = next((b for b in buckets if b['name'] == 'example-bucket-2'), None)
            assert bucket2 is not None
            assert bucket2['public_read'] is False

    def test_aws_ec2_enumeration(self, cloud_api):
        """Test d'énumération des instances EC2"""
        with patch('boto3.client') as mock_boto3:
            mock_ec2_client = Mock()
            mock_ec2_client.describe_instances.return_value = {
                'Reservations': [
                    {
                        'Instances': [
                            {
                                'InstanceId': 'i-1234567890abcdef0',
                                'InstanceType': 't2.micro',
                                'State': {'Name': 'running'},
                                'PublicIpAddress': '203.0.113.12',
                                'PrivateIpAddress': '10.0.1.12',
                                'SecurityGroups': [
                                    {
                                        'GroupName': 'web-servers',
                                        'GroupId': 'sg-903004f8'
                                    }
                                ],
                                'Tags': [
                                    {'Key': 'Name', 'Value': 'Web Server 1'},
                                    {'Key': 'Environment', 'Value': 'Production'}
                                ]
                            }
                        ]
                    }
                ]
            }
            
            mock_boto3.return_value = mock_ec2_client
            
            aws_credentials = {
                'access_key_id': 'AKIAIOSFODNN7EXAMPLE',
                'secret_access_key': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
                'region_name': 'us-east-1'
            }
            
            result = cloud_api.enumerate_aws_ec2_instances(aws_credentials)
            
            assert result['success'] is True
            assert 'instances' in result
            assert len(result['instances']) == 1
            
            instance = result['instances'][0]
            assert instance['instance_id'] == 'i-1234567890abcdef0'
            assert instance['instance_type'] == 't2.micro'
            assert instance['state'] == 'running'
            assert instance['public_ip'] == '203.0.113.12'
            assert instance['private_ip'] == '10.0.1.12'

    def test_azure_resource_enumeration(self, cloud_api):
        """Test d'énumération des ressources Azure"""
        with patch('azure.identity.ClientSecretCredential'), \
             patch('azure.mgmt.resource.ResourceManagementClient') as mock_resource_client, \
             patch('azure.mgmt.storage.StorageManagementClient') as mock_storage_client:
            
            # Mock du client de ressources
            mock_resource_instance = Mock()
            mock_resource_instance.resource_groups.list.return_value = [
                Mock(name='rg-production', location='East US'),
                Mock(name='rg-development', location='West US')
            ]
            mock_resource_client.return_value = mock_resource_instance
            
            # Mock du client de stockage
            mock_storage_instance = Mock()
            mock_storage_instance.storage_accounts.list.return_value = [
                Mock(
                    name='prodstorageaccount',
                    location='East US',
                    kind='StorageV2',
                    provisioning_state='Succeeded'
                )
            ]
            mock_storage_client.return_value = mock_storage_instance
            
            azure_credentials = {
                'subscription_id': '12345678-1234-1234-1234-123456789abc',
                'tenant_id': 'abcdefgh-1234-1234-1234-abcdefghijkl',
                'client_id': 'ijklmnop-1234-1234-1234-ijklmnopqrst',
                'client_secret': 'your-client-secret'
            }
            
            result = cloud_api.enumerate_azure_resources(azure_credentials)
            
            assert result['success'] is True
            assert 'resource_groups' in result
            assert 'storage_accounts' in result
            
            assert len(result['resource_groups']) == 2
            assert len(result['storage_accounts']) == 1
            
            rg = result['resource_groups'][0]
            assert rg['name'] in ['rg-production', 'rg-development']
            
            storage = result['storage_accounts'][0]
            assert storage['name'] == 'prodstorageaccount'
            assert storage['kind'] == 'StorageV2'

    def test_gcp_project_enumeration(self, cloud_api):
        """Test d'énumération des projets GCP"""
        with patch('google.oauth2.service_account.Credentials'), \
             patch('googleapiclient.discovery.build') as mock_build:
            
            mock_service = Mock()
            mock_projects = Mock()
            mock_projects.list.return_value = Mock(
                execute=lambda: {
                    'projects': [
                        {
                            'projectId': 'my-production-project',
                            'name': 'Production Environment',
                            'lifecycleState': 'ACTIVE'
                        },
                        {
                            'projectId': 'my-development-project',
                            'name': 'Development Environment',
                            'lifecycleState': 'ACTIVE'
                        }
                    ]
                }
            )
            mock_service.projects.return_value = mock_projects
            mock_build.return_value = mock_service
            
            gcp_credentials = {
                'service_account_key': '/path/to/service-account-key.json'
            }
            
            result = cloud_api.enumerate_gcp_projects(gcp_credentials)
            
            assert result['success'] is True
            assert 'projects' in result
            assert len(result['projects']) == 2
            
            project = result['projects'][0]
            assert project['project_id'] in ['my-production-project', 'my-development-project']
            assert project['lifecycle_state'] == 'ACTIVE'


class TestAPIErrorHandlingAndRecovery:
    """Tests de gestion d'erreurs et de récupération API"""

    def test_network_timeout_handling(self):
        """Test de gestion des timeouts réseau"""
        import requests
        
        shodan_api = ShodanAPI(api_key='test_key')
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            
            result = shodan_api.host_lookup('8.8.8.8')
            
            assert result['success'] is False
            assert 'timeout' in result['error'].lower()

    def test_connection_error_handling(self):
        """Test de gestion des erreurs de connexion"""
        import requests
        
        shodan_api = ShodanAPI(api_key='test_key')
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            
            result = shodan_api.host_lookup('8.8.8.8')
            
            assert result['success'] is False
            assert 'connection' in result['error'].lower()

    def test_api_retry_mechanism(self):
        """Test du mécanisme de retry automatique"""
        import requests
        
        shodan_api = ShodanAPI(api_key='test_key', max_retries=3)
        
        with patch('requests.get') as mock_get:
            # Premier appel: timeout, deuxième: succès
            mock_get.side_effect = [
                requests.exceptions.Timeout(),
                Mock(
                    status_code=200,
                    json=lambda: {'ip_str': '8.8.8.8', 'ports': [53, 443]}
                )
            ]
            
            result = shodan_api.host_lookup('8.8.8.8')
            
            assert result['success'] is True
            assert mock_get.call_count == 2  # Un retry effectué

    def test_invalid_json_response_handling(self):
        """Test de gestion des réponses JSON invalides"""
        shodan_api = ShodanAPI(api_key='test_key')
        
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                json=Mock(side_effect=ValueError("Invalid JSON")),
                text="Invalid JSON response"
            )
            
            result = shodan_api.host_lookup('8.8.8.8')
            
            assert result['success'] is False
            assert 'json' in result['error'].lower() or 'parse' in result['error'].lower()


class TestAPIPerformanceAndCaching:
    """Tests de performance et de mise en cache API"""

    def test_api_response_caching(self):
        """Test de mise en cache des réponses API"""
        shodan_api = ShodanAPI(api_key='test_key', enable_cache=True)
        
        with patch('requests.get') as mock_get:
            mock_response = {
                'ip_str': '8.8.8.8',
                'org': 'Google LLC',
                'ports': [53, 443]
            }
            
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: mock_response
            )
            
            # Premier appel
            result1 = shodan_api.host_lookup('8.8.8.8')
            assert result1['success'] is True
            
            # Deuxième appel (doit utiliser le cache)
            result2 = shodan_api.host_lookup('8.8.8.8')
            assert result2['success'] is True
            
            # Vérifier qu'un seul appel réseau a été fait
            assert mock_get.call_count == 1
            
            # Vérifier que les résultats sont identiques
            assert result1['host_info']['ip'] == result2['host_info']['ip']

    def test_bulk_api_operations_performance(self):
        """Test de performance des opérations API en masse"""
        import time
        
        shodan_api = ShodanAPI(api_key='test_key')
        cloud_api = CloudAPI()
        
        # Test avec 50 adresses IP
        ip_addresses = [f'192.168.1.{i}' for i in range(1, 51)]
        
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: {'ip_str': '192.168.1.1', 'ports': [80, 443]}
            )
            
            start_time = time.time()
            
            result = shodan_api.bulk_host_lookup(ip_addresses, parallel=True)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            assert result['success'] is True
            assert len(result['hosts']) == 50
            
            # Les opérations en parallèle doivent être plus rapides
            # (moins de 10 secondes pour 50 lookups)
            assert execution_time < 10.0


if __name__ == "__main__":
    # Exécution des tests
    pytest.main([__file__, "-v"])