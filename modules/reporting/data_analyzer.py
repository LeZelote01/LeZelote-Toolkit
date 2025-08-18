#!/usr/bin/env python3
"""
Data Analyzer Module - Pentest USB Toolkit

This module implements comprehensive data analysis capabilities including
result correlation, risk scoring algorithms, trend analysis, and statistical processing.

Author: Pentest USB Team
Version: 1.0.0
"""

import os
import sys
import json
import logging
import statistics
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import Counter, defaultdict
from datetime import datetime, timedelta

# Internal imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from core.utils.logging_handler import setup_logger
from core.utils.error_handler import handle_error
from core.db.sqlite_manager import DatabaseManager


class RiskLevel(Enum):
    """Risk level categories."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityCategory(Enum):
    """Vulnerability categories."""
    WEB_APPLICATION = "web_application"
    NETWORK = "network"
    SYSTEM = "system"
    DATABASE = "database"
    WIRELESS = "wireless"
    SOCIAL_ENGINEERING = "social_engineering"
    PHYSICAL = "physical"


@dataclass
class AnalysisResult:
    """Data structure for analysis results."""
    category: str
    value: Union[int, float, str, Dict, List]
    description: str
    confidence: float = 1.0
    timestamp: Optional[str] = None


@dataclass
class RiskScore:
    """Data structure for risk scoring."""
    overall_score: float
    category_scores: Dict[str, float]
    risk_factors: List[str]
    mitigation_priority: List[str]
    business_impact: str


@dataclass
class TrendAnalysis:
    """Data structure for trend analysis."""
    trend_type: str
    direction: str  # increasing, decreasing, stable
    percentage_change: float
    time_period: str
    data_points: List[Tuple[str, float]]


class DataAnalyzer:
    """Main class for data analysis operations."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = setup_logger(__name__)
        self.db_manager = DatabaseManager()
        
        # Analysis cache
        self.analysis_cache: Dict[str, Any] = {}
        
        # Risk scoring weights
        self.risk_weights = self._load_risk_weights()
        
        # CVSS scoring configuration
        self.cvss_config = self._load_cvss_config()
        
        self.logger.info("Initialized DataAnalyzer")

    def _load_risk_weights(self) -> Dict[str, float]:
        """Load risk scoring weights configuration."""
        return {
            'vulnerability_count': 0.3,
            'severity_distribution': 0.4,
            'exploitability': 0.2,
            'asset_criticality': 0.1,
            'network_exposure': 0.15,
            'data_sensitivity': 0.15,
            'compliance_impact': 0.1
        }

    def _load_cvss_config(self) -> Dict[str, Any]:
        """Load CVSS scoring configuration."""
        return {
            'base_metrics': {
                'attack_vector': {'network': 0.85, 'adjacent': 0.62, 'local': 0.55, 'physical': 0.2},
                'attack_complexity': {'low': 0.77, 'high': 0.44},
                'privileges_required': {'none': 0.85, 'low': 0.62, 'high': 0.27},
                'user_interaction': {'none': 0.85, 'required': 0.62},
                'scope': {'unchanged': 0.0, 'changed': 0.0},
                'impact': {'high': 0.56, 'low': 0.22, 'none': 0.0}
            },
            'temporal_metrics': {
                'exploit_code_maturity': {'not_defined': 1.0, 'high': 1.0, 'functional': 0.97, 'proof_of_concept': 0.94, 'unproven': 0.91},
                'remediation_level': {'not_defined': 1.0, 'official_fix': 0.95, 'temporary_fix': 0.96, 'workaround': 0.97, 'unavailable': 1.0},
                'report_confidence': {'not_defined': 1.0, 'confirmed': 1.0, 'reasonable': 0.96, 'unknown': 0.92}
            }
        }

    @handle_error
    def analyze_scan_results(self, scan_data: Dict[str, Any], 
                           analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Main method to analyze scan results and generate insights.
        
        Args:
            scan_data: Raw scan results from various modules
            analysis_type: Type of analysis (quick, standard, comprehensive)
            
        Returns:
            Dictionary containing analysis results and insights
        """
        self.logger.info("Starting scan results analysis")
        
        results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_type': analysis_type,
            'data_sources': list(scan_data.keys()),
            'vulnerability_analysis': {},
            'risk_assessment': {},
            'trend_analysis': {},
            'statistical_summary': {},
            'recommendations': [],
            'execution_time': 0
        }
        
        start_time = time.time()
        
        try:
            # Normalize and consolidate data
            normalized_data = self._normalize_scan_data(scan_data)
            
            # Vulnerability analysis
            vuln_analysis = self._analyze_vulnerabilities(normalized_data)
            results['vulnerability_analysis'] = vuln_analysis
            
            # Risk assessment and scoring
            risk_assessment = self._perform_risk_assessment(normalized_data, vuln_analysis)
            results['risk_assessment'] = risk_assessment
            
            # Statistical summary
            stats_summary = self._generate_statistical_summary(normalized_data)
            results['statistical_summary'] = stats_summary
            
            # Trend analysis (if historical data available)
            if self.config.get('enable_trend_analysis', True):
                trend_analysis = self._analyze_trends(normalized_data)
                results['trend_analysis'] = trend_analysis
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                vuln_analysis, risk_assessment, stats_summary
            )
            results['recommendations'] = recommendations
            
            # Correlation analysis
            correlations = self._perform_correlation_analysis(normalized_data)
            results['correlations'] = correlations
            
        except Exception as e:
            self.logger.error(f"Error during analysis: {e}")
            results['error'] = str(e)
        
        finally:
            results['execution_time'] = time.time() - start_time
            
        self.logger.info(f"Analysis completed in {results['execution_time']:.2f} seconds")
        return results

    def _normalize_scan_data(self, scan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize scan data from different modules into a consistent format."""
        self.logger.info("Normalizing scan data")
        
        normalized = {
            'vulnerabilities': [],
            'hosts': [],
            'services': [],
            'credentials': [],
            'network_topology': {},
            'metadata': {}
        }
        
        # Process reconnaissance data
        if 'reconnaissance' in scan_data:
            recon_data = scan_data['reconnaissance']
            
            # Extract hosts and services
            if 'network_scan' in recon_data:
                hosts = self._extract_hosts_from_nmap(recon_data['network_scan'])
                normalized['hosts'].extend(hosts)
            
            if 'domain_enum' in recon_data:
                domains = self._extract_domains(recon_data['domain_enum'])
                normalized['hosts'].extend(domains)
        
        # Process vulnerability data
        if 'vulnerability' in scan_data:
            vuln_data = scan_data['vulnerability']
            
            # Normalize vulnerability findings
            for scanner, results in vuln_data.items():
                vulns = self._normalize_vulnerabilities(scanner, results)
                normalized['vulnerabilities'].extend(vulns)
        
        # Process exploitation data
        if 'exploitation' in scan_data:
            exploit_data = scan_data['exploitation']
            
            # Mark exploitable vulnerabilities
            exploitable_vulns = self._extract_exploitable_vulns(exploit_data)
            normalized['exploitable_vulnerabilities'] = exploitable_vulns
        
        # Process credential data
        if 'credentials' in scan_data:
            cred_data = scan_data['credentials']
            normalized['credentials'] = self._normalize_credentials(cred_data)
        
        return normalized

    def _extract_hosts_from_nmap(self, nmap_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract host information from Nmap scan results."""
        hosts = []
        
        if isinstance(nmap_data, dict) and 'hosts' in nmap_data:
            for host_ip, host_info in nmap_data['hosts'].items():
                host_entry = {
                    'ip': host_ip,
                    'hostname': host_info.get('hostname', ''),
                    'os': host_info.get('os', 'unknown'),
                    'status': host_info.get('status', 'up'),
                    'ports': host_info.get('ports', []),
                    'services': self._extract_services_from_ports(host_info.get('ports', []))
                }
                hosts.append(host_entry)
        
        return hosts

    def _extract_services_from_ports(self, ports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract service information from port scan results."""
        services = []
        
        for port in ports:
            if port.get('state') == 'open':
                service = {
                    'port': port.get('port'),
                    'protocol': port.get('protocol', 'tcp'),
                    'service': port.get('service', 'unknown'),
                    'version': port.get('version', ''),
                    'product': port.get('product', ''),
                    'banner': port.get('banner', '')
                }
                services.append(service)
        
        return services

    def _normalize_vulnerabilities(self, scanner: str, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize vulnerability findings from different scanners."""
        vulnerabilities = []
        
        if scanner == 'nessus':
            vulns = self._normalize_nessus_vulns(results)
            vulnerabilities.extend(vulns)
        elif scanner == 'openvas':
            vulns = self._normalize_openvas_vulns(results)
            vulnerabilities.extend(vulns)
        elif scanner == 'zap':
            vulns = self._normalize_zap_vulns(results)
            vulnerabilities.extend(vulns)
        elif scanner == 'nuclei':
            vulns = self._normalize_nuclei_vulns(results)
            vulnerabilities.extend(vulns)
        
        return vulnerabilities

    def _normalize_nessus_vulns(self, nessus_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Normalize Nessus vulnerability results."""
        vulnerabilities = []
        
        if 'vulnerabilities' in nessus_results:
            for vuln in nessus_results['vulnerabilities']:
                normalized_vuln = {
                    'id': vuln.get('plugin_id', ''),
                    'title': vuln.get('plugin_name', ''),
                    'description': vuln.get('description', ''),
                    'severity': self._normalize_severity(vuln.get('severity', 'info')),
                    'cvss_score': vuln.get('cvss_score', 0.0),
                    'cve_ids': vuln.get('cve', []),
                    'solution': vuln.get('solution', ''),
                    'references': vuln.get('references', []),
                    'affected_hosts': vuln.get('hosts', []),
                    'category': self._categorize_vulnerability(vuln),
                    'scanner': 'nessus'
                }
                vulnerabilities.append(normalized_vuln)
        
        return vulnerabilities

    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity levels across different scanners."""
        severity_map = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low',
            'info': 'info',
            'informational': 'info',
            '4': 'critical',
            '3': 'high',
            '2': 'medium',
            '1': 'low',
            '0': 'info'
        }
        return severity_map.get(str(severity).lower(), 'info')

    def _categorize_vulnerability(self, vuln: Dict[str, Any]) -> str:
        """Categorize vulnerability based on its characteristics."""
        title = vuln.get('plugin_name', '').lower()
        description = vuln.get('description', '').lower()
        
        if any(keyword in title or keyword in description 
               for keyword in ['sql', 'injection', 'xss', 'csrf', 'web']):
            return VulnerabilityCategory.WEB_APPLICATION.value
        elif any(keyword in title or keyword in description 
                 for keyword in ['network', 'port', 'service', 'protocol']):
            return VulnerabilityCategory.NETWORK.value
        elif any(keyword in title or keyword in description 
                 for keyword in ['system', 'os', 'kernel', 'privilege']):
            return VulnerabilityCategory.SYSTEM.value
        elif any(keyword in title or keyword in description 
                 for keyword in ['database', 'mysql', 'postgres', 'oracle']):
            return VulnerabilityCategory.DATABASE.value
        elif any(keyword in title or keyword in description 
                 for keyword in ['wireless', 'wifi', 'wlan', 'bluetooth']):
            return VulnerabilityCategory.WIRELESS.value
        else:
            return VulnerabilityCategory.SYSTEM.value  # Default category

    def _analyze_vulnerabilities(self, normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive vulnerability analysis."""
        self.logger.info("Analyzing vulnerabilities")
        
        vulnerabilities = normalized_data.get('vulnerabilities', [])
        
        analysis = {
            'total_vulnerabilities': len(vulnerabilities),
            'severity_distribution': self._calculate_severity_distribution(vulnerabilities),
            'category_distribution': self._calculate_category_distribution(vulnerabilities),
            'cvss_statistics': self._calculate_cvss_statistics(vulnerabilities),
            'top_vulnerabilities': self._identify_top_vulnerabilities(vulnerabilities),
            'affected_hosts': self._analyze_affected_hosts(vulnerabilities),
            'exploitability_analysis': self._analyze_exploitability(vulnerabilities),
            'remediation_complexity': self._analyze_remediation_complexity(vulnerabilities)
        }
        
        return analysis

    def _calculate_severity_distribution(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate the distribution of vulnerability severities."""
        severity_counts = Counter()
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'info')
            severity_counts[severity] += 1
        
        total = len(vulnerabilities)
        
        return {
            'counts': dict(severity_counts),
            'percentages': {
                severity: (count / total * 100) if total > 0 else 0 
                for severity, count in severity_counts.items()
            },
            'total': total
        }

    def _calculate_category_distribution(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate the distribution of vulnerability categories."""
        category_counts = Counter()
        
        for vuln in vulnerabilities:
            category = vuln.get('category', 'unknown')
            category_counts[category] += 1
        
        total = len(vulnerabilities)
        
        return {
            'counts': dict(category_counts),
            'percentages': {
                category: (count / total * 100) if total > 0 else 0 
                for category, count in category_counts.items()
            }
        }

    def _calculate_cvss_statistics(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate CVSS score statistics."""
        cvss_scores = [vuln.get('cvss_score', 0.0) for vuln in vulnerabilities if vuln.get('cvss_score')]
        
        if not cvss_scores:
            return {
                'mean': 0.0,
                'median': 0.0,
                'max': 0.0,
                'min': 0.0,
                'std_dev': 0.0,
                'count': 0
            }
        
        return {
            'mean': statistics.mean(cvss_scores),
            'median': statistics.median(cvss_scores),
            'max': max(cvss_scores),
            'min': min(cvss_scores),
            'std_dev': statistics.stdev(cvss_scores) if len(cvss_scores) > 1 else 0.0,
            'count': len(cvss_scores)
        }

    def _identify_top_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify top vulnerabilities by severity and CVSS score."""
        # Sort by severity priority and CVSS score
        severity_priority = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1, 'info': 0}
        
        sorted_vulns = sorted(
            vulnerabilities,
            key=lambda v: (
                severity_priority.get(v.get('severity', 'info'), 0),
                v.get('cvss_score', 0.0)
            ),
            reverse=True
        )
        
        return sorted_vulns[:10]  # Top 10 vulnerabilities

    def _analyze_affected_hosts(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze which hosts are most affected by vulnerabilities."""
        host_vuln_count = defaultdict(int)
        host_severity_count = defaultdict(lambda: defaultdict(int))
        
        for vuln in vulnerabilities:
            affected_hosts = vuln.get('affected_hosts', [])
            severity = vuln.get('severity', 'info')
            
            for host in affected_hosts:
                host_vuln_count[host] += 1
                host_severity_count[host][severity] += 1
        
        # Sort hosts by vulnerability count
        most_affected = sorted(
            host_vuln_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'most_affected_hosts': most_affected[:10],
            'host_severity_breakdown': dict(host_severity_count),
            'total_affected_hosts': len(host_vuln_count)
        }

    def _perform_risk_assessment(self, normalized_data: Dict[str, Any], 
                                vuln_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment."""
        self.logger.info("Performing risk assessment")
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(normalized_data, vuln_analysis)
        
        # Identify critical risk factors
        critical_factors = self._identify_critical_risk_factors(normalized_data, vuln_analysis)
        
        # Generate business impact assessment
        business_impact = self._assess_business_impact(normalized_data, vuln_analysis)
        
        # Create mitigation roadmap
        mitigation_roadmap = self._create_mitigation_roadmap(normalized_data, vuln_analysis)
        
        return {
            'risk_score': risk_score,
            'critical_factors': critical_factors,
            'business_impact': business_impact,
            'mitigation_roadmap': mitigation_roadmap,
            'compliance_impact': self._assess_compliance_impact(normalized_data)
        }

    def _calculate_risk_score(self, normalized_data: Dict[str, Any], 
                            vuln_analysis: Dict[str, Any]) -> RiskScore:
        """Calculate overall risk score using weighted factors."""
        factors = {}
        
        # Vulnerability count factor
        total_vulns = vuln_analysis.get('total_vulnerabilities', 0)
        factors['vulnerability_count'] = min(total_vulns / 100.0, 1.0)  # Normalize to 0-1
        
        # Severity distribution factor
        severity_dist = vuln_analysis.get('severity_distribution', {}).get('percentages', {})
        critical_pct = severity_dist.get('critical', 0) / 100.0
        high_pct = severity_dist.get('high', 0) / 100.0
        factors['severity_distribution'] = (critical_pct * 0.6) + (high_pct * 0.4)
        
        # Exploitability factor
        exploitable_count = len(normalized_data.get('exploitable_vulnerabilities', []))
        factors['exploitability'] = min(exploitable_count / 10.0, 1.0)
        
        # Calculate weighted score
        weighted_score = 0.0
        for factor, weight in self.risk_weights.items():
            if factor in factors:
                weighted_score += factors[factor] * weight
        
        # Normalize to 0-10 scale
        overall_score = min(weighted_score * 10, 10.0)
        
        return RiskScore(
            overall_score=overall_score,
            category_scores=factors,
            risk_factors=self._identify_risk_factors(factors),
            mitigation_priority=self._prioritize_mitigation(factors),
            business_impact=self._determine_business_impact(overall_score)
        )

    def _generate_statistical_summary(self, normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive statistical summary."""
        return {
            'scan_coverage': {
                'total_hosts_scanned': len(normalized_data.get('hosts', [])),
                'total_services_identified': len(normalized_data.get('services', [])),
                'total_vulnerabilities': len(normalized_data.get('vulnerabilities', [])),
                'unique_vulnerability_types': len(set(
                    v.get('title', '') for v in normalized_data.get('vulnerabilities', [])
                ))
            },
            'discovery_statistics': self._calculate_discovery_stats(normalized_data),
            'temporal_analysis': self._analyze_temporal_patterns(normalized_data),
            'correlation_metrics': self._calculate_correlation_metrics(normalized_data)
        }

    def _generate_recommendations(self, vuln_analysis: Dict[str, Any], 
                                risk_assessment: Dict[str, Any], 
                                stats_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on analysis results."""
        recommendations = []
        
        # High-priority vulnerability remediation
        top_vulns = vuln_analysis.get('top_vulnerabilities', [])
        if top_vulns:
            recommendations.append({
                'category': 'immediate_action',
                'priority': 'high',
                'title': 'Address Critical Vulnerabilities',
                'description': f'Immediately remediate {len([v for v in top_vulns[:5] if v.get("severity") in ["critical", "high"]])} critical/high severity vulnerabilities',
                'affected_systems': len(vuln_analysis.get('affected_hosts', {}).get('most_affected_hosts', [])),
                'estimated_effort': 'high'
            })
        
        # Network segmentation recommendations
        if stats_summary.get('scan_coverage', {}).get('total_hosts_scanned', 0) > 10:
            recommendations.append({
                'category': 'architecture',
                'priority': 'medium',
                'title': 'Implement Network Segmentation',
                'description': 'Consider implementing network segmentation to limit attack surface',
                'affected_systems': 'network_infrastructure',
                'estimated_effort': 'medium'
            })
        
        return recommendations

    def calculate_cvss_score(self, base_metrics: Dict[str, str], 
                           temporal_metrics: Dict[str, str] = None) -> float:
        """Calculate CVSS v3.1 score based on provided metrics."""
        # This is a simplified CVSS calculation
        # Real implementation would follow official CVSS v3.1 specification
        
        base_score = 0.0
        
        # Base score calculation (simplified)
        av = self.cvss_config['base_metrics']['attack_vector'].get(
            base_metrics.get('attack_vector', 'network'), 0.85
        )
        ac = self.cvss_config['base_metrics']['attack_complexity'].get(
            base_metrics.get('attack_complexity', 'low'), 0.77
        )
        pr = self.cvss_config['base_metrics']['privileges_required'].get(
            base_metrics.get('privileges_required', 'none'), 0.85
        )
        
        # Simplified calculation
        base_score = (av + ac + pr) / 3 * 10
        
        # Apply temporal metrics if provided
        if temporal_metrics:
            temporal_multiplier = 1.0
            for metric, value in temporal_metrics.items():
                multiplier = self.cvss_config['temporal_metrics'].get(metric, {}).get(value, 1.0)
                temporal_multiplier *= multiplier
            
            base_score *= temporal_multiplier
        
        return min(base_score, 10.0)


def main():
    """Main function for testing the module."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Analyzer Module")
    parser.add_argument("--input-file", required=True, help="Input JSON file with scan results")
    parser.add_argument("--analysis-type", choices=['quick', 'standard', 'comprehensive'], 
                       default='standard', help="Type of analysis to perform")
    parser.add_argument("--output-file", help="Output file for analysis results")
    
    args = parser.parse_args()
    
    # Load scan data
    with open(args.input_file, 'r') as f:
        scan_data = json.load(f)
    
    # Initialize analyzer
    analyzer = DataAnalyzer()
    
    # Perform analysis
    results = analyzer.analyze_scan_results(scan_data, args.analysis_type)
    
    # Save results if output file specified
    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Analysis results saved to {args.output_file}")
    
    # Print summary
    print(f"\n=== Data Analysis Results ===")
    print(f"Analysis type: {results['analysis_type']}")
    print(f"Total vulnerabilities: {results['vulnerability_analysis'].get('total_vulnerabilities', 0)}")
    print(f"Risk score: {results['risk_assessment'].get('risk_score', {}).get('overall_score', 0):.2f}/10")
    print(f"Recommendations: {len(results['recommendations'])}")
    print(f"Execution time: {results['execution_time']:.2f} seconds")


if __name__ == "__main__":
    main()