#!/usr/bin/env python3
"""
CyberSec Toolkit Pro 2025 - Backend API Testing Suite
Validation complète des 35 services pour Sprint 1.8 - Tests finaux
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Tuple
import concurrent.futures
import threading

# Configuration de test
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"
TIMEOUT = 10
MAX_WORKERS = 5

class CyberSecTestSuite:
    def __init__(self):
        self.results = {}
        self.performance_metrics = {}
        self.failed_services = []
        self.passed_services = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def log(self, message: str, level: str = "INFO"):
        """Log avec timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_endpoint(self, endpoint: str, method: str = "GET", data: dict = None, 
                     expected_status: int = 200, service_name: str = "") -> Tuple[bool, dict, float]:
        """Test un endpoint avec métriques de performance"""
        start_time = time.time()
        
        try:
            url = f"{API_BASE}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, timeout=TIMEOUT)
            elif method == "POST":
                response = requests.post(url, json=data or {}, timeout=TIMEOUT)
            elif method == "PUT":
                response = requests.put(url, json=data or {}, timeout=TIMEOUT)
            elif method == "DELETE":
                response = requests.delete(url, timeout=TIMEOUT)
            else:
                return False, {"error": f"Méthode {method} non supportée"}, 0
                
            response_time = (time.time() - start_time) * 1000  # en ms
            
            # Vérifier le status code
            if response.status_code != expected_status:
                return False, {
                    "error": f"Status code {response.status_code}, attendu {expected_status}",
                    "response": response.text[:500]
                }, response_time
                
            # Parser la réponse JSON
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text[:500]}
                
            return True, response_data, response_time
            
        except requests.exceptions.Timeout:
            return False, {"error": "Timeout"}, (time.time() - start_time) * 1000
        except requests.exceptions.ConnectionError:
            return False, {"error": "Connection Error"}, (time.time() - start_time) * 1000
        except Exception as e:
            return False, {"error": str(e)}, (time.time() - start_time) * 1000

    def test_infrastructure(self):
        """Test de l'infrastructure de base"""
        self.log("🔧 Test Infrastructure de Base", "INFO")
        
        # Test endpoint racine
        success, data, response_time = self.test_endpoint("/", service_name="Root API")
        self.results["infrastructure"] = {
            "root_api": {
                "success": success,
                "response_time": response_time,
                "data": data
            }
        }
        
        if success:
            self.log(f"✅ API Root opérationnelle ({response_time:.1f}ms)")
            # Vérifier les services déclarés
            if "services" in data and "operational_services" in data["services"]:
                declared_services = len(data["services"]["operational_services"])
                self.log(f"📊 Services déclarés: {declared_services}/35")
        else:
            self.log(f"❌ API Root échouée: {data.get('error', 'Erreur inconnue')}")
            
        # Test health check
        success, data, response_time = self.test_endpoint("/health", service_name="Health Check")
        self.results["infrastructure"]["health"] = {
            "success": success,
            "response_time": response_time,
            "data": data
        }
        
        if success:
            self.log(f"✅ Health Check opérationnel ({response_time:.1f}ms)")
        else:
            self.log(f"❌ Health Check échoué: {data.get('error', 'Erreur inconnue')}")

    def test_cybersecurity_base_services(self):
        """Test des 11 services cybersécurité de base (Sprints 1.1-1.4)"""
        self.log("🛡️ Test Services Cybersécurité de Base (11 services)", "INFO")
        
        base_services = [
            ("/assistant/status", "Assistant IA Cybersécurité"),
            ("/pentesting/", "Pentesting OWASP Top 10"),
            ("/incident-response/", "Incident Response"),
            ("/digital-forensics/", "Digital Forensics"),
            ("/compliance/", "Compliance Management"),
            ("/vulnerability-management/", "Vulnerability Management"),
            ("/monitoring/", "Monitoring 24/7"),
            ("/threat-intelligence/", "Threat Intelligence"),
            ("/red-team/", "Red Team Operations"),
            ("/blue-team/", "Blue Team Defense"),
            ("/audit/", "Audit Automatisé")
        ]
        
        self.results["cybersecurity_base"] = {}
        
        for endpoint, service_name in base_services:
            success, data, response_time = self.test_endpoint(endpoint, service_name=service_name)
            
            service_key = service_name.lower().replace(" ", "_").replace("/", "")
            self.results["cybersecurity_base"][service_key] = {
                "success": success,
                "response_time": response_time,
                "data": data,
                "endpoint": endpoint
            }
            
            if success:
                self.log(f"✅ {service_name} opérationnel ({response_time:.1f}ms)")
                self.passed_services.append(service_name)
            else:
                self.log(f"❌ {service_name} échoué: {data.get('error', 'Erreur inconnue')}")
                self.failed_services.append(service_name)
                
            self.total_tests += 1
            if success:
                self.passed_tests += 1

    def test_ai_services(self):
        """Test des 6 services IA avancés (Sprint 1.5)"""
        self.log("🤖 Test Services IA Avancés (6 services)", "INFO")
        
        ai_services = [
            ("/cyber-ai/status", "Cyber AI"),
            ("/predictive-ai/status", "Predictive AI"),
            ("/automation-ai/status", "Automation AI"),
            ("/conversational-ai/status", "Conversational AI"),
            ("/business-ai/", "Business AI"),
            ("/code-analysis-ai/", "Code Analysis AI")
        ]
        
        self.results["ai_services"] = {}
        
        for endpoint, service_name in ai_services:
            success, data, response_time = self.test_endpoint(endpoint, service_name=service_name)
            
            service_key = service_name.lower().replace(" ", "_")
            self.results["ai_services"][service_key] = {
                "success": success,
                "response_time": response_time,
                "data": data,
                "endpoint": endpoint
            }
            
            if success:
                self.log(f"✅ {service_name} opérationnel ({response_time:.1f}ms)")
                self.passed_services.append(service_name)
            else:
                self.log(f"❌ {service_name} échoué: {data.get('error', 'Erreur inconnue')}")
                self.failed_services.append(service_name)
                
            self.total_tests += 1
            if success:
                self.passed_tests += 1

    def test_business_services(self):
        """Test des 5 services business (Sprint 1.6)"""
        self.log("💼 Test Services Business (5 services)", "INFO")
        
        business_services = [
            ("/crm/status", "CRM Business"),
            ("/billing/status", "Billing & Invoicing"),
            ("/analytics/status", "Analytics & Reports"),
            ("/planning/status", "Planning & Events"),
            ("/training/status", "Training & Certification")
        ]
        
        self.results["business_services"] = {}
        
        for endpoint, service_name in business_services:
            success, data, response_time = self.test_endpoint(endpoint, service_name=service_name)
            
            service_key = service_name.lower().replace(" ", "_").replace("&", "and")
            self.results["business_services"][service_key] = {
                "success": success,
                "response_time": response_time,
                "data": data,
                "endpoint": endpoint
            }
            
            if success:
                self.log(f"✅ {service_name} opérationnel ({response_time:.1f}ms)")
                self.passed_services.append(service_name)
            else:
                self.log(f"❌ {service_name} échoué: {data.get('error', 'Erreur inconnue')}")
                self.failed_services.append(service_name)
                
            self.total_tests += 1
            if success:
                self.passed_tests += 1

    def test_specialized_cybersecurity_services(self):
        """Test des 12 services cybersécurité spécialisés (Sprint 1.7)"""
        self.log("🔒 Test Services Cybersécurité Spécialisés (12 services)", "INFO")
        
        specialized_services = [
            ("/cloud-security/", "Cloud Security"),
            ("/mobile-security/", "Mobile Security"),
            ("/iot-security/", "IoT Security"),
            ("/web3-security/", "Web3 Security"),
            ("/ai-security/", "AI Security"),
            ("/network-security/", "Network Security"),
            ("/api-security/", "API Security"),
            ("/container-security/", "Container Security"),
            ("/iac-security/", "IaC Security"),
            ("/social-engineering/", "Social Engineering"),
            ("/soar/", "Security Orchestration (SOAR)"),
            ("/risk/", "Risk Assessment")
        ]
        
        self.results["specialized_cybersecurity"] = {}
        
        for endpoint, service_name in specialized_services:
            success, data, response_time = self.test_endpoint(endpoint, service_name=service_name)
            
            service_key = service_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
            self.results["specialized_cybersecurity"][service_key] = {
                "success": success,
                "response_time": response_time,
                "data": data,
                "endpoint": endpoint
            }
            
            if success:
                self.log(f"✅ {service_name} opérationnel ({response_time:.1f}ms)")
                self.passed_services.append(service_name)
            else:
                self.log(f"❌ {service_name} échoué: {data.get('error', 'Erreur inconnue')}")
                self.failed_services.append(service_name)
                
            self.total_tests += 1
            if success:
                self.passed_tests += 1

    def test_assistant_chat_functionality(self):
        """Test spécifique de la fonctionnalité chat de l'assistant"""
        self.log("💬 Test Fonctionnalité Chat Assistant", "INFO")
        
        # Test création de session
        success, data, response_time = self.test_endpoint(
            "/assistant/sessions/new", 
            method="POST",
            service_name="Assistant Session Creation"
        )
        
        if success and "session_id" in data:
            session_id = data["session_id"]
            self.log(f"✅ Session créée: {session_id}")
            
            # Test chat avec message
            chat_data = {
                "message": "Bonjour, pouvez-vous m'aider avec un audit de sécurité ?",
                "session_id": session_id
            }
            
            success, data, response_time = self.test_endpoint(
                "/assistant/chat",
                method="POST",
                data=chat_data,
                service_name="Assistant Chat"
            )
            
            if success and "response" in data:
                self.log(f"✅ Chat fonctionnel ({response_time:.1f}ms)")
                self.results["assistant_chat"] = {
                    "success": True,
                    "response_time": response_time,
                    "session_creation": True,
                    "chat_response": True
                }
            else:
                self.log(f"❌ Chat échoué: {data.get('error', 'Erreur inconnue')}")
                self.results["assistant_chat"] = {
                    "success": False,
                    "error": data.get('error', 'Erreur chat')
                }
        else:
            self.log(f"❌ Création session échouée: {data.get('error', 'Erreur inconnue')}")
            self.results["assistant_chat"] = {
                "success": False,
                "error": "Session creation failed"
            }

    def test_performance_load(self):
        """Test de charge avec requêtes simultanées"""
        self.log("⚡ Test de Performance et Charge", "INFO")
        
        # Endpoints critiques à tester en parallèle
        critical_endpoints = [
            "/",
            "/health",
            "/assistant/status",
            "/cloud-security/",
            "/mobile-security/",
            "/crm/"
        ]
        
        def test_concurrent_endpoint(endpoint):
            success, data, response_time = self.test_endpoint(endpoint)
            return endpoint, success, response_time
        
        # Test avec 10 requêtes simultanées
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(10):
                for endpoint in critical_endpoints:
                    futures.append(executor.submit(test_concurrent_endpoint, endpoint))
            
            results = []
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        
        total_time = time.time() - start_time
        
        # Analyser les résultats
        successful_requests = sum(1 for _, success, _ in results if success)
        total_requests = len(results)
        avg_response_time = sum(rt for _, _, rt in results) / len(results)
        
        self.results["performance"] = {
            "concurrent_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": (successful_requests / total_requests) * 100,
            "total_time": total_time,
            "avg_response_time": avg_response_time,
            "requests_per_second": total_requests / total_time
        }
        
        self.log(f"📊 Performance: {successful_requests}/{total_requests} réussies")
        self.log(f"📊 Temps de réponse moyen: {avg_response_time:.1f}ms")
        self.log(f"📊 Taux de succès: {(successful_requests/total_requests)*100:.1f}%")

    def generate_report(self):
        """Génère le rapport final de test"""
        self.log("📋 Génération du Rapport Final", "INFO")
        
        print("\n" + "="*80)
        print("🚀 RAPPORT FINAL - CYBERSEC TOOLKIT PRO 2025 - SPRINT 1.8")
        print("="*80)
        
        print(f"\n📊 RÉSULTATS GLOBAUX:")
        print(f"   • Services testés: {self.total_tests}")
        print(f"   • Services opérationnels: {self.passed_tests}")
        print(f"   • Services en échec: {len(self.failed_services)}")
        print(f"   • Taux de réussite: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if "performance" in self.results:
            perf = self.results["performance"]
            print(f"\n⚡ PERFORMANCE:")
            print(f"   • Temps de réponse moyen: {perf['avg_response_time']:.1f}ms")
            print(f"   • Taux de succès charge: {perf['success_rate']:.1f}%")
            print(f"   • Requêtes/seconde: {perf['requests_per_second']:.1f}")
        
        print(f"\n✅ SERVICES OPÉRATIONNELS ({len(self.passed_services)}):")
        for service in self.passed_services:
            print(f"   • {service}")
        
        if self.failed_services:
            print(f"\n❌ SERVICES EN ÉCHEC ({len(self.failed_services)}):")
            for service in self.failed_services:
                print(f"   • {service}")
        
        # Validation des objectifs Sprint 1.8
        print(f"\n🎯 VALIDATION OBJECTIFS SPRINT 1.8:")
        
        target_services = 35
        operational_services = self.passed_tests
        target_response_time = 400  # ms
        
        if "performance" in self.results:
            avg_response = self.results["performance"]["avg_response_time"]
        else:
            avg_response = 0
            
        print(f"   • Services opérationnels: {operational_services}/{target_services} " + 
              ("✅" if operational_services >= target_services else "❌"))
        print(f"   • Temps de réponse < 400ms: {avg_response:.1f}ms " + 
              ("✅" if avg_response < target_response_time else "❌"))
        print(f"   • Infrastructure stable: " + 
              ("✅" if self.results.get("infrastructure", {}).get("root_api", {}).get("success", False) else "❌"))
        
        # Décision GO/NO-GO
        go_criteria = [
            operational_services >= 30,  # Au moins 30/35 services (85%)
            avg_response < target_response_time,
            self.results.get("infrastructure", {}).get("root_api", {}).get("success", False)
        ]
        
        go_decision = all(go_criteria)
        
        print(f"\n🚦 DÉCISION COMMERCIALISATION:")
        print(f"   • Statut: {'🟢 GO' if go_decision else '🔴 NO-GO'}")
        print(f"   • Prêt pour Sprint 1.8: {'OUI' if go_decision else 'NON'}")
        
        if not go_decision:
            print(f"\n⚠️ ACTIONS REQUISES AVANT COMMERCIALISATION:")
            if operational_services < 30:
                print(f"   • Corriger les services en échec")
            if avg_response >= target_response_time:
                print(f"   • Optimiser les performances")
            if not self.results.get("infrastructure", {}).get("root_api", {}).get("success", False):
                print(f"   • Stabiliser l'infrastructure")
        
        print("\n" + "="*80)
        
        return go_decision

    def save_detailed_results(self):
        """Sauvegarde les résultats détaillés en JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"/app/test_results_{timestamp}.json"
        
        detailed_results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": len(self.failed_services),
                "success_rate": (self.passed_tests/self.total_tests)*100 if self.total_tests > 0 else 0
            },
            "passed_services": self.passed_services,
            "failed_services": self.failed_services,
            "detailed_results": self.results
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(detailed_results, f, indent=2, ensure_ascii=False)
            self.log(f"📄 Résultats détaillés sauvegardés: {filename}")
        except Exception as e:
            self.log(f"❌ Erreur sauvegarde: {str(e)}", "ERROR")

    def run_full_test_suite(self):
        """Exécute la suite complète de tests"""
        self.log("🚀 Démarrage Suite de Tests Complète CyberSec Toolkit Pro 2025", "INFO")
        start_time = time.time()
        
        try:
            # Tests séquentiels
            self.test_infrastructure()
            self.test_cybersecurity_base_services()
            self.test_ai_services()
            self.test_business_services()
            self.test_specialized_cybersecurity_services()
            self.test_assistant_chat_functionality()
            
            # Test de performance
            self.test_performance_load()
            
            # Génération du rapport
            go_decision = self.generate_report()
            
            # Sauvegarde des résultats
            self.save_detailed_results()
            
            total_time = time.time() - start_time
            self.log(f"⏱️ Tests terminés en {total_time:.1f}s", "INFO")
            
            return go_decision
            
        except KeyboardInterrupt:
            self.log("⚠️ Tests interrompus par l'utilisateur", "WARNING")
            return False
        except Exception as e:
            self.log(f"❌ Erreur critique: {str(e)}", "ERROR")
            return False

def main():
    """Point d'entrée principal"""
    print("🛡️ CyberSec Toolkit Pro 2025 - Suite de Tests Backend")
    print("📋 Validation complète des 35 services - Sprint 1.8")
    print("-" * 60)
    
    # Vérifier la connectivité de base
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=5)
        print(f"✅ Connectivité backend confirmée (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Impossible de se connecter au backend: {str(e)}")
        print(f"🔧 Vérifiez que le backend est démarré sur {BASE_URL}")
        sys.exit(1)
    
    # Exécuter les tests
    test_suite = CyberSecTestSuite()
    go_decision = test_suite.run_full_test_suite()
    
    # Code de sortie
    sys.exit(0 if go_decision else 1)

if __name__ == "__main__":
    main()