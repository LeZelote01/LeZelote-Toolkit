/**
 * Service API central pour CyberSec Toolkit Pro 2025
 */
import axios from 'axios';

// Configuration de base - Utiliser exclusivement REACT_APP_BACKEND_URL si défini, sinon routes relatives '/api'
const BACKEND_FROM_ENV = (import.meta?.env?.REACT_APP_BACKEND_URL && import.meta.env.REACT_APP_BACKEND_URL.trim()) ? import.meta.env.REACT_APP_BACKEND_URL.trim() : '';

// Base URL finale: si REACT_APP_BACKEND_URL est défini, on l'utilise, sinon on utilise '/api' (routage Ingress Kubernetes)
const API_BASE = BACKEND_FROM_ENV ? `${BACKEND_FROM_ENV}` : '';

if (!BACKEND_FROM_ENV) {
  console.warn('[API] REACT_APP_BACKEND_URL non défini. Utilisation du routage relatif "/api" via l\'Ingress.');
}

// Instance Axios configurée
const api = axios.create({
  baseURL: `${API_BASE}`,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Intercepteur pour les requêtes
api.interceptors.request.use(
  (config) => {
    // Ajouter token JWT si disponible
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur pour les réponses
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expiré ou invalide
      localStorage.removeItem('authToken');
      // Rediriger vers login si nécessaire
    }
    return Promise.reject(error);
  }
);

// Services API
export const apiService = {
  // Status et santé
  getStatus: () => api.get('/'),
  getHealth: () => api.get('/health'),

  // Services Cybersécurité (placeholders)
  cybersecurity: {
    audit: () => api.get('/audit/'),
    pentest: () => api.get('/pentesting/'),
    incident: () => api.get('/incident-response/'),
    forensics: () => api.get('/digital-forensics/'),
    compliance: () => api.get('/compliance/'),
    monitoring: () => api.get('/monitoring/')
  },

  // Services IA (placeholders)
  ai: {
    assistant: (message) => api.post('/assistant/', { message }),
    cyber: () => api.get('/cyber-ai/'),
    predictive: () => api.get('/predictive-ai/'),
    automation: () => api.get('/automation-ai/')
  },

  // Services Business (placeholders)
  business: {
    crm: () => api.get('/crm/'),
    billing: () => api.get('/billing/'),
    analytics: () => api.get('/analytics/'),
    planning: () => api.get('/planning/')
  },

  // Rapports
  reports: {
    generate: (type, data) => api.post('/reports/', { type, data }),
    list: () => api.get('/reports/'),
    download: (reportId) => api.get(`/reports/${reportId}/download`)
  }
};

export default api;