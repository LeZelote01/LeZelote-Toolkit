"""
Pentest-USB Toolkit - Metasploit API Interface
=============================================

Python interface to Metasploit Framework for exploitation.
Integrates MSF with the Pentest-USB Toolkit workflow.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import subprocess
import json
import time
import socket
from pathlib import Path
from typing import Dict, List, Any, Optional

from ..utils.logging_handler import get_logger
from ..utils.error_handler import PentestError
from ..utils.network_utils import NetworkValidator


class MetasploitAPI:
    """
    Metasploit Framework API interface
    """
    
    def __init__(self, msf_path: Optional[str] = None):
        """Initialize Metasploit API"""
        self.logger = get_logger(__name__)
        self.msf_path = msf_path or self._find_msf()
        self.validator = NetworkValidator()
        
        # RPC connection details
        self.rpc_host = "127.0.0.1"
        self.rpc_port = 55553
        self.rpc_token = None
        
        # Verify installation
        self._verify_installation()
        
        self.logger.info("MetasploitAPI initialized successfully")
    
    def _find_msf(self) -> str:
        """Find Metasploit executable"""
        import shutil
        msf_path = shutil.which('msfconsole')
        if not msf_path:
            # Try toolkit binaries
            for path in ['./tools/binaries/metasploit-framework/msfconsole']:
                if Path(path).exists():
                    return str(Path(path).parent)
        return msf_path or 'msfconsole'
    
    def _verify_installation(self):
        """Verify Metasploit installation"""
        try:
            result = subprocess.run([f"{self.msf_path}/msfconsole", "-v"], 
                                 capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                raise PentestError("Metasploit not properly installed")
        except Exception as e:
            self.logger.warning(f"Metasploit verification failed: {str(e)}")
            # Continue without MSF for now
    
    def start_rpc_service(self):
        """Start Metasploit RPC service"""
        try:
            cmd = [f"{self.msf_path}/msfrpcd", "-P", "password", "-S"]
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for service to start
            time.sleep(10)
            
            # Test connection
            if self._test_rpc_connection():
                self.logger.info("Metasploit RPC service started")
                return True
            else:
                raise PentestError("Failed to start MSF RPC service")
                
        except Exception as e:
            self.logger.error(f"Failed to start MSF RPC: {str(e)}")
            return False
    
    def _test_rpc_connection(self) -> bool:
        """Test RPC connection"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.rpc_host, self.rpc_port))
            sock.close()
            return result == 0
        except:
            return False
    
    def execute_module(self, module_type: str, module_name: str, 
                      options: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute Metasploit module
        
        Args:
            module_type: Type of module (exploit, auxiliary, payload, etc.)
            module_name: Name of the module
            options: Module options and parameters
            
        Returns:
            Execution results
        """
        try:
            # Build msfconsole command
            commands = [
                f"use {module_type}/{module_name}",
            ]
            
            # Set options
            for key, value in options.items():
                commands.append(f"set {key} {value}")
            
            # Execute
            if module_type == "exploit":
                commands.append("exploit")
            else:
                commands.append("run")
            
            commands.append("exit")
            
            # Create resource file
            resource_content = "\n".join(commands)
            resource_path = "/tmp/msf_resource.rc"
            
            with open(resource_path, "w") as f:
                f.write(resource_content)
            
            # Execute via msfconsole
            cmd = [f"{self.msf_path}/msfconsole", "-q", "-r", resource_path]
            
            self.logger.info(f"Executing MSF module: {module_type}/{module_name}")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Clean up
            Path(resource_path).unlink(missing_ok=True)
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "module": f"{module_type}/{module_name}",
                "options": options
            }
            
        except subprocess.TimeoutExpired:
            raise PentestError("MSF module execution timeout")
        except Exception as e:
            self.logger.error(f"MSF module execution error: {str(e)}")
            raise PentestError(f"MSF execution failed: {str(e)}")
    
    def search_exploits(self, target: str, service: str = None) -> List[Dict[str, Any]]:
        """Search for available exploits"""
        try:
            cmd = [f"{self.msf_path}/msfconsole", "-q", "-x"]
            
            if service:
                search_term = f"search {service}"
            else:
                search_term = f"search {target}"
            
            cmd.append(f"{search_term}; exit")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Parse search results
            exploits = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if 'exploit/' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        exploits.append({
                            "name": parts[0],
                            "disclosure_date": parts[1] if len(parts) > 1 else "",
                            "rank": parts[2] if len(parts) > 2 else "",
                            "description": " ".join(parts[3:]) if len(parts) > 3 else ""
                        })
            
            return exploits
            
        except Exception as e:
            self.logger.error(f"MSF search error: {str(e)}")
            return []
    
    def generate_payload(self, payload_type: str, lhost: str, lport: int, 
                        format_type: str = "exe") -> Dict[str, Any]:
        """Generate Metasploit payload"""
        try:
            cmd = [
                f"{self.msf_path}/msfvenom",
                "-p", payload_type,
                f"LHOST={lhost}",
                f"LPORT={lport}",
                "-f", format_type
            ]
            
            self.logger.info(f"Generating payload: {payload_type}")
            
            result = subprocess.run(cmd, capture_output=True, timeout=120)
            
            return {
                "success": result.returncode == 0,
                "payload": result.stdout,
                "error": result.stderr.decode() if result.stderr else None,
                "type": payload_type,
                "format": format_type
            }
            
        except Exception as e:
            self.logger.error(f"Payload generation error: {str(e)}")
            raise PentestError(f"Payload generation failed: {str(e)}")
    
    def start_handler(self, payload: str, lhost: str, lport: int) -> Dict[str, Any]:
        """Start exploit handler"""
        options = {
            "PAYLOAD": payload,
            "LHOST": lhost,
            "LPORT": str(lport)
        }
        
        return self.execute_module("exploit", "multi/handler", options)
    
    def get_sessions(self) -> List[Dict[str, Any]]:
        """Get active sessions"""
        try:
            cmd = [f"{self.msf_path}/msfconsole", "-q", "-x", "sessions -l; exit"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            sessions = []
            lines = result.stdout.split('\n')
            
            for line in lines:
                if line.strip() and not line.startswith('Active sessions'):
                    parts = line.split()
                    if len(parts) >= 4:
                        sessions.append({
                            "id": parts[0],
                            "type": parts[1],
                            "info": " ".join(parts[2:])
                        })
            
            return sessions
            
        except Exception as e:
            self.logger.error(f"Session listing error: {str(e)}")
            return []