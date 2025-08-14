#!/bin/bash
# Script de création de l'arborescence complète
# CyberSec Toolkit Pro 2025

echo "🏗️ Création de l'arborescence complète du projet..."

# 📋 DOCUMENTATION/ (déjà créée partiellement)
mkdir -p documentation

# 🐳 INFRASTRUCTURE/
echo "Création INFRASTRUCTURE..."
mkdir -p infrastructure
touch infrastructure/.env.example

# 📊 DATA & TEMPLATES/
echo "Création DATA & TEMPLATES..."
mkdir -p database/schemas
mkdir -p models
mkdir -p templates

# 📙 BACKEND/ - Structure complète
echo "Création BACKEND structure complète..."

# 🛡️ cybersecurity/ - 23 SERVICES CYBERSÉCURITÉ
mkdir -p backend/cybersecurity/audit
mkdir -p backend/cybersecurity/pentest
mkdir -p backend/cybersecurity/incident_response
mkdir -p backend/cybersecurity/digital_forensics
mkdir -p backend/cybersecurity/vulnerability_management
mkdir -p backend/cybersecurity/compliance
mkdir -p backend/cybersecurity/monitoring
mkdir -p backend/cybersecurity/red_team
mkdir -p backend/cybersecurity/blue_team
mkdir -p backend/cybersecurity/cloud_security
mkdir -p backend/cybersecurity/mobile_security
mkdir -p backend/cybersecurity/iot_security
mkdir -p backend/cybersecurity/web3_security
mkdir -p backend/cybersecurity/ai_security
mkdir -p backend/cybersecurity/network_security
mkdir -p backend/cybersecurity/api_security
mkdir -p backend/cybersecurity/container_security
mkdir -p backend/cybersecurity/iac_security
mkdir -p backend/cybersecurity/social_engineering
mkdir -p backend/cybersecurity/threat_intelligence
mkdir -p backend/cybersecurity/security_orchestration
mkdir -p backend/cybersecurity/risk_assessment
mkdir -p backend/cybersecurity/security_training

# 🧠 ai_core/ - 7 SERVICES IA
mkdir -p backend/ai_core/assistant
mkdir -p backend/ai_core/cyber_ai
mkdir -p backend/ai_core/conversational_ai
mkdir -p backend/ai_core/predictive_ai
mkdir -p backend/ai_core/business_ai
mkdir -p backend/ai_core/automation_ai
mkdir -p backend/ai_core/code_analysis_ai

# 💼 business/ - 5 SERVICES BUSINESS
mkdir -p backend/business/crm
mkdir -p backend/business/billing
mkdir -p backend/business/analytics
mkdir -p backend/business/planning
mkdir -p backend/business/training

# 🎨 FRONTEND/ - Structure complète
echo "Création FRONTEND structure complète..."
mkdir -p frontend/src/components/common
mkdir -p frontend/src/components/cybersecurity
mkdir -p frontend/src/components/ai
mkdir -p frontend/src/components/business
mkdir -p frontend/src/components/layouts
mkdir -p frontend/src/pages/Dashboard
mkdir -p frontend/src/pages/Security
mkdir -p frontend/src/pages/AI
mkdir -p frontend/src/pages/Business
mkdir -p frontend/src/pages/Reports
mkdir -p frontend/src/services
mkdir -p frontend/src/hooks
mkdir -p frontend/src/utils
mkdir -p frontend/src/store
mkdir -p frontend/src/styles

echo "✅ Arborescence complète créée!"