"""
Pentest-USB Toolkit - Report Generator Module
============================================

Professional report generation for penetration testing results.
Supports multiple formats and customizable templates.

Author: Pentest-USB Development Team
Version: 1.0.0
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from ...core.utils.logging_handler import get_logger
from ...core.utils.error_handler import PentestError
from ...core.utils.file_ops import FileOperations


class ReportGenerator:
    """
    Professional penetration testing report generator
    """
    
    def __init__(self, templates_dir: str = "data/templates/reports"):
        """Initialize Report Generator"""
        self.logger = get_logger(__name__)
        self.templates_dir = Path(templates_dir)
        self.file_ops = FileOperations()
        
        # Ensure templates directory exists
        self.file_ops.ensure_directory(self.templates_dir)
        
        self.logger.info("ReportGenerator module initialized")
    
    def generate_report(self, scan_data: Dict[str, Any], 
                       report_type: str = "full", 
                       format_type: str = "html",
                       output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate penetration testing report
        
        Args:
            scan_data: Complete scan results and data
            report_type: Type of report (full, executive, technical, compliance)
            format_type: Output format (html, pdf, docx, markdown)
            output_path: Custom output path
            
        Returns:
            Report generation results
        """
        try:
            self.logger.info(f"Generating {report_type} report in {format_type} format")
            
            # Validate input data
            if not scan_data:
                raise PentestError("No scan data provided for report generation")
            
            # Process and structure report data
            report_data = self._process_report_data(scan_data, report_type)
            
            # Generate report based on format
            if format_type == "html":
                report_content = self._generate_html_report(report_data, report_type)
                file_extension = ".html"
            elif format_type == "markdown":
                report_content = self._generate_markdown_report(report_data, report_type)
                file_extension = ".md"
            elif format_type == "json":
                report_content = self._generate_json_report(report_data)
                file_extension = ".json"
            else:
                raise PentestError(f"Unsupported report format: {format_type}")
            
            # Determine output path
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"pentest_report_{report_type}_{timestamp}{file_extension}"
                output_path = Path("reports") / filename
            
            # Ensure output directory exists
            output_path = Path(output_path)
            self.file_ops.ensure_directory(output_path.parent)
            
            # Write report to file
            if format_type == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report_content, f, indent=2, ensure_ascii=False)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
            
            report_result = {
                'status': 'success',
                'report_type': report_type,
                'format': format_type,
                'output_path': str(output_path),
                'file_size': output_path.stat().st_size,
                'timestamp': time.time(),
                'summary': self._generate_report_summary(report_data)
            }
            
            self.logger.info(f"Report generated successfully: {output_path}")
            return report_result
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {str(e)}")
            raise PentestError(f"Report generation failed: {str(e)}")
    
    def _process_report_data(self, scan_data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Process and structure scan data for report"""
        
        # Extract and organize scan results
        report_data = {
            'metadata': {
                'report_type': report_type,
                'generation_time': datetime.now().isoformat(),
                'toolkit_version': '1.0.0',
                'scan_summary': {}
            },
            'executive_summary': {},
            'scan_results': {},
            'vulnerabilities': [],
            'recommendations': [],
            'appendices': {}
        }
        
        # Process different types of scan data
        for module_name, module_data in scan_data.items():
            if isinstance(module_data, dict) and module_data.get('results'):
                report_data['scan_results'][module_name] = module_data
                
                # Extract vulnerabilities
                if module_name == 'vulnerability' or module_name == 'web_scanner':
                    vulns = self._extract_vulnerabilities(module_data)
                    report_data['vulnerabilities'].extend(vulns)
        
        # Generate executive summary
        report_data['executive_summary'] = self._generate_executive_summary(report_data)
        
        # Generate recommendations
        report_data['recommendations'] = self._generate_recommendations(report_data['vulnerabilities'])
        
        return report_data
    
    def _extract_vulnerabilities(self, module_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract vulnerability information from module data"""
        vulnerabilities = []
        
        results = module_data.get('results', {})
        
        # Handle different vulnerability data structures
        if 'vulnerabilities' in results:
            for vuln in results['vulnerabilities']:
                vulnerability = {
                    'id': vuln.get('id', 'N/A'),
                    'title': vuln.get('name', vuln.get('title', 'Unknown Vulnerability')),
                    'severity': vuln.get('severity', 'info'),
                    'cvss_score': vuln.get('cvss_score'),
                    'description': vuln.get('description', ''),
                    'affected_asset': vuln.get('url', vuln.get('target', '')),
                    'evidence': vuln.get('evidence', ''),
                    'solution': vuln.get('solution', ''),
                    'references': vuln.get('references', vuln.get('reference', '')),
                    'module_source': module_data.get('target', 'Unknown')
                }
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    def _generate_executive_summary(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        vulnerabilities = report_data.get('vulnerabilities', [])
        
        # Count vulnerabilities by severity
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'info').lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Calculate risk level
        risk_level = self._calculate_overall_risk(severity_counts)
        
        summary = {
            'total_vulnerabilities': len(vulnerabilities),
            'severity_breakdown': severity_counts,
            'overall_risk_level': risk_level,
            'key_findings': self._identify_key_findings(vulnerabilities),
            'critical_actions': self._generate_critical_actions(vulnerabilities)
        }
        
        return summary
    
    def _calculate_overall_risk(self, severity_counts: Dict[str, int]) -> str:
        """Calculate overall risk level based on vulnerability severities"""
        if severity_counts.get('critical', 0) > 0:
            return 'Critical'
        elif severity_counts.get('high', 0) >= 3:
            return 'High'
        elif severity_counts.get('high', 0) > 0 or severity_counts.get('medium', 0) >= 5:
            return 'Medium'
        elif severity_counts.get('medium', 0) > 0 or severity_counts.get('low', 0) >= 10:
            return 'Low'
        else:
            return 'Informational'
    
    def _identify_key_findings(self, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Identify key security findings"""
        key_findings = []
        
        # Group vulnerabilities by type and severity
        high_severity_vulns = [v for v in vulnerabilities if v.get('severity') in ['critical', 'high']]
        
        if high_severity_vulns:
            for vuln in high_severity_vulns[:5]:  # Top 5 critical findings
                finding = f"{vuln.get('title', 'Unknown')} - {vuln.get('severity', 'Unknown').title()} Risk"
                key_findings.append(finding)
        
        return key_findings
    
    def _generate_critical_actions(self, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Generate critical action items"""
        actions = []
        
        critical_vulns = [v for v in vulnerabilities if v.get('severity') == 'critical']
        high_vulns = [v for v in vulnerabilities if v.get('severity') == 'high']
        
        if critical_vulns:
            actions.append(f"Immediately address {len(critical_vulns)} critical vulnerabilities")
        
        if high_vulns:
            actions.append(f"Prioritize remediation of {len(high_vulns)} high-risk vulnerabilities")
        
        actions.append("Implement comprehensive security monitoring")
        actions.append("Establish regular security assessments")
        
        return actions
    
    def _generate_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate security recommendations"""
        recommendations = []
        
        # Generic recommendations based on common vulnerability patterns
        vuln_types = set()
        for vuln in vulnerabilities:
            title = vuln.get('title', '').lower()
            if 'sql injection' in title:
                vuln_types.add('sql_injection')
            elif 'xss' in title or 'cross-site scripting' in title:
                vuln_types.add('xss')
            elif 'authentication' in title:
                vuln_types.add('auth')
        
        if 'sql_injection' in vuln_types:
            recommendations.append({
                'category': 'Input Validation',
                'priority': 'High',
                'description': 'Implement parameterized queries and input validation to prevent SQL injection attacks'
            })
        
        if 'xss' in vuln_types:
            recommendations.append({
                'category': 'Output Encoding',
                'priority': 'High',
                'description': 'Implement proper output encoding and Content Security Policy (CSP) to prevent XSS attacks'
            })
        
        # Generic security recommendations
        recommendations.extend([
            {
                'category': 'Security Policies',
                'priority': 'Medium',
                'description': 'Establish and enforce comprehensive security policies and procedures'
            },
            {
                'category': 'Security Training',
                'priority': 'Medium',
                'description': 'Provide regular security awareness training for development and operations teams'
            },
            {
                'category': 'Vulnerability Management',
                'priority': 'High',
                'description': 'Implement a formal vulnerability management program with regular assessments'
            }
        ])
        
        return recommendations
    
    def _generate_html_report(self, report_data: Dict[str, Any], report_type: str) -> str:
        """Generate HTML report"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Penetration Test Report - {report_type.title()}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .section {{ margin-bottom: 30px; }}
                .vulnerability {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #333; }}
                .critical {{ border-left-color: #dc3545; }}
                .high {{ border-left-color: #fd7e14; }}
                .medium {{ border-left-color: #ffc107; }}
                .low {{ border-left-color: #28a745; }}
                .info {{ border-left-color: #17a2b8; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Penetration Testing Report</h1>
                <h2>{report_type.title()} Report</h2>
                <p>Generated: {report_data['metadata']['generation_time']}</p>
            </div>
        """
        
        # Executive Summary
        exec_summary = report_data.get('executive_summary', {})
        html_content += f"""
            <div class="section">
                <h2>Executive Summary</h2>
                <p><strong>Total Vulnerabilities Found:</strong> {exec_summary.get('total_vulnerabilities', 0)}</p>
                <p><strong>Overall Risk Level:</strong> {exec_summary.get('overall_risk_level', 'Unknown')}</p>
                
                <h3>Vulnerability Breakdown</h3>
                <table>
                    <tr><th>Severity</th><th>Count</th></tr>
        """
        
        for severity, count in exec_summary.get('severity_breakdown', {}).items():
            html_content += f"<tr><td>{severity.title()}</td><td>{count}</td></tr>"
        
        html_content += "</table></div>"
        
        # Vulnerabilities
        vulnerabilities = report_data.get('vulnerabilities', [])
        if vulnerabilities:
            html_content += '<div class="section"><h2>Vulnerabilities</h2>'
            
            for vuln in vulnerabilities:
                severity_class = vuln.get('severity', 'info').lower()
                html_content += f"""
                    <div class="vulnerability {severity_class}">
                        <h3>{vuln.get('title', 'Unknown Vulnerability')}</h3>
                        <p><strong>Severity:</strong> {vuln.get('severity', 'Unknown').title()}</p>
                        <p><strong>Affected Asset:</strong> {vuln.get('affected_asset', 'N/A')}</p>
                        <p><strong>Description:</strong> {vuln.get('description', 'No description available.')}</p>
                        <p><strong>Solution:</strong> {vuln.get('solution', 'No solution provided.')}</p>
                    </div>
                """
            
            html_content += '</div>'
        
        # Recommendations
        recommendations = report_data.get('recommendations', [])
        if recommendations:
            html_content += '<div class="section"><h2>Recommendations</h2><ol>'
            
            for rec in recommendations:
                html_content += f"""
                    <li>
                        <strong>{rec.get('category', 'General')} ({rec.get('priority', 'Medium')} Priority)</strong>
                        <p>{rec.get('description', 'No description available.')}</p>
                    </li>
                """
            
            html_content += '</ol></div>'
        
        html_content += """
            </body>
            </html>
        """
        
        return html_content
    
    def _generate_markdown_report(self, report_data: Dict[str, Any], report_type: str) -> str:
        """Generate Markdown report"""
        md_content = f"""# Penetration Testing Report - {report_type.title()}

**Generated:** {report_data['metadata']['generation_time']}

## Executive Summary

"""
        
        exec_summary = report_data.get('executive_summary', {})
        md_content += f"""
**Total Vulnerabilities:** {exec_summary.get('total_vulnerabilities', 0)}
**Overall Risk Level:** {exec_summary.get('overall_risk_level', 'Unknown')}

### Vulnerability Breakdown

| Severity | Count |
|----------|-------|
"""
        
        for severity, count in exec_summary.get('severity_breakdown', {}).items():
            md_content += f"| {severity.title()} | {count} |\n"
        
        # Vulnerabilities section
        vulnerabilities = report_data.get('vulnerabilities', [])
        if vulnerabilities:
            md_content += "\n## Vulnerabilities\n\n"
            
            for i, vuln in enumerate(vulnerabilities, 1):
                md_content += f"""### {i}. {vuln.get('title', 'Unknown Vulnerability')}

**Severity:** {vuln.get('severity', 'Unknown').title()}
**Affected Asset:** {vuln.get('affected_asset', 'N/A')}

**Description:** {vuln.get('description', 'No description available.')}

**Solution:** {vuln.get('solution', 'No solution provided.')}

---

"""
        
        # Recommendations
        recommendations = report_data.get('recommendations', [])
        if recommendations:
            md_content += "## Recommendations\n\n"
            
            for i, rec in enumerate(recommendations, 1):
                md_content += f"""{i}. **{rec.get('category', 'General')} ({rec.get('priority', 'Medium')} Priority)**
   {rec.get('description', 'No description available.')}

"""
        
        return md_content
    
    def _generate_json_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON report"""
        return report_data
    
    def _generate_report_summary(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report summary statistics"""
        vulnerabilities = report_data.get('vulnerabilities', [])
        
        return {
            'total_vulnerabilities': len(vulnerabilities),
            'sections_included': len([k for k, v in report_data.items() if v]),
            'executive_summary': bool(report_data.get('executive_summary')),
            'recommendations_count': len(report_data.get('recommendations', []))
        }
    
    def generate_executive_report(self, scan_data: Dict[str, Any], output_path: str = None) -> Dict[str, Any]:
        """Generate executive summary report"""
        return self.generate_report(scan_data, "executive", "html", output_path)
    
    def generate_technical_report(self, scan_data: Dict[str, Any], output_path: str = None) -> Dict[str, Any]:
        """Generate technical detailed report"""
        return self.generate_report(scan_data, "technical", "html", output_path)
    
    def generate_compliance_report(self, scan_data: Dict[str, Any], framework: str = "general", output_path: str = None) -> Dict[str, Any]:
        """Generate compliance-focused report"""
        return self.generate_report(scan_data, f"compliance_{framework}", "html", output_path)