#!/usr/bin/env python3
"""
Pentest-USB Toolkit - Custom Reconnaissance Tools

This module provides custom reconnaissance tools and automations
for the Pentest-USB Toolkit. It includes specialized scripts for
network discovery, domain enumeration, and advanced OSINT gathering.

Author: Pentest-USB Team
Version: 1.0.0
"""

import os
import sys
import json
import subprocess
import threading
import time
import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
import ipaddress
import dns.resolver
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkDiscovery:
    """Advanced network discovery and port scanning"""
    
    def __init__(self, max_threads: int = 50):
        self.max_threads = max_threads
        self.open_ports = []
        
    def ping_sweep(self, network: str) -> List[str]:
        """Perform ping sweep on network range"""
        logger.info(f"Starting ping sweep on {network}")
        alive_hosts = []
        
        try:
            net = ipaddress.ip_network(network, strict=False)
            hosts = list(net.hosts())
            
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                future_to_host = {
                    executor.submit(self._ping_host, str(host)): host 
                    for host in hosts
                }
                
                for future in as_completed(future_to_host):
                    host = future_to_host[future]
                    try:
                        if future.result():
                            alive_hosts.append(str(host))
                            logger.info(f"Host alive: {host}")
                    except Exception as e:
                        logger.error(f"Error pinging {host}: {e}")
                        
        except Exception as e:
            logger.error(f"Error in ping sweep: {e}")
            
        return alive_hosts
    
    def _ping_host(self, host: str) -> bool:
        """Ping single host"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ['ping', '-n', '1', '-w', '1000', host],
                    capture_output=True, text=True, timeout=5
                )
            else:  # Linux/macOS
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '1', host],
                    capture_output=True, text=True, timeout=5
                )
            return result.returncode == 0
        except:
            return False
    
    def port_scan(self, host: str, ports: List[int]) -> Dict[int, bool]:
        """Fast TCP port scan"""
        logger.info(f"Scanning {len(ports)} ports on {host}")
        results = {}
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            future_to_port = {
                executor.submit(self._scan_port, host, port): port 
                for port in ports
            }
            
            for future in as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    results[port] = future.result()
                    if results[port]:
                        logger.info(f"Open port found: {host}:{port}")
                except Exception as e:
                    logger.error(f"Error scanning {host}:{port}: {e}")
                    results[port] = False
                    
        return results
    
    def _scan_port(self, host: str, port: int) -> bool:
        """Scan single port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def service_detection(self, host: str, port: int) -> Dict[str, Any]:
        """Basic service detection"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((host, port))
            
            # Send generic probe
            sock.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
            banner = sock.recv(1024).decode('utf-8', errors='ignore')
            sock.close()
            
            service_info = {
                'port': port,
                'state': 'open',
                'banner': banner[:200],  # First 200 chars
                'service': self._identify_service(port, banner)
            }
            
            return service_info
            
        except Exception as e:
            return {
                'port': port,
                'state': 'open',
                'banner': '',
                'service': 'unknown',
                'error': str(e)
            }
    
    def _identify_service(self, port: int, banner: str) -> str:
        """Basic service identification"""
        common_services = {
            21: 'ftp',
            22: 'ssh',
            23: 'telnet',
            25: 'smtp',
            53: 'dns',
            80: 'http',
            110: 'pop3',
            143: 'imap',
            443: 'https',
            993: 'imaps',
            995: 'pop3s'
        }
        
        if port in common_services:
            return common_services[port]
        
        banner_lower = banner.lower()
        if 'http' in banner_lower:
            return 'http'
        elif 'ssh' in banner_lower:
            return 'ssh'
        elif 'ftp' in banner_lower:
            return 'ftp'
        else:
            return 'unknown'


class SubdomainEnumerator:
    """Advanced subdomain enumeration"""
    
    def __init__(self):
        self.subdomains = set()
        self.wordlist_path = "/app/data/wordlists/dns/subdomains.txt"
        
    def brute_force_subdomains(self, domain: str, wordlist: Optional[str] = None) -> List[str]:
        """Brute force subdomain discovery"""
        logger.info(f"Starting subdomain brute force for {domain}")
        
        wordlist_file = wordlist or self.wordlist_path
        if not os.path.exists(wordlist_file):
            logger.warning(f"Wordlist not found: {wordlist_file}")
            # Use basic wordlist
            subdomains_to_test = ['www', 'mail', 'admin', 'api', 'dev', 'test', 'staging']
        else:
            with open(wordlist_file, 'r') as f:
                subdomains_to_test = [line.strip() for line in f if line.strip()]
        
        valid_subdomains = []
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_subdomain = {
                executor.submit(self._check_subdomain, f"{sub}.{domain}"): f"{sub}.{domain}"
                for sub in subdomains_to_test
            }
            
            for future in as_completed(future_to_subdomain):
                subdomain = future_to_subdomain[future]
                try:
                    if future.result():
                        valid_subdomains.append(subdomain)
                        logger.info(f"Valid subdomain: {subdomain}")
                except Exception as e:
                    logger.error(f"Error checking {subdomain}: {e}")
        
        return valid_subdomains
    
    def _check_subdomain(self, subdomain: str) -> bool:
        """Check if subdomain exists"""
        try:
            dns.resolver.resolve(subdomain, 'A')
            return True
        except:
            return False
    
    def certificate_transparency_search(self, domain: str) -> List[str]:
        """Search certificate transparency logs"""
        logger.info(f"Searching CT logs for {domain}")
        
        try:
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                certificates = response.json()
                subdomains = set()
                
                for cert in certificates:
                    name_value = cert.get('name_value', '')
                    for name in name_value.split('\n'):
                        name = name.strip()
                        if name.endswith(f'.{domain}') and '*' not in name:
                            subdomains.add(name)
                
                return list(subdomains)
                
        except Exception as e:
            logger.error(f"Error searching CT logs: {e}")
            
        return []


class OSINTGatherer:
    """OSINT information gathering"""
    
    def __init__(self):
        self.results = {}
        
    def email_harvesting(self, domain: str) -> List[str]:
        """Basic email harvesting from search engines"""
        logger.info(f"Harvesting emails for {domain}")
        
        emails = set()
        
        # Google search simulation (basic)
        search_queries = [
            f"site:{domain} '@{domain}'",
            f"'{domain}' email",
            f"'{domain}' contact"
        ]
        
        # This is a simplified version - in real implementation,
        # you would integrate with theHarvester or similar tools
        logger.info(f"Would search for emails using queries: {search_queries}")
        
        # Simulate some results for demonstration
        simulated_emails = [
            f"admin@{domain}",
            f"info@{domain}",
            f"contact@{domain}"
        ]
        
        return simulated_emails
    
    def whois_lookup(self, domain: str) -> Dict[str, Any]:
        """WHOIS information gathering"""
        logger.info(f"WHOIS lookup for {domain}")
        
        try:
            import whois
            w = whois.whois(domain)
            
            whois_info = {
                'domain_name': w.domain_name,
                'registrar': w.registrar,
                'creation_date': str(w.creation_date) if w.creation_date else None,
                'expiration_date': str(w.expiration_date) if w.expiration_date else None,
                'name_servers': w.name_servers,
                'emails': w.emails
            }
            
            return whois_info
            
        except ImportError:
            logger.warning("python-whois not installed, using basic lookup")
            return self._basic_whois(domain)
        except Exception as e:
            logger.error(f"WHOIS lookup failed: {e}")
            return {}
    
    def _basic_whois(self, domain: str) -> Dict[str, Any]:
        """Basic WHOIS using system command"""
        try:
            result = subprocess.run(
                ['whois', domain],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                return {'raw_whois': result.stdout}
            else:
                return {'error': 'WHOIS lookup failed'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def social_media_search(self, target: str) -> Dict[str, List[str]]:
        """Social media presence search"""
        logger.info(f"Searching social media for {target}")
        
        platforms = [
            'twitter.com',
            'facebook.com',
            'linkedin.com',
            'instagram.com',
            'github.com'
        ]
        
        results = {}
        
        for platform in platforms:
            # This would typically integrate with APIs or web scraping
            # For now, we'll just log the search
            logger.info(f"Would search {platform} for {target}")
            results[platform] = [f"https://{platform}/{target}"]
        
        return results


class ReconOrchestrator:
    """Main reconnaissance orchestrator"""
    
    def __init__(self):
        self.network_discovery = NetworkDiscovery()
        self.subdomain_enum = SubdomainEnumerator()
        self.osint_gatherer = OSINTGatherer()
        
    def full_recon(self, target: str, profile: str = "default") -> Dict[str, Any]:
        """Perform full reconnaissance on target"""
        logger.info(f"Starting full reconnaissance on {target} with profile {profile}")
        
        results = {
            'target': target,
            'profile': profile,
            'timestamp': time.time(),
            'results': {}
        }
        
        try:
            # Check if target is IP or domain
            if self._is_ip(target):
                results['results'] = self._recon_ip(target, profile)
            else:
                results['results'] = self._recon_domain(target, profile)
                
        except Exception as e:
            logger.error(f"Error during reconnaissance: {e}")
            results['error'] = str(e)
            
        return results
    
    def _is_ip(self, target: str) -> bool:
        """Check if target is IP address"""
        try:
            ipaddress.ip_address(target)
            return True
        except:
            return False
    
    def _recon_ip(self, target: str, profile: str) -> Dict[str, Any]:
        """Reconnaissance for IP target"""
        results = {}
        
        if profile in ["default", "comprehensive"]:
            # Port scan
            common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]
            if profile == "comprehensive":
                common_ports.extend(range(1, 1025))  # Extended port range
                
            port_results = self.network_discovery.port_scan(target, common_ports)
            open_ports = [port for port, is_open in port_results.items() if is_open]
            
            results['open_ports'] = open_ports
            
            # Service detection on open ports
            services = []
            for port in open_ports[:10]:  # Limit to first 10 ports
                service_info = self.network_discovery.service_detection(target, port)
                services.append(service_info)
                
            results['services'] = services
            
        return results
    
    def _recon_domain(self, target: str, profile: str) -> Dict[str, Any]:
        """Reconnaissance for domain target"""
        results = {}
        
        if profile in ["default", "comprehensive"]:
            # Subdomain enumeration
            subdomains = self.subdomain_enum.brute_force_subdomains(target)
            if profile == "comprehensive":
                ct_subdomains = self.subdomain_enum.certificate_transparency_search(target)
                subdomains.extend(ct_subdomains)
                subdomains = list(set(subdomains))  # Remove duplicates
                
            results['subdomains'] = subdomains
            
            # OSINT gathering
            osint_results = {}
            osint_results['whois'] = self.osint_gatherer.whois_lookup(target)
            osint_results['emails'] = self.osint_gatherer.email_harvesting(target)
            
            if profile == "comprehensive":
                osint_results['social_media'] = self.osint_gatherer.social_media_search(target)
                
            results['osint'] = osint_results
            
        return results


def main():
    """Main function for testing"""
    recon = ReconOrchestrator()
    
    # Example usage
    print("=== Pentest-USB Custom Reconnaissance Tools ===")
    print("Testing network discovery...")
    
    # Test with a local network (adjust as needed)
    # results = recon.full_recon("192.168.1.0/24", "default")
    
    # Test with a domain
    results = recon.full_recon("example.com", "default")
    
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()