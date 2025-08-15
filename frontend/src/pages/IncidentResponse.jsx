import React, { useState, useEffect } from 'react';
import { ShieldExclamationIcon, PlayIcon, ClipboardDocumentListIcon, ChartBarIcon, EyeIcon } from '@heroicons/react/24/outline';

// URL backend cohérente avec le projet (priorité REACT_APP_BACKEND_URL)
const BACKEND_URL = import.meta.env.REACT_APP_BACKEND_URL || 
                   import.meta.env.VITE_BACKEND_URL || 
                   'http://localhost:8000';

const IncidentResponse = () => {
  const [incidents, setIncidents] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [playbooks, setPlaybooks] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [serviceStatus, setServiceStatus] = useState({});

  useEffect(() => {
    fetchServiceStatus();
    fetchIncidents();
    fetchStatistics();
    fetchPlaybooks();
  }, []);

  const fetchServiceStatus = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/incident-response/`);
      const data = await response.json();
      setServiceStatus(data);
    } catch (error) {
      console.error('Erreur récupération status:', error);
    }
  };

  const fetchIncidents = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/incident-response/incidents`);
      const data = await response.json();
      setIncidents(data.incidents || []);
    } catch (error) {
      console.error('Erreur récupération incidents:', error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/incident-response/statistics`);
      const data = await response.json();
      setStatistics(data);
    } catch (error) {
      console.error('Erreur récupération statistiques:', error);
    }
  };

  const fetchPlaybooks = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/incident-response/playbooks`);
      const data = await response.json();
      setPlaybooks(data.playbooks || []);
    } catch (error) {
      console.error('Erreur récupération playbooks:', error);
    }
  };

  const StatusCard = ({ title, value, icon: Icon, color = "bg-blue-500" }) => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center">
        <div className={`${color} rounded-md p-3`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );

  const SeverityBadge = ({ severity }) => {
    const colors = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800',
      info: 'bg-blue-100 text-blue-800'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[severity] || colors.info}`}>
        {severity}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🚨 Incident Response</h1>
          <p className="text-gray-600 mt-2">
            Gestion complète des incidents de sécurité avec réponse automatisée
          </p>
        </div>

        {/* Service Status */}
        <div className="mb-8 bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">État du Service</h2>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
              <span className="text-sm font-medium text-green-600">
                {serviceStatus.status === 'operational' ? 'Opérationnel' : 'Indisponible'}
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{serviceStatus.active_incidents || 0}</div>
              <div className="text-sm text-gray-600">Incidents Actifs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{serviceStatus.playbooks_available || 0}</div>
              <div className="text-sm text-gray-600">Playbooks Disponibles</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{serviceStatus.incident_categories?.length || 0}</div>
              <div className="text-sm text-gray-600">Types d'Incidents</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{serviceStatus.severity_levels?.length || 0}</div>
              <div className="text-sm text-gray-600">Niveaux de Gravité</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: "Vue d'ensemble", icon: ChartBarIcon },
              { id: 'incidents', label: 'Incidents', icon: ShieldExclamationIcon },
              { id: 'playbooks', label: 'Playbooks', icon: PlayIcon },
              { id: 'statistics', label: 'Statistiques', icon: ClipboardDocumentListIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                  activeTab === tab.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content based on active tab */}
        <div className="bg-white rounded-lg shadow-md">
          {activeTab === 'overview' && (
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Vue d'ensemble des capacités</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-700 mb-3">🔧 Fonctionnalités Clés</h4>
                  <ul className="space-y-2">
                    {[
                      'Réponse automatisée aux incidents',
                      'Exécution de playbooks personnalisés',
                      'Gestion des preuves numériques',
                      'Intelligence des menaces intégrée',
                      'Surveillance temps réel',
                      'Rapports de conformité'
                    ].map((feature, index) => (
                      <li key={index} className="flex items-center text-sm text-gray-600">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-700 mb-3">📊 Types d'Incidents Supportés</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {serviceStatus.incident_categories?.map((category, index) => (
                      <div key={index} className="bg-gray-50 rounded-md p-2 text-center">
                        <span className="text-xs font-medium text-gray-700">{category}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">🚀 Actions Rapides</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 transition-colors">
                    Déclarer Incident Critique
                  </button>
                  <button className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700 transition-colors">
                    Lancer Investigation
                  </button>
                  <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
                    Créer Rapport
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'incidents' && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Incidents de Sécurité</h3>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                  Nouvel Incident
                </button>
              </div>

              {incidents.length === 0 ? (
                <div className="text-center py-12">
                  <ShieldExclamationIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 text-lg">Aucun incident en cours</p>
                  <p className="text-gray-400 text-sm">Les incidents apparaîtront ici une fois déclarés</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Titre</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Gravité</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Créé</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {incidents.map((incident) => (
                        <tr key={incident.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {incident.id.substring(0, 8)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{incident.title}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <SeverityBadge severity={incident.severity} />
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{incident.status}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(incident.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button className="text-blue-600 hover:text-blue-900 mr-3">
                              <EyeIcon className="h-4 w-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === 'playbooks' && (
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Playbooks de Réponse</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {playbooks.map((playbook, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center mb-3">
                      <PlayIcon className="h-6 w-6 text-blue-600 mr-2" />
                      <h4 className="font-semibold text-gray-900">{playbook.name}</h4>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{playbook.description}</p>
                    
                    <div className="space-y-2 text-xs text-gray-500">
                      <div>Étapes: {playbook.steps_count}</div>
                      <div>Automatisées: {playbook.automated_steps}</div>
                      <div>Durée estimée: {playbook.estimated_duration}</div>
                    </div>
                    
                    <div className="mt-4 flex flex-wrap gap-1">
                      {playbook.incident_types?.map((type, idx) => (
                        <span key={idx} className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                          {type}
                        </span>
                      ))}
                    </div>
                    
                    <button className="mt-4 w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors">
                      Exécuter Playbook
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'statistics' && (
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Statistiques des Incidents</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatusCard
                  title="Total Incidents"
                  value={statistics.total_incidents || 0}
                  icon={ShieldExclamationIcon}
                  color="bg-blue-500"
                />
                <StatusCard
                  title="Incidents Confinés"
                  value={statistics.contained_incidents || 0}
                  icon={ChartBarIcon}
                  color="bg-green-500"
                />
                <StatusCard
                  title="Taux de Confinement"
                  value={`${statistics.containment_rate_percent || 0}%`}
                  icon={ClipboardDocumentListIcon}
                  color="bg-purple-500"
                />
                <StatusCard
                  title="Temps Moyen (min)"
                  value={statistics.average_response_time_minutes || 'N/A'}
                  icon={EyeIcon}
                  color="bg-orange-500"
                />
              </div>

              {(statistics.by_status || statistics.by_severity) && (
                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                  {statistics.by_status && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-700 mb-3">Par Statut</h4>
                      <div className="space-y-2">
                        {Object.entries(statistics.by_status).map(([status, count]) => (
                          <div key={status} className="flex justify-between">
                            <span className="text-sm text-gray-600">{status}</span>
                            <span className="text-sm font-medium">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {statistics.by_severity && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-700 mb-3">Par Gravité</h4>
                      <div className="space-y-2">
                        {Object.entries(statistics.by_severity).map(([severity, count]) => (
                          <div key={severity} className="flex justify-between">
                            <span className="text-sm text-gray-600">{severity}</span>
                            <span className="text-sm font-medium">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IncidentResponse;