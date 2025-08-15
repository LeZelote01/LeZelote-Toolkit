"""
IaC Security Module - Scanner
Scanner pour l'audit sécurité Infrastructure as Code
"""
import json
import re
import yaml
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from .models import SecurityFinding, ScanResult, ComplianceRule, IaCResource

class IaCSecurityScanner:
    """Scanner principal pour l'audit IaC"""
    
    def __init__(self):
        self.rules = self._load_security_rules()
        self.supported_types = ["terraform", "cloudformation", "ansible", "kubernetes"]
    
    def _load_security_rules(self) -> List[ComplianceRule]:
        """Charge les règles de sécurité prédéfinies"""
        return [
            ComplianceRule(
                rule_id="TF001",
                name="S3 Bucket Public Read",
                description="S3 bucket allows public read access",
                severity="high",
                category="security",
                frameworks=["CIS", "NIST"],
                iac_types=["terraform", "cloudformation"]
            ),
            ComplianceRule(
                rule_id="TF002", 
                name="EC2 Instance Without Security Group",
                description="EC2 instance launched without proper security group",
                severity="medium",
                category="security",
                frameworks=["CIS", "NIST"],
                iac_types=["terraform", "cloudformation"]
            ),
            ComplianceRule(
                rule_id="TF003",
                name="Unencrypted EBS Volume",
                description="EBS volume is not encrypted at rest",
                severity="high",
                category="security", 
                frameworks=["CIS", "NIST", "PCI-DSS"],
                iac_types=["terraform", "cloudformation"]
            ),
            ComplianceRule(
                rule_id="K8001",
                name="Privileged Container",
                description="Container running with privileged access",
                severity="critical",
                category="security",
                frameworks=["CIS Kubernetes"],
                iac_types=["kubernetes"]
            ),
            ComplianceRule(
                rule_id="K8002",
                name="No Resource Limits",
                description="Container without CPU/memory limits",
                severity="medium",
                category="best_practices",
                frameworks=["CIS Kubernetes"],
                iac_types=["kubernetes"]
            )
        ]
    
    async def scan_iac_content(self, content: str, iac_type: str, scan_options: Dict[str, Any] = None) -> ScanResult:
        """Scanne le contenu IaC pour détecter les problèmes de sécurité"""
        scan_id = str(uuid.uuid4())
        
        try:
            # Parse le contenu selon le type
            if iac_type == "terraform":
                resources = self._parse_terraform(content)
            elif iac_type == "cloudformation":
                resources = self._parse_cloudformation(content)
            elif iac_type == "ansible":
                resources = self._parse_ansible(content)
            elif iac_type == "kubernetes":
                resources = self._parse_kubernetes(content)
            else:
                raise ValueError(f"Type IaC non supporté: {iac_type}")
            
            # Applique les règles de sécurité
            findings = []
            for resource in resources:
                resource_findings = self._apply_security_rules(resource, iac_type)
                findings.extend(resource_findings)
            
            # Calcule le score de conformité
            compliance_score = self._calculate_compliance_score(findings, len(resources))
            
            # Génère les recommandations
            recommendations = self._generate_recommendations(findings)
            
            # Crée le résumé par sévérité
            summary = self._create_severity_summary(findings)
            
            return ScanResult(
                scan_id=scan_id,
                status="completed",
                source_type="content",
                iac_type=iac_type,
                created_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat(),
                total_resources=len(resources),
                findings=findings,
                summary=summary,
                compliance_score=compliance_score,
                recommendations=recommendations
            )
            
        except Exception as e:
            return ScanResult(
                scan_id=scan_id,
                status="failed",
                source_type="content",
                iac_type=iac_type,
                created_at=datetime.now().isoformat(),
                total_resources=0,
                findings=[],
                summary={"error": str(e)},
                compliance_score=0.0,
                recommendations=[f"Erreur lors du scan: {str(e)}"]
            )
    
    def _parse_terraform(self, content: str) -> List[IaCResource]:
        """Parse le contenu Terraform"""
        resources = []
        lines = content.split('\n')
        
        # Regex simple pour détecter les ressources Terraform
        resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"'
        
        for i, line in enumerate(lines):
            match = re.search(resource_pattern, line)
            if match:
                resource_type = match.group(1)
                resource_name = match.group(2)
                
                # Extraction basique de la configuration (simplifiée)
                config = self._extract_terraform_config(lines, i)
                
                resources.append(IaCResource(
                    resource_type=resource_type,
                    resource_name=resource_name,
                    file_path="terraform.tf",
                    line_number=i + 1,
                    configuration=config
                ))
        
        return resources
    
    def _parse_cloudformation(self, content: str) -> List[IaCResource]:
        """Parse le contenu CloudFormation"""
        resources = []
        try:
            # Tente de parser en YAML d'abord, puis JSON
            try:
                cf_template = yaml.safe_load(content)
            except:
                cf_template = json.loads(content)
            
            if 'Resources' in cf_template:
                for resource_name, resource_def in cf_template['Resources'].items():
                    resources.append(IaCResource(
                        resource_type=resource_def.get('Type', 'Unknown'),
                        resource_name=resource_name,
                        file_path="template.yaml",
                        configuration=resource_def.get('Properties', {})
                    ))
        
        except Exception as e:
            print(f"Erreur parsing CloudFormation: {e}")
        
        return resources
    
    def _parse_ansible(self, content: str) -> List[IaCResource]:
        """Parse le contenu Ansible"""
        resources = []
        try:
            ansible_playbook = yaml.safe_load(content)
            
            if isinstance(ansible_playbook, list):
                for play in ansible_playbook:
                    if 'tasks' in play:
                        for task in play['tasks']:
                            # Extrait le module utilisé
                            for key, value in task.items():
                                if key not in ['name', 'when', 'tags']:
                                    resources.append(IaCResource(
                                        resource_type=f"ansible.{key}",
                                        resource_name=task.get('name', f'task_{key}'),
                                        file_path="playbook.yml",
                                        configuration=value if isinstance(value, dict) else {}
                                    ))
        
        except Exception as e:
            print(f"Erreur parsing Ansible: {e}")
        
        return resources
    
    def _parse_kubernetes(self, content: str) -> List[IaCResource]:
        """Parse le contenu Kubernetes"""
        resources = []
        try:
            # Sépare les documents YAML multiples
            documents = content.split('---')
            
            for doc in documents:
                if doc.strip():
                    k8s_resource = yaml.safe_load(doc)
                    if k8s_resource and 'kind' in k8s_resource:
                        resources.append(IaCResource(
                            resource_type=k8s_resource['kind'],
                            resource_name=k8s_resource.get('metadata', {}).get('name', 'unnamed'),
                            file_path="k8s.yaml",
                            configuration=k8s_resource.get('spec', {})
                        ))
        
        except Exception as e:
            print(f"Erreur parsing Kubernetes: {e}")
        
        return resources
    
    def _extract_terraform_config(self, lines: List[str], start_line: int) -> Dict[str, Any]:
        """Extrait la configuration d'une ressource Terraform (méthode simplifiée)"""
        config = {}
        brace_count = 0
        in_resource = False
        
        for i in range(start_line, len(lines)):
            line = lines[i].strip()
            
            if '{' in line:
                brace_count += line.count('{')
                in_resource = True
            
            if in_resource and '=' in line and not line.startswith('#'):
                parts = line.split('=', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().rstrip(',')
                    config[key] = value
            
            if '}' in line:
                brace_count -= line.count('}')
                if brace_count <= 0:
                    break
        
        return config
    
    def _apply_security_rules(self, resource: IaCResource, iac_type: str) -> List[SecurityFinding]:
        """Applique les règles de sécurité à une ressource"""
        findings = []
        
        # Filtre les règles applicables à ce type d'IaC
        applicable_rules = [rule for rule in self.rules if iac_type in rule.iac_types]
        
        for rule in applicable_rules:
            # Logique de détection simplifiée basée sur le type de ressource
            if self._rule_matches_resource(rule, resource):
                findings.append(SecurityFinding(
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    title=rule.name,
                    description=rule.description,
                    file_path=resource.file_path,
                    line_number=resource.line_number,
                    resource_type=resource.resource_type,
                    remediation=self._get_remediation(rule.rule_id),
                    compliance_frameworks=rule.frameworks
                ))
        
        return findings
    
    def _rule_matches_resource(self, rule: ComplianceRule, resource: IaCResource) -> bool:
        """Détermine si une règle s'applique à une ressource (logique simplifiée)"""
        
        # Exemples de logique de matching
        if rule.rule_id == "TF001" and "aws_s3_bucket" in resource.resource_type:
            # Vérifier si le bucket a une ACL publique
            acl = resource.configuration.get('acl', '')
            return 'public' in str(acl).lower()
        
        elif rule.rule_id == "TF002" and "aws_instance" in resource.resource_type:
            # Vérifier si l'instance EC2 a un security group
            return 'security_groups' not in resource.configuration
        
        elif rule.rule_id == "TF003" and "aws_ebs_volume" in resource.resource_type:
            # Vérifier si le volume EBS est chiffré
            encrypted = resource.configuration.get('encrypted', 'false')
            return str(encrypted).lower() != 'true'
        
        elif rule.rule_id == "K8001" and resource.resource_type == "Pod":
            # Vérifier si le container est privilégié
            containers = resource.configuration.get('containers', [])
            for container in containers:
                if isinstance(container, dict):
                    security_context = container.get('securityContext', {})
                    if security_context.get('privileged', False):
                        return True
        
        elif rule.rule_id == "K8002" and resource.resource_type in ["Pod", "Deployment"]:
            # Vérifier si les limites de ressources sont définies
            containers = resource.configuration.get('containers', [])
            for container in containers:
                if isinstance(container, dict):
                    resources = container.get('resources', {})
                    if not resources.get('limits'):
                        return True
        
        return False
    
    def _get_remediation(self, rule_id: str) -> str:
        """Retourne les conseils de remédiation pour une règle"""
        remediations = {
            "TF001": "Définir une ACL privée ou utiliser bucket policies restrictives",
            "TF002": "Ajouter un security group avec des règles restrictives",
            "TF003": "Activer le chiffrement avec encrypted = true",
            "K8001": "Retirer privileged: true du securityContext",
            "K8002": "Définir des limites CPU/mémoire dans resources.limits"
        }
        return remediations.get(rule_id, "Consulter la documentation de sécurité")
    
    def _calculate_compliance_score(self, findings: List[SecurityFinding], total_resources: int) -> float:
        """Calcule un score de conformité"""
        if total_resources == 0:
            return 100.0
        
        # Score basé sur la sévérité des findings
        penalty_weights = {
            "critical": 10,
            "high": 5,
            "medium": 2,
            "low": 1
        }
        
        total_penalty = sum(penalty_weights.get(finding.severity, 1) for finding in findings)
        max_possible_penalty = total_resources * penalty_weights["critical"]
        
        if max_possible_penalty == 0:
            return 100.0
        
        score = max(0, 100 - (total_penalty / max_possible_penalty * 100))
        return round(score, 2)
    
    def _create_severity_summary(self, findings: List[SecurityFinding]) -> Dict[str, int]:
        """Crée un résumé par sévérité"""
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for finding in findings:
            if finding.severity in summary:
                summary[finding.severity] += 1
        
        return summary
    
    def _generate_recommendations(self, findings: List[SecurityFinding]) -> List[str]:
        """Génère des recommandations basées sur les findings"""
        recommendations = []
        
        severity_counts = self._create_severity_summary(findings)
        
        if severity_counts["critical"] > 0:
            recommendations.append(f"🚨 {severity_counts['critical']} problème(s) critique(s) détecté(s) - Action immédiate requise")
        
        if severity_counts["high"] > 0:
            recommendations.append(f"⚠️ {severity_counts['high']} problème(s) de sévérité élevée - Corriger rapidement")
        
        if len(findings) == 0:
            recommendations.append("✅ Aucun problème de sécurité détecté - Bonne configuration")
        else:
            recommendations.append("📚 Consulter les guides de bonnes pratiques de sécurité IaC")
            recommendations.append("🔍 Effectuer des scans réguliers avant déploiement")
        
        return recommendations

# Instance globale du scanner
iac_scanner = IaCSecurityScanner()