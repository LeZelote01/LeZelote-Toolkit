"""
Pentest-USB Toolkit - Shodan API Interface
==========================================

Python interface to Shodan for internet-wide asset discovery.
Integrates Shodan with the Pentest-USB Toolkit workflow.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
from ipaddress import ip_address, ip_network

from ..utils.logging_handler import get_logger
from ..utils.error_handler import PentestError
from ..utils.network_utils import NetworkValidator


class ShodanAPI:
    """
    Shodan API interface for internet asset discovery
    """
    
    def __init__(self, api_key: str):
        """Initialize Shodan API"""
        self.logger = get_logger(__name__)
        self.api_key = api_key
        self.base_url = "https://api.shodan.io"
        self.session = requests.Session()
        self.validator = NetworkValidator()
        
        # Set default timeout
        self.session.timeout = 30
        
        # Verify API key
        self._verify_api_key()
        
        self.logger.info("ShodanAPI initialized successfully")
    
    def _verify_api_key(self):
        """Verify Shodan API key"""
        try:
            response = self._make_request('/api-info')
            if not response.get('scan_credits'):
                self.logger.warning("Limited Shodan API access - no scan credits")
        except Exception as e:
            raise PentestError(f"Invalid Shodan API key: {str(e)}")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request to Shodan"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            request_params = {'key': self.api_key}
            if params:
                request_params.update(params)
            
            response = self.session.get(url, params=request_params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response:
                error_msg = e.response.json().get('error', str(e))
            else:
                error_msg = str(e)
            raise PentestError(f"Shodan API request failed: {error_msg}")
        except json.JSONDecodeError as e:
            raise PentestError(f"Failed to parse Shodan response: {str(e)}")
    
    def search(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """
        Search Shodan database
        
        Args:
            query: Search query (e.g., "apache", "port:80", "org:Microsoft")
            limit: Maximum number of results
            
        Returns:
            Search results
        """
        try:
            self.logger.info(f"Searching Shodan: {query}")
            
            params = {
                'query': query,
                'limit': min(limit, 1000)  # Shodan API limit
            }
            
            response = self._make_request('/shodan/host/search', params)
            
            # Process results
            results = {
                'query': query,
                'total': response.get('total', 0),
                'matches': response.get('matches', []),
                'facets': response.get('facets', {}),
                'processed_results': []
            }
            
            # Process each match
            for match in response.get('matches', []):
                processed_match = self._process_host_data(match)
                results['processed_results'].append(processed_match)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Shodan search error: {str(e)}")
            raise PentestError(f"Shodan search failed: {str(e)}")
    
    def host_info(self, ip: str) -> Dict[str, Any]:
        """
        Get detailed information about a host
        
        Args:
            ip: IP address
            
        Returns:
            Host information
        """
        try:
            # Validate IP address
            ip_address(ip)  # This will raise ValueError if invalid
            
            self.logger.info(f"Getting Shodan host info: {ip}")
            
            response = self._make_request(f'/shodan/host/{ip}')
            
            return self._process_host_data(response)
            
        except ValueError:
            raise PentestError(f"Invalid IP address: {ip}")
        except Exception as e:
            self.logger.error(f"Host info error: {str(e)}")
            raise PentestError(f"Failed to get host info: {str(e)}")
    
    def _process_host_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and normalize host data"""
        processed = {
            'ip': data.get('ip_str'),
            'hostnames': data.get('hostnames', []),
            'domains': data.get('domains', []),
            'country': data.get('location', {}).get('country_name'),
            'city': data.get('location', {}).get('city'),
            'organization': data.get('org'),
            'isp': data.get('isp'),
            'ports': [],
            'services': [],
            'vulnerabilities': [],
            'last_update': data.get('last_update')
        }
        
        # Extract port and service information
        for item in data.get('data', []):
            port_info = {
                'port': item.get('port'),
                'protocol': item.get('transport'),
                'service': item.get('product'),
                'version': item.get('version'),
                'banner': item.get('data', '').strip()[:200]  # Limit banner length
            }
            processed['ports'].append(port_info)
            
            # Extract service details
            if item.get('product'):
                service_info = {
                    'name': item.get('product'),
                    'version': item.get('version'),
                    'port': item.get('port'),
                    'protocol': item.get('transport')
                }
                processed['services'].append(service_info)
            
            # Extract vulnerabilities
            for vuln in item.get('vulns', []):
                processed['vulnerabilities'].append(vuln)
        
        return processed
    
    def search_by_organization(self, org_name: str) -> Dict[str, Any]:
        """Search by organization name"""
        query = f'org:"{org_name}"'
        return self.search(query)
    
    def search_by_port(self, port: int) -> Dict[str, Any]:
        """Search by port number"""
        query = f'port:{port}'
        return self.search(query)
    
    def search_by_service(self, service: str) -> Dict[str, Any]:
        """Search by service name"""
        query = f'product:"{service}"'
        return self.search(query)
    
    def search_by_vulnerability(self, cve: str) -> Dict[str, Any]:
        """Search by CVE number"""
        query = f'vuln:{cve}'
        return self.search(query)
    
    def search_network_range(self, network: str) -> Dict[str, Any]:
        """
        Search within network range
        
        Args:
            network: Network range (e.g., "192.168.1.0/24")
            
        Returns:
            Search results for the network range
        """
        try:
            # Validate network range
            ip_network(network)
            
            query = f'net:{network}'
            return self.search(query)
            
        except ValueError:
            raise PentestError(f"Invalid network range: {network}")
    
    def get_services_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate services summary from search results"""
        summary = {
            'total_hosts': len(results.get('processed_results', [])),
            'countries': {},
            'organizations': {},
            'services': {},
            'ports': {},
            'vulnerabilities': set()
        }
        
        for host in results.get('processed_results', []):
            # Count countries
            country = host.get('country')
            if country:
                summary['countries'][country] = summary['countries'].get(country, 0) + 1
            
            # Count organizations
            org = host.get('organization')
            if org:
                summary['organizations'][org] = summary['organizations'].get(org, 0) + 1
            
            # Count services and ports
            for service in host.get('services', []):
                service_name = service.get('name')
                port = service.get('port')
                
                if service_name:
                    summary['services'][service_name] = summary['services'].get(service_name, 0) + 1
                
                if port:
                    summary['ports'][port] = summary['ports'].get(port, 0) + 1
            
            # Collect vulnerabilities
            for vuln in host.get('vulnerabilities', []):
                summary['vulnerabilities'].add(vuln)
        
        # Convert set to list for JSON serialization
        summary['vulnerabilities'] = list(summary['vulnerabilities'])
        
        return summary
    
    def domain_info(self, domain: str) -> Dict[str, Any]:
        """
        Get domain information
        
        Args:
            domain: Domain name
            
        Returns:
            Domain information from Shodan
        """
        try:
            self.logger.info(f"Getting domain info: {domain}")
            
            response = self._make_request(f'/dns/domain/{domain}')
            
            return {
                'domain': domain,
                'subdomains': response.get('subdomains', []),
                'data': response.get('data', []),
                'more': response.get('more', False)
            }
            
        except Exception as e:
            self.logger.error(f"Domain info error: {str(e)}")
            raise PentestError(f"Failed to get domain info: {str(e)}")
    
    def get_my_ip(self) -> str:
        """Get current public IP address"""
        try:
            response = self._make_request('/tools/myip')
            return response
        except Exception as e:
            self.logger.error(f"Get IP error: {str(e)}")
            return None
    
    def comprehensive_search(self, target: str) -> Dict[str, Any]:
        """
        Perform comprehensive Shodan search
        
        Args:
            target: Target (can be IP, domain, or organization)
            
        Returns:
            Comprehensive search results
        """
        try:
            self.logger.info(f"Starting comprehensive Shodan search: {target}")
            
            results = {
                'target': target,
                'timestamp': time.time(),
                'searches': {},
                'summary': {}
            }
            
            # Determine target type and search accordingly
            try:
                # Try as IP address
                ip_address(target)
                results['searches']['host_info'] = self.host_info(target)
                results['searches']['network_search'] = self.search(f'ip:{target}')
            except ValueError:
                # Try as domain
                if '.' in target and not target.replace('.', '').isdigit():
                    results['searches']['domain_info'] = self.domain_info(target)
                    results['searches']['domain_search'] = self.search(f'hostname:{target}')
                else:
                    # Treat as organization
                    results['searches']['org_search'] = self.search_by_organization(target)
            
            # Generate summary
            all_results = []
            for search_type, search_data in results['searches'].items():
                if isinstance(search_data, dict) and 'processed_results' in search_data:
                    all_results.extend(search_data['processed_results'])
                elif isinstance(search_data, dict) and 'ip' in search_data:
                    all_results.append(search_data)
            
            if all_results:
                results['summary'] = self.get_services_summary({'processed_results': all_results})
            
            return results
            
        except Exception as e:
            self.logger.error(f"Comprehensive search error: {str(e)}")
            raise PentestError(f"Comprehensive search failed: {str(e)}")