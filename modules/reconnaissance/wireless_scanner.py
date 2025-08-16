"""
Pentest-USB Toolkit - Wireless Scanner Module
============================================

Wireless network discovery and security assessment.
Integrates Aircrack-ng suite, Kismet for comprehensive wireless reconnaissance.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import subprocess
import json
import time
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import tempfile

from ...core.utils.logging_handler import get_logger
from ...core.utils.error_handler import PentestError


class WirelessScanner:
    """
    Wireless network scanner and security assessment module
    """
    
    def __init__(self):
        """Initialize Wireless Scanner"""
        self.logger = get_logger(__name__)
        
        # Tool paths
        self.tools = {
            'airodump-ng': self._find_tool('airodump-ng'),
            'aircrack-ng': self._find_tool('aircrack-ng'),
            'aireplay-ng': self._find_tool('aireplay-ng'),
            'airmon-ng': self._find_tool('airmon-ng'),
            'kismet': self._find_tool('kismet'),
            'iwconfig': self._find_tool('iwconfig'),
            'iwlist': self._find_tool('iwlist'),
            'reaver': self._find_tool('reaver'),
            'wash': self._find_tool('wash')
        }
        
        # Wireless interface management
        self.available_interfaces = []
        self.monitor_interfaces = []
        
        # Security assessment categories
        self.security_levels = {
            'open': 0,
            'wep': 1,
            'wps': 2,
            'wpa': 3,
            'wpa2': 4,
            'wpa3': 5
        }
        
        # Results storage
        self.discovered_networks = {
            'access_points': [],
            'clients': [],
            'hidden_networks': [],
            'wps_enabled': [],
            'weak_security': []
        }
        
        self._detect_wireless_interfaces()
        self.logger.info("WirelessScanner module initialized")
    
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
            f'/usr/bin/{tool_name}',
            f'/usr/sbin/{tool_name}'
        ]
        
        for path in potential_paths:
            if Path(path).exists():
                return str(Path(path).absolute())
        
        self.logger.warning(f"Tool {tool_name} not found")
        return None
    
    def _detect_wireless_interfaces(self):
        """Detect available wireless interfaces"""
        try:
            if self.tools['iwconfig']:
                result = subprocess.run([self.tools['iwconfig']], 
                                      capture_output=True, text=True, timeout=10)
                
                # Parse iwconfig output for wireless interfaces
                lines = result.stdout.split('\n')
                current_interface = None
                
                for line in lines:
                    # Interface line starts with interface name (no leading spaces)
                    if line and not line.startswith(' ') and 'IEEE 802.11' in line:
                        interface_name = line.split()[0]
                        self.available_interfaces.append(interface_name)
            
            # Alternative detection using /proc/net/wireless
            try:
                with open('/proc/net/wireless', 'r') as f:
                    for line in f:
                        if ':' in line and not line.strip().startswith('Inter'):
                            interface = line.split(':')[0].strip()
                            if interface not in self.available_interfaces:
                                self.available_interfaces.append(interface)
            except FileNotFoundError:
                pass
            
            self.logger.info(f"Detected wireless interfaces: {self.available_interfaces}")
            
        except Exception as e:
            self.logger.error(f"Wireless interface detection failed: {str(e)}")
    
    def scan_wireless_networks(self, interface: str = None, profile: str = "default") -> Dict[str, Any]:
        """
        Scan wireless networks in the area
        
        Args:
            interface: Wireless interface to use (auto-detect if None)
            profile: Scan profile (quick, default, comprehensive, passive)
            
        Returns:
            Wireless scan results
        """
        try:
            self.logger.info(f"Starting wireless network scan (profile: {profile})")
            
            # Select interface
            if not interface:
                if not self.available_interfaces:
                    raise PentestError("No wireless interfaces available")
                interface = self.available_interfaces[0]
            
            # Validate interface
            if interface not in self.available_interfaces:
                self.logger.warning(f"Interface {interface} not in detected interfaces")
            
            # Clear previous results
            for key in self.discovered_networks:
                if isinstance(self.discovered_networks[key], list):
                    self.discovered_networks[key].clear()
            
            # Initialize results structure
            results = {
                'interface_used': interface,
                'profile': profile,
                'timestamp': time.time(),
                'scan_duration': 0,
                'networks_found': {},
                'security_assessment': {},
                'tool_results': {},
                'summary': {}
            }
            
            start_time = time.time()
            
            # Execute scan based on profile
            if profile == "quick":
                results = self._quick_wireless_scan(interface, results)
            elif profile == "comprehensive":
                results = self._comprehensive_wireless_scan(interface, results)
            elif profile == "passive":
                results = self._passive_wireless_scan(interface, results)
            else:
                results = self._default_wireless_scan(interface, results)
            
            results['scan_duration'] = time.time() - start_time
            
            # Process discovered networks
            results['networks_found'] = self._process_discovered_networks()
            
            # Security assessment
            results['security_assessment'] = self._assess_wireless_security(results['networks_found'])
            
            # Generate summary
            results['summary'] = self._generate_scan_summary(results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Wireless scan failed: {str(e)}")
            raise PentestError(f"Wireless scan failed: {str(e)}")
    
    def _quick_wireless_scan(self, interface: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Quick wireless scan using basic iwlist"""
        try:
            if self.tools['iwlist']:
                iwlist_results = self._run_iwlist_scan(interface)
                results['tool_results']['iwlist'] = len(iwlist_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Quick wireless scan failed: {str(e)}")
            return results
    
    def _default_wireless_scan(self, interface: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Default wireless scan using airodump-ng"""
        try:
            # Monitor mode setup and airodump scan
            monitor_interface = self._enable_monitor_mode(interface)
            if monitor_interface:
                airodump_results = self._run_airodump_scan(monitor_interface)
                results['tool_results']['airodump'] = len(airodump_results)
                
                # WPS detection
                if self.tools['wash']:
                    wps_results = self._run_wps_scan(monitor_interface)
                    results['tool_results']['wps_scan'] = len(wps_results)
                
                self._disable_monitor_mode(monitor_interface, interface)
            else:
                # Fallback to iwlist
                iwlist_results = self._run_iwlist_scan(interface)
                results['tool_results']['iwlist'] = len(iwlist_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Default wireless scan failed: {str(e)}")
            return results
    
    def _comprehensive_wireless_scan(self, interface: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive wireless scan using all available tools"""
        try:
            # Monitor mode setup
            monitor_interface = self._enable_monitor_mode(interface)
            
            if monitor_interface:
                # Extended airodump scan
                airodump_results = self._run_extended_airodump_scan(monitor_interface)
                results['tool_results']['airodump'] = len(airodump_results)
                
                # WPS scanning
                if self.tools['wash']:
                    wps_results = self._run_wps_scan(monitor_interface)
                    results['tool_results']['wps_scan'] = len(wps_results)
                
                # Hidden network detection
                hidden_results = self._detect_hidden_networks(monitor_interface)
                results['tool_results']['hidden_detection'] = len(hidden_results)
                
                # Client detection
                client_results = self._detect_wireless_clients(monitor_interface)
                results['tool_results']['client_detection'] = len(client_results)
                
                # Kismet integration if available
                if self.tools['kismet']:
                    kismet_results = self._run_kismet_scan(monitor_interface)
                    results['tool_results']['kismet'] = len(kismet_results)
                
                self._disable_monitor_mode(monitor_interface, interface)
            else:
                # Fallback to managed mode scans
                iwlist_results = self._run_iwlist_scan(interface)
                results['tool_results']['iwlist'] = len(iwlist_results)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Comprehensive wireless scan failed: {str(e)}")
            return results
    
    def _passive_wireless_scan(self, interface: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Passive wireless monitoring"""
        try:
            monitor_interface = self._enable_monitor_mode(interface)
            
            if monitor_interface:
                # Passive monitoring with airodump
                passive_results = self._run_passive_monitoring(monitor_interface)
                results['tool_results']['passive_monitoring'] = len(passive_results)
                
                self._disable_monitor_mode(monitor_interface, interface)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Passive wireless scan failed: {str(e)}")
            return results
    
    def _enable_monitor_mode(self, interface: str) -> Optional[str]:
        """Enable monitor mode on wireless interface"""
        try:
            if not self.tools['airmon-ng']:
                self.logger.warning("airmon-ng not available, cannot enable monitor mode")
                return None
            
            self.logger.info(f"Enabling monitor mode on {interface}")
            
            # Kill conflicting processes
            subprocess.run([self.tools['airmon-ng'], 'check', 'kill'], 
                         capture_output=True, timeout=30)
            
            # Enable monitor mode
            result = subprocess.run([self.tools['airmon-ng'], 'start', interface], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse output to find monitor interface name
                monitor_interface = None
                for line in result.stdout.split('\n'):
                    if 'monitor mode enabled' in line.lower():
                        # Extract monitor interface name (usually interfacemon or interface with suffix)
                        words = line.split()
                        for word in words:
                            if 'mon' in word or word.startswith(interface):
                                monitor_interface = word
                                break
                        break
                
                if not monitor_interface:
                    # Common naming convention
                    monitor_interface = f"{interface}mon"
                
                self.monitor_interfaces.append(monitor_interface)
                self.logger.info(f"Monitor mode enabled: {monitor_interface}")
                return monitor_interface
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to enable monitor mode: {str(e)}")
            return None
    
    def _disable_monitor_mode(self, monitor_interface: str, original_interface: str):
        """Disable monitor mode and restore original interface"""
        try:
            if not self.tools['airmon-ng']:
                return
            
            self.logger.info(f"Disabling monitor mode on {monitor_interface}")
            
            subprocess.run([self.tools['airmon-ng'], 'stop', monitor_interface], 
                         capture_output=True, timeout=30)
            
            if monitor_interface in self.monitor_interfaces:
                self.monitor_interfaces.remove(monitor_interface)
            
        except Exception as e:
            self.logger.error(f"Failed to disable monitor mode: {str(e)}")
    
    def _run_iwlist_scan(self, interface: str) -> List[Dict[str, Any]]:
        """Run iwlist scan for wireless networks"""
        try:
            if not self.tools['iwlist']:
                return []
            
            self.logger.info(f"Running iwlist scan on {interface}")
            
            result = subprocess.run([self.tools['iwlist'], interface, 'scan'], 
                                  capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                return []
            
            # Parse iwlist output
            networks = self._parse_iwlist_output(result.stdout)
            
            # Store in discovered networks
            self.discovered_networks['access_points'].extend(networks)
            
            return networks
            
        except subprocess.TimeoutExpired:
            self.logger.warning("iwlist scan timeout")
            return []
        except Exception as e:
            self.logger.error(f"iwlist scan failed: {str(e)}")
            return []
    
    def _parse_iwlist_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse iwlist scan output"""
        networks = []
        current_network = {}
        
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            
            if line.startswith('Cell '):
                # New network entry
                if current_network:
                    networks.append(current_network)
                current_network = {}
                
                # Extract BSSID
                if 'Address:' in line:
                    current_network['bssid'] = line.split('Address: ')[1].strip()
            
            elif 'ESSID:' in line:
                essid = line.split('ESSID:')[1].strip().strip('"')
                current_network['essid'] = essid if essid else '<hidden>'
            
            elif 'Frequency:' in line:
                freq_part = line.split('Frequency:')[1].split('(')[0].strip()
                try:
                    frequency = float(freq_part.split()[0])
                    current_network['frequency'] = frequency
                    current_network['channel'] = self._frequency_to_channel(frequency)
                except:
                    pass
            
            elif 'Quality=' in line:
                try:
                    quality_part = line.split('Quality=')[1].split()[0]
                    current_network['signal_quality'] = quality_part
                except:
                    pass
            
            elif 'Signal level=' in line:
                try:
                    signal_part = line.split('Signal level=')[1].split()[0]
                    current_network['signal_level'] = signal_part
                except:
                    pass
            
            elif 'Encryption key:' in line:
                encryption = 'on' in line.lower()
                current_network['encryption'] = encryption
            
            elif 'IE: WPA' in line:
                current_network['security'] = 'WPA'
            elif 'IE: IEEE 802.11i/WPA2' in line:
                current_network['security'] = 'WPA2'
        
        # Add the last network
        if current_network:
            networks.append(current_network)
        
        return networks
    
    def _frequency_to_channel(self, frequency: float) -> int:
        """Convert frequency to channel number"""
        if 2412 <= frequency <= 2484:
            # 2.4 GHz band
            if frequency == 2484:
                return 14
            else:
                return int((frequency - 2412) / 5) + 1
        elif 5170 <= frequency <= 5825:
            # 5 GHz band
            return int((frequency - 5000) / 5)
        else:
            return 0
    
    def _run_airodump_scan(self, monitor_interface: str) -> List[Dict[str, Any]]:
        """Run airodump-ng scan"""
        try:
            if not self.tools['airodump-ng']:
                return []
            
            self.logger.info(f"Running airodump-ng scan on {monitor_interface}")
            
            # Create temporary files
            with tempfile.NamedTemporaryFile(prefix='airodump_', suffix='.csv', delete=False) as f:
                temp_prefix = f.name[:-4]  # Remove .csv extension
            
            # Run airodump-ng for 30 seconds
            cmd = [
                self.tools['airodump-ng'], 
                '--write', temp_prefix,
                '--output-format', 'csv',
                monitor_interface
            ]
            
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(30)  # Scan for 30 seconds
            process.terminate()
            process.wait()
            
            # Parse results
            networks = self._parse_airodump_output(f"{temp_prefix}-01.csv")
            
            # Cleanup
            for file_path in Path(temp_prefix).parent.glob(f"{Path(temp_prefix).name}*"):
                file_path.unlink(missing_ok=True)
            
            # Store in discovered networks
            self.discovered_networks['access_points'].extend(networks)
            
            return networks
            
        except Exception as e:
            self.logger.error(f"airodump-ng scan failed: {str(e)}")
            return []
    
    def _run_extended_airodump_scan(self, monitor_interface: str) -> List[Dict[str, Any]]:
        """Run extended airodump-ng scan"""
        # Similar to _run_airodump_scan but with longer duration and channel hopping
        return self._run_airodump_scan(monitor_interface)
    
    def _parse_airodump_output(self, csv_file: str) -> List[Dict[str, Any]]:
        """Parse airodump-ng CSV output"""
        networks = []
        
        try:
            if not Path(csv_file).exists():
                return networks
            
            with open(csv_file, 'r') as f:
                lines = f.readlines()
            
            # Find the start of AP data
            ap_start = None
            for i, line in enumerate(lines):
                if line.startswith('BSSID'):
                    ap_start = i + 1
                    break
            
            if ap_start is None:
                return networks
            
            # Parse AP data
            for i in range(ap_start, len(lines)):
                line = lines[i].strip()
                if not line or line.startswith('Station MAC'):
                    break
                
                parts = line.split(',')
                if len(parts) >= 14:
                    network = {
                        'bssid': parts[0].strip(),
                        'first_seen': parts[1].strip(),
                        'last_seen': parts[2].strip(),
                        'channel': parts[3].strip(),
                        'speed': parts[4].strip(),
                        'privacy': parts[5].strip(),
                        'cipher': parts[6].strip(),
                        'authentication': parts[7].strip(),
                        'power': parts[8].strip(),
                        'beacons': parts[9].strip(),
                        'iv': parts[10].strip(),
                        'lan_ip': parts[11].strip(),
                        'id_length': parts[12].strip(),
                        'essid': parts[13].strip() if parts[13].strip() else '<hidden>',
                        'key': parts[14].strip() if len(parts) > 14 else ''
                    }
                    
                    # Determine security type
                    privacy = parts[5].strip().upper()
                    if 'WPA2' in privacy:
                        network['security'] = 'WPA2'
                    elif 'WPA' in privacy:
                        network['security'] = 'WPA'
                    elif 'WEP' in privacy:
                        network['security'] = 'WEP'
                    elif privacy == '' or privacy == 'OPN':
                        network['security'] = 'Open'
                    else:
                        network['security'] = privacy
                    
                    networks.append(network)
            
        except Exception as e:
            self.logger.error(f"Failed to parse airodump output: {str(e)}")
        
        return networks
    
    def _run_wps_scan(self, monitor_interface: str) -> List[Dict[str, Any]]:
        """Run WPS scan using wash"""
        try:
            if not self.tools['wash']:
                return []
            
            self.logger.info(f"Running WPS scan with wash on {monitor_interface}")
            
            result = subprocess.run([self.tools['wash'], '-i', monitor_interface], 
                                  capture_output=True, text=True, timeout=60)
            
            wps_networks = []
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if ':' in line and len(line.split()) >= 3:
                        parts = line.split()
                        if len(parts) >= 6:
                            wps_network = {
                                'bssid': parts[0],
                                'channel': parts[1],
                                'rssi': parts[2],
                                'wps_version': parts[3],
                                'wps_locked': parts[4],
                                'essid': ' '.join(parts[5:])
                            }
                            wps_networks.append(wps_network)
            
            self.discovered_networks['wps_enabled'].extend(wps_networks)
            return wps_networks
            
        except Exception as e:
            self.logger.error(f"WPS scan failed: {str(e)}")
            return []
    
    def _detect_hidden_networks(self, monitor_interface: str) -> List[Dict[str, Any]]:
        """Detect hidden networks"""
        # Placeholder - would require more advanced techniques
        hidden_networks = []
        
        for network in self.discovered_networks['access_points']:
            if network.get('essid') in ['<hidden>', '', None]:
                hidden_networks.append(network)
        
        self.discovered_networks['hidden_networks'].extend(hidden_networks)
        return hidden_networks
    
    def _detect_wireless_clients(self, monitor_interface: str) -> List[Dict[str, Any]]:
        """Detect wireless clients"""
        # Placeholder - would parse client data from airodump
        return []
    
    def _run_kismet_scan(self, monitor_interface: str) -> List[Dict[str, Any]]:
        """Run Kismet scan"""
        # Placeholder - Kismet integration would be complex
        self.logger.info("Kismet integration placeholder")
        return []
    
    def _run_passive_monitoring(self, monitor_interface: str) -> List[Dict[str, Any]]:
        """Run passive wireless monitoring"""
        # Similar to airodump but longer duration
        return self._run_airodump_scan(monitor_interface)
    
    def _process_discovered_networks(self) -> Dict[str, Any]:
        """Process and organize discovered networks"""
        return {
            'access_points': self.discovered_networks['access_points'],
            'wps_enabled': self.discovered_networks['wps_enabled'],
            'hidden_networks': self.discovered_networks['hidden_networks'],
            'total_networks': len(self.discovered_networks['access_points'])
        }
    
    def _assess_wireless_security(self, networks: Dict[str, Any]) -> Dict[str, Any]:
        """Assess security of discovered wireless networks"""
        assessment = {
            'security_breakdown': {},
            'vulnerable_networks': [],
            'recommendations': []
        }
        
        # Analyze security types
        security_counts = {}
        for ap in networks.get('access_points', []):
            security = ap.get('security', 'Unknown')
            security_counts[security] = security_counts.get(security, 0) + 1
            
            # Identify vulnerable networks
            if security in ['Open', 'WEP']:
                assessment['vulnerable_networks'].append({
                    'essid': ap.get('essid'),
                    'bssid': ap.get('bssid'),
                    'security': security,
                    'risk': 'High' if security == 'Open' else 'Medium'
                })
        
        assessment['security_breakdown'] = security_counts
        
        # WPS vulnerabilities
        wps_count = len(networks.get('wps_enabled', []))
        if wps_count > 0:
            assessment['recommendations'].append(f"Found {wps_count} networks with WPS enabled - potential security risk")
        
        # Hidden networks
        hidden_count = len(networks.get('hidden_networks', []))
        if hidden_count > 0:
            assessment['recommendations'].append(f"Found {hidden_count} hidden networks - investigate further")
        
        return assessment
    
    def _generate_scan_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate wireless scan summary"""
        networks = results.get('networks_found', {})
        security_assessment = results.get('security_assessment', {})
        
        summary = {
            'scan_duration': results.get('scan_duration', 0),
            'total_networks_found': networks.get('total_networks', 0),
            'wps_enabled_count': len(networks.get('wps_enabled', [])),
            'hidden_networks_count': len(networks.get('hidden_networks', [])),
            'vulnerable_networks': len(security_assessment.get('vulnerable_networks', [])),
            'security_types': security_assessment.get('security_breakdown', {}),
            'interface_used': results.get('interface_used'),
            'tools_used': list(results.get('tool_results', {}).keys())
        }
        
        return summary
    
    def quick_scan(self, interface: str = None) -> Dict[str, Any]:
        """Perform quick wireless scan"""
        return self.scan_wireless_networks(interface, "quick")
    
    def comprehensive_scan(self, interface: str = None) -> Dict[str, Any]:
        """Perform comprehensive wireless scan"""
        return self.scan_wireless_networks(interface, "comprehensive")
    
    def passive_scan(self, interface: str = None) -> Dict[str, Any]:
        """Perform passive wireless monitoring"""
        return self.scan_wireless_networks(interface, "passive")
    
    def get_available_interfaces(self) -> List[str]:
        """Get list of available wireless interfaces"""
        return self.available_interfaces