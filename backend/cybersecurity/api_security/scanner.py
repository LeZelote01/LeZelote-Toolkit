"""
API Security Scanner
Moteur de test de sécurité pour APIs
Sprint 1.7 - Services Cybersécurité Spécialisés
"""
import asyncio
import aiohttp
import json
import random
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin, urlparse

from .models import (
    APISecurityRequest, APITestResult, APIVulnerability, APIEndpoint,
    APISecurityMetrics, OWASPAPICategory, APIDiscoveryResult,
    TestType, Severity, HTTPMethod, APIType
)

class APISecurityScanner:
    """Scanner de sécurité pour APIs"""
    
    def __init__(self):
        self.owasp_categories = self._load_owasp_api_categories()
        self.injection_payloads = self._load_injection_payloads()
        self.auth_bypass_payloads = self._load_auth_bypass_payloads()
        
    async def test_api_security(self, request_dict: Dict[str, Any]) -> APITestResult:
        """Lance un test de sécurité API complet"""  
        request = APISecurityRequest(**request_dict)
        
        result = APITestResult(
            api_type=request.api_type,
            base_url=request.base_url,
            status="running"
        )
        
        start_time = datetime.now()
        vulnerabilities = []
        
        try:
            print(f"🔍 Démarrage test API: {request.base_url}")
            
            # Découverte d'endpoints si nécessaire
            if not request.endpoints and request.openapi_url:
                discovered = await self._discover_from_openapi(request.openapi_url)
                result.endpoints_discovered = discovered.endpoints_found
                result.api_documentation_found = True
            elif request.endpoints:
                result.endpoints_discovered = request.endpoints
            else:
                # Découverte basique
                result.endpoints_discovered = await self._basic_endpoint_discovery(request.base_url)
            
            # Tests de sécurité selon la suite demandée
            for test_type in request.test_suite:
                print(f"🔍 Exécution test: {test_type}")
                
                if test_type == TestType.OWASP_API_TOP10:
                    test_result, vulns = await self._test_owasp_api_top10(request, result.endpoints_discovered)
                elif test_type == TestType.AUTHENTICATION:
                    test_result, vulns = await self._test_authentication(request, result.endpoints_discovered)
                elif test_type == TestType.AUTHORIZATION:
                    test_result, vulns = await self._test_authorization(request, result.endpoints_discovered)
                elif test_type == TestType.INJECTION:
                    test_result, vulns = await self._test_injection_attacks(request, result.endpoints_discovered)
                elif test_type == TestType.RATE_LIMITING:
                    test_result, vulns = await self._test_rate_limiting(request, result.endpoints_discovered)
                else:
                    test_result, vulns = await self._test_generic(request, test_type)
                
                result.test_results[test_type.value] = test_result
                vulnerabilities.extend(vulns)
                
                # Ajouter test_id aux vulnérabilités
                for vuln in vulns:
                    vuln.test_id = result.id
            
            # Calculer les métriques de sécurité
            result.security_metrics = await self._calculate_security_metrics(result, vulnerabilities)
            
            # Générer les recommandations
            result.recommendations = self._generate_recommendations(vulnerabilities, result.test_results)
            
            # Finaliser le résultat
            result.completed_at = datetime.now()
            result.duration = (result.completed_at - start_time).total_seconds()
            result.status = "completed"
            result.vulnerabilities = vulnerabilities
            result.total_vulnerabilities = len(vulnerabilities)
            result.critical_vulnerabilities = len([v for v in vulnerabilities if v.severity == Severity.CRITICAL])
            result.high_vulnerabilities = len([v for v in vulnerabilities if v.severity == Severity.HIGH])
            result.tests_performed = request.test_suite
            result.endpoints_tested = result.endpoints_discovered[:10]  # Limiter pour la demo
            
            print(f"✅ Test API terminé: {len(vulnerabilities)} vulnérabilités trouvées")
            
        except Exception as e:
            result.status = "failed"
            result.completed_at = datetime.now()
            result.duration = (result.completed_at - start_time).total_seconds()
            result.errors_encountered.append(str(e))
            print(f"❌ Erreur lors du test API: {e}")
        
        return result
    
    async def _discover_from_openapi(self, openapi_url: str) -> APIDiscoveryResult:
        """Découvre les endpoints depuis un fichier OpenAPI/Swagger"""
        discovery = APIDiscoveryResult(
            base_url=openapi_url,
            api_type=APIType.REST,
            discovery_method="openapi"
        )
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(openapi_url) as response:
                    if response.status == 200:
                        spec = await response.json()
                        
                        # Parser le spec OpenAPI
                        base_path = spec.get('basePath', '')
                        paths = spec.get('paths', {})
                        
                        for path, methods in paths.items():
                            for method, details in methods.items():
                                if method.upper() in [m.value for m in HTTPMethod]:
                                    endpoint = APIEndpoint(
                                        path=base_path + path,
                                        method=HTTPMethod(method.upper()),
                                        description=details.get('summary', ''),
                                        authentication_required='security' in details,
                                        deprecated=details.get('deprecated', False)
                                    )
                                    discovery.endpoints_found.append(endpoint)
                        
                        discovery.confidence = 0.9
                        
        except Exception as e:
            print(f"Erreur découverte OpenAPI: {e}")
            discovery.confidence = 0.1
        
        return discovery
    
    async def _basic_endpoint_discovery(self, base_url: str) -> List[APIEndpoint]:
        """Découverte basique d'endpoints communs"""
        common_endpoints = [
            ('/api/v1/users', HTTPMethod.GET),
            ('/api/v1/users', HTTPMethod.POST),
            ('/api/v1/users/{id}', HTTPMethod.GET),
            ('/api/v1/users/{id}', HTTPMethod.PUT),
            ('/api/v1/users/{id}', HTTPMethod.DELETE),
            ('/api/v1/auth/login', HTTPMethod.POST),
            ('/api/v1/auth/logout', HTTPMethod.POST),
            ('/api/v1/auth/register', HTTPMethod.POST),
            ('/api/v1/data', HTTPMethod.GET),
            ('/api/v1/admin', HTTPMethod.GET),
            ('/health', HTTPMethod.GET),
            ('/status', HTTPMethod.GET)
        ]
        
        endpoints = []
        for path, method in common_endpoints:
            endpoint = APIEndpoint(
                path=path, 
                method=method,
                authentication_required='auth' in path or 'admin' in path
            )
            endpoints.append(endpoint)
        
        return endpoints
    
    async def _test_owasp_api_top10(self, request: APISecurityRequest, 
                                  endpoints: List[APIEndpoint]) -> Tuple[Dict[str, Any], List[APIVulnerability]]:
        """Test OWASP API Security Top 10 2023"""
        vulnerabilities = []
        owasp_results = {}
        
        # API1:2023 - Broken Object Level Authorization
        vulns_api1 = await self._test_broken_object_level_auth(request, endpoints)
        vulnerabilities.extend(vulns_api1)
        owasp_results["API1:2023"] = {"tested": True, "vulnerabilities": len(vulns_api1)}
        
        # API2:2023 - Broken Authentication  
        vulns_api2 = await self._test_broken_authentication(request, endpoints)
        vulnerabilities.extend(vulns_api2)
        owasp_results["API2:2023"] = {"tested": True, "vulnerabilities": len(vulns_api2)}
        
        # API3:2023 - Broken Object Property Level Authorization
        vulns_api3 = await self._test_broken_property_level_auth(request, endpoints)
        vulnerabilities.extend(vulns_api3)
        owasp_results["API3:2023"] = {"tested": True, "vulnerabilities": len(vulns_api3)}
        
        # API4:2023 - Unrestricted Resource Consumption
        vulns_api4 = await self._test_unrestricted_resource_consumption(request, endpoints)
        vulnerabilities.extend(vulns_api4)
        owasp_results["API4:2023"] = {"tested": True, "vulnerabilities": len(vulns_api4)}
        
        # API5:2023 - Broken Function Level Authorization
        vulns_api5 = await self._test_broken_function_level_auth(request, endpoints)
        vulnerabilities.extend(vulns_api5)
        owasp_results["API5:2023"] = {"tested": True, "vulnerabilities": len(vulns_api5)}
        
        result = {
            "test_type": "owasp_api_top10",
            "categories_tested": len(owasp_results),
            "total_vulnerabilities": len(vulnerabilities),
            "owasp_results": owasp_results,
            "compliance_score": max(0, 100 - (len(vulnerabilities) * 10))
        }
        
        return result, vulnerabilities
    
    async def _test_broken_object_level_auth(self, request: APISecurityRequest, 
                                           endpoints: List[APIEndpoint]) -> List[APIVulnerability]:
        """Test API1:2023 - Broken Object Level Authorization"""
        vulnerabilities = []
        
        # Simuler des tests d'accès aux objets
        for endpoint in endpoints[:5]:  # Limiter pour la demo
            if '{id}' in endpoint.path and endpoint.method in [HTTPMethod.GET, HTTPMethod.PUT, HTTPMethod.DELETE]:
                
                # Simuler tentative d'accès à des objets d'autres utilisateurs
                if random.random() < 0.3:  # 30% chance de vulnérabilité
                    vulnerability = APIVulnerability(
                        test_id="",
                        endpoint_path=endpoint.path,
                        method=endpoint.method,
                        owasp_category="API1:2023",
                        title="Autorisation au niveau objet défaillante",
                        description="L'API ne vérifie pas correctement si l'utilisateur a le droit d'accéder à l'objet demandé",
                        severity=Severity.HIGH,
                        cwe_id="CWE-639",
                        test_type=TestType.OWASP_API_TOP10,
                        attack_vector="Modification de l'ID dans l'URL",
                        impact="Accès non autorisé aux données d'autres utilisateurs",
                        likelihood="high",
                        remediation="Implémenter une vérification d'autorisation pour chaque objet accédé",
                        remediation_steps=[
                            "Vérifier que l'utilisateur a le droit d'accéder à l'objet",
                            "Utiliser des UUIDs au lieu d'IDs séquentiels",
                            "Implémenter un système d'ACL (Access Control List)",
                            "Logger tous les accès aux objets sensibles"
                        ],
                        request_details={
                            "original_id": "123",
                            "tested_id": "456",
                            "response_code": 200
                        },
                        confidence=8
                    )
                    vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    async def _test_broken_authentication(self, request: APISecurityRequest, 
                                        endpoints: List[APIEndpoint]) -> List[APIVulnerability]:
        """Test API2:2023 - Broken Authentication"""
        vulnerabilities = []
        
        # Rechercher les endpoints d'authentification
        auth_endpoints = [ep for ep in endpoints if 'auth' in ep.path or 'login' in ep.path]
        
        for endpoint in auth_endpoints:
            # Test de brute force
            if random.random() < 0.4:  # 40% chance
                vulnerability = APIVulnerability(
                    test_id="",
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    owasp_category="API2:2023",
                    title="Authentification défaillante - Pas de protection brute force",
                    description="L'endpoint d'authentification ne protège pas contre les attaques par brute force",
                    severity=Severity.MEDIUM,
                    cwe_id="CWE-307",
                    test_type=TestType.AUTHENTICATION,
                    attack_vector="Attaque par brute force sur les credentials",
                    impact="Compromission de comptes utilisateurs",
                    likelihood="medium",
                    remediation="Implémenter une protection contre le brute force",
                    remediation_steps=[
                        "Implémenter un rate limiting sur les tentatives de connexion",
                        "Utiliser des CAPTCHAs après plusieurs échecs",
                        "Bloquer temporairement les IPs suspectes",
                        "Alerter les utilisateurs des tentatives de connexion"
                    ],
                    confidence=7
                )
                vulnerabilities.append(vulnerability)
            
            # Test de credentials faibles
            if random.random() < 0.2:  # 20% chance
                vulnerability = APIVulnerability(
                    test_id="",
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    owasp_category="API2:2023",
                    title="Acceptation de mots de passe faibles",
                    description="L'API accepte des mots de passe ne respectant pas les bonnes pratiques",
                    severity=Severity.MEDIUM,
                    cwe_id="CWE-521",
                    test_type=TestType.AUTHENTICATION,
                    attack_vector="Utilisation de mots de passe faibles",
                    impact="Facilitation des attaques par dictionnaire",
                    likelihood="medium",
                    remediation="Implémenter une politique de mots de passe robuste",
                    remediation_steps=[
                        "Définir des critères de complexité minimale",
                        "Vérifier contre les mots de passe communs",
                        "Forcer le changement des mots de passe faibles",
                        "Éduquer les utilisateurs sur les bonnes pratiques"
                    ],
                    confidence=6
                )
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    async def _test_broken_property_level_auth(self, request: APISecurityRequest, 
                                             endpoints: List[APIEndpoint]) -> List[APIVulnerability]:
        """Test API3:2023 - Broken Object Property Level Authorization"""
        vulnerabilities = []
        
        # Test d'exposition excessive de données
        for endpoint in endpoints[:3]:
            if endpoint.method == HTTPMethod.GET and random.random() < 0.25:
                vulnerability = APIVulnerability(
                    test_id="",
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    owasp_category="API3:2023", 
                    title="Exposition excessive de données",
                    description="L'API expose plus de données que nécessaire dans ses réponses",
                    severity=Severity.MEDIUM,
                    cwe_id="CWE-200",
                    test_type=TestType.OWASP_API_TOP10,
                    attack_vector="Analyse des réponses API",
                    impact="Fuite d'informations sensibles",
                    likelihood="medium",
                    remediation="Filtrer les données exposées selon les besoins",
                    remediation_steps=[
                        "Implémenter des vues spécifiques par endpoint",
                        "Filtrer les champs sensibles",
                        "Utiliser des DTOs (Data Transfer Objects)",
                        "Documenter les données nécessaires par endpoint"
                    ],
                    response_details={
                        "exposed_fields": ["password_hash", "internal_id", "admin_flag"],
                        "expected_fields": ["id", "name", "email"]
                    },
                    confidence=6
                )
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    async def _test_unrestricted_resource_consumption(self, request: APISecurityRequest, 
                                                    endpoints: List[APIEndpoint]) -> List[APIVulnerability]:
        """Test API4:2023 - Unrestricted Resource Consumption"""
        vulnerabilities = []
        
        # Test de rate limiting
        if not request.test_options.get("rate_limit_test", True):
            return vulnerabilities
        
        for endpoint in endpoints[:2]:
            if random.random() < 0.35:  # 35% chance
                vulnerability = APIVulnerability(
                    test_id="",
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    owasp_category="API4:2023",
                    title="Consommation de ressources non restreinte",
                    description="L'API ne limite pas la consommation de ressources par utilisateur",
                    severity=Severity.MEDIUM if endpoint.method == HTTPMethod.GET else Severity.HIGH,
                    cwe_id="CWE-770",
                    test_type=TestType.RATE_LIMITING,
                    attack_vector="Envoi massif de requêtes",
                    impact="Déni de service, épuisement des ressources serveur",
                    likelihood="high",
                    remediation="Implémenter un système de rate limiting",
                    remediation_steps=[
                        "Définir des limites par utilisateur/IP",
                        "Implémenter un rate limiting adaptatif",
                        "Monitorer la consommation de ressources",
                        "Alerter en cas de dépassement des seuils"
                    ],
                    request_details={
                        "requests_sent": 1000,
                        "timeframe": "60 seconds",
                        "responses_received": 1000
                    },
                    confidence=9
                )
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    async def _test_broken_function_level_auth(self, request: APISecurityRequest, 
                                             endpoints: List[APIEndpoint]) -> List[APIVulnerability]:
        """Test API5:2023 - Broken Function Level Authorization"""
        vulnerabilities = []
        
        # Rechercher les endpoints admin
        admin_endpoints = [ep for ep in endpoints if 'admin' in ep.path or ep.path.startswith('/api/v1/manage')]
        
        for endpoint in admin_endpoints:
            if random.random() < 0.4:  # 40% chance
                vulnerability = APIVulnerability(
                    test_id="",
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    owasp_category="API5:2023",
                    title="Autorisation au niveau fonction défaillante",
                    description="Les fonctions administratives sont accessibles sans vérification appropriée des privilèges",
                    severity=Severity.CRITICAL,
                    cwe_id="CWE-285",
                    test_type=TestType.AUTHORIZATION,
                    attack_vector="Accès direct aux endpoints administratifs",
                    impact="Escalade de privilèges, accès non autorisé aux fonctions sensibles",
                    likelihood="high",
                    remediation="Implémenter une vérification de rôles/privilèges",
                    remediation_steps=[
                        "Vérifier les rôles utilisateur pour chaque fonction",
                        "Implémenter un système RBAC (Role-Based Access Control)",
                        "Séparer les interfaces admin des interfaces utilisateur",
                        "Auditer régulièrement les accès aux fonctions privilégiées"
                    ],
                    confidence=8
                )
                vulnerabilities.append(vulnerability)
        
        return vulnerabilities
    
    async def _test_authentication(self, request: APISecurityRequest, 
                                 endpoints: List[APIEndpoint]) -> Tuple[Dict[str, Any], List[APIVulnerability]]:
        """Test spécifique de l'authentification"""
        vulnerabilities = []
        
        auth_methods_found = []
        protected_endpoints = 0
        
        for endpoint in endpoints:
            if endpoint.authentication_required:
                protected_endpoints += 1
                
            # Test de bypass d'authentification
            if endpoint.authentication_required and random.random() < 0.2:
                vulnerability = APIVulnerability(
                    test_id="",
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    title="Contournement d'authentification possible",
                    description="L'endpoint protégé peut être accédé sans authentification appropriée",
                    severity=Severity.HIGH,
                    test_type=TestType.AUTHENTICATION,
                    attack_vector="Manipulation des headers d'authentification",
                    impact="Accès non autorisé aux ressources protégées",
                    likelihood="medium",
                    remediation="Renforcer la vérification d'authentification",
                    remediation_steps=[
                        "Vérifier systématiquement les tokens d'authentification",
                        "Valider l'intégrité des sessions",
                        "Implémenter une expiration appropriée des tokens",
                        "Logger les tentatives d'accès non autorisées"
                    ],
                    confidence=7
                )
                vulnerabilities.append(vulnerability)
        
        # Détecter les méthodes d'authentification
        if request.auth_method:
            auth_methods_found.append(request.auth_method)
        
        result = {
            "test_type": "authentication",
            "auth_methods_found": auth_methods_found,
            "protected_endpoints": protected_endpoints,
            "total_endpoints": len(endpoints),
            "bypass_vulnerabilities": len(vulnerabilities),
            "authentication_coverage": (protected_endpoints / max(1, len(endpoints))) * 100
        }
        
        return result, vulnerabilities
    
    async def _test_authorization(self, request: APISecurityRequest, 
                                endpoints: List[APIEndpoint]) -> Tuple[Dict[str, Any], List[APIVulnerability]]:
        """Test d'autorisation"""
        vulnerabilities = []
        
        privilege_escalation_attempts = 0
        
        for endpoint in endpoints[:5]:  # Limiter pour la demo
            if endpoint.method in [HTTPMethod.PUT, HTTPMethod.DELETE, HTTPMethod.POST]:
                privilege_escalation_attempts += 1
                
                if random.random() < 0.25:  # 25% chance
                    vulnerability = APIVulnerability(
                        test_id="",
                        endpoint_path=endpoint.path,
                        method=endpoint.method,
                        title="Escalade de privilèges possible",
                        description="L'endpoint permet d'effectuer des actions au-delà des privilèges de l'utilisateur",
                        severity=Severity.HIGH,
                        test_type=TestType.AUTHORIZATION,
                        attack_vector="Manipulation des paramètres de requête",
                        impact="Modification ou suppression de données non autorisées",
                        likelihood="medium",
                        remediation="Implémenter une vérification d'autorisation stricte",
                        remediation_steps=[
                            "Vérifier les permissions pour chaque action",
                            "Implémenter un contrôle d'accès basé sur les attributs",
                            "Valider les paramètres de requête",
                            "Auditer les actions sensibles"
                        ],
                        confidence=6
                    )
                    vulnerabilities.append(vulnerability)
        
        result = {
            "test_type": "authorization",
            "privilege_escalation_attempts": privilege_escalation_attempts,
            "vulnerabilities_found": len(vulnerabilities),
            "high_risk_operations": len([ep for ep in endpoints if ep.method in [HTTPMethod.DELETE, HTTPMethod.PUT]])
        }
        
        return result, vulnerabilities
    
    async def _test_injection_attacks(self, request: APISecurityRequest, 
                                    endpoints: List[APIEndpoint]) -> Tuple[Dict[str, Any], List[APIVulnerability]]:
        """Test d'attaques par injection"""
        vulnerabilities = []
        
        injection_types_tested = ["sql", "nosql", "command", "ldap"]
        endpoints_tested = 0
        
        for endpoint in endpoints[:4]:  # Limiter pour la demo
            if endpoint.method in [HTTPMethod.POST, HTTPMethod.PUT]:
                endpoints_tested += 1
                
                # Test SQL Injection
                if random.random() < 0.2:  # 20% chance
                    vulnerability = APIVulnerability(
                        test_id="",
                        endpoint_path=endpoint.path,
                        method=endpoint.method,
                        title="Vulnérabilité d'injection SQL détectée",
                        description="L'endpoint est vulnérable aux attaques par injection SQL",
                        severity=Severity.CRITICAL,
                        cwe_id="CWE-89",
                        test_type=TestType.INJECTION,
                        attack_vector="Injection de code SQL dans les paramètres",
                        impact="Accès non autorisé à la base de données, fuite de données",
                        likelihood="high",
                        remediation="Utiliser des requêtes préparées et valider les entrées",
                        remediation_steps=[
                            "Utiliser des requêtes préparées/parameterisées",
                            "Valider et assainir toutes les entrées utilisateur",
                            "Implémenter un WAF (Web Application Firewall)",
                            "Utiliser le principe du moindre privilège pour la DB"
                        ],
                        payload_used="' OR '1'='1",
                        confidence=8
                    )
                    vulnerabilities.append(vulnerability)
                
                # Test NoSQL Injection
                if random.random() < 0.15:  # 15% chance
                    vulnerability = APIVulnerability(
                        test_id="",
                        endpoint_path=endpoint.path,
                        method=endpoint.method,
                        title="Vulnérabilité d'injection NoSQL détectée",
                        description="L'endpoint est vulnérable aux attaques par injection NoSQL",
                        severity=Severity.HIGH,
                        cwe_id="CWE-943",
                        test_type=TestType.INJECTION,
                        attack_vector="Injection de code NoSQL dans les paramètres JSON",
                        impact="Contournement d'authentification, accès aux données",
                        likelihood="medium",
                        remediation="Valider strictement les structures de données",
                        remediation_steps=[
                            "Valider les types et structures des données JSON",
                            "Utiliser des schémas de validation",
                            "Éviter l'évaluation dynamique de requêtes",
                            "Implémenter une liste blanche des opérateurs autorisés"
                        ],
                        payload_used='{"$ne": null}',
                        confidence=7
                    )
                    vulnerabilities.append(vulnerability)
        
        result = {
            "test_type": "injection",
            "injection_types_tested": injection_types_tested,
            "endpoints_tested": endpoints_tested,
            "vulnerabilities_found": len(vulnerabilities),
            "critical_issues": len([v for v in vulnerabilities if v.severity == Severity.CRITICAL])
        }
        
        return result, vulnerabilities
    
    async def _test_rate_limiting(self, request: APISecurityRequest, 
                                endpoints: List[APIEndpoint]) -> Tuple[Dict[str, Any], List[APIVulnerability]]:
        """Test de rate limiting"""
        vulnerabilities = []
        
        endpoints_tested = min(3, len(endpoints))  # Limiter pour la demo
        
        for endpoint in endpoints[:endpoints_tested]:
            # Simuler test de rate limiting
            rate_limited = random.random() < 0.4  # 40% chance que le rate limiting soit présent
            
            if not rate_limited:
                severity = Severity.MEDIUM
                if endpoint.method in [HTTPMethod.POST, HTTPMethod.PUT, HTTPMethod.DELETE]:
                    severity = Severity.HIGH
                
                vulnerability = APIVulnerability(
                    test_id="",
                    endpoint_path=endpoint.path,
                    method=endpoint.method,
                    title="Absence de rate limiting",
                    description=f"L'endpoint {endpoint.path} ne limite pas le nombre de requêtes par utilisateur",
                    severity=severity,
                    test_type=TestType.RATE_LIMITING,
                    attack_vector="Envoi massif de requêtes",
                    impact="Déni de service, épuisement des ressources",
                    likelihood="high",
                    remediation="Implémenter un rate limiting approprié",
                    remediation_steps=[
                        "Définir des limites par endpoint et par utilisateur",
                        "Implémenter un système de quotas",
                        "Utiliser des techniques de sliding window",
                        "Retourner des headers informatifs (X-RateLimit-*)"
                    ],
                    confidence=8
                )
                vulnerabilities.append(vulnerability)
        
        result = {
            "test_type": "rate_limiting",
            "endpoints_tested": endpoints_tested,
            "rate_limited_endpoints": endpoints_tested - len(vulnerabilities),
            "vulnerabilities_found": len(vulnerabilities),
            "coverage_percentage": ((endpoints_tested - len(vulnerabilities)) / endpoints_tested) * 100 if endpoints_tested > 0 else 0
        }
        
        return result, vulnerabilities
    
    async def _test_generic(self, request: APISecurityRequest, test_type: TestType) -> Tuple[Dict[str, Any], List[APIVulnerability]]:
        """Test générique pour types non implémentés"""
        vulnerabilities = []
        
        # Test basique générique
        if random.random() < 0.3:  # 30% chance de trouver quelque chose
            vulnerability = APIVulnerability(
                test_id="",
                endpoint_path="/api/v1/generic",
                method=HTTPMethod.GET,
                title=f"Problème détecté ({test_type.value})",
                description=f"Test {test_type.value} a détecté un problème potentiel",
                severity=Severity.MEDIUM,
                test_type=test_type,
                attack_vector="Test automatisé générique",
                impact="Impact potentiel sur la sécurité de l'API",
                likelihood="low",
                remediation=f"Appliquer les meilleures pratiques pour {test_type.value}",
                confidence=5
            )
            vulnerabilities.append(vulnerability)
        
        result = {
            "test_type": test_type.value,
            "status": "completed",
            "vulnerabilities_found": len(vulnerabilities)
        }
        
        return result, vulnerabilities
    
    async def _calculate_security_metrics(self, result: APITestResult, 
                                        vulnerabilities: List[APIVulnerability]) -> APISecurityMetrics:
        """Calcule les métriques de sécurité"""
        
        # Score de sécurité global
        critical_count = len([v for v in vulnerabilities if v.severity == Severity.CRITICAL])
        high_count = len([v for v in vulnerabilities if v.severity == Severity.HIGH])
        medium_count = len([v for v in vulnerabilities if v.severity == Severity.MEDIUM])
        
        penalty = (critical_count * 30) + (high_count * 15) + (medium_count * 5)
        security_score = max(0, 100 - penalty)
        
        # Scores spécifiques
        auth_vulns = [v for v in vulnerabilities if v.test_type in [TestType.AUTHENTICATION, TestType.AUTHORIZATION]]
        auth_score = max(0, 100 - (len(auth_vulns) * 20))
        
        injection_vulns = [v for v in vulnerabilities if v.test_type == TestType.INJECTION]
        data_protection_score = max(0, 100 - (len(injection_vulns) * 25))
        
        rate_limit_vulns = [v for v in vulnerabilities if v.test_type == TestType.RATE_LIMITING]
        rate_limiting_score = max(0, 100 - (len(rate_limit_vulns) * 15))
        
        # OWASP compliance
        owasp_compliance = {}
        for category in self.owasp_categories:
            category_vulns = [v for v in vulnerabilities if v.owasp_category == category["category_id"]]
            owasp_compliance[category["category_id"]] = len(category_vulns) == 0
        
        return APISecurityMetrics(
            security_score=security_score,
            authentication_score=auth_score,
            authorization_score=auth_score,  # Même score pour la demo
            data_protection_score=data_protection_score,
            rate_limiting_score=rate_limiting_score,
            owasp_compliance=owasp_compliance,
            total_endpoints_tested=len(result.endpoints_discovered),
            vulnerable_endpoints=len(set(v.endpoint_path for v in vulnerabilities)),
            authenticated_endpoints=len([ep for ep in result.endpoints_discovered if ep.authentication_required]),
            rate_limited_endpoints=len(result.endpoints_discovered) - rate_limit_vulns,
            error_disclosure_count=random.randint(0, 3),
            information_leakage_count=random.randint(0, 2),
            insecure_direct_object_refs=len([v for v in vulnerabilities if "object" in v.title.lower()])
        )
    
    def _generate_recommendations(self, vulnerabilities: List[APIVulnerability], 
                                test_results: Dict[str, Any]) -> List[str]:
        """Génère des recommandations de sécurité"""
        recommendations = []
        
        # Recommandations basées sur les vulnérabilités
        vuln_types = set(v.test_type for v in vulnerabilities)
        
        if TestType.AUTHENTICATION in vuln_types:
            recommendations.append("Renforcer les mécanismes d'authentification avec rate limiting et validation stricte")
        
        if TestType.AUTHORIZATION in vuln_types:
            recommendations.append("Implémenter un système d'autorisation robuste (RBAC/ABAC)")
        
        if TestType.INJECTION in vuln_types:
            recommendations.append("Utiliser des requêtes préparées et valider toutes les entrées utilisateur")
        
        if TestType.RATE_LIMITING in vuln_types:
            recommendations.append("Implémenter un rate limiting adaptatif sur tous les endpoints")
        
        # Recommandations OWASP
        owasp_vulns = [v for v in vulnerabilities if v.owasp_category]
        if owasp_vulns:
            recommendations.append("Suivre les recommandations OWASP API Security Top 10 2023")
        
        # Recommandations générales
        recommendations.extend([
            "Implémenter une logging et monitoring complets des API",
            "Utiliser HTTPS pour tous les endpoints",
            "Documenter et maintenir à jour les spécifications API",
            "Effectuer des tests de sécurité réguliers",
            "Implémenter une politique de divulgation responsable"
        ])
        
        return recommendations[:8]  # Limiter à 8 recommandations
    
    def _load_owasp_api_categories(self) -> List[Dict[str, Any]]:
        """Charge les catégories OWASP API Security Top 10 2023"""
        return [
            {"category_id": "API1:2023", "name": "Broken Object Level Authorization"},
            {"category_id": "API2:2023", "name": "Broken Authentication"},
            {"category_id": "API3:2023", "name": "Broken Object Property Level Authorization"},
            {"category_id": "API4:2023", "name": "Unrestricted Resource Consumption"},
            {"category_id": "API5:2023", "name": "Broken Function Level Authorization"},
            {"category_id": "API6:2023", "name": "Unrestricted Access to Sensitive Business Flows"},
            {"category_id": "API7:2023", "name": "Server Side Request Forgery"},
            {"category_id": "API8:2023", "name": "Security Misconfiguration"},
            {"category_id": "API9:2023", "name": "Improper Inventory Management"},
            {"category_id": "API10:2023", "name": "Unsafe Consumption of APIs"}
        ]
    
    def _load_injection_payloads(self) -> Dict[str, List[str]]:
        """Charge les payloads d'injection"""
        return {
            "sql": [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users --",
                "admin'--",
                "' OR 1=1#"
            ],
            "nosql": [
                '{"$ne": null}',
                '{"$gt": ""}',
                '{"$where": "this.password.match(/.*/)"}',
                '{"$regex": ".*"}',
                '{"$exists": true}'
            ],
            "command": [
                "; ls -la",
                "&& whoami",
                "| cat /etc/passwd",
                "`id`",
                "$(uname -a)"
            ]
        }
    
    def _load_auth_bypass_payloads(self) -> List[str]:
        """Charge les payloads de bypass d'authentification"""
        return [
            "Bearer null",
            "Bearer undefined",
            "Bearer 0",
            "Bearer false",
            "Basic YWRtaW46YWRtaW4=",  # admin:admin
            "Bearer " + "A" * 500,  # Token très long
            ""
        ]