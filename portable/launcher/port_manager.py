"""
Gestionnaire de ports pour l'environnement portable CyberSec Toolkit Pro 2025
Détection automatique des ports libres avec validation robuste
Version finale - 35 services opérationnels
"""
import socket
import json
import time
import requests
from pathlib import Path

class PortManager:
    def __init__(self):
        self.config_file = Path(__file__).parent.parent / "config" / "ports.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        # Ports fixes selon config projet (8000 backend, 8002 frontend)
        self.default_backend_port = 8000
        self.default_frontend_port = 8002
        self.default_database_port = 8003  # SQLite n'utilise pas de port mais pour uniformité
        
    def is_port_free(self, port, timeout=3):
        """Vérifie si un port est libre avec timeout"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex(('localhost', port))
                return result != 0  # Port libre si connexion échoue
        except OSError:
            return False
    
    def test_service_health(self, port, path="/api/", timeout=5):
        """Test la santé d'un service sur un port donné"""
        try:
            response = requests.get(f"http://localhost:{port}{path}", timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def find_free_ports(self, start_port=8000, count=3, preferred_ports=None):
        """Trouve des ports libres en priorisant les ports préférés"""
        if preferred_ports:
            # Vérifier d'abord les ports préférés
            if all(self.is_port_free(port) for port in preferred_ports):
                return preferred_ports
        
        free_ports = []
        port = start_port
        consecutive_free = 0
        
        while len(free_ports) < count and port < start_port + 1000:
            if self.is_port_free(port):
                free_ports.append(port)
                consecutive_free += 1
            else:
                # Reset pour maintenir la consécutivité si nécessaire
                if consecutive_free > 0 and len(free_ports) < count:
                    consecutive_free = 0
            port += 1
                
        return free_ports[:count] if len(free_ports) >= count else None
    
    def get_ports_config(self, force_defaults=True):
        """Charge ou génère la configuration des ports avec priorité aux defaults"""
        # Configuration par défaut pour cohérence projet (ports fixes)
        default_config = {
            "backend": self.default_backend_port,
            "frontend": self.default_frontend_port, 
            "database": self.default_database_port
        }
        
        if force_defaults:
            # Vérifier que les ports par défaut sont libres
            if all(self.is_port_free(port) for port in default_config.values()):
                self._save_config(default_config)
                return default_config
        
        # Charger config existante si présente
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                    
                # Vérifier que les ports sont toujours libres
                if all(self.is_port_free(port) for port in config.values()):
                    return config
            except Exception as e:
                print(f"⚠️ Erreur chargement config ports: {e}")
        
        # Générer de nouveaux ports en essayant de garder les defaults
        preferred = [self.default_backend_port, self.default_frontend_port, self.default_database_port]
        ports = self.find_free_ports(preferred_ports=preferred)
        
        if ports and len(ports) >= 3:
            config = {
                "backend": ports[0],
                "frontend": ports[1], 
                "database": ports[2]
            }
            self._save_config(config)
            return config
            
        # Fallback absolu avec ports fixes projet
        print("⚠️ Utilisation fallback ports fixes")
        return default_config
    
    def _save_config(self, config):
        """Sauvegarde la configuration des ports"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde config ports: {e}")
    
    def validate_services_ports(self, config, max_wait=30):
        """Valide que les services sont accessibles sur leurs ports"""
        print("🔍 Validation des services sur leurs ports...")
        
        services_status = {}
        start_time = time.time()
        
        # Test backend
        if self.test_service_health(config["backend"], "/api/"):
            services_status["backend"] = "✅ Opérationnel"
        else:
            services_status["backend"] = "❌ Non accessible"
        
        # Test frontend (pas d'API, juste port ouvert)
        if not self.is_port_free(config["frontend"]):
            services_status["frontend"] = "✅ Opérationnel"
        else:
            services_status["frontend"] = "❌ Non démarré"
        
        elapsed = time.time() - start_time
        services_status["validation_time"] = f"{elapsed:.2f}s"
        
        return services_status

    def get_service_stats(self, backend_port):
        """Récupère les statistiques des 35 services"""
        try:
            response = requests.get(f"http://localhost:{backend_port}/api/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "total_services": data.get("services", {}).get("total_planned", 0),
                    "operational_services": data.get("services", {}).get("implemented", 0),
                    "phase": data.get("services", {}).get("phase", "Unknown"),
                    "operational_services_list": data.get("services", {}).get("operational_services", [])
                }
        except Exception as e:
            print(f"⚠️ Erreur récupération stats services: {e}")
        
        return {"total_services": 35, "operational_services": 0, "phase": "Unknown"}

if __name__ == "__main__":
    manager = PortManager()
    print("🔧 Configuration des ports pour CyberSec Toolkit Pro 2025...")
    
    # Obtenir la configuration
    ports = manager.get_ports_config()
    print(f"📊 Ports configurés: {ports}")
    
    # Test de validation si les services tournent
    print("\n🧪 Test de validation des services...")
    validation = manager.validate_services_ports(ports)
    for service, status in validation.items():
        print(f"  {service}: {status}")
        
    # Stats des services si backend accessible
    if "✅" in validation.get("backend", ""):
        stats = manager.get_service_stats(ports["backend"])
        print(f"\n📈 Services opérationnels: {stats['operational_services']}/{stats['total_services']}")
        print(f"🎯 Phase: {stats['phase']}")