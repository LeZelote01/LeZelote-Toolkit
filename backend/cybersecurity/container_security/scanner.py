"""
Container Security Module - Scanner Engine
Moteur de scan des vulnérabilités conteneurs
"""
import asyncio
import json
import subprocess
import tempfile
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib
import re

from .models import (
    ContainerVulnerability, ImageInfo, ComplianceCheck, 
    SecretFound, SeverityLevel, ScanStatus, ContainerScan
)

class ContainerScanner:
    """Moteur de scan de sécurité pour conteneurs"""
    
    def __init__(self):
        self.vulnerability_db_path = "/app/data/container_vulns.json"
        self.secrets_patterns = self._load_secrets_patterns()
        self.compliance_rules = self._load_compliance_rules()
    
    async def scan_image(self, image_name: str, scan_options: Dict[str, Any] = None) -> ContainerScan:
        """Lance un scan complet d'une image conteneur"""
        scan_id = self._generate_scan_id(image_name)
        
        try:
            scan = ContainerScan(
                scan_id=scan_id,
                status=ScanStatus.RUNNING,
                scan_type=scan_options.get("scan_type", "vulnerability"),
                image_info=await self._get_image_info(image_name),
                created_at=datetime.now(),
                started_at=datetime.now(),
                scan_options=scan_options or {}
            )
            
            # Étapes du scan
            if scan_options.get("enable_vulnerability_scan", True):
                scan.vulnerabilities = await self._scan_vulnerabilities(image_name)
                scan.total_vulnerabilities = len(scan.vulnerabilities)
                scan.severity_breakdown = self._calculate_severity_breakdown(scan.vulnerabilities)
            
            if scan_options.get("enable_secrets_detection", True):
                scan.secrets_found = await self._detect_secrets(image_name)
            
            if scan_options.get("enable_compliance_checks", True):
                scan.compliance_checks = await self._check_compliance(image_name)
                scan.compliance_score = self._calculate_compliance_score(scan.compliance_checks)
            
            # Génération des recommandations
            scan.hardening_recommendations = self._generate_recommendations(scan)
            
            # Finalisation
            scan.completed_at = datetime.now()
            scan.status = ScanStatus.COMPLETED
            scan.scan_duration = str(scan.completed_at - scan.started_at)
            
            return scan
            
        except Exception as e:
            scan.status = ScanStatus.FAILED
            scan.error_message = str(e)
            scan.completed_at = datetime.now()
            return scan
    
    async def _get_image_info(self, image_name: str) -> ImageInfo:
        """Récupère les informations de l'image"""
        try:
            # Simulation - en réalité on utiliserait docker inspect ou équivalent
            return ImageInfo(
                name=image_name.split(':')[0] if ':' in image_name else image_name,
                tag=image_name.split(':')[1] if ':' in image_name else 'latest',
                size="245.2 MB",
                layers=12,
                base_image="ubuntu:20.04",
                architecture="amd64",
                os="linux",
                created=datetime.now(),
                labels={
                    "maintainer": "nginx Docker Maintainers",
                    "version": "1.21.6"
                }
            )
        except Exception as e:
            raise Exception(f"Erreur récupération info image: {str(e)}")
    
    async def _scan_vulnerabilities(self, image_name: str) -> List[ContainerVulnerability]:
        """Scan des vulnérabilités de l'image"""
        vulnerabilities = []
        
        try:
            # Simulation avec base de vulnérabilités
            sample_vulns = [
                {
                    "cve_id": "CVE-2023-4911",
                    "severity": "critical",
                    "package": "glibc",
                    "installed_version": "2.31-0ubuntu9.9",
                    "fixed_version": "2.31-0ubuntu9.12",
                    "description": "Buffer overflow in glibc's ld.so allowing privilege escalation",
                    "cvss_score": 9.8,
                    "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                },
                {
                    "cve_id": "CVE-2023-38545",
                    "severity": "high",
                    "package": "curl",
                    "installed_version": "7.68.0-1ubuntu2.18",
                    "fixed_version": "7.68.0-1ubuntu2.20",
                    "description": "Heap buffer overflow in libcurl's SOCKS5 proxy handshake",
                    "cvss_score": 7.5
                },
                {
                    "cve_id": "CVE-2023-44487",
                    "severity": "high",
                    "package": "nginx",
                    "installed_version": "1.18.0-0ubuntu1.4",
                    "fixed_version": "1.18.0-0ubuntu1.5",
                    "description": "HTTP/2 Rapid Reset attack vulnerability",
                    "cvss_score": 7.5
                }
            ]
            
            for vuln_data in sample_vulns:
                vulnerability = ContainerVulnerability(
                    cve_id=vuln_data["cve_id"],
                    severity=SeverityLevel(vuln_data["severity"]),
                    package=vuln_data["package"],
                    installed_version=vuln_data["installed_version"],
                    fixed_version=vuln_data.get("fixed_version"),
                    description=vuln_data["description"],
                    cvss_score=vuln_data.get("cvss_score"),
                    cvss_vector=vuln_data.get("cvss_vector"),
                    references=[f"https://nvd.nist.gov/vuln/detail/{vuln_data['cve_id']}"],
                    published_date=datetime.now()
                )
                vulnerabilities.append(vulnerability)
            
            return vulnerabilities
            
        except Exception as e:
            raise Exception(f"Erreur scan vulnérabilités: {str(e)}")
    
    async def _detect_secrets(self, image_name: str) -> List[SecretFound]:
        """Détection de secrets dans l'image"""
        secrets = []
        
        try:
            # Simulation détection de secrets
            sample_secrets = [
                {
                    "type": "API Key",
                    "location": "/app/config.json",
                    "severity": "high",
                    "pattern": "api_key: sk-...",
                    "confidence": 0.95
                },
                {
                    "type": "Database Password",
                    "location": "/etc/app/database.conf",
                    "severity": "critical",
                    "pattern": "password=secretpassword123",
                    "confidence": 0.88
                }
            ]
            
            for secret_data in sample_secrets:
                secret = SecretFound(
                    type=secret_data["type"],
                    location=secret_data["location"],
                    severity=SeverityLevel(secret_data["severity"]),
                    pattern=secret_data["pattern"],
                    confidence=secret_data["confidence"]
                )
                secrets.append(secret)
            
            return secrets
            
        except Exception as e:
            raise Exception(f"Erreur détection secrets: {str(e)}")
    
    async def _check_compliance(self, image_name: str) -> List[ComplianceCheck]:
        """Vérification de conformité"""
        checks = []
        
        try:
            # Simulation vérifications CIS Docker
            sample_checks = [
                {
                    "standard": "CIS Docker",
                    "rule_id": "4.1",
                    "rule_name": "Ensure a user for the container has been created",
                    "status": "failed",
                    "severity": "medium",
                    "description": "Container is running as root user",
                    "remediation": "Create and use a non-root user for the container"
                },
                {
                    "standard": "CIS Docker",
                    "rule_id": "4.6",
                    "rule_name": "Ensure sensitive host system directories are not mounted",
                    "status": "passed",
                    "severity": "high",
                    "description": "No sensitive host directories mounted"
                }
            ]
            
            for check_data in sample_checks:
                check = ComplianceCheck(
                    standard=check_data["standard"],
                    rule_id=check_data["rule_id"],
                    rule_name=check_data["rule_name"],
                    status=check_data["status"],
                    severity=SeverityLevel(check_data["severity"]),
                    description=check_data["description"],
                    remediation=check_data.get("remediation")
                )
                checks.append(check)
            
            return checks
            
        except Exception as e:
            raise Exception(f"Erreur vérification conformité: {str(e)}")
    
    def _calculate_severity_breakdown(self, vulnerabilities: List[ContainerVulnerability]) -> Dict[str, int]:
        """Calcule la répartition des vulnérabilités par sévérité"""
        breakdown = {"critical": 0, "high": 0, "medium": 0, "low": 0, "negligible": 0}
        
        for vuln in vulnerabilities:
            breakdown[vuln.severity.value] += 1
        
        return breakdown
    
    def _calculate_compliance_score(self, checks: List[ComplianceCheck]) -> float:
        """Calcule le score de conformité"""
        if not checks:
            return 0.0
        
        passed = len([c for c in checks if c.status == "passed"])
        total = len(checks)
        
        return round((passed / total) * 100, 1)
    
    def _generate_recommendations(self, scan: ContainerScan) -> List[str]:
        """Génère des recommandations de sécurisation"""
        recommendations = []
        
        # Recommandations basées sur les vulnérabilités
        if scan.severity_breakdown.get("critical", 0) > 0:
            recommendations.append("🔴 CRITIQUE: Mettre à jour immédiatement les packages avec vulnérabilités critiques")
        
        if scan.severity_breakdown.get("high", 0) > 0:
            recommendations.append("🟠 Mettre à jour les packages avec vulnérabilités élevées")
        
        # Recommandations basées sur les secrets
        if scan.secrets_found:
            recommendations.append("🔐 Supprimer les secrets hardcodés et utiliser des variables d'environnement")
        
        # Recommandations basées sur la conformité
        failed_checks = [c for c in scan.compliance_checks if c.status == "failed"]
        if failed_checks:
            recommendations.append("📋 Corriger les problèmes de conformité identifiés")
        
        # Recommandations génériques
        recommendations.extend([
            "🐳 Utiliser des images de base minimales (distroless, alpine)",
            "👤 Configurer un utilisateur non-root pour le conteneur",
            "🏷️ Utiliser des tags de version spécifiques au lieu de 'latest'",
            "🔒 Activer le système de fichiers en lecture seule quand possible",
            "📊 Implémenter des limites de ressources appropriées"
        ])
        
        return recommendations[:8]  # Limiter à 8 recommandations max
    
    def _generate_scan_id(self, image_name: str) -> str:
        """Génère un ID unique pour le scan"""
        timestamp = datetime.now().isoformat()
        data = f"{image_name}_{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _load_secrets_patterns(self) -> Dict[str, List[str]]:
        """Charge les patterns de détection de secrets"""
        return {
            "api_keys": [
                r"api[_-]?key[s]?\s*[:=]\s*['\"]?([a-zA-Z0-9_-]+)['\"]?",
                r"sk-[a-zA-Z0-9_-]{20,}",
                r"AKIA[0-9A-Z]{16}"
            ],
            "passwords": [
                r"password[s]?\s*[:=]\s*['\"]?([^\s'\"]+)['\"]?",
                r"passwd\s*[:=]\s*['\"]?([^\s'\"]+)['\"]?"
            ],
            "tokens": [
                r"token[s]?\s*[:=]\s*['\"]?([a-zA-Z0-9_.-]+)['\"]?",
                r"bearer\s+([a-zA-Z0-9_.-]+)"
            ]
        }
    
    def _load_compliance_rules(self) -> Dict[str, List[Dict]]:
        """Charge les règles de conformité"""
        return {
            "cis_docker": [
                {
                    "rule_id": "4.1",
                    "name": "Ensure a user for the container has been created",
                    "check": "user_created"
                },
                {
                    "rule_id": "4.6", 
                    "name": "Ensure sensitive host system directories are not mounted",
                    "check": "no_sensitive_mounts"
                }
            ]
        }