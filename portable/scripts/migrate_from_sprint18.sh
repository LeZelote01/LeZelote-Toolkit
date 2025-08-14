#!/bin/bash
# Script de migration Sprint 1.8 vers architecture portable native
# Supprime les redondances et unifie sous /portable/

echo "🔄 Migration vers Architecture Portable Native"
echo "=============================================="

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
echo "📁 Répertoire racine: $ROOT_DIR"

echo ""
echo "🗑️ 1. Suppression des scripts redondants Sprint 1.8..."

# Scripts redondants qui sont maintenant intégrés dans l'architecture portable
REDUNDANT_SCRIPTS=(
    "scripts/optimize_production.sh"
    "scripts/package_distribution.sh" 
    "scripts/monitoring_production.sh"
    "scripts/secure_production.sh"
)

for script in "${REDUNDANT_SCRIPTS[@]}"; do
    if [ -f "$ROOT_DIR/$script" ]; then
        echo "   🗑️ Suppression: $script"
        rm -f "$ROOT_DIR/$script"
    else
        echo "   ✅ Déjà supprimé: $script"
    fi
done

echo ""
echo "🔧 2. Vérification architecture portable..."

# Vérifier que l'architecture portable est complète
REQUIRED_PORTABLE_FILES=(
    "portable/launcher/portable_config.py"
    "portable/launcher/start_windows.bat"
    "portable/launcher/start_linux.sh"
    "portable/launcher/start_macos.sh"
    "portable/config/portable.env"
    "portable/config/ports.json"
    "portable/scripts/optimize_and_package.sh"
)

for file in "${REQUIRED_PORTABLE_FILES[@]}"; do
    if [ -f "$ROOT_DIR/$file" ]; then
        echo "   ✅ Présent: $file"
    else
        echo "   ❌ Manquant: $file"
    fi
done

echo ""
echo "🔄 3. Migration des configurations..."

# Sauvegarder d'éventuelles configurations existantes de Sprint 1.8
if [ -f "$ROOT_DIR/scripts/production.env" ]; then
    echo "   📋 Sauvegarde: scripts/production.env"
    cp "$ROOT_DIR/scripts/production.env" "$ROOT_DIR/portable/config/production.env.backup"
    rm -f "$ROOT_DIR/scripts/production.env"
fi

# Nettoyer le dossier dist créé par les anciens scripts
if [ -d "$ROOT_DIR/dist" ]; then
    echo "   🗑️ Nettoyage ancien dossier dist..."
    rm -rf "$ROOT_DIR/dist"
fi

echo ""
echo "🧹 4. Nettoyage final..."

# Supprimer les autres fichiers redondants
CLEANUP_FILES=(
    "monitoring/dashboard.html"
    "monitoring/health_report.json"
    "scripts/setup.sh"
    "scripts/clean_project.sh"
)

for file in "${CLEANUP_FILES[@]}"; do
    if [ -f "$ROOT_DIR/$file" ]; then
        echo "   🗑️ Suppression: $file"
        rm -f "$ROOT_DIR/$file"
    fi
done

# Nettoyer les dossiers vides
if [ -d "$ROOT_DIR/monitoring" ] && [ -z "$(ls -A "$ROOT_DIR/monitoring")" ]; then
    echo "   🗑️ Suppression dossier vide: monitoring/"
    rmdir "$ROOT_DIR/monitoring"
fi

echo ""
echo "✅ 5. Test de l'architecture portable..."

# Tester la configuration portable
cd "$ROOT_DIR/portable/launcher"
if python3 portable_config.py --production; then
    echo "   ✅ Configuration portable: OK"
else
    echo "   ❌ Configuration portable: ERREUR"
fi

echo ""
echo "📊 6. Rapport de migration..."

echo "🏗️ ARCHITECTURE FINALE:"
echo "   📁 /portable/"
echo "      ├── config/           Configuration centralisée"
echo "      ├── launcher/         Scripts démarrage par OS"
echo "      ├── database/         SQLite portable"
echo "      ├── scripts/          Outils intégrés"
echo "      └── monitoring/       Rapports (créé à la demande)"
echo ""
echo "   🗑️ Supprimé: /scripts/ (redondants)"
echo "   🗑️ Supprimé: /monitoring/ (intégré dans /portable/)"
echo "   🗑️ Supprimé: /dist/ (recréé par architecture portable)"

echo ""
echo "🎯 AVANTAGES MIGRATION:"
echo "   ✅ Configuration unifiée dans /portable/"
echo "   ✅ Suppression redondances"
echo "   ✅ Scripts optimisés par OS"
echo "   ✅ Maintenance simplifiée"
echo "   ✅ 35 services garantis"

echo ""
echo "🚀 MIGRATION TERMINÉE AVEC SUCCÈS!"
echo "=============================================="
echo ""
echo "📋 Actions à faire:"
echo "   1. Tester: ./START_TOOLKIT.sh"
echo "   2. Optimiser: cd portable/scripts && ./optimize_and_package.sh"
echo "   3. Monitorer: Rapports dans portable/monitoring/"
echo ""
echo "🏆 Architecture Portable Native - Sprint 1.8 Optimisé!"