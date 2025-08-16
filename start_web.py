#!/usr/bin/env python3
"""
Démarrage de l'interface web du LeZelote-Toolkit
==============================================
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def start_web_interface():
    """Démarrer l'interface web"""
    try:
        print("🌐 Démarrage de l'interface web LeZelote-Toolkit...")
        
        # Import Flask app
        from interfaces.web.app import PentestWebApp
        
        # Initialize web app
        web_app = PentestWebApp()
        
        # Start the server
        print("🚀 Interface web démarrée sur http://localhost:5000")
        print("📱 Interface accessible depuis votre navigateur")
        print("🛑 Appuyez sur Ctrl+C pour arrêter")
        
        web_app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n👋 Interface web arrêtée")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_web_interface()