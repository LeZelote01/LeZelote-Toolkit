#!/bin/bash
# Script de validation de l'arborescence CyberSec Toolkit Pro 2025
# VALIDATION DE CONFORMITÉ ARCHITECTURALE STRICTE

echo "🔍 VALIDATION DE L'ARBORESCENCE COMPLÈTE"
echo "========================================"
echo "⚠️  VÉRIFICATION DE CONFORMITÉ À ARCHITECTURE.md"
echo

# Compteurs
ERRORS=0
WARNINGS=0

# Fonction de validation
validate_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1"
    else
        echo "❌ $1 - MANQUANT"
        ((ERRORS++))
    fi
}

validate_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
    else
        echo "❌ $1 - MANQUANT"
        ((ERRORS++))
    fi
}

echo
echo "📋 DOCUMENTATION"
echo "----------------"
validate_file "README.md"
validate_file "ARCHITECTURE.md"
validate_file "ROADMAP.md"
validate_file "DEPLOYMENT.md"
validate_file "STRUCTURE_COMPLETE.md"

echo
echo "🐳 INFRASTRUCTURE"
echo "-----------------"
validate_dir "infrastructure"
validate_file "infrastructure/.env.example"
validate_file "infrastructure/docker-compose.prod.yml"
validate_file "docker-compose.yml"
validate_file "Makefile"

echo
echo "📊 DATA & TEMPLATES"
echo "-------------------"
validate_dir "database"
validate_dir "database/schemas"
validate_file "database/schemas/users.py"
validate_file "database/schemas/services.py"
validate_dir "models"
validate_dir "templates"
validate_file "templates/report_template.html"

echo
echo "📙 BACKEND"
echo "----------"
validate_dir "backend"
validate_file "backend/server.py"
validate_file "backend/config.py"
validate_file "backend/requirements.txt"
validate_file "backend/Dockerfile"
validate_file "backend/__init__.py"

echo
echo "🛡️ SERVICES CYBERSÉCURITÉ (23)"
echo "-------------------------------"
validate_dir "backend/cybersecurity"
validate_file "backend/cybersecurity/__init__.py"

CYBER_SERVICES=(
    "audit" "pentest" "incident_response" "digital_forensics"
    "vulnerability_management" "compliance" "monitoring"
    "red_team" "blue_team" "cloud_security" "mobile_security"
    "iot_security" "web3_security" "ai_security" "network_security"
    "api_security" "container_security" "iac_security"
    "social_engineering" "threat_intelligence" "security_orchestration"
    "risk_assessment" "security_training"
)

for service in "${CYBER_SERVICES[@]}"; do
    validate_dir "backend/cybersecurity/$service"
    validate_file "backend/cybersecurity/$service/__init__.py"
    validate_file "backend/cybersecurity/$service/main.py"
done

echo
echo "🧠 SERVICES IA (7)"
echo "------------------"
validate_dir "backend/ai_core"
validate_file "backend/ai_core/__init__.py"

AI_SERVICES=(
    "assistant" "cyber_ai" "conversational_ai" "predictive_ai"
    "business_ai" "automation_ai" "code_analysis_ai"
)

for service in "${AI_SERVICES[@]}"; do
    validate_dir "backend/ai_core/$service"
    validate_file "backend/ai_core/$service/__init__.py"
    validate_file "backend/ai_core/$service/main.py"
done

echo
echo "💼 SERVICES BUSINESS (5)"
echo "------------------------"
validate_dir "backend/business"
validate_file "backend/business/__init__.py"

BUSINESS_SERVICES=("crm" "billing" "analytics" "planning" "training")

for service in "${BUSINESS_SERVICES[@]}"; do
    validate_dir "backend/business/$service"
    validate_file "backend/business/$service/__init__.py"
    validate_file "backend/business/$service/main.py"
done

echo
echo "🎨 FRONTEND"
echo "-----------"
validate_dir "frontend"
validate_dir "frontend/src"
validate_dir "frontend/public"
validate_file "frontend/package.json"
validate_file "frontend/tailwind.config.js"
validate_file "frontend/postcss.config.js"
validate_file "frontend/vite.config.js"
validate_file "frontend/Dockerfile"

echo
echo "🎨 FRONTEND STRUCTURE"
echo "--------------------"
validate_dir "frontend/src/components"
validate_dir "frontend/src/components/common"
validate_dir "frontend/src/components/cybersecurity"
validate_dir "frontend/src/components/ai"  
validate_dir "frontend/src/components/business"
validate_dir "frontend/src/components/layouts"
validate_file "frontend/src/components/common/ServiceCard.jsx"
validate_file "frontend/src/components/layouts/Sidebar.jsx"

validate_dir "frontend/src/pages"
validate_dir "frontend/src/pages/Dashboard"
validate_file "frontend/src/pages/Dashboard/Dashboard.jsx"
validate_dir "frontend/src/pages/Security"
validate_dir "frontend/src/pages/AI"
validate_dir "frontend/src/pages/Business"
validate_dir "frontend/src/pages/Reports"

validate_dir "frontend/src/services"
validate_file "frontend/src/services/api.js"
validate_dir "frontend/src/hooks"
validate_dir "frontend/src/utils"
validate_file "frontend/src/utils/constants.js"
validate_dir "frontend/src/store"
validate_dir "frontend/src/styles"
validate_file "frontend/src/styles/globals.css"

validate_file "frontend/src/App.js"
validate_file "frontend/src/index.js"

echo
echo "📊 RÉSUMÉ VALIDATION"
echo "===================="
echo "❌ Erreurs: $ERRORS"
echo "⚠️ Avertissements: $WARNINGS"

if [ $ERRORS -eq 0 ]; then
    echo "🎉 VALIDATION RÉUSSIE - Arborescence 100% conforme à l'architecture !"
    echo "✅ Tous les 35 services sont structurés et prêts pour l'implémentation"  
    echo "📖 RAPPEL : Consulter ARCHITECTURE.md avant toute modification"
    echo "🔒 RÈGLES : Lire REGLES_DEVELOPPEMENT.md pour les directives complètes"
    echo "🚀 Prêt pour Sprint 1.1 - Infrastructure & Assistant IA"
    exit 0
else
    echo "💥 VALIDATION ÉCHOUÉE - $ERRORS éléments manquants"
    echo "⚠️  VÉRIFIER la conformité avec ARCHITECTURE.md"
    echo "🔧 UTILISER ./scripts/clean_project.sh pour nettoyer si nécessaire"
    exit 1
fi