#!/bin/bash
# CyberSec Toolkit Pro 2025 - Lanceur universel portable
# Auto-détection de l'OS et démarrage approprié

echo ""
echo " ================================================"
echo "  🛡️ CyberSec TOOLKIT PRO 2025 - PORTABLE USB"
echo " ================================================"
echo ""

# Détection automatique de l'OS
OS_TYPE=$(uname -s 2>/dev/null || echo "Unknown")

case "$OS_TYPE" in
    "Linux")
        echo "🐧 Système détecté: Linux"
        ./portable/launcher/start_linux.sh
        ;;
    "Darwin") 
        echo "🍎 Système détecté: macOS"
        ./portable/launcher/start_macos.sh
        ;;
    *)
        echo "🖥️ Système: $OS_TYPE"
        echo "⚠️ Pour Windows, utilisez START_TOOLKIT.bat"
        echo ""
        echo "Tentative de démarrage générique..."
        ./portable/launcher/start_linux.sh
        ;;
esac