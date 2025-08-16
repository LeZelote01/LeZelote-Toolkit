#!/usr/bin/env python3
"""
Compliance Checker Module - Pentest USB Toolkit

This module implements comprehensive compliance checking capabilities including
regulatory framework mapping, compliance gap analysis, audit trail generation,
and standards validation.

Author: Pentest USB Team
Version: 1.0.0
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

# Internal imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from core.utils.logging_handler import setup_logger
from core.utils.error_handler import handle_error


class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    GDPR = "gdpr"
    SOX = "sox"
    NIST = "nist"
    ISO_27001 = "iso_27001"
    CIS = "cis"
    OWASP = "owasp"


class ComplianceStatus(Enum):
    """Compliance status levels."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


@dataclass
class ComplianceRequirement:
    """Data structure for compliance requirements."""
    framework: ComplianceFramework
    requirement_id: str
    title: str
    description: str
    category: str
    priority: str  # high, medium, low
    testing_procedures: List[str]
    evidence_required: List[str]


@dataclass
class ComplianceResult:
    """Result of compliance checking."""
    requirement: ComplianceRequirement
    status: ComplianceStatus
    score: float  # 0.0 to 1.0
    findings: List[str]
    evidence: List[str]
    recommendations: List[str]
    last_tested: str


@dataclass
class ComplianceReport:
    """Comprehensive compliance report."""
    framework: ComplianceFramework
    overall_score: float
    compliant_count: int
    non_compliant_count: int
    partially_compliant_count: int
    total_requirements: int
    results: List[ComplianceResult]
    summary: Dict[str, Any]
    recommendations: List[str]
    report_date: str


class ComplianceChecker:
    """Main class for compliance checking operations."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = setup_logger(__name__)
        
        # Load compliance frameworks and requirements
        self.frameworks = self._load_compliance_frameworks()
        
        # Evidence mapping
        self.evidence_mappings = self._load_evidence_mappings()
        
        self.logger.info("Initialized ComplianceChecker")

    def _load_compliance_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """Load compliance framework definitions and requirements."""
        return {
            ComplianceFramework.PCI_DSS.value: {
                'name': 'Payment Card Industry Data Security Standard',
                'version': '4.0',
                'requirements': {
                    '1': {
                        'title': 'Install and maintain network security controls',
                        'category': 'Network Security',
                        'priority': 'high',
                        'testing_procedures': [
                            'Verify firewall configuration',
                            'Test network segmentation',
                            'Review access controls'
                        ]
                    },
                    '2': {
                        'title': 'Apply secure configurations to all system components',
                        'category': 'System Configuration',
                        'priority': 'high',
                        'testing_procedures': [
                            'Review default passwords',
                            'Verify secure configurations',
                            'Test unnecessary services'
                        ]
                    },
                    '3': {
                        'title': 'Protect stored cardholder data',
                        'category': 'Data Protection',
                        'priority': 'critical',
                        'testing_procedures': [
                            'Verify encryption of stored data',
                            'Test key management procedures',
                            'Review data retention policies'
                        ]
                    },
                    '6': {
                        'title': 'Develop and maintain secure systems and software',
                        'category': 'Secure Development',
                        'priority': 'high',
                        'testing_procedures': [
                            'Review vulnerability management',
                            'Test web application security',
                            'Verify secure coding practices'
                        ]
                    },
                    '11': {
                        'title': 'Test security of systems and networks regularly',
                        'category': 'Security Testing',
                        'priority': 'high',
                        'testing_procedures': [
                            'Perform vulnerability scans',
                            'Conduct penetration testing',
                            'Review security monitoring'
                        ]
                    }
                }
            },
            ComplianceFramework.OWASP.value: {
                'name': 'OWASP Top 10 Web Application Security Risks',
                'version': '2021',
                'requirements': {
                    'A01': {
                        'title': 'Broken Access Control',
                        'category': 'Access Control',
                        'priority': 'critical',
                        'testing_procedures': [
                            'Test for privilege escalation',
                            'Verify access controls',
                            'Test authorization bypass'
                        ]
                    },
                    'A02': {
                        'title': 'Cryptographic Failures',
                        'category': 'Cryptography',
                        'priority': 'high',
                        'testing_procedures': [
                            'Test encryption implementation',
                            'Verify key management',
                            'Test data in transit protection'
                        ]
                    },
                    'A03': {
                        'title': 'Injection',
                        'category': 'Input Validation',
                        'priority': 'critical',
                        'testing_procedures': [
                            'Test for SQL injection',
                            'Test for command injection',
                            'Verify input validation'
                        ]
                    },
                    'A06': {
                        'title': 'Vulnerable and Outdated Components',
                        'category': 'Component Security',
                        'priority': 'high',
                        'testing_procedures': [
                            'Inventory all components',
                            'Check for known vulnerabilities',
                            'Verify update procedures'
                        ]
                    }
                }
            },
            ComplianceFramework.NIST.value: {
                'name': 'NIST Cybersecurity Framework',
                'version': '1.1',
                'requirements': {
                    'ID.AM': {
                        'title': 'Asset Management',
                        'category': 'Identify',
                        'priority': 'high',
                        'testing_procedures': [
                            'Verify asset inventory',
                            'Test asset classification',
                            'Review ownership assignments'
                        ]
                    },
                    'PR.AC': {
                        'title': 'Access Control',
                        'category': 'Protect',
                        'priority': 'high',
                        'testing_procedures': [
                            'Test identity management',
                            'Verify access permissions',
                            'Review privileged accounts'
                        ]
                    },
                    'DE.CM': {
                        'title': 'Security Continuous Monitoring',
                        'category': 'Detect',
                        'priority': 'medium',
                        'testing_procedures': [
                            'Review monitoring systems',
                            'Test detection capabilities',
                            'Verify log analysis'
                        ]
                    }
                }
            }
        }

    def _load_evidence_mappings(self) -> Dict[str, List[str]]:
        """Load mappings between vulnerabilities and compliance requirements."""
        return {
            'sql_injection': ['PCI_DSS_6', 'OWASP_A03'],
            'cross_site_scripting': ['PCI_DSS_6', 'OWASP_A03'],
            'broken_access_control': ['PCI_DSS_1', 'OWASP_A01', 'NIST_PR.AC'],
            'cryptographic_failure': ['PCI_DSS_3', 'OWASP_A02'],
            'vulnerable_components': ['PCI_DSS_6', 'OWASP_A06'],
            'unencrypted_data': ['PCI_DSS_3', 'OWASP_A02'],
            'weak_authentication': ['PCI_DSS_2', 'NIST_PR.AC'],
            'missing_security_updates': ['PCI_DSS_6', 'OWASP_A06'],
            'insufficient_logging': ['NIST_DE.CM'],
            'network_segmentation': ['PCI_DSS_1']
        }

    @handle_error
    def assess_compliance(self, scan_results: Dict[str, Any], 
                         frameworks: List[ComplianceFramework] = None) -> Dict[str, Any]:
        """
        Assess compliance against specified frameworks.
        
        Args:
            scan_results: Results from vulnerability scans and assessments
            frameworks: List of frameworks to assess against
            
        Returns:
            Dictionary containing compliance assessment results
        """
        self.logger.info("Starting compliance assessment")
        
        if frameworks is None:
            frameworks = [ComplianceFramework.OWASP, ComplianceFramework.PCI_DSS]
        
        results = {
            'assessment_date': datetime.now().isoformat(),
            'frameworks_assessed': [f.value for f in frameworks],
            'compliance_reports': [],
            'overall_summary': {},
            'recommendations': [],
            'execution_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Generate compliance reports for each framework
            for framework in frameworks:
                self.logger.info(f"Assessing compliance for {framework.value}")
                
                report = self._assess_framework_compliance(framework, scan_results)
                results['compliance_reports'].append(report.__dict__)
            
            # Generate overall summary
            overall_summary = self._generate_overall_summary(results['compliance_reports'])
            results['overall_summary'] = overall_summary
            
            # Generate cross-framework recommendations
            recommendations = self._generate_cross_framework_recommendations(results['compliance_reports'])
            results['recommendations'] = recommendations
        
        except Exception as e:
            self.logger.error(f"Error during compliance assessment: {e}")
            results['error'] = str(e)
        
        finally:
            results['execution_time'] = time.time() - start_time
            
        self.logger.info(f"Compliance assessment completed in {results['execution_time']:.2f} seconds")
        return results

    def _assess_framework_compliance(self, framework: ComplianceFramework, 
                                   scan_results: Dict[str, Any]) -> ComplianceReport:
        """Assess compliance against a specific framework."""
        framework_def = self.frameworks.get(framework.value, {})
        requirements = framework_def.get('requirements', {})
        
        compliance_results = []
        compliant_count = 0
        non_compliant_count = 0
        partially_compliant_count = 0
        
        # Assess each requirement
        for req_id, req_def in requirements.items():
            requirement = ComplianceRequirement(
                framework=framework,
                requirement_id=req_id,
                title=req_def['title'],
                description=req_def.get('description', ''),
                category=req_def['category'],
                priority=req_def['priority'],
                testing_procedures=req_def['testing_procedures'],
                evidence_required=req_def.get('evidence_required', [])
            )
            
            # Assess compliance for this requirement
            result = self._assess_requirement_compliance(requirement, scan_results)
            compliance_results.append(result)
            
            # Count status
            if result.status == ComplianceStatus.COMPLIANT:
                compliant_count += 1
            elif result.status == ComplianceStatus.NON_COMPLIANT:
                non_compliant_count += 1
            elif result.status == ComplianceStatus.PARTIALLY_COMPLIANT:
                partially_compliant_count += 1
        
        # Calculate overall score
        total_requirements = len(requirements)
        overall_score = (compliant_count + (partially_compliant_count * 0.5)) / total_requirements if total_requirements > 0 else 0.0
        
        # Generate framework-specific recommendations
        recommendations = self._generate_framework_recommendations(compliance_results, framework)
        
        return ComplianceReport(
            framework=framework,
            overall_score=overall_score,
            compliant_count=compliant_count,
            non_compliant_count=non_compliant_count,
            partially_compliant_count=partially_compliant_count,
            total_requirements=total_requirements,
            results=compliance_results,
            summary={
                'framework_name': framework_def.get('name', ''),
                'version': framework_def.get('version', ''),
                'compliance_percentage': overall_score * 100
            },
            recommendations=recommendations,
            report_date=datetime.now().isoformat()
        )

    def _assess_requirement_compliance(self, requirement: ComplianceRequirement, 
                                     scan_results: Dict[str, Any]) -> ComplianceResult:
        """Assess compliance for a specific requirement."""
        findings = []
        evidence = []
        recommendations = []
        
        # Map scan results to compliance evidence
        if requirement.framework == ComplianceFramework.OWASP:
            status, score = self._assess_owasp_requirement(requirement, scan_results, findings, evidence)
        elif requirement.framework == ComplianceFramework.PCI_DSS:
            status, score = self._assess_pci_requirement(requirement, scan_results, findings, evidence)
        elif requirement.framework == ComplianceFramework.NIST:
            status, score = self._assess_nist_requirement(requirement, scan_results, findings, evidence)
        else:
            status = ComplianceStatus.UNKNOWN
            score = 0.0
        
        # Generate specific recommendations based on findings
        if status != ComplianceStatus.COMPLIANT:
            recommendations = self._generate_requirement_recommendations(requirement, findings)
        
        return ComplianceResult(
            requirement=requirement,
            status=status,
            score=score,
            findings=findings,
            evidence=evidence,
            recommendations=recommendations,
            last_tested=datetime.now().isoformat()
        )

    def _assess_owasp_requirement(self, requirement: ComplianceRequirement, 
                                scan_results: Dict[str, Any], 
                                findings: List[str], evidence: List[str]) -> Tuple[ComplianceStatus, float]:
        """Assess OWASP Top 10 requirement compliance."""
        vulnerabilities = scan_results.get('vulnerability', {}).get('vulnerabilities', [])
        
        req_id = requirement.requirement_id
        
        if req_id == 'A01':  # Broken Access Control
            access_control_vulns = [v for v in vulnerabilities 
                                  if 'access control' in v.get('title', '').lower() or 
                                     'authorization' in v.get('title', '').lower()]
            
            if not access_control_vulns:
                return ComplianceStatus.COMPLIANT, 1.0
            else:
                critical_high_count = len([v for v in access_control_vulns 
                                         if v.get('severity') in ['critical', 'high']])
                if critical_high_count > 0:
                    findings.append(f"Found {critical_high_count} critical/high severity access control vulnerabilities")
                    return ComplianceStatus.NON_COMPLIANT, 0.0
                else:
                    findings.append(f"Found {len(access_control_vulns)} low/medium severity access control issues")
                    return ComplianceStatus.PARTIALLY_COMPLIANT, 0.5
        
        elif req_id == 'A02':  # Cryptographic Failures
            crypto_vulns = [v for v in vulnerabilities 
                          if any(keyword in v.get('title', '').lower() 
                                for keyword in ['ssl', 'tls', 'encryption', 'crypto', 'certificate'])]
            
            if not crypto_vulns:
                return ComplianceStatus.COMPLIANT, 1.0
            else:
                critical_count = len([v for v in crypto_vulns if v.get('severity') == 'critical'])
                if critical_count > 0:
                    findings.append(f"Found {critical_count} critical cryptographic vulnerabilities")
                    return ComplianceStatus.NON_COMPLIANT, 0.0
                else:
                    return ComplianceStatus.PARTIALLY_COMPLIANT, 0.7
        
        elif req_id == 'A03':  # Injection
            injection_vulns = [v for v in vulnerabilities 
                             if any(keyword in v.get('title', '').lower() 
                                   for keyword in ['injection', 'sqli', 'xss', 'command injection'])]
            
            if not injection_vulns:
                return ComplianceStatus.COMPLIANT, 1.0
            else:
                critical_high_count = len([v for v in injection_vulns 
                                         if v.get('severity') in ['critical', 'high']])
                if critical_high_count > 0:
                    findings.append(f"Found {critical_high_count} critical/high severity injection vulnerabilities")
                    return ComplianceStatus.NON_COMPLIANT, 0.0
                else:
                    return ComplianceStatus.PARTIALLY_COMPLIANT, 0.6
        
        elif req_id == 'A06':  # Vulnerable and Outdated Components
            component_vulns = [v for v in vulnerabilities 
                             if any(keyword in v.get('title', '').lower() 
                                   for keyword in ['outdated', 'vulnerable component', 'cve', 'version'])]
            
            if not component_vulns:
                return ComplianceStatus.COMPLIANT, 1.0
            else:
                high_risk_count = len([v for v in component_vulns if v.get('cvss_score', 0) >= 7.0])
                if high_risk_count > 5:
                    findings.append(f"Found {high_risk_count} high-risk vulnerable components")
                    return ComplianceStatus.NON_COMPLIANT, 0.0
                elif high_risk_count > 0:
                    findings.append(f"Found {high_risk_count} vulnerable components")
                    return ComplianceStatus.PARTIALLY_COMPLIANT, 0.6
                else:
                    return ComplianceStatus.COMPLIANT, 1.0
        
        return ComplianceStatus.UNKNOWN, 0.5

    def _assess_pci_requirement(self, requirement: ComplianceRequirement, 
                              scan_results: Dict[str, Any], 
                              findings: List[str], evidence: List[str]) -> Tuple[ComplianceStatus, float]:
        """Assess PCI DSS requirement compliance."""
        vulnerabilities = scan_results.get('vulnerability', {}).get('vulnerabilities', [])
        network_data = scan_results.get('reconnaissance', {})
        
        req_id = requirement.requirement_id
        
        if req_id == '1':  # Network security controls
            # Check for network segmentation and firewall evidence
            open_ports = []
            if 'network_scan' in network_data:
                hosts = network_data['network_scan'].get('hosts', {})
                for host, data in hosts.items():
                    open_ports.extend(data.get('ports', []))
            
            high_risk_ports = [p for p in open_ports if p.get('port') in [21, 23, 135, 139, 445]]
            
            if len(high_risk_ports) > 0:
                findings.append(f"Found {len(high_risk_ports)} high-risk open ports")
                return ComplianceStatus.NON_COMPLIANT, 0.3
            else:
                return ComplianceStatus.COMPLIANT, 1.0
        
        elif req_id == '3':  # Protect stored cardholder data
            # Look for encryption-related vulnerabilities
            encryption_vulns = [v for v in vulnerabilities 
                              if any(keyword in v.get('title', '').lower() 
                                    for keyword in ['unencrypted', 'weak encryption', 'plaintext'])]
            
            if encryption_vulns:
                critical_count = len([v for v in encryption_vulns if v.get('severity') == 'critical'])
                if critical_count > 0:
                    findings.append(f"Found {critical_count} critical encryption vulnerabilities")
                    return ComplianceStatus.NON_COMPLIANT, 0.0
                else:
                    return ComplianceStatus.PARTIALLY_COMPLIANT, 0.6
            else:
                return ComplianceStatus.COMPLIANT, 1.0
        
        elif req_id == '6':  # Secure systems and software
            # Check for web application vulnerabilities
            web_vulns = [v for v in vulnerabilities 
                        if v.get('category') == 'web_application']
            
            if not web_vulns:
                return ComplianceStatus.COMPLIANT, 1.0
            else:
                critical_high_count = len([v for v in web_vulns 
                                         if v.get('severity') in ['critical', 'high']])
                total_vulns = len(web_vulns)
                
                if critical_high_count > 0:
                    findings.append(f"Found {critical_high_count} critical/high web application vulnerabilities")
                    return ComplianceStatus.NON_COMPLIANT, 0.2
                elif total_vulns > 10:
                    findings.append(f"Found {total_vulns} web application vulnerabilities")
                    return ComplianceStatus.PARTIALLY_COMPLIANT, 0.5
                else:
                    return ComplianceStatus.PARTIALLY_COMPLIANT, 0.7
        
        elif req_id == '11':  # Test security regularly
            # This requirement is inherently met by performing the scan
            evidence.append("Vulnerability scan performed as part of regular security testing")
            return ComplianceStatus.COMPLIANT, 1.0
        
        return ComplianceStatus.UNKNOWN, 0.5

    def _assess_nist_requirement(self, requirement: ComplianceRequirement, 
                               scan_results: Dict[str, Any], 
                               findings: List[str], evidence: List[str]) -> Tuple[ComplianceStatus, float]:
        """Assess NIST Framework requirement compliance."""
        # Simplified NIST assessment
        req_id = requirement.requirement_id
        
        if req_id == 'ID.AM':  # Asset Management
            hosts_count = len(scan_results.get('reconnaissance', {}).get('network_scan', {}).get('hosts', {}))
            if hosts_count > 0:
                evidence.append(f"Identified {hosts_count} network assets")
                return ComplianceStatus.PARTIALLY_COMPLIANT, 0.7  # Partial because we only have network view
            else:
                return ComplianceStatus.UNKNOWN, 0.5
        
        elif req_id == 'PR.AC':  # Access Control
            auth_vulns = [v for v in scan_results.get('vulnerability', {}).get('vulnerabilities', []) 
                         if 'authentication' in v.get('title', '').lower() or 
                            'authorization' in v.get('title', '').lower()]
            
            if not auth_vulns:
                return ComplianceStatus.COMPLIANT, 1.0
            else:
                findings.append(f"Found {len(auth_vulns)} authentication/authorization issues")
                return ComplianceStatus.PARTIALLY_COMPLIANT, 0.6
        
        elif req_id == 'DE.CM':  # Security Continuous Monitoring
            # This is partially met by performing vulnerability scanning
            evidence.append("Vulnerability monitoring performed")
            return ComplianceStatus.PARTIALLY_COMPLIANT, 0.6
        
        return ComplianceStatus.UNKNOWN, 0.5

    def _generate_requirement_recommendations(self, requirement: ComplianceRequirement, 
                                           findings: List[str]) -> List[str]:
        """Generate specific recommendations for a requirement."""
        recommendations = []
        
        if requirement.framework == ComplianceFramework.OWASP:
            if requirement.requirement_id == 'A01':
                recommendations.extend([
                    "Implement proper access control mechanisms",
                    "Review and test authorization logic",
                    "Apply principle of least privilege"
                ])
            elif requirement.requirement_id == 'A03':
                recommendations.extend([
                    "Implement input validation and parameterized queries",
                    "Use prepared statements for database access",
                    "Apply output encoding"
                ])
        
        elif requirement.framework == ComplianceFramework.PCI_DSS:
            if requirement.requirement_id == '1':
                recommendations.extend([
                    "Implement network segmentation",
                    "Configure firewall rules to deny all unnecessary traffic",
                    "Regularly review and update network access controls"
                ])
            elif requirement.requirement_id == '6':
                recommendations.extend([
                    "Implement secure coding practices",
                    "Perform regular vulnerability assessments",
                    "Establish change management procedures"
                ])
        
        return recommendations

    def _generate_framework_recommendations(self, results: List[ComplianceResult], 
                                         framework: ComplianceFramework) -> List[str]:
        """Generate framework-wide recommendations."""
        recommendations = []
        
        # Analyze non-compliant requirements
        non_compliant = [r for r in results if r.status == ComplianceStatus.NON_COMPLIANT]
        partially_compliant = [r for r in results if r.status == ComplianceStatus.PARTIALLY_COMPLIANT]
        
        if len(non_compliant) > 0:
            recommendations.append(f"Priority action required: {len(non_compliant)} requirements are non-compliant")
        
        if len(partially_compliant) > 0:
            recommendations.append(f"Improvement needed: {len(partially_compliant)} requirements are partially compliant")
        
        # Framework-specific recommendations
        if framework == ComplianceFramework.OWASP:
            recommendations.append("Follow OWASP secure coding guidelines")
            recommendations.append("Implement regular security testing in SDLC")
        
        elif framework == ComplianceFramework.PCI_DSS:
            recommendations.append("Consider engaging a Qualified Security Assessor (QSA)")
            recommendations.append("Implement continuous monitoring for PCI DSS compliance")
        
        return recommendations

    def _generate_overall_summary(self, compliance_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall summary across all frameworks."""
        total_requirements = sum(report['total_requirements'] for report in compliance_reports)
        total_compliant = sum(report['compliant_count'] for report in compliance_reports)
        total_non_compliant = sum(report['non_compliant_count'] for report in compliance_reports)
        
        overall_compliance_rate = (total_compliant / total_requirements * 100) if total_requirements > 0 else 0
        
        return {
            'total_frameworks_assessed': len(compliance_reports),
            'total_requirements_assessed': total_requirements,
            'overall_compliance_rate': overall_compliance_rate,
            'total_compliant': total_compliant,
            'total_non_compliant': total_non_compliant,
            'frameworks_summary': [
                {
                    'framework': report['framework'],
                    'compliance_rate': report['summary']['compliance_percentage'],
                    'status': 'good' if report['summary']['compliance_percentage'] >= 80 else
                             'fair' if report['summary']['compliance_percentage'] >= 60 else 'poor'
                }
                for report in compliance_reports
            ]
        }

    def _generate_cross_framework_recommendations(self, compliance_reports: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations that span multiple frameworks."""
        recommendations = []
        
        # Analyze common themes across frameworks
        all_findings = []
        for report in compliance_reports:
            for result in report['results']:
                all_findings.extend(result['findings'])
        
        # Common security themes
        if any('injection' in finding.lower() for finding in all_findings):
            recommendations.append("Implement comprehensive input validation across all applications")
        
        if any('encryption' in finding.lower() for finding in all_findings):
            recommendations.append("Review and strengthen encryption implementations")
        
        if any('access control' in finding.lower() for finding in all_findings):
            recommendations.append("Implement enterprise-wide access control framework")
        
        # Overall recommendations
        recommendations.extend([
            "Establish regular compliance monitoring processes",
            "Implement security awareness training programs",
            "Consider automated compliance monitoring tools"
        ])
        
        return recommendations


def main():
    """Main function for testing the module."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Compliance Checker Module")
    parser.add_argument("--input-file", required=True, help="Input JSON file with scan results")
    parser.add_argument("--frameworks", nargs='+', 
                       choices=['pci_dss', 'owasp', 'nist', 'iso_27001', 'hipaa', 'gdpr'],
                       default=['owasp', 'pci_dss'], help="Compliance frameworks to assess")
    parser.add_argument("--output-file", help="Output file for compliance report")
    
    args = parser.parse_args()
    
    # Load scan data
    with open(args.input_file, 'r') as f:
        scan_data = json.load(f)
    
    # Convert framework strings to enums
    framework_map = {
        'pci_dss': ComplianceFramework.PCI_DSS,
        'owasp': ComplianceFramework.OWASP,
        'nist': ComplianceFramework.NIST,
        'iso_27001': ComplianceFramework.ISO_27001,
        'hipaa': ComplianceFramework.HIPAA,
        'gdpr': ComplianceFramework.GDPR
    }
    
    frameworks = [framework_map[f] for f in args.frameworks if f in framework_map]
    
    # Initialize compliance checker
    checker = ComplianceChecker()
    
    # Perform compliance assessment
    results = checker.assess_compliance(scan_data, frameworks)
    
    # Save results if output file specified
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Compliance report saved to {args.output_file}")
    
    # Print summary
    print(f"\n=== Compliance Assessment Results ===")
    print(f"Frameworks assessed: {', '.join(args.frameworks)}")
    print(f"Overall compliance rate: {results['overall_summary'].get('overall_compliance_rate', 0):.1f}%")
    print(f"Total requirements: {results['overall_summary'].get('total_requirements_assessed', 0)}")
    print(f"Compliant: {results['overall_summary'].get('total_compliant', 0)}")
    print(f"Non-compliant: {results['overall_summary'].get('total_non_compliant', 0)}")
    print(f"Execution time: {results['execution_time']:.2f} seconds")


if __name__ == "__main__":
    main()