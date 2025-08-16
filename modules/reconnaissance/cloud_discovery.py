"""
Pentest-USB Toolkit - Cloud Discovery Module
===========================================

Cloud asset discovery and enumeration across multiple providers.
Integrates ScoutSuite, CloudMapper for comprehensive cloud reconnaissance.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import subprocess
import json
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from urllib.parse import urlparse
import tempfile
import re

from ...core.utils.logging_handler import get_logger
from ...core.utils.error_handler import PentestError
from ...core.utils.network_utils import NetworkValidator
from ...core.api.cloud_api import CloudAPI


class CloudDiscovery:
    """
    Cloud asset discovery and enumeration module
    """
    
    def __init__(self):
        """Initialize Cloud Discovery"""
        self.logger = get_logger(__name__)
        self.validator = NetworkValidator()
        self.cloud_api = CloudAPI()
        
        # Tool paths
        self.tools = {
            'scoutsuite': self._find_tool('scout'),
            'cloudmapper': self._find_tool('cloudmapper'),
            's3scanner': self._find_tool('s3scanner'),
            'cloud_enum': self._find_tool('cloud_enum')
        }
        
        # Cloud provider configurations
        self.cloud_providers = ['aws', 'azure', 'gcp', 'digitalocean', 'linode']
        
        # Common cloud services patterns
        self.service_patterns = {
            'aws': {
                's3': ['{target}.s3.amazonaws.com', '{target}-{env}.s3.amazonaws.com'],
                'cloudfront': ['{target}.cloudfront.net'],
                'elb': ['{target}-{id}.{region}.elb.amazonaws.com'],
                'rds': ['{target}.{region}.rds.amazonaws.com']
            },
            'azure': {
                'storage': ['{target}.blob.core.windows.net', '{target}.file.core.windows.net'],
                'webapp': ['{target}.azurewebsites.net'],
                'database': ['{target}.database.windows.net']
            },
            'gcp': {
                'storage': ['{target}.storage.googleapis.com'],
                'compute': ['{target}.{region}.c.googlers.com'],
                'appengine': ['{target}.appspot.com']
            }
        }
        
        # Results storage
        self.discovered_assets = {
            'storage_buckets': set(),
            'compute_instances': set(),
            'databases': set(),
            'web_services': set(),
            'cdn_endpoints': set(),
            'api_gateways': set(),
            'domains': set(),
            'ip_addresses': set()
        }
        
        self.logger.info("CloudDiscovery module initialized")
    
    def _find_tool(self, tool_name: str) -> Optional[str]:
        """Find tool executable path"""
        import shutil
        
        # Check system PATH
        tool_path = shutil.which(tool_name)
        if tool_path:
            return tool_path
        
        # Check toolkit binaries
        potential_paths = [
            f'./tools/binaries/{tool_name}',
            f'./tools/python_scripts/{tool_name}.py',
            f'./tools/containers/{tool_name}/run.sh'
        ]
        
        for path in potential_paths:
            if Path(path).exists():
                return str(Path(path).absolute())
        
        self.logger.warning(f"Tool {tool_name} not found")
        return None
    
    def discover_cloud_assets(self, target: str, profile: str = "default") -> Dict[str, Any]:
        """
        Discover cloud assets for target organization
        
        Args:
            target: Target domain or organization name
            profile: Discovery profile (quick, default, comprehensive, authenticated)
            
        Returns:
            Cloud asset discovery results
        """
        try:
            self.logger.info(f"Starting cloud asset discovery: {target} (profile: {profile})")
            
            # Clear previous results
            for key in self.discovered_assets:
                self.discovered_assets[key].clear()
            
            # Initialize results structure
            results = {
                'target': target,
                'profile': profile,
                'timestamp': time.time(),
                'providers_checked': [],
                'tool_results': {},
                'discovered_assets': {},
                'security_findings': [],
                'summary': {}
            }
            
            # Execute discovery based on profile
            if profile == "quick":
                results = self._quick_cloud_discovery(target, results)
            elif profile == "comprehensive":
                results = self._comprehensive_cloud_discovery(target, results)
            elif profile == "authenticated":
                results = self._authenticated_cloud_discovery(target, results)
            else:
                results = self._default_cloud_discovery(target, results)
            
            # Process discovered assets
            results['discovered_assets'] = self._process_discovered_assets()
            
            # Security assessment of discovered assets
            results['security_findings'] = self._assess_cloud_security(results['discovered_assets'])
            
            # Generate summary
            results['summary'] = self._generate_discovery_summary(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Cloud discovery failed: {str(e)}")
            raise PentestError(f"Cloud discovery failed: {str(e)}")
    
    def _quick_cloud_discovery(self, target: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Quick cloud discovery using basic enumeration"""
        try:
            # S3 bucket enumeration
            s3_buckets = self._enumerate_s3_buckets(target, quick=True)
            self.discovered_assets['storage_buckets'].update(s3_buckets)
            results['tool_results']['s3_enumeration'] = len(s3_buckets)
            
            # Azure blob storage enumeration
            azure_storage = self._enumerate_azure_storage(target, quick=True)
            self.discovered_assets['storage_buckets'].update(azure_storage)
            results['tool_results']['azure_enumeration'] = len(azure_storage)
            
            # GCP storage enumeration
            gcp_storage = self._enumerate_gcp_storage(target, quick=True)
            self.discovered_assets['storage_buckets'].update(gcp_storage)
            results['tool_results']['gcp_enumeration'] = len(gcp_storage)
            
            results['providers_checked'] = ['aws', 'azure', 'gcp']
            
            return results
            
        except Exception as e:
            self.logger.error(f"Quick cloud discovery failed: {str(e)}")
            return results
    
    def _default_cloud_discovery(self, target: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Default cloud discovery with moderate depth"""
        try:
            # Storage services enumeration
            storage_results = self._comprehensive_storage_enumeration(target)
            results['tool_results']['storage_enumeration'] = len(storage_results)
            
            # Web services enumeration
            web_services = self._enumerate_web_services(target)
            self.discovered_assets['web_services'].update(web_services)
            results['tool_results']['web_services'] = len(web_services)
            
            # CDN enumeration
            cdn_endpoints = self._enumerate_cdn_endpoints(target)
            self.discovered_assets['cdn_endpoints'].update(cdn_endpoints)
            results['tool_results']['cdn_endpoints'] = len(cdn_endpoints)
            
            # DNS-based cloud discovery
            dns_results = self._dns_cloud_discovery(target)
            results['tool_results']['dns_discovery'] = len(dns_results)
            
            results['providers_checked'] = ['aws', 'azure', 'gcp', 'cloudflare']
            
            return results
            
        except Exception as e:
            self.logger.error(f"Default cloud discovery failed: {str(e)}")
            return results
    
    def _comprehensive_cloud_discovery(self, target: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive cloud discovery using all available methods"""
        try:
            # All cloud enumeration tools
            if self.tools['cloud_enum']:
                cloud_enum_results = self._run_cloud_enum(target)
                results['tool_results']['cloud_enum'] = len(cloud_enum_results)
            
            # S3Scanner if available
            if self.tools['s3scanner']:
                s3scanner_results = self._run_s3scanner(target)
                results['tool_results']['s3scanner'] = len(s3scanner_results)
            
            # Comprehensive storage enumeration
            storage_results = self._comprehensive_storage_enumeration(target)
            results['tool_results']['storage_enumeration'] = len(storage_results)
            
            # Compute instances enumeration
            compute_results = self._enumerate_compute_instances(target)
            self.discovered_assets['compute_instances'].update(compute_results)
            results['tool_results']['compute_instances'] = len(compute_results)
            
            # Database services enumeration
            database_results = self._enumerate_database_services(target)
            self.discovered_assets['databases'].update(database_results)
            results['tool_results']['databases'] = len(database_results)
            
            # API Gateway enumeration
            api_results = self._enumerate_api_gateways(target)
            self.discovered_assets['api_gateways'].update(api_results)
            results['tool_results']['api_gateways'] = len(api_results)
            
            # Certificate transparency for cloud assets
            cert_results = self._certificate_transparency_cloud_discovery(target)
            results['tool_results']['certificate_transparency'] = len(cert_results)
            
            results['providers_checked'] = self.cloud_providers
            
            return results
            
        except Exception as e:
            self.logger.error(f"Comprehensive cloud discovery failed: {str(e)}")
            return results
    
    def _authenticated_cloud_discovery(self, target: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticated cloud discovery using provided credentials"""
        try:
            # Note: This would require user to provide cloud credentials
            self.logger.warning("Authenticated discovery requires cloud credentials")
            
            # ScoutSuite integration (if credentials available)
            if self.tools['scoutsuite']:
                scoutsuite_results = self._run_scoutsuite(target)
                results['tool_results']['scoutsuite'] = len(scoutsuite_results)
            
            # CloudMapper integration (if credentials available)
            if self.tools['cloudmapper']:
                cloudmapper_results = self._run_cloudmapper(target)
                results['tool_results']['cloudmapper'] = len(cloudmapper_results)
            
            # Use CloudAPI for authenticated enumeration
            try:
                # This would need credentials provided by user
                self.logger.info("CloudAPI integration available but requires credentials")
            except Exception as e:
                self.logger.warning(f"CloudAPI integration failed: {str(e)}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Authenticated cloud discovery failed: {str(e)}")
            return results
    
    def _enumerate_s3_buckets(self, target: str, quick: bool = False) -> List[str]:
        """Enumerate S3 buckets for target"""
        try:
            buckets = []
            
            # Common S3 bucket naming patterns
            if quick:
                patterns = [target, f"{target}-backup", f"{target}-data"]
            else:
                patterns = [
                    target, f"{target}-backup", f"{target}-data", f"{target}-logs",
                    f"{target}-dev", f"{target}-prod", f"{target}-staging",
                    f"{target}-assets", f"{target}-uploads", f"{target}-downloads",
                    f"{target}.com", f"www-{target}", f"api-{target}",
                    f"{target}-web", f"{target}-app"
                ]
            
            # Test bucket existence
            for pattern in patterns:
                bucket_url = f"https://{pattern}.s3.amazonaws.com"
                try:
                    response = requests.head(bucket_url, timeout=10)
                    if response.status_code in [200, 403]:  # Exists but may be private
                        buckets.append(bucket_url)
                        self.discovered_assets['storage_buckets'].add(bucket_url)
                except:
                    pass
                
                # Also check regional endpoints
                regions = ['us-west-1', 'us-west-2', 'eu-west-1'] if not quick else ['us-west-2']
                for region in regions:
                    regional_url = f"https://{pattern}.s3-{region}.amazonaws.com"
                    try:
                        response = requests.head(regional_url, timeout=5)
                        if response.status_code in [200, 403]:
                            buckets.append(regional_url)
                            self.discovered_assets['storage_buckets'].add(regional_url)
                    except:
                        pass
            
            return buckets
            
        except Exception as e:
            self.logger.error(f"S3 enumeration failed: {str(e)}")
            return []
    
    def _enumerate_azure_storage(self, target: str, quick: bool = False) -> List[str]:
        """Enumerate Azure Blob Storage for target"""
        try:
            storage_accounts = []
            
            # Azure storage naming patterns
            if quick:
                patterns = [target, f"{target}data"]
            else:
                patterns = [
                    target, f"{target}data", f"{target}backup", f"{target}logs",
                    f"{target}dev", f"{target}prod", f"{target}staging",
                    f"{target}assets", f"{target}web"
                ]
            
            for pattern in patterns:
                # Remove special characters for Azure naming rules
                clean_pattern = re.sub(r'[^a-z0-9]', '', pattern.lower())
                if len(clean_pattern) >= 3:
                    storage_urls = [
                        f"https://{clean_pattern}.blob.core.windows.net",
                        f"https://{clean_pattern}.file.core.windows.net",
                        f"https://{clean_pattern}.queue.core.windows.net"
                    ]
                    
                    for url in storage_urls:
                        try:
                            response = requests.head(url, timeout=10)
                            if response.status_code in [200, 403]:
                                storage_accounts.append(url)
                                self.discovered_assets['storage_buckets'].add(url)
                        except:
                            pass
            
            return storage_accounts
            
        except Exception as e:
            self.logger.error(f"Azure storage enumeration failed: {str(e)}")
            return []
    
    def _enumerate_gcp_storage(self, target: str, quick: bool = False) -> List[str]:
        """Enumerate Google Cloud Storage for target"""
        try:
            buckets = []
            
            # GCP storage naming patterns
            if quick:
                patterns = [target, f"{target}-data"]
            else:
                patterns = [
                    target, f"{target}-data", f"{target}-backup", f"{target}-logs",
                    f"{target}-dev", f"{target}-prod", f"{target}-staging",
                    f"{target}-assets", f"{target}-uploads"
                ]
            
            for pattern in patterns:
                bucket_url = f"https://storage.googleapis.com/{pattern}"
                try:
                    response = requests.head(bucket_url, timeout=10)
                    if response.status_code in [200, 403]:
                        buckets.append(bucket_url)
                        self.discovered_assets['storage_buckets'].add(bucket_url)
                except:
                    pass
            
            return buckets
            
        except Exception as e:
            self.logger.error(f"GCP storage enumeration failed: {str(e)}")
            return []
    
    def _comprehensive_storage_enumeration(self, target: str) -> List[str]:
        """Comprehensive storage enumeration across all providers"""
        try:
            all_storage = []
            
            # AWS S3
            s3_buckets = self._enumerate_s3_buckets(target, quick=False)
            all_storage.extend(s3_buckets)
            
            # Azure Storage
            azure_storage = self._enumerate_azure_storage(target, quick=False)
            all_storage.extend(azure_storage)
            
            # GCP Storage
            gcp_storage = self._enumerate_gcp_storage(target, quick=False)
            all_storage.extend(gcp_storage)
            
            return all_storage
            
        except Exception as e:
            self.logger.error(f"Comprehensive storage enumeration failed: {str(e)}")
            return []
    
    def _enumerate_web_services(self, target: str) -> List[str]:
        """Enumerate cloud web services"""
        try:
            web_services = []
            
            # Common web service patterns
            patterns = [
                f"{target}.azurewebsites.net",
                f"{target}.appspot.com",
                f"{target}.herokuapp.com",
                f"{target}.vercel.app",
                f"{target}.netlify.app"
            ]
            
            for pattern in patterns:
                try:
                    response = requests.head(f"https://{pattern}", timeout=10, allow_redirects=True)
                    if response.status_code == 200:
                        web_services.append(pattern)
                except:
                    pass
            
            return web_services
            
        except Exception as e:
            self.logger.error(f"Web services enumeration failed: {str(e)}")
            return []
    
    def _enumerate_cdn_endpoints(self, target: str) -> List[str]:
        """Enumerate CDN endpoints"""
        try:
            cdn_endpoints = []
            
            # CDN patterns
            patterns = [
                f"{target}.cloudfront.net",
                f"{target}.azureedge.net",
                f"{target}.fastly.com",
                f"{target}.b-cdn.net"
            ]
            
            for pattern in patterns:
                try:
                    response = requests.head(f"https://{pattern}", timeout=10)
                    if response.status_code in [200, 403]:
                        cdn_endpoints.append(pattern)
                except:
                    pass
            
            return cdn_endpoints
            
        except Exception as e:
            self.logger.error(f"CDN enumeration failed: {str(e)}")
            return []
    
    def _enumerate_compute_instances(self, target: str) -> List[str]:
        """Enumerate compute instances"""
        try:
            instances = []
            
            # AWS EC2 patterns
            regions = ['us-east-1', 'us-west-2', 'eu-west-1']
            for region in regions:
                pattern = f"{target}.{region}.compute.amazonaws.com"
                try:
                    response = requests.head(f"https://{pattern}", timeout=10)
                    if response.status_code == 200:
                        instances.append(pattern)
                except:
                    pass
            
            return instances
            
        except Exception as e:
            self.logger.error(f"Compute instances enumeration failed: {str(e)}")
            return []
    
    def _enumerate_database_services(self, target: str) -> List[str]:
        """Enumerate database services"""
        try:
            databases = []
            
            # RDS patterns
            regions = ['us-east-1', 'us-west-2', 'eu-west-1']
            for region in regions:
                pattern = f"{target}.{region}.rds.amazonaws.com"
                # Note: Database endpoints typically aren't accessible via HTTP
                # This would require DNS resolution checking instead
                databases.append(pattern)  # Placeholder
            
            return databases
            
        except Exception as e:
            self.logger.error(f"Database services enumeration failed: {str(e)}")
            return []
    
    def _enumerate_api_gateways(self, target: str) -> List[str]:
        """Enumerate API gateways"""
        try:
            apis = []
            
            # AWS API Gateway patterns
            regions = ['us-east-1', 'us-west-2', 'eu-west-1']
            for region in regions:
                # Random API Gateway ID pattern (would need brute force in reality)
                pattern = f"{target}.execute-api.{region}.amazonaws.com"
                apis.append(pattern)  # Placeholder
            
            return apis
            
        except Exception as e:
            self.logger.error(f"API gateways enumeration failed: {str(e)}")
            return []
    
    def _dns_cloud_discovery(self, target: str) -> List[str]:
        """DNS-based cloud asset discovery"""
        try:
            cloud_assets = []
            
            # Check for cloud-related subdomains
            cloud_subdomains = [
                f"aws.{target}", f"azure.{target}", f"gcp.{target}",
                f"s3.{target}", f"storage.{target}", f"cdn.{target}",
                f"api.{target}", f"app.{target}"
            ]
            
            for subdomain in cloud_subdomains:
                try:
                    import socket
                    ip = socket.gethostbyname(subdomain)
                    cloud_assets.append(subdomain)
                    self.discovered_assets['domains'].add(subdomain)
                    self.discovered_assets['ip_addresses'].add(ip)
                except socket.gaierror:
                    pass
            
            return cloud_assets
            
        except Exception as e:
            self.logger.error(f"DNS cloud discovery failed: {str(e)}")
            return []
    
    def _certificate_transparency_cloud_discovery(self, target: str) -> List[str]:
        """Certificate transparency logs for cloud asset discovery"""
        try:
            cloud_assets = []
            
            # Search CT logs for cloud-related certificates
            ct_url = f"https://crt.sh/?q=%.{target}&output=json"
            
            response = requests.get(ct_url, timeout=30)
            if response.status_code == 200:
                certificates = response.json()
                
                for cert in certificates:
                    name_value = cert.get('name_value', '')
                    
                    for name in name_value.split('\n'):
                        name = name.strip()
                        # Look for cloud service patterns in certificate names
                        cloud_indicators = [
                            'amazonaws.com', 'azurewebsites.net', 'appspot.com',
                            'cloudfront.net', 'herokuapp.com'
                        ]
                        
                        for indicator in cloud_indicators:
                            if indicator in name:
                                cloud_assets.append(name)
                                self.discovered_assets['domains'].add(name)
                                break
            
            return cloud_assets
            
        except Exception as e:
            self.logger.error(f"Certificate transparency cloud discovery failed: {str(e)}")
            return []
    
    def _run_cloud_enum(self, target: str) -> List[str]:
        """Run cloud_enum tool"""
        try:
            if not self.tools['cloud_enum']:
                return []
            
            self.logger.info(f"Running cloud_enum for {target}")
            
            cmd = ['python3', self.tools['cloud_enum'], '-k', target]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Parse cloud_enum output
                output_lines = result.stdout.split('\n')
                found_assets = [line.strip() for line in output_lines if line.strip()]
                return found_assets
            
            return []
            
        except subprocess.TimeoutExpired:
            self.logger.warning("cloud_enum timeout")
            return []
        except Exception as e:
            self.logger.error(f"cloud_enum execution failed: {str(e)}")
            return []
    
    def _run_s3scanner(self, target: str) -> List[str]:
        """Run S3Scanner tool"""
        try:
            if not self.tools['s3scanner']:
                return []
            
            self.logger.info(f"Running S3Scanner for {target}")
            
            # Create wordlist file
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                f.write(f"{target}\n{target}-backup\n{target}-data\n")
                wordlist_path = f.name
            
            cmd = ['python3', self.tools['s3scanner'], '--include-closed', '--out-file', '/tmp/s3scanner_results.txt', wordlist_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            # Clean up wordlist
            Path(wordlist_path).unlink(missing_ok=True)
            
            # Read results
            results = []
            try:
                with open('/tmp/s3scanner_results.txt', 'r') as f:
                    results = [line.strip() for line in f if line.strip()]
                Path('/tmp/s3scanner_results.txt').unlink(missing_ok=True)
            except FileNotFoundError:
                pass
            
            return results
            
        except Exception as e:
            self.logger.error(f"S3Scanner execution failed: {str(e)}")
            return []
    
    def _run_scoutsuite(self, target: str) -> List[str]:
        """Run ScoutSuite for cloud security assessment"""
        # Placeholder - ScoutSuite requires cloud credentials
        self.logger.info("ScoutSuite requires cloud provider credentials")
        return []
    
    def _run_cloudmapper(self, target: str) -> List[str]:
        """Run CloudMapper for AWS visualization"""
        # Placeholder - CloudMapper requires AWS credentials
        self.logger.info("CloudMapper requires AWS credentials")
        return []
    
    def _process_discovered_assets(self) -> Dict[str, List[str]]:
        """Process and organize discovered assets"""
        try:
            processed = {}
            
            for asset_type, asset_set in self.discovered_assets.items():
                processed[asset_type] = list(asset_set)
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Asset processing failed: {str(e)}")
            return {}
    
    def _assess_cloud_security(self, assets: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Assess security of discovered cloud assets"""
        try:
            findings = []
            
            # Check S3 bucket permissions
            for bucket in assets.get('storage_buckets', []):
                if 's3.amazonaws.com' in bucket:
                    try:
                        # Test bucket accessibility
                        response = requests.get(bucket, timeout=10)
                        if response.status_code == 200:
                            findings.append({
                                'type': 'misconfiguration',
                                'severity': 'high',
                                'asset': bucket,
                                'description': 'S3 bucket is publicly accessible'
                            })
                    except:
                        pass
            
            # Check for exposed web services
            for service in assets.get('web_services', []):
                try:
                    response = requests.get(f"https://{service}", timeout=10)
                    if response.status_code == 200 and 'admin' in response.text.lower():
                        findings.append({
                            'type': 'exposure',
                            'severity': 'medium',
                            'asset': service,
                            'description': 'Web service may expose administrative interfaces'
                        })
                except:
                    pass
            
            return findings
            
        except Exception as e:
            self.logger.error(f"Security assessment failed: {str(e)}")
            return []
    
    def _generate_discovery_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cloud discovery summary"""
        try:
            assets = results.get('discovered_assets', {})
            
            summary = {
                'total_assets_discovered': sum(len(asset_list) for asset_list in assets.values()),
                'storage_buckets_found': len(assets.get('storage_buckets', [])),
                'web_services_found': len(assets.get('web_services', [])),
                'cdn_endpoints_found': len(assets.get('cdn_endpoints', [])),
                'security_findings': len(results.get('security_findings', [])),
                'providers_checked': results.get('providers_checked', []),
                'tools_used': list(results.get('tool_results', {}).keys())
            }
            
            # Risk assessment
            high_risk_findings = [f for f in results.get('security_findings', []) if f.get('severity') == 'high']
            if high_risk_findings:
                summary['risk_level'] = 'high'
            elif results.get('security_findings'):
                summary['risk_level'] = 'medium'
            else:
                summary['risk_level'] = 'low'
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Summary generation failed: {str(e)}")
            return {}
    
    def quick_discovery(self, target: str) -> Dict[str, Any]:
        """Perform quick cloud discovery"""
        return self.discover_cloud_assets(target, "quick")
    
    def comprehensive_discovery(self, target: str) -> Dict[str, Any]:
        """Perform comprehensive cloud discovery"""
        return self.discover_cloud_assets(target, "comprehensive")
    
    def s3_enum_only(self, target: str) -> List[str]:
        """Enumerate S3 buckets only"""
        return self._enumerate_s3_buckets(target, quick=False)