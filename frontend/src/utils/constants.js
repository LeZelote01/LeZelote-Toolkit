/**
 * Constantes globales pour CyberSec Toolkit Pro 2025
 */

// Information application
export const APP_INFO = {
  name: 'CyberSec Toolkit Pro 2025',
  version: '1.0.0',
  description: "L'outil cybersécurité freelance le plus avancé au monde"
};

// Services disponibles
export const SERVICES = {
  CYBERSECURITY: {
    total: 23,
    services: [
      'audit', 'pentest', 'incident_response', 'digital_forensics',
      'vulnerability_management', 'compliance', 'monitoring',
      'red_team', 'blue_team', 'cloud_security', 'mobile_security',
      'iot_security', 'web3_security', 'ai_security', 'network_security',
      'api_security', 'container_security', 'iac_security',
      'social_engineering', 'threat_intelligence', 'security_orchestration',
      'risk_assessment', 'security_training'
    ]
  },
  AI_CORE: {
    total: 7,
    services: [
      'assistant', 'cyber_ai', 'conversational_ai', 'predictive_ai',
      'business_ai', 'automation_ai', 'code_analysis_ai'
    ]
  },
  BUSINESS: {
    total: 5,
    services: ['crm', 'billing', 'analytics', 'planning', 'training']
  }
};

// Phases de développement
export const DEVELOPMENT_PHASES = {
  PHASE_1: {
    name: 'MVP Fonctionnel',
    duration: 'Semaines 1-2',
    services: ['Assistant IA', 'Tests Pénétration', 'Génération Rapports', 'Interface UI']
  },
  PHASE_2: {
    name: 'Services Premium',
    duration: 'Semaines 3-4',
    services: ['Incident Response', 'Digital Forensics', 'Compliance', 'Business Tools']
  },
  PHASE_3: {
    name: 'Différenciation Avancée',
    duration: 'Semaines 5-8',
    services: ['Red/Blue Team', 'Cloud Security', 'Mobile Security', 'Services Spécialisés']
  },
  PHASE_4: {
    name: 'Innovation & Scale',
    duration: 'Semaines 9-12',
    services: ['Web3 Security', 'IoT Security', 'AI Security', 'Full Automation']
  }
};

// Statuts des services
export const SERVICE_STATUS = {
  PLANNED: 'planned',
  IN_PROGRESS: 'in_progress', 
  IMPLEMENTED: 'implemented',
  TESTED: 'tested',
  DEPLOYED: 'deployed'
};

// Couleurs thème
export const THEME_COLORS = {
  primary: '#3B82F6',
  secondary: '#8B5CF6',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  cybersecurity: '#DC2626',
  ai: '#8B5CF6',
  business: '#059669'
};

// Messages par défaut
export const DEFAULT_MESSAGES = {
  LOADING: 'Chargement en cours...',
  ERROR: 'Une erreur est survenue',
  NO_DATA: 'Aucune donnée disponible',
  SUCCESS: 'Opération réussie'
};