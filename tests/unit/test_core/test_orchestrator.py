"""
Unit Tests for PentestOrchestrator
=================================

Tests for the main orchestration engine that manages
the complete pentesting workflow.

Author: Pentest-USB Development Team  
Version: 1.0.0
"""

import os
import sys
import unittest
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.engine.orchestrator import PentestOrchestrator, WorkflowState
from core.utils.error_handler import PentestError


class TestPentestOrchestrator(unittest.TestCase):
    """Test cases for PentestOrchestrator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.target = "192.168.1.100"
        self.profile = "quick"
        
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        config_content = """
modules:
  reconnaissance:
    enabled: true
    timeout: 300
  vulnerability:
    enabled: true
    timeout: 600
  exploitation:
    enabled: false
  post_exploitation:
    enabled: false
"""
        self.temp_config.write(config_content)
        self.temp_config.close()
        
        # Mock dependencies
        self.mock_consent_manager = Mock()
        self.mock_task_scheduler = Mock()
        self.mock_parallel_executor = Mock()
        self.mock_resource_manager = Mock()
        
    def tearDown(self):
        """Clean up test fixtures"""
        os.unlink(self.temp_config.name)
    
    @patch('core.engine.orchestrator.ConsentManager')
    @patch('core.engine.orchestrator.TaskScheduler')
    @patch('core.engine.orchestrator.ParallelExecutor')
    @patch('core.engine.orchestrator.ResourceManager')
    def test_orchestrator_initialization(self, mock_resource_mgr, mock_parallel_exec, 
                                       mock_task_sched, mock_consent_mgr):
        """Test orchestrator initialization"""
        # Arrange
        mock_consent_mgr.return_value = self.mock_consent_manager
        mock_task_sched.return_value = self.mock_task_scheduler
        mock_parallel_exec.return_value = self.mock_parallel_executor
        mock_resource_mgr.return_value = self.mock_resource_manager
        
        # Act
        orchestrator = PentestOrchestrator(
            target=self.target,
            profile=self.profile,
            config_path=self.temp_config.name
        )
        
        # Assert
        self.assertEqual(orchestrator.target, self.target)
        self.assertEqual(orchestrator.profile, self.profile)
        self.assertEqual(orchestrator.state, WorkflowState.INITIALIZED)
        self.assertIsNotNone(orchestrator.workflow_data)
        self.assertEqual(orchestrator.workflow_data['target'], self.target)
        
        # Verify mocks were called
        mock_consent_mgr.assert_called_once()
        mock_task_sched.assert_called_once()
        mock_parallel_exec.assert_called_once()
        mock_resource_mgr.assert_called_once()
    
    @patch('core.engine.orchestrator.ConsentManager')
    @patch('core.engine.orchestrator.TaskScheduler')
    @patch('core.engine.orchestrator.ParallelExecutor')
    @patch('core.engine.orchestrator.ResourceManager')
    def test_orchestrator_invalid_config(self, mock_resource_mgr, mock_parallel_exec,
                                        mock_task_sched, mock_consent_mgr):
        """Test orchestrator with invalid config file"""
        # Act & Assert
        with self.assertRaises(PentestError):
            PentestOrchestrator(
                target=self.target,
                profile=self.profile,
                config_path="/nonexistent/config.yaml"
            )
    
    @patch('core.engine.orchestrator.ConsentManager')
    @patch('core.engine.orchestrator.TaskScheduler')
    @patch('core.engine.orchestrator.ParallelExecutor')
    @patch('core.engine.orchestrator.ResourceManager')
    def test_load_config_success(self, mock_resource_mgr, mock_parallel_exec,
                                mock_task_sched, mock_consent_mgr):
        """Test successful configuration loading"""
        # Arrange
        mock_consent_mgr.return_value = self.mock_consent_manager
        mock_task_sched.return_value = self.mock_task_scheduler
        mock_parallel_exec.return_value = self.mock_parallel_executor
        mock_resource_mgr.return_value = self.mock_resource_manager
        
        # Act
        orchestrator = PentestOrchestrator(
            target=self.target,
            profile=self.profile,
            config_path=self.temp_config.name
        )
        
        # Assert
        self.assertIsNotNone(orchestrator.config)
        self.assertIn('modules', orchestrator.config)
        self.assertTrue(orchestrator.config['modules']['reconnaissance']['enabled'])
    
    @patch('core.engine.orchestrator.ConsentManager')
    @patch('core.engine.orchestrator.TaskScheduler')
    @patch('core.engine.orchestrator.ParallelExecutor')
    @patch('core.engine.orchestrator.ResourceManager')
    def test_consent_verification_failure(self, mock_resource_mgr, mock_parallel_exec,
                                         mock_task_sched, mock_consent_mgr):
        """Test workflow failure due to consent verification"""
        # Arrange
        mock_consent_mgr.return_value = self.mock_consent_manager
        mock_task_sched.return_value = self.mock_task_scheduler
        mock_parallel_exec.return_value = self.mock_parallel_executor
        mock_resource_mgr.return_value = self.mock_resource_manager
        
        # Mock consent manager to return False
        self.mock_consent_manager.verify_consent.return_value = False
        
        orchestrator = PentestOrchestrator(
            target=self.target,
            profile=self.profile,
            config_path=self.temp_config.name
        )
        
        # Act & Assert
        with self.assertRaises(PentestError) as context:
            orchestrator.run_workflow()
        
        self.assertIn("Consent verification failed", str(context.exception))
        self.mock_consent_manager.verify_consent.assert_called_once_with(self.target)
    
    @patch('core.engine.orchestrator.ConsentManager')
    @patch('core.engine.orchestrator.TaskScheduler') 
    @patch('core.engine.orchestrator.ParallelExecutor')
    @patch('core.engine.orchestrator.ResourceManager')
    @patch('modules.reconnaissance.network_scanner')
    @patch('modules.reconnaissance.domain_enum')
    @patch('modules.reconnaissance.osint_gather')
    def test_reconnaissance_phase(self, mock_osint, mock_domain, mock_network,
                                 mock_resource_mgr, mock_parallel_exec,
                                 mock_task_sched, mock_consent_mgr):
        """Test reconnaissance phase execution"""
        # Arrange
        mock_consent_mgr.return_value = self.mock_consent_manager
        mock_task_sched.return_value = self.mock_task_scheduler
        mock_parallel_exec.return_value = self.mock_parallel_executor
        mock_resource_mgr.return_value = self.mock_resource_manager
        
        self.mock_consent_manager.verify_consent.return_value = True
        
        # Mock reconnaissance results
        mock_recon_results = {
            'network_scan': {'hosts': ['192.168.1.100'], 'ports': [80, 443]},
            'domain_enum': {'subdomains': ['www.example.com', 'api.example.com']},
            'osint': {'emails': ['admin@example.com'], 'technologies': ['Apache']}
        }
        self.mock_parallel_executor.execute_tasks.return_value = mock_recon_results
        
        orchestrator = PentestOrchestrator(
            target=self.target,
            profile="full",  # Use full profile to trigger all recon modules
            config_path=self.temp_config.name
        )
        
        # Act
        orchestrator._run_reconnaissance()
        
        # Assert
        self.assertEqual(orchestrator.state, WorkflowState.RECON_COMPLETE)
        self.assertIn('reconnaissance', orchestrator.workflow_data['phases'])
        self.assertEqual(
            orchestrator.workflow_data['phases']['reconnaissance']['results'],
            mock_recon_results
        )
        self.mock_parallel_executor.execute_tasks.assert_called_once()
    
    @patch('core.engine.orchestrator.ConsentManager')
    @patch('core.engine.orchestrator.TaskScheduler')
    @patch('core.engine.orchestrator.ParallelExecutor')
    @patch('core.engine.orchestrator.ResourceManager')
    def test_get_status(self, mock_resource_mgr, mock_parallel_exec,
                       mock_task_sched, mock_consent_mgr):
        """Test status reporting"""
        # Arrange
        mock_consent_mgr.return_value = self.mock_consent_manager
        mock_task_sched.return_value = self.mock_task_scheduler
        mock_parallel_exec.return_value = self.mock_parallel_executor
        mock_resource_mgr.return_value = self.mock_resource_manager
        
        # Mock resource usage
        mock_usage = {'cpu': 25.5, 'memory': 512, 'disk': 1024}
        self.mock_resource_manager.get_current_usage.return_value = mock_usage
        
        orchestrator = PentestOrchestrator(
            target=self.target,
            profile=self.profile,
            config_path=self.temp_config.name
        )
        
        # Act
        status = orchestrator.get_status()
        
        # Assert
        self.assertEqual(status['target'], self.target)
        self.assertEqual(status['profile'], self.profile)
        self.assertEqual(status['state'], WorkflowState.INITIALIZED.value)
        self.assertEqual(status['resource_usage'], mock_usage)
        self.assertIn('start_time', status)
        self.assertIn('phases_completed', status)
    
    @patch('core.engine.orchestrator.ConsentManager')
    @patch('core.engine.orchestrator.TaskScheduler')
    @patch('core.engine.orchestrator.ParallelExecutor')
    @patch('core.engine.orchestrator.ResourceManager')
    def test_pause_resume_workflow(self, mock_resource_mgr, mock_parallel_exec,
                                  mock_task_sched, mock_consent_mgr):
        """Test workflow pause and resume functionality"""
        # Arrange
        mock_consent_mgr.return_value = self.mock_consent_manager
        mock_task_sched.return_value = self.mock_task_scheduler
        mock_parallel_exec.return_value = self.mock_parallel_executor
        mock_resource_mgr.return_value = self.mock_resource_manager
        
        orchestrator = PentestOrchestrator(
            target=self.target,
            profile=self.profile,
            config_path=self.temp_config.name
        )
        
        # Act - Pause workflow
        orchestrator.pause_workflow()
        
        # Assert - Check paused state
        self.assertEqual(orchestrator.state, WorkflowState.PAUSED)
        
        # Act - Resume workflow
        orchestrator.resume_workflow()
        
        # Assert - Check resumed state (should be INITIALIZED for empty workflow)
        self.assertEqual(orchestrator.state, WorkflowState.INITIALIZED)
    
    @patch('core.engine.orchestrator.ConsentManager')
    @patch('core.engine.orchestrator.TaskScheduler')
    @patch('core.engine.orchestrator.ParallelExecutor')
    @patch('core.engine.orchestrator.ResourceManager')
    def test_human_approval_required(self, mock_resource_mgr, mock_parallel_exec,
                                    mock_task_sched, mock_consent_mgr):
        """Test human approval mechanism"""
        # Arrange
        mock_consent_mgr.return_value = self.mock_consent_manager
        mock_task_sched.return_value = self.mock_task_scheduler
        mock_parallel_exec.return_value = self.mock_parallel_executor
        mock_resource_mgr.return_value = self.mock_resource_manager
        
        orchestrator = PentestOrchestrator(
            target=self.target,
            profile=self.profile,
            config_path=self.temp_config.name
        )
        
        # Act
        approval = orchestrator._request_human_approval('exploitation')
        
        # Assert - Should return False for safety by default
        self.assertFalse(approval)
    
    def test_workflow_state_transitions(self):
        """Test workflow state enumeration"""
        # Test all states are defined
        expected_states = [
            'initialized', 'reconnaissance_running', 'reconnaissance_complete',
            'vulnerability_running', 'vulnerability_complete', 'exploitation_pending',
            'exploitation_running', 'exploitation_complete', 'post_exploitation_running',
            'post_exploitation_complete', 'reporting', 'complete', 'failed', 'paused'
        ]
        
        actual_states = [state.value for state in WorkflowState]
        
        for expected_state in expected_states:
            self.assertIn(expected_state, actual_states)


if __name__ == '__main__':
    unittest.main()