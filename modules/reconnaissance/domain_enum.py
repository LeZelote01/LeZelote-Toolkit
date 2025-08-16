"""
Pentest-USB Toolkit - Domain Enumeration Module
===============================================

Domain and subdomain discovery using multiple OSINT sources.
Integrates Amass, Subfinder, Sublist3r, and certificate transparency logs.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import subprocess
import json
import time
import requests
import dns.resolver
import ssl
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urlparse
from pathlib import Path

from ...core.utils.logging_handler import get_logger
from ...core.utils.error_handler import PentestError
from ...core.utils.network_utils import NetworkValidator


class DomainEnumerator:
    """
    Domain and subdomain enumeration module
    """
    
    def __init__(self):
        """Initialize Domain Enumerator"""
        self.logger = get_logger(__name__)
        self.validator = NetworkValidator()
        self.discovered_domains = set()
        
        # Tool paths
        self.tools = {
            'amass': self._find_tool('amass'),
            'subfinder': self._find_tool('subfinder'),
            'sublist3r': self._find_tool('sublist3r')
        }
        
        # DNS resolvers
        self.dns_resolvers = [
            '8.8.8.8', '8.8.4.4',  # Google
            '1.1.1.1', '1.0.0.1',  # Cloudflare
            '208.67.222.222', '208.67.220.220'  # OpenDNS
        ]
        
        self.logger.info("DomainEnumerator module initialized")
    
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
            f'./tools/binaries/linux/{tool_name}',
            f'./tools/python_scripts/{tool_name}.py'
        ]
        
        for path in potential_paths:
            if Path(path).exists():
                return str(Path(path).absolute())
        
        self.logger.warning(f"Tool {tool_name} not found")
        return None
    
    def enumerate_domain(self, domain: str, profile: str = "default") -> Dict[str, Any]:
        """
        Enumerate subdomains for target domain
        
        Args:
            domain: Target domain (e.g., "example.com")
            profile: Enumeration profile (quick, default, comprehensive)
            
        Returns:
            Domain enumeration results
        """
        try:
            self.logger.info(f"Starting domain enumeration: {domain} (profile: {profile})")
            
            # Validate domain
            if not self._validate_domain(domain):
                raise PentestError(f"Invalid domain: {domain}")
            
            # Clear previous results
            self.discovered_domains.clear()
            
            # Run enumeration based on profile
            results = {
                'target_domain': domain,
                'profile': profile,
                'timestamp': time.time(),
                'subdomains': set(),
                'active_subdomains': set(),
                'tool_results': {},
                'certificate_transparency': [],
                'dns_records': {},
                'summary': {}
            }
            
            # Execute enumeration tools
            if profile == "quick":
                results = self._quick_enumeration(domain, results)
            elif profile == "comprehensive":
                results = self._comprehensive_enumeration(domain, results)
            else:
                results = self._default_enumeration(domain, results)
            
            # Validate discovered subdomains
            results['active_subdomains'] = self._validate_subdomains(
                list(results['subdomains']), domain
            )
            
            # Generate DNS records for active subdomains
            results['dns_records'] = self._get_dns_records(
                list(results['active_subdomains'])
            )
            
            # Generate summary
            results['summary'] = self._generate_summary(results)
            
            # Convert sets to lists for JSON serialization
            results['subdomains'] = list(results['subdomains'])
            results['active_subdomains'] = list(results['active_subdomains'])
            
            return results
            
        except Exception as e:
            self.logger.error(f"Domain enumeration failed: {str(e)}")
            raise PentestError(f"Domain enumeration failed: {str(e)}")
    
    def _validate_domain(self, domain: str) -> bool:
        """Validate domain format"""
        try:
            # Remove protocol if present
            if domain.startswith(('http://', 'https://')):
                domain = urlparse(domain).netloc
            
            # Basic domain validation
            if not domain or '.' not in domain:
                return False
            
            # Check if domain resolves
            try:
                socket.gethostbyname(domain)
                return True
            except socket.gaierror:
                self.logger.warning(f"Domain {domain} does not resolve")
                return True  # Still allow enumeration for dormant domains
                
        except Exception:
            return False
    
    def _quick_enumeration(self, domain: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Quick enumeration using certificate transparency only"""
        try:
            # Certificate transparency logs
            ct_domains = self._certificate_transparency_search(domain)
            results['certificate_transparency'] = ct_domains
            results['subdomains'].update(ct_domains)
            
            # Basic DNS enumeration
            dns_subdomains = self._basic_dns_enumeration(domain)
            results['subdomains'].update(dns_subdomains)
            
            results['tool_results']['certificate_transparency'] = len(ct_domains)
            results['tool_results']['dns_enumeration'] = len(dns_subdomains)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Quick enumeration failed: {str(e)}")
            return results
    
    def _default_enumeration(self, domain: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Default enumeration using available tools"""
        try:
            # Certificate transparency
            ct_domains = self._certificate_transparency_search(domain)
            results['certificate_transparency'] = ct_domains
            results['subdomains'].update(ct_domains)
            
            # Subfinder enumeration
            if self.tools['subfinder']:
                subfinder_domains = self._run_subfinder(domain)
                results['subdomains'].update(subfinder_domains)
                results['tool_results']['subfinder'] = len(subfinder_domains)
            
            # DNS enumeration
            dns_subdomains = self._basic_dns_enumeration(domain)
            results['subdomains'].update(dns_subdomains)
            results['tool_results']['dns_enumeration'] = len(dns_subdomains)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Default enumeration failed: {str(e)}")
            return results
    
    def _comprehensive_enumeration(self, domain: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive enumeration using all available tools"""
        try:
            # Certificate transparency
            ct_domains = self._certificate_transparency_search(domain)
            results['certificate_transparency'] = ct_domains
            results['subdomains'].update(ct_domains)
            
            # Run all available tools
            enumeration_functions = [
                ('amass', self._run_amass),
                ('subfinder', self._run_subfinder),
                ('sublist3r', self._run_sublist3r)
            ]
            
            for tool_name, enum_func in enumeration_functions:
                if self.tools[tool_name]:
                    try:
                        tool_domains = enum_func(domain)
                        results['subdomains'].update(tool_domains)
                        results['tool_results'][tool_name] = len(tool_domains)
                    except Exception as e:
                        self.logger.error(f"{tool_name} failed: {str(e)}")
                        results['tool_results'][tool_name] = 0
            
            # Advanced DNS enumeration
            dns_subdomains = self._advanced_dns_enumeration(domain)
            results['subdomains'].update(dns_subdomains)
            results['tool_results']['dns_enumeration'] = len(dns_subdomains)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Comprehensive enumeration failed: {str(e)}")
            return results
    
    def _certificate_transparency_search(self, domain: str) -> List[str]:
        """Search certificate transparency logs for subdomains"""
        try:
            self.logger.info(f"Searching certificate transparency logs for {domain}")
            
            subdomains = set()
            
            # crt.sh API
            try:
                url = f"https://crt.sh/?q=%.{domain}&output=json"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    certificates = response.json()
                    
                    for cert in certificates:
                        name_value = cert.get('name_value', '')
                        
                        # Parse certificate names
                        for name in name_value.split('\n'):
                            name = name.strip()
                            if name.endswith(f'.{domain}') or name == domain:
                                # Remove wildcards
                                if name.startswith('*.'):
                                    name = name[2:]
                                subdomains.add(name)
            
            except Exception as e:
                self.logger.error(f"crt.sh search failed: {str(e)}")
            
            # Censys API (if available)
            try:
                self._censys_certificate_search(domain, subdomains)
            except Exception as e:
                self.logger.debug(f"Censys search failed: {str(e)}")
            
            return list(subdomains)
            
        except Exception as e:
            self.logger.error(f"Certificate transparency search failed: {str(e)}")
            return []
    
    def _censys_certificate_search(self, domain: str, subdomains: Set[str]):
        """Search Censys for certificates (placeholder for API integration)"""
        # Placeholder for Censys API integration
        # Would require API credentials
        pass
    
    def _run_amass(self, domain: str) -> List[str]:
        """Run Amass for subdomain enumeration"""
        try:
            if not self.tools['amass']:
                return []
            
            self.logger.info(f"Running Amass for {domain}")
            
            cmd = [self.tools['amass'], 'enum', '-d', domain, '-o', '/tmp/amass_results.txt']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Read results from output file
                try:
                    with open('/tmp/amass_results.txt', 'r') as f:
                        subdomains = [line.strip() for line in f if line.strip()]
                    
                    # Clean up
                    Path('/tmp/amass_results.txt').unlink(missing_ok=True)
                    
                    return subdomains
                except FileNotFoundError:
                    return []
            
            return []
            
        except subprocess.TimeoutExpired:
            self.logger.warning("Amass timeout")
            return []
        except Exception as e:
            self.logger.error(f"Amass execution failed: {str(e)}")
            return []
    
    def _run_subfinder(self, domain: str) -> List[str]:
        """Run Subfinder for subdomain enumeration"""
        try:
            if not self.tools['subfinder']:
                return []
            
            self.logger.info(f"Running Subfinder for {domain}")
            
            cmd = [self.tools['subfinder'], '-d', domain, '-silent']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                subdomains = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                return subdomains
            
            return []
            
        except subprocess.TimeoutExpired:
            self.logger.warning("Subfinder timeout")
            return []
        except Exception as e:
            self.logger.error(f"Subfinder execution failed: {str(e)}")
            return []
    
    def _run_sublist3r(self, domain: str) -> List[str]:
        """Run Sublist3r for subdomain enumeration"""
        try:
            if not self.tools['sublist3r']:
                return []
            
            self.logger.info(f"Running Sublist3r for {domain}")
            
            # Sublist3r is typically a Python script
            if self.tools['sublist3r'].endswith('.py'):
                cmd = ['python3', self.tools['sublist3r'], '-d', domain, '-o', '/tmp/sublist3r_results.txt']
            else:
                cmd = [self.tools['sublist3r'], '-d', domain, '-o', '/tmp/sublist3r_results.txt']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            
            # Read results from output file
            try:
                with open('/tmp/sublist3r_results.txt', 'r') as f:
                    subdomains = [line.strip() for line in f if line.strip()]
                
                # Clean up
                Path('/tmp/sublist3r_results.txt').unlink(missing_ok=True)
                
                return subdomains
            except FileNotFoundError:
                return []
            
        except subprocess.TimeoutExpired:
            self.logger.warning("Sublist3r timeout")
            return []
        except Exception as e:
            self.logger.error(f"Sublist3r execution failed: {str(e)}")
            return []
    
    def _basic_dns_enumeration(self, domain: str) -> List[str]:
        """Basic DNS subdomain enumeration"""
        try:
            subdomains = set()
            
            # Common subdomains wordlist
            common_subdomains = [
                'www', 'mail', 'ftp', 'admin', 'test', 'dev', 'staging', 'api',
                'app', 'web', 'server', 'ns1', 'ns2', 'mx', 'smtp', 'pop',
                'imap', 'webmail', 'secure', 'vpn', 'remote', 'portal',
                'dashboard', 'control', 'panel', 'cpanel', 'blog', 'shop'
            ]
            
            # Test common subdomains
            for subdomain in common_subdomains:
                test_domain = f"{subdomain}.{domain}"
                if self._test_dns_resolution(test_domain):
                    subdomains.add(test_domain)
            
            return list(subdomains)
            
        except Exception as e:
            self.logger.error(f"Basic DNS enumeration failed: {str(e)}")
            return []
    
    def _advanced_dns_enumeration(self, domain: str) -> List[str]:
        """Advanced DNS enumeration with larger wordlist"""
        try:
            subdomains = set()
            
            # Extended wordlist
            extended_subdomains = [
                'www', 'mail', 'ftp', 'admin', 'test', 'dev', 'staging', 'api',
                'app', 'web', 'server', 'ns1', 'ns2', 'mx', 'smtp', 'pop',
                'imap', 'webmail', 'secure', 'vpn', 'remote', 'portal',
                'dashboard', 'control', 'panel', 'cpanel', 'blog', 'shop',
                'store', 'payment', 'billing', 'support', 'help', 'docs',
                'wiki', 'forum', 'chat', 'mobile', 'beta', 'alpha',
                'demo', 'sandbox', 'qa', 'uat', 'prod', 'production'
            ]
            
            # Use ThreadPoolExecutor for parallel DNS queries
            with ThreadPoolExecutor(max_workers=10) as executor:
                future_to_subdomain = {
                    executor.submit(self._test_dns_resolution, f"{sub}.{domain}"): f"{sub}.{domain}"
                    for sub in extended_subdomains
                }
                
                for future in as_completed(future_to_subdomain):
                    test_domain = future_to_subdomain[future]
                    try:
                        if future.result():
                            subdomains.add(test_domain)
                    except Exception as e:
                        self.logger.debug(f"DNS test failed for {test_domain}: {str(e)}")
            
            return list(subdomains)
            
        except Exception as e:
            self.logger.error(f"Advanced DNS enumeration failed: {str(e)}")
            return []
    
    def _test_dns_resolution(self, domain: str) -> bool:
        """Test if domain resolves to IP address"""
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False
    
    def _validate_subdomains(self, subdomains: List[str], parent_domain: str) -> Set[str]:
        """Validate discovered subdomains are active"""
        try:
            active_subdomains = set()
            
            self.logger.info(f"Validating {len(subdomains)} discovered subdomains")
            
            # Use ThreadPoolExecutor for parallel validation
            with ThreadPoolExecutor(max_workers=15) as executor:
                future_to_subdomain = {
                    executor.submit(self._validate_single_subdomain, subdomain): subdomain
                    for subdomain in subdomains
                }
                
                for future in as_completed(future_to_subdomain):
                    subdomain = future_to_subdomain[future]
                    try:
                        if future.result():
                            active_subdomains.add(subdomain)
                    except Exception as e:
                        self.logger.debug(f"Validation failed for {subdomain}: {str(e)}")
            
            self.logger.info(f"Found {len(active_subdomains)} active subdomains")
            return active_subdomains
            
        except Exception as e:
            self.logger.error(f"Subdomain validation failed: {str(e)}")
            return set()
    
    def _validate_single_subdomain(self, subdomain: str) -> bool:
        """Validate single subdomain"""
        try:
            # DNS resolution test
            ip = socket.gethostbyname(subdomain)
            
            # HTTP connectivity test (optional, quick check)
            try:
                response = requests.head(f"http://{subdomain}", timeout=5)
                return True
            except:
                # Even if HTTP fails, DNS resolution means it's valid
                return True
                
        except socket.gaierror:
            return False
        except Exception:
            return False
    
    def _get_dns_records(self, domains: List[str]) -> Dict[str, Any]:
        """Get DNS records for domains"""
        try:
            dns_records = {}
            
            for domain in domains[:20]:  # Limit to avoid timeouts
                try:
                    records = {}
                    
                    # A records
                    try:
                        a_records = dns.resolver.resolve(domain, 'A')
                        records['A'] = [str(record) for record in a_records]
                    except:
                        pass
                    
                    # CNAME records
                    try:
                        cname_records = dns.resolver.resolve(domain, 'CNAME')
                        records['CNAME'] = [str(record) for record in cname_records]
                    except:
                        pass
                    
                    # MX records
                    try:
                        mx_records = dns.resolver.resolve(domain, 'MX')
                        records['MX'] = [str(record) for record in mx_records]
                    except:
                        pass
                    
                    if records:
                        dns_records[domain] = records
                        
                except Exception as e:
                    self.logger.debug(f"DNS record lookup failed for {domain}: {str(e)}")
            
            return dns_records
            
        except Exception as e:
            self.logger.error(f"DNS records collection failed: {str(e)}")
            return {}
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enumeration summary"""
        try:
            summary = {
                'total_subdomains_discovered': len(results['subdomains']),
                'active_subdomains': len(results['active_subdomains']),
                'certificate_transparency_results': len(results['certificate_transparency']),
                'tools_used': list(results['tool_results'].keys()),
                'dns_records_collected': len(results['dns_records'])
            }
            
            # Add tool-specific counts
            for tool, count in results['tool_results'].items():
                summary[f'{tool}_results'] = count
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Summary generation failed: {str(e)}")
            return {}
    
    def quick_enum(self, domain: str) -> Dict[str, Any]:
        """Perform quick domain enumeration"""
        return self.enumerate_domain(domain, "quick")
    
    def comprehensive_enum(self, domain: str) -> Dict[str, Any]:
        """Perform comprehensive domain enumeration"""
        return self.enumerate_domain(domain, "comprehensive")
    
    def certificate_transparency_only(self, domain: str) -> List[str]:
        """Get subdomains from certificate transparency logs only"""
        return self._certificate_transparency_search(domain)