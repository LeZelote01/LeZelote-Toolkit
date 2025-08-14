import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ServiceCard from '../../components/common/ServiceCard';
import {
  Shield, Brain, Building2, FileText, Activity,
  Lock, Zap, Globe, Smartphone, AlertTriangle
} from 'lucide-react';

const Dashboard = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8002';
        const response = await axios.get(`${API_BASE}/api/`);
        setStatus(response.data);
      } catch (error) {
        console.error('Erreur lors de la récupération du statut:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
  }, []);

  const servicesData = {
    cybersecurity: [
      { icon: <Shield />, title: "Audit Sécurité", description: "Audit sécurité automatisé", phase: "Sprint 1.2" },
      { icon: <Lock />, title: "Tests Pénétration", description: "Tests OWASP Top 10", phase: "Sprint 1.2" },
      { icon: <AlertTriangle />, title: "Incident Response", description: "Réponse incidents 24/7", phase: "Sprint 2.1" },
      { icon: <Activity />, title: "Digital Forensics", description: "Analyse forensique avancée", phase: "Sprint 2.1" },
      { icon: <FileText />, title: "Compliance", description: "Conformité multi-standards", phase: "Sprint 2.2" },
      { icon: <Globe />, title: "Cloud Security", description: "Sécurité AWS/Azure/GCP", phase: "Sprint 3.2" }
    ],
    ai: [
      { icon: <Brain />, title: "Assistant IA", description: "Chat cybersécurité expert", phase: "Sprint 1.1" },
      { icon: <Zap />, title: "IA Cybersécurité", description: "IA spécialisée sécurité", phase: "Sprint 2.1" },
      { icon: <Activity />, title: "IA Prédictive", description: "Prédiction des menaces", phase: "Sprint 3.2" },
      { icon: <Brain />, title: "Automatisation IA", description: "Automation complète", phase: "Sprint 4.2" }
    ],
    business: [
      { icon: <Building2 />, title: "CRM", description: "Gestion clients/projets", phase: "Sprint 2.2" },
      { icon: <FileText />, title: "Facturation", description: "Facturation automatisée", phase: "Sprint 2.2" },
      { icon: <Activity />, title: "Analytics", description: "Analytics business", phase: "Sprint 2.2" }
    ]
  };

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement du tableau de bord...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        {/* En-tête */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🛡️ CyberSec Toolkit Pro 2025
          </h1>
          <p className="text-gray-600 text-lg">
            L'outil cybersécurité freelance le plus avancé au monde
          </p>
        </div>

        {/* Statut global */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-semibold mb-4 flex items-center">
            <Activity className="w-6 h-6 mr-2 text-blue-600" />
            État du Projet
          </h2>
          
          {status ? (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-1">
                  {status.services?.total_planned || 35}
                </div>
                <div className="text-sm text-gray-600">Services Planifiés</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-1">
                  {status.services?.implemented || 0}
                </div>
                <div className="text-sm text-gray-600">Services Implémentés</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-yellow-600 mb-1">
                  {status.version || "1.0.0"}
                </div>
                <div className="text-sm text-gray-600">Version</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-1">
                  {status.services?.phase?.split(' - ')[0] || "Level 0"}
                </div>
                <div className="text-sm text-gray-600">Phase Actuelle</div>
              </div>
            </div>
          ) : (
            <p className="text-gray-500">Erreur lors du chargement du statut</p>
          )}
        </div>

        {/* Services Cybersécurité */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4 flex items-center">
            <Shield className="w-6 h-6 mr-2 text-red-600" />
            Services Cybersécurité (0/23)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {servicesData.cybersecurity.map((service, index) => (
              <ServiceCard
                key={index}
                icon={service.icon}
                title={service.title}
                description={service.description}
                status="planned"
                phase={service.phase}
              />
            ))}
          </div>
        </div>

        {/* Services IA */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4 flex items-center">
            <Brain className="w-6 h-6 mr-2 text-purple-600" />
            Services Intelligence Artificielle (0/7)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {servicesData.ai.map((service, index) => (
              <ServiceCard
                key={index}
                icon={service.icon}
                title={service.title}
                description={service.description}
                status="planned"
                phase={service.phase}
              />
            ))}
          </div>
        </div>

        {/* Services Business */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4 flex items-center">
            <Building2 className="w-6 h-6 mr-2 text-green-600" />
            Services Business (0/5)
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {servicesData.business.map((service, index) => (
              <ServiceCard
                key={index}
                icon={service.icon}
                title={service.title}
                description={service.description}
                status="planned"
                phase={service.phase}
              />
            ))}
          </div>
        </div>

        {/* Prochaines étapes */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
          <h2 className="text-2xl font-semibold mb-4">🚀 Prochaines Étapes</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold mb-2">Phase 1 : MVP Fonctionnel</h3>
              <ul className="space-y-1 opacity-90">
                <li>• Configurer infrastructure (Docker + FastAPI + React)</li>
                <li>• Implémenter Assistant IA conversationnel</li>
                <li>• Créer tests de pénétration de base</li>
                <li>• Générer rapports PDF professionnels</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Objectifs Business</h3>
              <ul className="space-y-1 opacity-90">
                <li>• 2x augmentation tarifs possibles</li>
                <li>• 50% réduction temps audit</li>
                <li>• Services premium facturables</li>
                <li>• Interface moderne niveau enterprise</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;