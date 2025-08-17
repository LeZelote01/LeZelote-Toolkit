"""
Pentest-USB Toolkit - OSINT Gathering Module
===========================================

Open Source Intelligence gathering using multiple tools and sources.
Integrates theHarvester, SpiderFoot, Recon-ng for comprehensive OSINT collection.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import subprocess
import json
import time
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from urllib.parse import urlparse, urljoin
import tempfile
import os

from ...core.utils.logging_handler import get_logger
from ...core.utils.error_handler import PentestError
from ...core.utils.network_utils import NetworkValidator


class OSINTGatherer:
    """
    Open Source Intelligence gathering module
    """
    
    def __init__(self):
        """Initialize OSINT Gatherer"""
        self.logger = get_logger(__name__)
        self.validator = NetworkValidator()
        
        # Tool paths
        self.tools = {
            'theharvester': self._find_tool('theHarvester'),
            'spiderfoot': self._find_tool('spiderfoot'),
            'recon-ng': self._find_tool('recon-ng')
        }
        
        # OSINT sources configuration
        self.search_engines = [
            'google', 'bing', 'yahoo', 'duckduckgo',
            'linkedin', 'twitter', 'instagram'
        ]
        
        self.social_platforms = [
            'linkedin', 'twitter', 'facebook', 'instagram',
            'github', 'reddit', 'youtube'
        ]
        
        # Results storage
        self.collected_data = {
            'emails': set(),
            'domains': set(),
            'subdomains': set(),
            'urls': set(),
            'people': set(),
            'usernames': set(),
            'phone_numbers': set(),
            'social_profiles': set(),
            'documents': set(),
            'ip_addresses': set()
        }
        
        self.logger.info("OSINTGatherer module initialized")
    
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
    
    def gather_osint(self, target: str, profile: str = "default") -> Dict[str, Any]:
        """
        Gather OSINT information for target
        
        Args:
            target: Target domain, company, or person name
            profile: Gathering profile (quick, default, comprehensive, social)
            
        Returns:
            OSINT gathering results
        """
        try:
            self.logger.info(f"Starting OSINT gathering: {target} (profile: {profile})")
            
            # Clear previous results
            for key in self.collected_data:
                self.collected_data[key].clear()
            
            # Determine target type
            target_type = self._determine_target_type(target)
            
            # Initialize results structure
            results = {
                'target': target,
                'target_type': target_type,
                'profile': profile,
                'timestamp': time.time(),
                'tool_results': {},
                'source_breakdown': {},
                'collected_data': {},
                'summary': {}
            }
            
            # Execute gathering based on profile
            if profile == "quick":
                results = self._quick_osint_gathering(target, target_type, results)
            elif profile == "comprehensive":
                results = self._comprehensive_osint_gathering(target, target_type, results)
            elif profile == "social":
                results = self._social_osint_gathering(target, target_type, results)
            else:
                results = self._default_osint_gathering(target, target_type, results)
            
            # Process and deduplicate collected data
            results['collected_data'] = self._process_collected_data()
            
            # Generate summary
            results['summary'] = self._generate_osint_summary(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"OSINT gathering failed: {str(e)}")
            raise PentestError(f"OSINT gathering failed: {str(e)}")
    
    def _determine_target_type(self, target: str) -> str:
        """Determine if target is domain, company, or person"""
        if '.' in target and not ' ' in target:
            # Likely a domain
            return 'domain'
        elif '@' in target:
            # Email address
            return 'email'
        elif len(target.split()) > 1:
            # Multiple words, likely person or company name
            return 'person_or_company'
        else:
            # Single word, could be username or company
            return 'username_or_company'
    
    def _quick_osint_gathering(self, target: str, target_type: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Quick OSINT gathering using basic methods"""
        try:
            # Search engines queries
            search_results = self._search_engine_osint(target, engines=['google'])
            results['source_breakdown']['search_engines'] = len(search_results)
            
            # Basic email harvesting if it's a domain
            if target_type == 'domain':
                emails = self._basic_email_harvest(target)
                self.collected_data['emails'].update(emails)
                results['source_breakdown']['email_harvest'] = len(emails)
            
            # Social media quick search
            social_results = self._quick_social_search(target)
            results['source_breakdown']['social_media'] = len(social_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Quick OSINT gathering failed: {str(e)}")
            return results
    
    def _default_osint_gathering(self, target: str, target_type: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Default OSINT gathering using available tools"""
        try:
            # theHarvester if available
            if self.tools['theharvester']:
                harvester_results = self._run_theharvester(target, target_type)
                results['tool_results']['theharvester'] = len(harvester_results.get('emails', []))
            
            # Search engines
            search_results = self._search_engine_osint(target)
            results['source_breakdown']['search_engines'] = len(search_results)
            
            # Social media search
            social_results = self._social_media_osint(target)
            results['source_breakdown']['social_media'] = len(social_results)
            
            # Document metadata search
            document_results = self._document_metadata_search(target)
            results['source_breakdown']['documents'] = len(document_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Default OSINT gathering failed: {str(e)}")
            return results
    
    def _comprehensive_osint_gathering(self, target: str, target_type: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive OSINT gathering using all available tools"""
        try:
            # All available tools
            tool_functions = [
                ('theharvester', self._run_theharvester),
                ('spiderfoot', self._run_spiderfoot),
                ('recon-ng', self._run_recon_ng)
            ]
            
            for tool_name, tool_func in tool_functions:
                if self.tools[tool_name]:
                    try:
                        tool_results = tool_func(target, target_type)
                        results['tool_results'][tool_name] = len(tool_results.get('emails', []))
                    except Exception as e:
                        self.logger.error(f"{tool_name} failed: {str(e)}")
                        results['tool_results'][tool_name] = 0
            
            # Comprehensive search engines
            search_results = self._comprehensive_search_engine_osint(target)
            results['source_breakdown']['search_engines'] = len(search_results)
            
            # Deep social media analysis
            social_results = self._comprehensive_social_media_osint(target)
            results['source_breakdown']['social_media'] = len(social_results)
            
            # Code repositories search
            code_results = self._code_repository_search(target)
            results['source_breakdown']['code_repositories'] = len(code_results)
            
            # Breach data search (public sources only)
            breach_results = self._breach_data_search(target)
            results['source_breakdown']['breach_data'] = len(breach_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Comprehensive OSINT gathering failed: {str(e)}")
            return results
    
    def _social_osint_gathering(self, target: str, target_type: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Social media focused OSINT gathering"""
        try:
            # Deep social media search
            social_results = self._comprehensive_social_media_osint(target)
            results['source_breakdown']['social_media'] = len(social_results)
            
            # Username enumeration across platforms
            username_results = self._username_enumeration(target)
            results['source_breakdown']['username_enumeration'] = len(username_results)
            
            # Professional networks
            professional_results = self._professional_networks_search(target)
            results['source_breakdown']['professional_networks'] = len(professional_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Social OSINT gathering failed: {str(e)}")
            return results
    
    def _run_theharvester(self, target: str, target_type: str) -> Dict[str, Any]:
        """Run theHarvester for email and subdomain harvesting"""
        try:
            if not self.tools['theharvester']:
                return {}
            
            self.logger.info(f"Running theHarvester for {target}")
            
            results = {'emails': [], 'domains': [], 'hosts': []}
            
            # Run theHarvester with multiple sources
            sources = ['google', 'bing', 'linkedin', 'twitter']
            
            for source in sources:
                try:
                    cmd = [
                        'python3', self.tools['theharvester'],
                        '-d', target,
                        '-l', '100',
                        '-b', source
                    ]
                    
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    
                    if result.returncode == 0:
                        # Parse theHarvester output
                        output = result.stdout
                        
                        # Extract emails
                        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', output)
                        results['emails'].extend(emails)
                        self.collected_data['emails'].update(emails)
                        
                        # Extract hosts/subdomains
                        hosts = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', output)
                        results['hosts'].extend(hosts)
                        self.collected_data['subdomains'].update(hosts)
                        
                except subprocess.TimeoutExpired:
                    self.logger.warning(f"theHarvester timeout for source {source}")
                except Exception as e:
                    self.logger.error(f"theHarvester failed for source {source}: {str(e)}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"theHarvester execution failed: {str(e)}")
            return {}
    
    def _run_spiderfoot(self, target: str, target_type: str) -> Dict[str, Any]:
        """Run SpiderFoot for comprehensive OSINT"""
        try:
            if not self.tools['spiderfoot']:
                return {}
            
            self.logger.info(f"Running SpiderFoot for {target}")
            
            # SpiderFoot typically requires a web interface
            # This is a placeholder for command-line integration
            # In practice, would need to use SpiderFoot API or CLI if available
            
            return {'placeholder': 'SpiderFoot integration needed'}
            
        except Exception as e:
            self.logger.error(f"SpiderFoot execution failed: {str(e)}")
            return {}
    
    def _run_recon_ng(self, target: str, target_type: str) -> Dict[str, Any]:
        """Run Recon-ng for OSINT gathering"""
        try:
            if not self.tools['recon-ng']:
                return {}
            
            self.logger.info(f"Running Recon-ng for {target}")
            
            # Recon-ng integration would require module setup
            # This is a placeholder for proper integration
            
            return {'placeholder': 'Recon-ng integration needed'}
            
        except Exception as e:
            self.logger.error(f"Recon-ng execution failed: {str(e)}")
            return {}
    
    def _search_engine_osint(self, target: str, engines: List[str] = None) -> List[Dict[str, Any]]:
        """Perform search engine OSINT"""
        try:
            if engines is None:
                engines = ['google']
            
            results = []
            
            # Search queries for different types of information
            queries = [
                f'"{target}" email',
                f'"{target}" contact',
                f'"{target}" phone',
                f'"{target}" address',
                f'site:{target}' if '.' in target else f'"{target}" company'
            ]
            
            for query in queries:
                # Placeholder for search engine API integration
                # In practice, would use Google Custom Search API, Bing API, etc.
                self.logger.debug(f"Search query: {query}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Search engine OSINT failed: {str(e)}")
            return []
    
    def _comprehensive_search_engine_osint(self, target: str) -> List[Dict[str, Any]]:
        """Comprehensive search engine OSINT with multiple engines"""
        results = []
        
        for engine in self.search_engines:
            try:
                engine_results = self._search_engine_osint(target, [engine])
                results.extend(engine_results)
            except Exception as e:
                self.logger.debug(f"Search engine {engine} failed: {str(e)}")
        
        return results
    
    def _basic_email_harvest(self, domain: str) -> Set[str]:
        """Basic email harvesting for domain"""
        try:
            emails = set()
            
            # Common email patterns
            common_emails = [
                f'info@{domain}', f'admin@{domain}', f'support@{domain}',
                f'contact@{domain}', f'sales@{domain}', f'office@{domain}',
                f'hello@{domain}', f'team@{domain}', f'help@{domain}'
            ]
            
            # Test if emails are mentioned in robots.txt, sitemap, etc.
            try:
                response = requests.get(f'http://{domain}/robots.txt', timeout=10)
                if response.status_code == 200:
                    found_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response.text)
                    emails.update(found_emails)
            except:
                pass
            
            return emails
            
        except Exception as e:
            self.logger.error(f"Email harvesting failed: {str(e)}")
            return set()
    
    def _quick_social_search(self, target: str) -> List[Dict[str, Any]]:
        """Quick social media search"""
        try:
            results = []
            
            # Check common social media platforms
            platforms = {
                'linkedin': f'https://www.linkedin.com/company/{target}',
                'twitter': f'https://twitter.com/{target}',
                'facebook': f'https://www.facebook.com/{target}',
                'instagram': f'https://www.instagram.com/{target}'
            }
            
            for platform, url in platforms.items():
                try:
                    response = requests.head(url, timeout=10, allow_redirects=True)
                    if response.status_code == 200:
                        results.append({
                            'platform': platform,
                            'url': url,
                            'status': 'found'
                        })
                        self.collected_data['social_profiles'].add(url)
                except:
                    pass
            
            return results
            
        except Exception as e:
            self.logger.error(f"Quick social search failed: {str(e)}")
            return []
    
    def _social_media_osint(self, target: str) -> List[Dict[str, Any]]:
        """Social media OSINT gathering"""
        return self._quick_social_search(target)
    
    def _comprehensive_social_media_osint(self, target: str) -> List[Dict[str, Any]]:
        """Comprehensive social media OSINT"""
        results = []
        
        # Extended social media platforms
        extended_platforms = [
            'linkedin', 'twitter', 'facebook', 'instagram', 'youtube',
            'github', 'reddit', 'pinterest', 'tiktok', 'snapchat'
        ]
        
        for platform in extended_platforms:
            try:
                platform_results = self._search_single_platform(target, platform)
                results.extend(platform_results)
            except Exception as e:
                self.logger.debug(f"Platform {platform} search failed: {str(e)}")
        
        return results
    
    def _search_single_platform(self, target: str, platform: str) -> List[Dict[str, Any]]:
        """Search single social media platform"""
        # Placeholder for platform-specific searches
        return []
    
    def _document_metadata_search(self, target: str) -> List[Dict[str, Any]]:
        """Search for documents and extract metadata"""
        try:
            results = []
            
            # File types to search for
            file_types = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']
            
            for file_type in file_types:
                # Google dorking for file types
                query = f'site:{target} filetype:{file_type}'
                self.logger.debug(f"Document search: {query}")
                # Placeholder for actual search implementation
            
            return results
            
        except Exception as e:
            self.logger.error(f"Document metadata search failed: {str(e)}")
            return []
    
    def _code_repository_search(self, target: str) -> List[Dict[str, Any]]:
        """Search code repositories for mentions"""
        try:
            results = []
            
            # GitHub API search (requires API key for full access)
            github_url = f'https://api.github.com/search/repositories?q={target}'
            
            try:
                response = requests.get(github_url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    for repo in data.get('items', [])[:10]:  # Limit results
                        results.append({
                            'platform': 'github',
                            'name': repo.get('name'),
                            'url': repo.get('html_url'),
                            'description': repo.get('description')
                        })
                        self.collected_data['urls'].add(repo.get('html_url', ''))
            except:
                pass
            
            return results
            
        except Exception as e:
            self.logger.error(f"Code repository search failed: {str(e)}")
            return []
    
    def _breach_data_search(self, target: str) -> List[Dict[str, Any]]:
        """Search for breach data (public sources only)"""
        try:
            results = []
            
            # Placeholder for HaveIBeenPwned API or similar
            # Note: This should only use public, legitimate breach notification services
            self.logger.info(f"Checking public breach databases for {target}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Breach data search failed: {str(e)}")
            return []
    
    def _username_enumeration(self, target: str) -> List[Dict[str, Any]]:
        """Enumerate usernames across platforms"""
        try:
            results = []
            
            # Sherlock-style username enumeration
            platforms = [
                'github', 'twitter', 'instagram', 'reddit', 'youtube',
                'linkedin', 'facebook', 'pinterest', 'tumblr'
            ]
            
            for platform in platforms:
                try:
                    # Check if username exists on platform
                    # This is a placeholder - actual implementation would check each platform's API
                    pass
                except:
                    pass
            
            return results
            
        except Exception as e:
            self.logger.error(f"Username enumeration failed: {str(e)}")
            return []
    
    def _professional_networks_search(self, target: str) -> List[Dict[str, Any]]:
        """Search professional networking sites"""
        try:
            results = []
            
            # LinkedIn, Xing, etc.
            professional_sites = ['linkedin', 'xing', 'behance', 'dribbble']
            
            for site in professional_sites:
                try:
                    # Search for profiles or company pages
                    pass
                except:
                    pass
            
            return results
            
        except Exception as e:
            self.logger.error(f"Professional networks search failed: {str(e)}")
            return []
    
    def _process_collected_data(self) -> Dict[str, List[str]]:
        """Process and deduplicate collected data"""
        try:
            processed = {}
            
            for data_type, data_set in self.collected_data.items():
                # Convert sets to lists and clean data
                cleaned_data = []
                for item in data_set:
                    if item and isinstance(item, str):
                        item = item.strip()
                        if item and item not in cleaned_data:
                            cleaned_data.append(item)
                
                processed[data_type] = cleaned_data
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Data processing failed: {str(e)}")
            return {}
    
    def _generate_osint_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate OSINT gathering summary"""
        try:
            collected = results.get('collected_data', {})
            
            summary = {
                'total_emails_found': len(collected.get('emails', [])),
                'total_domains_found': len(collected.get('domains', [])),
                'total_social_profiles': len(collected.get('social_profiles', [])),
                'total_usernames': len(collected.get('usernames', [])),
                'total_documents': len(collected.get('documents', [])),
                'tools_used': list(results.get('tool_results', {}).keys()),
                'sources_used': list(results.get('source_breakdown', {}).keys())
            }
            
            # Calculate data richness score
            data_points = sum([
                len(collected.get('emails', [])),
                len(collected.get('social_profiles', [])),
                len(collected.get('phone_numbers', [])),
                len(collected.get('usernames', []))
            ])
            
            if data_points >= 50:
                summary['data_richness'] = 'high'
            elif data_points >= 20:
                summary['data_richness'] = 'medium'
            elif data_points >= 5:
                summary['data_richness'] = 'low'
            else:
                summary['data_richness'] = 'minimal'
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Summary generation failed: {str(e)}")
            return {}
    
    def quick_osint(self, target: str) -> Dict[str, Any]:
        """Perform quick OSINT gathering"""
        return self.gather_osint(target, "quick")
    
    def comprehensive_osint(self, target: str) -> Dict[str, Any]:
        """Perform comprehensive OSINT gathering"""
        return self.gather_osint(target, "comprehensive")
    
    def social_osint(self, target: str) -> Dict[str, Any]:
        """Perform social media focused OSINT"""
        return self.gather_osint(target, "social")
    
    def email_harvest_only(self, domain: str) -> List[str]:
        """Harvest emails for domain only"""
        if self.tools['theharvester']:
            results = self._run_theharvester(domain, 'domain')
            return results.get('emails', [])
        else:
            return list(self._basic_email_harvest(domain))