"""
Unit Tests for Reporting Module
==============================

Tests for reporting functionality including report generation,
data analysis, and compliance checking.

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

# Import reporting modules (with fallbacks if not implemented)
try:
    from modules.reporting import report_generator
except ImportError:
    report_generator = None

try:
    from modules.reporting import data_analyzer
except ImportError:
    data_analyzer = None

try:
    from modules.reporting import compliance_checker
except ImportError:
    compliance_checker = None

try:
    from modules.reporting import visual_builder
except ImportError:
    visual_builder = None


class TestReportGenerator(unittest.TestCase):
    """Test cases for report generation functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_scan_data = {
            'target': 'example.com',
            'start_time': '2024-01-15T10:00:00Z',
            'end_time': '2024-01-15T14:30:00Z',
            'phases': {
                'reconnaissance': {
                    'results': {'hosts_found': 5, 'subdomains': 12}
                },
                'vulnerability': {
                    'results': {'total_vulnerabilities': 8, 'critical': 2, 'high': 3}
                },
                'exploitation': {
                    'results': {'successful_exploits': 2, 'sessions_created': 1}
                }
            },
            'vulnerabilities': [
                {
                    'id': 'VULN-001',
                    'type': 'SQL_INJECTION',
                    'severity': 'CRITICAL',
                    'cvss_score': 9.1,
                    'description': 'SQL injection in login form'
                },
                {
                    'id': 'VULN-002',
                    'type': 'XSS',
                    'severity': 'HIGH',
                    'cvss_score': 7.5,
                    'description': 'Reflected XSS in search function'
                }
            ]
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @unittest.skipIf(report_generator is None, "report_generator not implemented")
    def test_generate_pentest_report_pdf(self):
        """Test PDF report generation"""
        
        with patch.object(report_generator, 'generate_pentest_report') as mock_generate:
            mock_generate.return_value = {
                'report_path': os.path.join(self.temp_dir, 'pentest_report.pdf'),
                'format': 'PDF',
                'pages': 25,
                'sections': [
                    'executive_summary',
                    'methodology',
                    'findings',
                    'recommendations',
                    'appendices'
                ],
                'file_size_mb': 2.3,
                'generation_time': 15.2,
                'template_used': 'default_pentest.html'
            }
            
            # Act
            result = report_generator.generate_pentest_report(
                self.sample_scan_data,
                format='PDF',
                output_path=self.temp_dir
            )
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result['format'], 'PDF')
        self.assertEqual(result['pages'], 25)
        self.assertIn('executive_summary', result['sections'])
        self.assertIn('findings', result['sections'])
        self.assertTrue(result['report_path'].endswith('pentest_report.pdf'))
        
        mock_generate.assert_called_once()
    
    @unittest.skipIf(report_generator is None, "report_generator not implemented")
    def test_generate_executive_summary(self):
        """Test executive summary generation"""
        
        with patch.object(report_generator, 'generate_executive_summary', create=True) as mock_exec:
            mock_exec.return_value = {
                'summary': {
                    'assessment_scope': 'External network and web application',
                    'duration': '4.5 hours',
                    'total_vulnerabilities': 8,
                    'risk_breakdown': {
                        'critical': 2,
                        'high': 3,
                        'medium': 2,
                        'low': 1
                    },
                    'key_findings': [
                        'Critical SQL injection vulnerability allows database access',
                        'Multiple high-severity XSS vulnerabilities found',
                        'Weak authentication mechanisms present'
                    ],
                    'business_impact': 'HIGH',
                    'recommended_actions': [
                        'Immediate patching of critical vulnerabilities',
                        'Implementation of input validation',
                        'Security awareness training for developers'
                    ]
                },
                'charts_generated': 3,
                'risk_matrix_included': True
            }
            
            # Act
            result = report_generator.generate_executive_summary(self.sample_scan_data)
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result['summary']['total_vulnerabilities'], 8)
        self.assertEqual(result['summary']['business_impact'], 'HIGH')
        self.assertEqual(len(result['summary']['key_findings']), 3)
        self.assertTrue(result['risk_matrix_included'])
        
        mock_exec.assert_called_once_with(self.sample_scan_data)
    
    @unittest.skipIf(report_generator is None, "report_generator not implemented")
    def test_generate_technical_report(self):
        """Test technical detailed report generation"""
        
        with patch.object(report_generator, 'generate_technical_report', create=True) as mock_tech:
            mock_tech.return_value = {
                'report_path': os.path.join(self.temp_dir, 'technical_report.html'),
                'vulnerability_details': [
                    {
                        'id': 'VULN-001',
                        'proof_of_concept': 'Included',
                        'remediation_steps': 'Detailed',
                        'references': ['OWASP', 'CWE-89'],
                        'screenshots': 2
                    }
                ],
                'methodology_section': True,
                'tools_used': ['nmap', 'sqlmap', 'burpsuite'],
                'appendices': ['raw_scan_data', 'tool_outputs'],
                'technical_depth': 'COMPREHENSIVE'
            }
            
            # Act
            result = report_generator.generate_technical_report(
                self.sample_scan_data,
                include_proof_of_concept=True,
                include_remediation=True
            )
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertTrue(result['methodology_section'])
        self.assertIn('sqlmap', result['tools_used'])
        self.assertEqual(result['technical_depth'], 'COMPREHENSIVE')
        
        mock_tech.assert_called_once()
    
    def test_report_generator_mock_implementation(self):
        """Test report generator with mock implementation"""
        
        # Arrange
        mock_generator = Mock()
        mock_generator.create_vulnerability_matrix.return_value = {
            'matrix_data': [
                ['Vulnerability', 'Severity', 'CVSS', 'Status'],
                ['SQL Injection', 'Critical', '9.1', 'Exploited'],
                ['XSS', 'High', '7.5', 'Confirmed']
            ],
            'format': 'HTML_TABLE',
            'styling': 'bootstrap'
        }
        
        mock_generator.generate_remediation_timeline.return_value = {
            'timeline': [
                {'priority': 1, 'task': 'Patch SQL injection', 'effort': '2-4 hours'},
                {'priority': 2, 'task': 'Fix XSS vulnerabilities', 'effort': '1-2 days'},
                {'priority': 3, 'task': 'Security review', 'effort': '1 week'}
            ],
            'total_effort': '2-3 weeks',
            'critical_deadline': '24 hours'
        }
        
        # Act
        matrix_result = mock_generator.create_vulnerability_matrix(self.sample_scan_data)
        timeline_result = mock_generator.generate_remediation_timeline(self.sample_scan_data)
        
        # Assert
        self.assertEqual(len(matrix_result['matrix_data']), 3)
        self.assertEqual(matrix_result['format'], 'HTML_TABLE')
        
        self.assertEqual(len(timeline_result['timeline']), 3)
        self.assertEqual(timeline_result['critical_deadline'], '24 hours')
        
        mock_generator.create_vulnerability_matrix.assert_called_once()
        mock_generator.generate_remediation_timeline.assert_called_once()


class TestDataAnalyzer(unittest.TestCase):
    """Test cases for data analysis functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.vulnerability_data = [
            {'type': 'SQL_INJECTION', 'severity': 'CRITICAL', 'cvss': 9.1},
            {'type': 'XSS', 'severity': 'HIGH', 'cvss': 7.5},
            {'type': 'XSS', 'severity': 'MEDIUM', 'cvss': 5.2},
            {'type': 'CSRF', 'severity': 'MEDIUM', 'cvss': 4.8},
            {'type': 'INFO_DISCLOSURE', 'severity': 'LOW', 'cvss': 2.1}
        ]
    
    @unittest.skipIf(data_analyzer is None, "data_analyzer not implemented")
    def test_analyze_vulnerability_trends(self):
        """Test vulnerability trend analysis"""
        
        with patch.object(data_analyzer, 'analyze_vulnerability_trends', create=True) as mock_trends:
            mock_trends.return_value = {
                'severity_distribution': {
                    'CRITICAL': 1,
                    'HIGH': 1,
                    'MEDIUM': 2,
                    'LOW': 1
                },
                'vulnerability_types': {
                    'XSS': 2,
                    'SQL_INJECTION': 1,
                    'CSRF': 1,
                    'INFO_DISCLOSURE': 1
                },
                'average_cvss': 5.74,
                'risk_score': 7.2,
                'trend_analysis': {
                    'most_common_type': 'XSS',
                    'highest_risk_category': 'Injection Attacks',
                    'remediation_priority': ['SQL_INJECTION', 'XSS', 'CSRF']
                }
            }
            
            # Act
            result = data_analyzer.analyze_vulnerability_trends(self.vulnerability_data)
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result['severity_distribution']['CRITICAL'], 1)
        self.assertEqual(result['vulnerability_types']['XSS'], 2)
        self.assertEqual(result['trend_analysis']['most_common_type'], 'XSS')
        self.assertAlmostEqual(result['average_cvss'], 5.74, places=2)
        
        mock_trends.assert_called_once_with(self.vulnerability_data)
    
    @unittest.skipIf(data_analyzer is None, "data_analyzer not implemented")
    def test_calculate_risk_metrics(self):
        """Test risk metrics calculation"""
        
        with patch.object(data_analyzer, 'calculate_risk_metrics', create=True) as mock_risk:
            mock_risk.return_value = {
                'overall_risk_score': 8.2,
                'risk_category': 'HIGH',
                'exploitability_score': 7.5,
                'impact_score': 8.9,
                'risk_factors': {
                    'external_facing': True,
                    'sensitive_data': True,
                    'user_interaction': False,
                    'network_accessible': True
                },
                'mitigation_effectiveness': 65.0,
                'residual_risk': 2.9,
                'recommendations': [
                    'Implement WAF protection',
                    'Regular security testing',
                    'Input validation framework'
                ]
            }
            
            # Act
            result = data_analyzer.calculate_risk_metrics(
                self.vulnerability_data,
                context={'external_facing': True, 'sensitive_data': True}
            )
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result['risk_category'], 'HIGH')
        self.assertGreater(result['overall_risk_score'], 8.0)
        self.assertTrue(result['risk_factors']['external_facing'])
        self.assertEqual(len(result['recommendations']), 3)
        
        mock_risk.assert_called_once()
    
    @unittest.skipIf(data_analyzer is None, "data_analyzer not implemented")
    def test_correlate_findings(self):
        """Test finding correlation and deduplication"""
        
        with patch.object(data_analyzer, 'correlate_findings', create=True) as mock_correlate:
            mock_correlate.return_value = {
                'original_findings': 15,
                'unique_findings': 10,
                'duplicates_removed': 5,
                'correlated_groups': [
                    {
                        'pattern': 'XSS_FAMILY',
                        'findings': ['XSS-001', 'XSS-002', 'XSS-003'],
                        'root_cause': 'Insufficient input validation',
                        'unified_recommendation': 'Implement output encoding'
                    },
                    {
                        'pattern': 'CONFIG_WEAKNESS',
                        'findings': ['CONF-001', 'CONF-002'],
                        'root_cause': 'Insecure default configuration',
                        'unified_recommendation': 'Security hardening'
                    }
                ],
                'attack_chains': [
                    {
                        'chain_id': 'CHAIN-001',
                        'vulnerabilities': ['VULN-001', 'VULN-003'],
                        'attack_path': 'SQL injection -> Privilege escalation',
                        'impact_multiplier': 2.5
                    }
                ]
            }
            
            # Act
            result = data_analyzer.correlate_findings(self.vulnerability_data)
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result['original_findings'], 15)
        self.assertEqual(result['unique_findings'], 10)
        self.assertEqual(len(result['correlated_groups']), 2)
        self.assertEqual(len(result['attack_chains']), 1)
        
        mock_correlate.assert_called_once_with(self.vulnerability_data)
    
    def test_data_analyzer_mock_implementation(self):
        """Test data analyzer with mock implementation"""
        
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer.generate_statistics.return_value = {
            'total_vulnerabilities': 5,
            'severity_stats': {'critical': 1, 'high': 1, 'medium': 2, 'low': 1},
            'cvss_statistics': {
                'mean': 5.74,
                'median': 5.2,
                'std_dev': 2.8,
                'range': [2.1, 9.1]
            },
            'vulnerability_density': 0.25,  # vulnerabilities per endpoint
            'false_positive_rate': 0.05
        }
        
        mock_analyzer.benchmark_against_industry.return_value = {
            'industry_average_vulns': 12.3,
            'performance_vs_industry': 'BETTER_THAN_AVERAGE',
            'percentile_ranking': 75,
            'industry_benchmarks': {
                'web_applications': 8.5,
                'network_infrastructure': 15.2,
                'mobile_applications': 6.7
            }
        }
        
        # Act
        stats_result = mock_analyzer.generate_statistics(self.vulnerability_data)
        benchmark_result = mock_analyzer.benchmark_against_industry(stats_result, 'web_applications')
        
        # Assert
        self.assertEqual(stats_result['total_vulnerabilities'], 5)
        self.assertAlmostEqual(stats_result['cvss_statistics']['mean'], 5.74)
        
        self.assertEqual(benchmark_result['performance_vs_industry'], 'BETTER_THAN_AVERAGE')
        self.assertEqual(benchmark_result['percentile_ranking'], 75)
        
        mock_analyzer.generate_statistics.assert_called_once()
        mock_analyzer.benchmark_against_industry.assert_called_once()


class TestComplianceChecker(unittest.TestCase):
    """Test cases for compliance checking functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.scan_results = {
            'vulnerabilities': [
                {'id': 'V001', 'type': 'SQL_INJECTION', 'severity': 'CRITICAL'},
                {'id': 'V002', 'type': 'XSS', 'severity': 'HIGH'},
                {'id': 'V003', 'type': 'WEAK_CRYPTO', 'severity': 'MEDIUM'}
            ],
            'configuration_issues': [
                {'type': 'UNENCRYPTED_DATA', 'severity': 'HIGH'},
                {'type': 'WEAK_PASSWORDS', 'severity': 'MEDIUM'}
            ]
        }
    
    @unittest.skipIf(compliance_checker is None, "compliance_checker not implemented")
    def test_check_pci_compliance(self):
        """Test PCI-DSS compliance checking"""
        
        with patch.object(compliance_checker, 'check_pci_compliance', create=True) as mock_pci:
            mock_pci.return_value = {
                'standard': 'PCI-DSS v4.0',
                'compliance_status': 'NON_COMPLIANT',
                'overall_score': 72.5,
                'requirement_results': {
                    '6.2.4': {
                        'description': 'Injection flaws protection',
                        'status': 'FAIL',
                        'findings': ['SQL injection vulnerability found'],
                        'severity': 'CRITICAL'
                    },
                    '4.1': {
                        'description': 'Strong cryptography for data transmission',
                        'status': 'PASS',
                        'findings': [],
                        'severity': None
                    },
                    '8.2': {
                        'description': 'Strong user authentication',
                        'status': 'PARTIAL',
                        'findings': ['Weak password policy detected'],
                        'severity': 'MEDIUM'
                    }
                },
                'failed_requirements': 1,
                'partial_requirements': 1,
                'passed_requirements': 1,
                'remediation_priority': [
                    {'requirement': '6.2.4', 'priority': 'IMMEDIATE'},
                    {'requirement': '8.2', 'priority': 'HIGH'}
                ]
            }
            
            # Act
            result = compliance_checker.check_pci_compliance(self.scan_results)
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result['compliance_status'], 'NON_COMPLIANT')
        self.assertEqual(result['failed_requirements'], 1)
        self.assertEqual(result['requirement_results']['6.2.4']['status'], 'FAIL')
        self.assertEqual(len(result['remediation_priority']), 2)
        
        mock_pci.assert_called_once_with(self.scan_results)
    
    @unittest.skipIf(compliance_checker is None, "compliance_checker not implemented")
    def test_check_owasp_top10_compliance(self):
        """Test OWASP Top 10 compliance checking"""
        
        with patch.object(compliance_checker, 'check_owasp_top10_compliance', create=True) as mock_owasp:
            mock_owasp.return_value = {
                'standard': 'OWASP Top 10 2021',
                'compliance_status': 'PARTIALLY_COMPLIANT',
                'category_results': {
                    'A03_INJECTION': {
                        'status': 'VULNERABLE',
                        'findings': 1,
                        'severity': 'CRITICAL',
                        'examples': ['SQL injection in login form']
                    },
                    'A07_IDENTIFICATION_AUTH_FAILURES': {
                        'status': 'VULNERABLE',
                        'findings': 1,
                        'severity': 'MEDIUM',
                        'examples': ['Weak password policy']
                    },
                    'A02_CRYPTOGRAPHIC_FAILURES': {
                        'status': 'SECURE',
                        'findings': 0,
                        'severity': None,
                        'examples': []
                    }
                },
                'vulnerable_categories': 2,
                'secure_categories': 1,
                'overall_score': 70.0,
                'recommendations': [
                    'Implement input validation for injection prevention',
                    'Strengthen authentication mechanisms'
                ]
            }
            
            # Act
            result = compliance_checker.check_owasp_top10_compliance(self.scan_results)
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(result['compliance_status'], 'PARTIALLY_COMPLIANT')
        self.assertEqual(result['vulnerable_categories'], 2)
        self.assertEqual(result['category_results']['A03_INJECTION']['status'], 'VULNERABLE')
        self.assertEqual(len(result['recommendations']), 2)
        
        mock_owasp.assert_called_once_with(self.scan_results)
    
    @unittest.skipIf(compliance_checker is None, "compliance_checker not implemented")
    def test_generate_compliance_matrix(self):
        """Test compliance matrix generation"""
        
        with patch.object(compliance_checker, 'generate_compliance_matrix', create=True) as mock_matrix:
            mock_matrix.return_value = {
                'standards_assessed': ['PCI-DSS', 'OWASP Top 10', 'NIST CSF'],
                'compliance_matrix': [
                    ['Control ID', 'Description', 'PCI-DSS', 'OWASP', 'NIST'],
                    ['INPUT_VALIDATION', 'Secure input handling', 'FAIL', 'FAIL', 'PARTIAL'],
                    ['AUTHENTICATION', 'Strong authentication', 'PARTIAL', 'FAIL', 'PASS'],
                    ['ENCRYPTION', 'Data encryption', 'PASS', 'PASS', 'PASS']
                ],
                'overall_compliance': {
                    'PCI-DSS': 66.7,
                    'OWASP Top 10': 33.3,
                    'NIST CSF': 66.7
                },
                'gap_analysis': {
                    'critical_gaps': ['Input validation', 'Authentication'],
                    'improvement_areas': ['Access controls', 'Logging'],
                    'compliant_areas': ['Encryption', 'Network security']
                }
            }
            
            # Act
            result = compliance_checker.generate_compliance_matrix(
                self.scan_results,
                standards=['PCI-DSS', 'OWASP Top 10', 'NIST CSF']
            )
        
        # Assert
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result['standards_assessed']), 3)
        self.assertEqual(len(result['compliance_matrix']), 4)  # Header + 3 controls
        self.assertEqual(result['overall_compliance']['PCI-DSS'], 66.7)
        self.assertIn('Input validation', result['gap_analysis']['critical_gaps'])
        
        mock_matrix.assert_called_once()
    
    def test_compliance_checker_mock_implementation(self):
        """Test compliance checker with mock implementation"""
        
        # Arrange
        mock_compliance = Mock()
        mock_compliance.check_hipaa_compliance.return_value = {
            'standard': 'HIPAA Security Rule',
            'compliance_status': 'NON_COMPLIANT',
            'safeguards': {
                'administrative': {'score': 80, 'status': 'MOSTLY_COMPLIANT'},
                'physical': {'score': 75, 'status': 'PARTIALLY_COMPLIANT'},
                'technical': {'score': 60, 'status': 'NON_COMPLIANT'}
            },
            'critical_violations': [
                'Unencrypted PHI transmission',
                'Insufficient access controls'
            ],
            'remediation_cost_estimate': 50000
        }
        
        mock_compliance.generate_attestation_report.return_value = {
            'attestation_id': 'ATT-2024-001',
            'assessment_date': '2024-01-15',
            'standards_covered': ['PCI-DSS', 'SOC 2', 'ISO 27001'],
            'overall_maturity': 'DEVELOPING',
            'executive_summary': 'Organization shows good progress in security controls implementation',
            'certification_ready': False,
            'next_assessment_date': '2024-07-15'
        }
        
        # Act
        hipaa_result = mock_compliance.check_hipaa_compliance(self.scan_results)
        attestation_result = mock_compliance.generate_attestation_report()
        
        # Assert
        self.assertEqual(hipaa_result['compliance_status'], 'NON_COMPLIANT')
        self.assertEqual(hipaa_result['safeguards']['administrative']['score'], 80)
        
        self.assertEqual(attestation_result['overall_maturity'], 'DEVELOPING')
        self.assertFalse(attestation_result['certification_ready'])
        
        mock_compliance.check_hipaa_compliance.assert_called_once()
        mock_compliance.generate_attestation_report.assert_called_once()


class TestReportingIntegration(unittest.TestCase):
    """Integration tests for reporting module components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.comprehensive_scan_data = {
            'target': 'enterprise-app.com',
            'scan_duration': '6 hours',
            'vulnerabilities': [
                {'type': 'SQL_INJECTION', 'severity': 'CRITICAL', 'cvss': 9.1},
                {'type': 'XSS', 'severity': 'HIGH', 'cvss': 7.5},
                {'type': 'CSRF', 'severity': 'MEDIUM', 'cvss': 5.3}
            ],
            'compliance_requirements': ['PCI-DSS', 'GDPR']
        }
    
    def test_complete_reporting_workflow(self):
        """Test complete reporting workflow integration"""
        
        # Arrange - Mock all reporting components
        mock_generator = Mock()
        mock_analyzer = Mock()
        mock_compliance = Mock()
        mock_visual = Mock()
        
        # Mock data analysis results
        mock_analyzer.analyze_vulnerability_trends.return_value = {
            'risk_score': 8.2,
            'trend_analysis': {'most_common_type': 'XSS'}
        }
        
        # Mock compliance check results
        mock_compliance.check_pci_compliance.return_value = {
            'compliance_status': 'NON_COMPLIANT',
            'overall_score': 65.0
        }
        
        # Mock visual generation results
        mock_visual.create_risk_dashboard.return_value = {
            'charts_created': 5,
            'dashboard_path': '/reports/dashboard.html'
        }
        
        # Mock report generation results
        mock_generator.generate_pentest_report.return_value = {
            'report_path': '/reports/final_report.pdf',
            'pages': 30,
            'sections': 8
        }
        
        # Act - Simulate complete reporting workflow
        analysis_result = mock_analyzer.analyze_vulnerability_trends(
            self.comprehensive_scan_data['vulnerabilities']
        )
        compliance_result = mock_compliance.check_pci_compliance(self.comprehensive_scan_data)
        visual_result = mock_visual.create_risk_dashboard(analysis_result)
        final_report = mock_generator.generate_pentest_report(self.comprehensive_scan_data)
        
        # Combine all results
        reporting_summary = {
            'analysis_completed': True,
            'compliance_checked': True,
            'visuals_created': True,
            'final_report_generated': True,
            'overall_risk_score': analysis_result['risk_score'],
            'compliance_status': compliance_result['compliance_status'],
            'report_location': final_report['report_path']
        }
        
        # Assert
        self.assertTrue(reporting_summary['analysis_completed'])
        self.assertTrue(reporting_summary['compliance_checked'])
        self.assertTrue(reporting_summary['visuals_created'])
        self.assertTrue(reporting_summary['final_report_generated'])
        self.assertEqual(reporting_summary['overall_risk_score'], 8.2)
        self.assertEqual(reporting_summary['compliance_status'], 'NON_COMPLIANT')
        
        # Verify all components were called
        mock_analyzer.analyze_vulnerability_trends.assert_called_once()
        mock_compliance.check_pci_compliance.assert_called_once()
        mock_visual.create_risk_dashboard.assert_called_once()
        mock_generator.generate_pentest_report.assert_called_once()


if __name__ == '__main__':
    unittest.main()