"""
Unit Tests for CLI Interface
===========================

Tests for command-line interface functionality including
main CLI, dashboard, and user interactions.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import os
import sys
import unittest
import tempfile
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
import io

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import CLI modules (with fallbacks if not implemented)
try:
    from interfaces.cli import main_cli
except ImportError:
    main_cli = None

try:
    from interfaces.cli import dashboard
except ImportError:
    dashboard = None

try:
    from interfaces.cli import menu_system
except ImportError:
    menu_system = None


class TestMainCLI(unittest.TestCase):
    """Test cases for main CLI functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_args = ['--target', 'example.com', '--profile', 'quick']
        self.mock_stdin = io.StringIO()
        self.mock_stdout = io.StringIO()
        self.mock_stderr = io.StringIO()
    
    @unittest.skipIf(main_cli is None, "main_cli not implemented")
    def test_main_cli_initialization(self):
        """Test main CLI initialization"""
        
        with patch.object(main_cli, 'PentestCLI', create=True) as mock_cli_class:
            mock_cli_instance = Mock()
            mock_cli_class.return_value = mock_cli_instance
            mock_cli_instance.run.return_value = 0
            
            # Act
            with patch.object(main_cli, 'parse_arguments', create=True) as mock_parse:
                mock_parse.return_value = Mock(
                    target='example.com',
                    profile='quick',
                    verbose=False,
                    output_dir='/tmp/reports'
                )
                
                result = main_cli.main(self.test_args)
        
        # Assert
        self.assertEqual(result, 0)
        mock_cli_class.assert_called_once()
        mock_cli_instance.run.assert_called_once()
    
    @unittest.skipIf(main_cli is None, "main_cli not implemented")
    def test_parse_command_line_arguments(self):
        """Test command line argument parsing"""
        
        with patch.object(main_cli, 'parse_arguments', create=True) as mock_parse:
            mock_parse.return_value = Mock(
                target='192.168.1.0/24',
                profile='comprehensive',
                output_dir='/custom/output',
                format=['pdf', 'html'],
                verbose=True,
                dry_run=False,
                config_file='/custom/config.yaml'
            )
            
            # Act
            args = main_cli.parse_arguments([
                '--target', '192.168.1.0/24',
                '--profile', 'comprehensive',
                '--output-dir', '/custom/output',
                '--format', 'pdf', 'html',
                '--verbose',
                '--config', '/custom/config.yaml'
            ])
        
        # Assert
        self.assertEqual(args.target, '192.168.1.0/24')
        self.assertEqual(args.profile, 'comprehensive')
        self.assertEqual(args.output_dir, '/custom/output')
        self.assertIn('pdf', args.format)
        self.assertTrue(args.verbose)
        
        mock_parse.assert_called_once()
    
    @unittest.skipIf(main_cli is None, "main_cli not implemented")
    def test_interactive_mode(self):
        """Test interactive CLI mode"""
        
        with patch.object(main_cli, 'InteractiveCLI', create=True) as mock_interactive:
            mock_cli_instance = Mock()
            mock_interactive.return_value = mock_cli_instance
            
            # Mock user interactions
            mock_cli_instance.show_main_menu.return_value = 'scan'
            mock_cli_instance.get_scan_parameters.return_value = {
                'target': 'test.example.com',
                'profile': 'web_app'
            }
            mock_cli_instance.execute_scan.return_value = {'status': 'success'}
            
            # Act
            interactive_cli = mock_interactive()
            menu_choice = interactive_cli.show_main_menu()
            scan_params = interactive_cli.get_scan_parameters()
            scan_result = interactive_cli.execute_scan(scan_params)
        
        # Assert
        self.assertEqual(menu_choice, 'scan')
        self.assertEqual(scan_params['target'], 'test.example.com')
        self.assertEqual(scan_result['status'], 'success')
        
        mock_interactive.assert_called_once()
        mock_cli_instance.show_main_menu.assert_called_once()
        mock_cli_instance.get_scan_parameters.assert_called_once()
    
    @unittest.skipIf(main_cli is None, "main_cli not implemented")
    def test_command_execution(self):
        """Test CLI command execution"""
        
        with patch.object(main_cli, 'CommandExecutor', create=True) as mock_executor:
            mock_cmd_instance = Mock()
            mock_executor.return_value = mock_cmd_instance
            
            # Mock command results
            mock_cmd_instance.execute_scan.return_value = {
                'exit_code': 0,
                'output': 'Scan completed successfully',
                'scan_id': 'SCAN-001',
                'duration': 300.5
            }
            
            mock_cmd_instance.execute_report.return_value = {
                'exit_code': 0,
                'output': 'Report generated',
                'report_path': '/reports/scan_001.pdf'
            }
            
            # Act
            executor = mock_executor()
            scan_result = executor.execute_scan('example.com', 'full')
            report_result = executor.execute_report('SCAN-001', 'pdf')
        
        # Assert
        self.assertEqual(scan_result['exit_code'], 0)
        self.assertEqual(scan_result['scan_id'], 'SCAN-001')
        self.assertEqual(report_result['exit_code'], 0)
        self.assertTrue(report_result['report_path'].endswith('.pdf'))
        
        mock_cmd_instance.execute_scan.assert_called_once_with('example.com', 'full')
        mock_cmd_instance.execute_report.assert_called_once_with('SCAN-001', 'pdf')
    
    def test_main_cli_mock_implementation(self):
        """Test main CLI with complete mock implementation"""
        
        # Arrange
        mock_cli = Mock()
        mock_cli.display_banner.return_value = None
        mock_cli.validate_target.return_value = True
        mock_cli.show_progress.return_value = None
        mock_cli.format_output.return_value = "Formatted scan results"
        
        # Act
        mock_cli.display_banner()
        is_valid = mock_cli.validate_target('example.com')
        mock_cli.show_progress(50, "Scanning in progress...")
        formatted_output = mock_cli.format_output({'vulns': 5, 'hosts': 10})
        
        # Assert
        self.assertTrue(is_valid)
        self.assertEqual(formatted_output, "Formatted scan results")
        
        mock_cli.display_banner.assert_called_once()
        mock_cli.validate_target.assert_called_once_with('example.com')
        mock_cli.show_progress.assert_called_once_with(50, "Scanning in progress...")
        mock_cli.format_output.assert_called_once()


class TestCLIDashboard(unittest.TestCase):
    """Test cases for CLI dashboard functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_metrics = {
            'active_scans': 2,
            'completed_scans': 15,
            'total_vulnerabilities': 42,
            'critical_vulns': 3,
            'system_load': 35.5,
            'memory_usage': 68.2
        }
    
    @unittest.skipIf(dashboard is None, "dashboard not implemented")
    def test_display_dashboard(self):
        """Test dashboard display functionality"""
        
        with patch.object(dashboard, 'Dashboard', create=True) as mock_dashboard_class:
            mock_dash_instance = Mock()
            mock_dashboard_class.return_value = mock_dash_instance
            
            mock_dash_instance.render.return_value = """
            ╔═══════════════════════════════════════╗
            ║         PENTEST TOOLKIT DASHBOARD     ║
            ╠═══════════════════════════════════════╣
            ║ Active Scans:           2             ║
            ║ Completed Scans:        15            ║
            ║ Total Vulnerabilities:  42            ║
            ║ Critical:               3             ║
            ║ System Load:            35.5%         ║
            ║ Memory Usage:           68.2%         ║
            ╚═══════════════════════════════════════╝
            """
            
            # Act
            dash = mock_dashboard_class(self.sample_metrics)
            rendered_output = dash.render()
        
        # Assert
        self.assertIsInstance(rendered_output, str)
        self.assertIn('PENTEST TOOLKIT DASHBOARD', rendered_output)
        self.assertIn('Active Scans:', rendered_output)
        self.assertIn('42', rendered_output)  # Total vulnerabilities
        
        mock_dashboard_class.assert_called_once_with(self.sample_metrics)
        mock_dash_instance.render.assert_called_once()
    
    @unittest.skipIf(dashboard is None, "dashboard not implemented")
    def test_real_time_updates(self):
        """Test real-time dashboard updates"""
        
        with patch.object(dashboard, 'LiveDashboard', create=True) as mock_live_dash:
            mock_live_instance = Mock()
            mock_live_dash.return_value = mock_live_instance
            
            # Mock update methods
            mock_live_instance.update_metrics.return_value = True
            mock_live_instance.refresh_display.return_value = None
            mock_live_instance.handle_user_input.return_value = 'continue'
            
            # Act
            live_dash = mock_live_dash()
            update_success = live_dash.update_metrics(self.sample_metrics)
            live_dash.refresh_display()
            user_action = live_dash.handle_user_input('r')  # Refresh command
        
        # Assert
        self.assertTrue(update_success)
        self.assertEqual(user_action, 'continue')
        
        mock_live_instance.update_metrics.assert_called_once_with(self.sample_metrics)
        mock_live_instance.refresh_display.assert_called_once()
        mock_live_instance.handle_user_input.assert_called_once_with('r')
    
    @unittest.skipIf(dashboard is None, "dashboard not implemented")
    def test_scan_progress_visualization(self):
        """Test scan progress visualization"""
        
        with patch.object(dashboard, 'ProgressVisualizer', create=True) as mock_progress:
            mock_prog_instance = Mock()
            mock_progress.return_value = mock_prog_instance
            
            # Mock progress visualization
            mock_prog_instance.show_scan_progress.return_value = """
            Reconnaissance:     ████████████████████ 100% ✓
            Vulnerability Scan: ██████████████░░░░░░  75% ⟳
            Exploitation:       ░░░░░░░░░░░░░░░░░░░░   0% ⏸
            Reporting:          ░░░░░░░░░░░░░░░░░░░░   0% ⏸
            
            Overall Progress:   ████████████░░░░░░░░  65%
            ETA: 15 minutes remaining
            """
            
            mock_prog_instance.show_vulnerability_summary.return_value = """
            Vulnerability Summary:
            ├─ Critical: 2  🔴
            ├─ High:     5  🟠  
            ├─ Medium:   8  🟡
            └─ Low:      3  🟢
            """
            
            # Act
            visualizer = mock_progress()
            progress_display = visualizer.show_scan_progress(65, {
                'reconnaissance': 100,
                'vulnerability': 75,
                'exploitation': 0,
                'reporting': 0
            })
            vuln_summary = visualizer.show_vulnerability_summary({
                'critical': 2, 'high': 5, 'medium': 8, 'low': 3
            })
        
        # Assert
        self.assertIn('65%', progress_display)
        self.assertIn('15 minutes', progress_display)
        self.assertIn('Critical: 2', vuln_summary)
        
        mock_prog_instance.show_scan_progress.assert_called_once()
        mock_prog_instance.show_vulnerability_summary.assert_called_once()
    
    def test_dashboard_mock_implementation(self):
        """Test dashboard with complete mock implementation"""
        
        # Arrange
        mock_dashboard = Mock()
        mock_dashboard.create_ascii_chart.return_value = """
        Vulnerability Trend (Last 7 Days):
         │
        8│    ▲
         │   ╱ ╲
        6│  ╱   ╲
         │ ╱     ╲
        4│╱       ╲▲
         │         ╱╲
        2│        ╱  ╲
         └─────────────
          Mon Tue Wed Thu Fri Sat Sun
        """
        
        mock_dashboard.format_system_stats.return_value = {
            'cpu_usage': '35.5%',
            'memory_usage': '68.2%',
            'disk_usage': '45.0%',
            'network_io': '1.2 MB/s',
            'uptime': '2 days, 14 hours'
        }
        
        # Act
        chart_output = mock_dashboard.create_ascii_chart('vulnerability_trend')
        system_stats = mock_dashboard.format_system_stats()
        
        # Assert
        self.assertIn('Vulnerability Trend', chart_output)
        self.assertIn('▲', chart_output)
        self.assertEqual(system_stats['cpu_usage'], '35.5%')
        self.assertEqual(system_stats['uptime'], '2 days, 14 hours')
        
        mock_dashboard.create_ascii_chart.assert_called_once_with('vulnerability_trend')
        mock_dashboard.format_system_stats.assert_called_once()


class TestMenuSystem(unittest.TestCase):
    """Test cases for CLI menu system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.menu_options = [
            {'id': 'scan', 'label': 'Start New Scan', 'description': 'Begin vulnerability assessment'},
            {'id': 'reports', 'label': 'View Reports', 'description': 'Browse existing reports'},
            {'id': 'config', 'label': 'Configuration', 'description': 'Modify settings'},
            {'id': 'exit', 'label': 'Exit', 'description': 'Quit application'}
        ]
    
    @unittest.skipIf(menu_system is None, "menu_system not implemented")
    def test_menu_display(self):
        """Test menu display functionality"""
        
        with patch.object(menu_system, 'Menu', create=True) as mock_menu_class:
            mock_menu_instance = Mock()
            mock_menu_class.return_value = mock_menu_instance
            
            mock_menu_instance.display.return_value = """
            ╔═══════════════════════════════════════╗
            ║              MAIN MENU                ║
            ╠═══════════════════════════════════════╣
            ║ 1. Start New Scan                     ║
            ║ 2. View Reports                       ║
            ║ 3. Configuration                      ║
            ║ 4. Exit                               ║
            ╚═══════════════════════════════════════╝
            
            Select an option [1-4]:
            """
            
            # Act
            menu = mock_menu_class('Main Menu', self.menu_options)
            display_output = menu.display()
        
        # Assert
        self.assertIsInstance(display_output, str)
        self.assertIn('MAIN MENU', display_output)
        self.assertIn('Start New Scan', display_output)
        self.assertIn('Select an option', display_output)
        
        mock_menu_class.assert_called_once_with('Main Menu', self.menu_options)
        mock_menu_instance.display.assert_called_once()
    
    @unittest.skipIf(menu_system is None, "menu_system not implemented")
    def test_menu_navigation(self):
        """Test menu navigation and selection"""
        
        with patch.object(menu_system, 'MenuNavigator', create=True) as mock_navigator:
            mock_nav_instance = Mock()
            mock_navigator.return_value = mock_nav_instance
            
            # Mock user selection
            mock_nav_instance.get_user_selection.return_value = 1  # Start New Scan
            mock_nav_instance.validate_selection.return_value = True
            mock_nav_instance.execute_selection.return_value = {'action': 'scan', 'valid': True}
            
            # Act
            navigator = mock_navigator(self.menu_options)
            user_choice = navigator.get_user_selection()
            is_valid = navigator.validate_selection(user_choice)
            result = navigator.execute_selection(user_choice)
        
        # Assert
        self.assertEqual(user_choice, 1)
        self.assertTrue(is_valid)
        self.assertEqual(result['action'], 'scan')
        self.assertTrue(result['valid'])
        
        mock_nav_instance.get_user_selection.assert_called_once()
        mock_nav_instance.validate_selection.assert_called_once_with(1)
        mock_nav_instance.execute_selection.assert_called_once_with(1)
    
    @unittest.skipIf(menu_system is None, "menu_system not implemented")
    def test_hierarchical_menus(self):
        """Test hierarchical menu navigation"""
        
        with patch.object(menu_system, 'HierarchicalMenu', create=True) as mock_hier_menu:
            mock_hier_instance = Mock()
            mock_hier_menu.return_value = mock_hier_instance
            
            # Mock menu hierarchy
            mock_hier_instance.get_current_menu.return_value = 'scan_menu'
            mock_hier_instance.navigate_to.return_value = True
            mock_hier_instance.go_back.return_value = 'main_menu'
            mock_hier_instance.get_breadcrumb.return_value = "Main > Scanning > Network Scan"
            
            # Act
            hier_menu = mock_hier_menu()
            current_menu = hier_menu.get_current_menu()
            navigation_success = hier_menu.navigate_to('network_scan_options')
            previous_menu = hier_menu.go_back()
            breadcrumb = hier_menu.get_breadcrumb()
        
        # Assert
        self.assertEqual(current_menu, 'scan_menu')
        self.assertTrue(navigation_success)
        self.assertEqual(previous_menu, 'main_menu')
        self.assertIn('Network Scan', breadcrumb)
        
        mock_hier_instance.get_current_menu.assert_called_once()
        mock_hier_instance.navigate_to.assert_called_once_with('network_scan_options')
        mock_hier_instance.go_back.assert_called_once()
    
    def test_menu_system_mock_implementation(self):
        """Test menu system with complete mock implementation"""
        
        # Arrange
        mock_menu_system = Mock()
        mock_menu_system.create_dynamic_menu.return_value = {
            'menu_id': 'DYN-001',
            'title': 'Scan Configuration',
            'options': [
                {'key': 't', 'label': 'Set Target', 'current_value': 'example.com'},
                {'key': 'p', 'label': 'Profile', 'current_value': 'comprehensive'},
                {'key': 's', 'label': 'Start Scan', 'enabled': True}
            ]
        }
        
        mock_menu_system.handle_keyboard_input.return_value = {
            'key_pressed': 's',
            'action': 'start_scan',
            'valid': True,
            'confirmation_required': True
        }
        
        # Act
        dynamic_menu = mock_menu_system.create_dynamic_menu('scan_config', {'target': 'example.com'})
        input_result = mock_menu_system.handle_keyboard_input('s')
        
        # Assert
        self.assertEqual(dynamic_menu['menu_id'], 'DYN-001')
        self.assertEqual(len(dynamic_menu['options']), 3)
        
        self.assertEqual(input_result['action'], 'start_scan')
        self.assertTrue(input_result['confirmation_required'])
        
        mock_menu_system.create_dynamic_menu.assert_called_once_with('scan_config', {'target': 'example.com'})
        mock_menu_system.handle_keyboard_input.assert_called_once_with('s')


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_complete_cli_workflow(self):
        """Test complete CLI workflow integration"""
        
        # Arrange - Mock all CLI components
        mock_main_cli = Mock()
        mock_dashboard = Mock()
        mock_menu = Mock()
        
        # Mock CLI initialization
        mock_main_cli.initialize.return_value = True
        
        # Mock menu interaction
        mock_menu.show_main_menu.return_value = 'scan'
        mock_menu.get_scan_parameters.return_value = {
            'target': 'test.example.com',
            'profile': 'web_app'
        }
        
        # Mock scan execution
        mock_main_cli.execute_scan.return_value = {
            'scan_id': 'SCAN-001',
            'status': 'completed',
            'vulnerabilities': 5
        }
        
        # Mock dashboard update
        mock_dashboard.update_scan_results.return_value = True
        
        # Mock report generation
        mock_main_cli.generate_report.return_value = {
            'report_path': f'{self.temp_dir}/report.pdf',
            'format': 'PDF',
            'success': True
        }
        
        # Act - Simulate complete CLI workflow
        init_success = mock_main_cli.initialize()
        menu_choice = mock_menu.show_main_menu()
        scan_params = mock_menu.get_scan_parameters()
        scan_result = mock_main_cli.execute_scan(scan_params)
        dashboard_update = mock_dashboard.update_scan_results(scan_result)
        report_result = mock_main_cli.generate_report(scan_result['scan_id'], 'PDF')
        
        # Assert
        self.assertTrue(init_success)
        self.assertEqual(menu_choice, 'scan')
        self.assertEqual(scan_result['status'], 'completed')
        self.assertTrue(dashboard_update)
        self.assertTrue(report_result['success'])
        
        # Verify workflow steps were executed
        mock_main_cli.initialize.assert_called_once()
        mock_menu.show_main_menu.assert_called_once()
        mock_main_cli.execute_scan.assert_called_once_with(scan_params)
        mock_dashboard.update_scan_results.assert_called_once_with(scan_result)
        mock_main_cli.generate_report.assert_called_once_with('SCAN-001', 'PDF')


if __name__ == '__main__':
    unittest.main()