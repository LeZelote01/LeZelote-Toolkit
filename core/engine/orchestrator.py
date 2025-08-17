"""
Pentest-USB Toolkit - Main Orchestrator
=======================================

Main orchestration engine that manages the complete pentesting workflow
from reconnaissance through post-exploitation and reporting.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import os
import sys
import time
import yaml
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path

# Fix imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.utils.logging_handler import get_logger
from core.utils.error_handler import PentestError
from core.security.consent_manager import ConsentManager
from core.engine.task_scheduler import TaskScheduler
from core.engine.parallel_executor import ParallelExecutor
from core.engine.resource_manager import ResourceManager


class WorkflowState(Enum):
    """Workflow state enumeration"""
    INITIALIZED = "initialized"
    RECON_RUNNING = "reconnaissance_running"
    RECON_COMPLETE = "reconnaissance_complete"
    VULN_RUNNING = "vulnerability_running"
    VULN_COMPLETE = "vulnerability_complete"
    EXPLOIT_PENDING = "exploitation_pending"
    EXPLOIT_RUNNING = "exploitation_running"
    EXPLOIT_COMPLETE = "exploitation_complete"
    POST_EXPLOIT_RUNNING = "post_exploitation_running"
    POST_EXPLOIT_COMPLETE = "post_exploitation_complete"
    REPORTING = "reporting"
    COMPLETE = "complete"
    FAILED = "failed"
    PAUSED = "paused"


class PentestOrchestrator:
    """
    Main orchestrator class that manages the complete penetration testing workflow.
    
    This class coordinates all phases of penetration testing:
    - Reconnaissance
    - Vulnerability Assessment  
    - Exploitation (with human approval)
    - Post-exploitation (with human approval)
    - Reporting
    """
    
    def __init__(self, target: str, profile: str = "full", config_path: str = None):
        """
        Initialize the orchestrator
        
        Args:
            target (str): Target IP, domain or network range
            profile (str): Scan profile (quick, full, stealth, etc.)
            config_path (str): Path to configuration file
        """
        self.target = target
        self.profile = profile
        self.config_path = config_path or "/app/config/main_config.yaml"
        
        # Initialize logger
        self.logger = get_logger(__name__)
        self.logger.info(f"Initializing PentestOrchestrator for target: {target}")
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize state
        self.state = WorkflowState.INITIALIZED
        self.workflow_data = {
            'target': target,
            'profile': profile,
            'start_time': datetime.now(),
            'phases': {},
            'results': {},
            'evidence': []
        }
        
        # Initialize components
        self.consent_manager = ConsentManager()
        self.task_scheduler = TaskScheduler(self.config)
        self.parallel_executor = ParallelExecutor(self.config)
        self.resource_manager = ResourceManager(self.config)
        
        # Human approval points
        self.human_approval_required = {
            'exploitation': False,
            'post_exploitation': False
        }
        
        self.logger.info("PentestOrchestrator initialized successfully")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.logger.debug(f"Configuration loaded from {self.config_path}")
                return config
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")
            raise PentestError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing configuration: {e}")
            raise PentestError(f"Error parsing configuration: {e}")
    
    def run_workflow(self) -> Dict[str, Any]:
        """
        Run the complete pentesting workflow
        
        Returns:
            Dict containing all results and evidence
        """
        try:
            self.logger.info("Starting complete pentesting workflow")
            self._update_state(WorkflowState.INITIALIZED)
            
            # Check consent and authorization
            if not self.consent_manager.verify_consent(self.target):
                raise PentestError("Consent verification failed. Cannot proceed.")
            
            # Phase 1: Reconnaissance
            self._run_reconnaissance()
            
            # Phase 2: Vulnerability Assessment
            self._run_vulnerability_assessment()
            
            # Human approval checkpoint for exploitation
            if self.config.get('modules', {}).get('exploitation', {}).get('enabled', False):
                if self._request_human_approval('exploitation'):
                    self._run_exploitation()
            
            # Human approval checkpoint for post-exploitation
            if self.config.get('modules', {}).get('post_exploitation', {}).get('enabled', False):
                if self._request_human_approval('post_exploitation'):
                    self._run_post_exploitation()
            
            # Phase 5: Generate Report
            self._generate_report()
            
            self._update_state(WorkflowState.COMPLETE)
            self.workflow_data['end_time'] = datetime.now()
            
            self.logger.info("Pentesting workflow completed successfully")
            return self.workflow_data
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {str(e)}")
            self._update_state(WorkflowState.FAILED)
            self.workflow_data['error'] = str(e)
            raise PentestError(f"Workflow execution failed: {str(e)}")
    
    def _run_reconnaissance(self):
        """Execute reconnaissance phase"""
        self.logger.info("Starting reconnaissance phase")
        self._update_state(WorkflowState.RECON_RUNNING)
        
        try:
            # Load reconnaissance module
            from modules.reconnaissance import network_scanner, domain_enum, osint_gather
            
            # Run reconnaissance tasks
            recon_tasks = []
            
            # Network scanning
            if self.profile in ['full', 'network', 'comprehensive']:
                recon_tasks.append(('network_scan', network_scanner.full_network_scan, [self.target]))
            
            # Domain enumeration
            if self.profile in ['full', 'web_app', 'comprehensive']:
                recon_tasks.append(('domain_enum', domain_enum.enumerate_domains, [self.target]))
            
            # OSINT gathering
            if self.profile in ['full', 'comprehensive']:
                recon_tasks.append(('osint', osint_gather.gather_intelligence, [self.target]))
            
            # Execute tasks in parallel
            recon_results = self.parallel_executor.execute_tasks(recon_tasks)
            
            self.workflow_data['phases']['reconnaissance'] = {
                'start_time': datetime.now(),
                'results': recon_results,
                'status': 'completed'
            }
            
            self._update_state(WorkflowState.RECON_COMPLETE)
            self.logger.info("Reconnaissance phase completed")
            
        except Exception as e:
            self.logger.error(f"Reconnaissance phase failed: {str(e)}")
            raise PentestError(f"Reconnaissance failed: {str(e)}")
    
    def _run_vulnerability_assessment(self):
        """Execute vulnerability assessment phase"""
        self.logger.info("Starting vulnerability assessment phase")
        self._update_state(WorkflowState.VULN_RUNNING)
        
        try:
            from modules.vulnerability import web_scanner, network_vuln
            
            vuln_tasks = []
            
            # Web vulnerability scanning
            if self.profile in ['full', 'web_app', 'comprehensive']:
                vuln_tasks.append(('web_scan', web_scanner.comprehensive_web_scan, [self.target]))
            
            # Network vulnerability scanning
            if self.profile in ['full', 'network', 'comprehensive']:
                vuln_tasks.append(('network_vuln', network_vuln.scan_network_vulnerabilities, [self.target]))
            
            # Execute vulnerability scans
            vuln_results = self.parallel_executor.execute_tasks(vuln_tasks)
            
            self.workflow_data['phases']['vulnerability'] = {
                'start_time': datetime.now(),
                'results': vuln_results,
                'status': 'completed'
            }
            
            self._update_state(WorkflowState.VULN_COMPLETE)
            self.logger.info("Vulnerability assessment phase completed")
            
        except Exception as e:
            self.logger.error(f"Vulnerability assessment failed: {str(e)}")
            raise PentestError(f"Vulnerability assessment failed: {str(e)}")
    
    def _run_exploitation(self):
        """Execute exploitation phase (requires human approval)"""
        self.logger.info("Starting exploitation phase")
        self._update_state(WorkflowState.EXPLOIT_RUNNING)
        
        try:
            from modules.exploitation import web_exploit, network_exploit
            
            # Get vulnerabilities from previous phase
            vulnerabilities = self.workflow_data['phases']['vulnerability']['results']
            
            exploit_tasks = []
            
            # Web exploitation
            if 'web_scan' in vulnerabilities:
                web_vulns = vulnerabilities['web_scan']
                for vuln in web_vulns:
                    if vuln.get('exploitable', False):
                        exploit_tasks.append(('web_exploit', web_exploit.exploit_vulnerability, [vuln]))
            
            # Network exploitation
            if 'network_vuln' in vulnerabilities:
                network_vulns = vulnerabilities['network_vuln']
                for vuln in network_vulns:
                    if vuln.get('exploitable', False):
                        exploit_tasks.append(('network_exploit', network_exploit.exploit_vulnerability, [vuln]))
            
            # Execute exploitation tasks
            exploit_results = self.parallel_executor.execute_tasks(exploit_tasks)
            
            self.workflow_data['phases']['exploitation'] = {
                'start_time': datetime.now(),
                'results': exploit_results,
                'status': 'completed'
            }
            
            self._update_state(WorkflowState.EXPLOIT_COMPLETE)
            self.logger.info("Exploitation phase completed")
            
        except Exception as e:
            self.logger.error(f"Exploitation phase failed: {str(e)}")
            raise PentestError(f"Exploitation failed: {str(e)}")
    
    def _run_post_exploitation(self):
        """Execute post-exploitation phase (requires human approval)"""
        self.logger.info("Starting post-exploitation phase")
        self._update_state(WorkflowState.POST_EXPLOIT_RUNNING)
        
        try:
            from modules.post_exploit import credential_access, lateral_movement
            
            # Get successful exploits from previous phase
            exploits = self.workflow_data['phases']['exploitation']['results']
            
            post_exploit_tasks = []
            
            # Credential access
            for exploit in exploits:
                if exploit.get('success', False):
                    post_exploit_tasks.append(('credential_access', credential_access.dump_credentials, [exploit['target']]))
                    post_exploit_tasks.append(('lateral_movement', lateral_movement.attempt_lateral_movement, [exploit['target']]))
            
            # Execute post-exploitation tasks
            post_exploit_results = self.parallel_executor.execute_tasks(post_exploit_tasks)
            
            self.workflow_data['phases']['post_exploitation'] = {
                'start_time': datetime.now(),
                'results': post_exploit_results,
                'status': 'completed'
            }
            
            self._update_state(WorkflowState.POST_EXPLOIT_COMPLETE)
            self.logger.info("Post-exploitation phase completed")
            
        except Exception as e:
            self.logger.error(f"Post-exploitation phase failed: {str(e)}")
            raise PentestError(f"Post-exploitation failed: {str(e)}")
    
    def _generate_report(self):
        """Generate final report"""
        self.logger.info("Starting report generation")
        self._update_state(WorkflowState.REPORTING)
        
        try:
            from modules.reporting import report_generator
            
            report_path = report_generator.generate_pentest_report(self.workflow_data)
            
            self.workflow_data['report_path'] = report_path
            self.logger.info(f"Report generated: {report_path}")
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            raise PentestError(f"Report generation failed: {str(e)}")
    
    def _request_human_approval(self, phase: str) -> bool:
        """Request human approval for sensitive phases"""
        self.logger.info(f"Requesting human approval for {phase} phase")
        
        # In a real implementation, this would interact with the user interface
        # For now, we'll return False (no approval) to prevent automatic exploitation
        
        approval_message = f"""
        HUMAN APPROVAL REQUIRED
        ======================
        
        Phase: {phase.upper()}
        Target: {self.target}
        
        The system is requesting approval to proceed with {phase}.
        This phase may involve active exploitation of vulnerabilities.
        
        Please review the findings and authorize the next phase manually.
        """
        
        self.logger.warning(approval_message)
        print(approval_message)
        
        # Return False for safety - require manual intervention
        return False
    
    def _update_state(self, new_state: WorkflowState):
        """Update workflow state"""
        self.state = new_state
        self.workflow_data['current_state'] = new_state.value
        self.logger.debug(f"Workflow state updated to: {new_state.value}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            'state': self.state.value,
            'target': self.target,
            'profile': self.profile,
            'start_time': self.workflow_data['start_time'],
            'phases_completed': list(self.workflow_data['phases'].keys()),
            'resource_usage': self.resource_manager.get_current_usage()
        }
    
    def pause_workflow(self):
        """Pause the workflow execution"""
        self.logger.info("Pausing workflow")
        self._update_state(WorkflowState.PAUSED)
    
    def resume_workflow(self):
        """Resume paused workflow"""
        self.logger.info("Resuming workflow")
        # Resume from the last completed phase
        if 'reconnaissance' not in self.workflow_data['phases']:
            self._update_state(WorkflowState.INITIALIZED)
        elif 'vulnerability' not in self.workflow_data['phases']:
            self._update_state(WorkflowState.RECON_COMPLETE)
        elif 'exploitation' not in self.workflow_data['phases']:
            self._update_state(WorkflowState.VULN_COMPLETE)
        else:
            self._update_state(WorkflowState.EXPLOIT_COMPLETE)