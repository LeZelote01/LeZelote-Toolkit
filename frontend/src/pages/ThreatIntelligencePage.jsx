import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  PlayIcon, 
  PauseIcon, 
  MagnifyingGlassIcon,
  ShieldExclamationIcon,
  GlobeAltIcon,
  DocumentTextIcon,
  CogIcon,
  PlusIcon,
  EyeIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  FunnelIcon,
  CloudArrowDownIcon,
  UserGroupIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const api = axios.create({ baseURL: API_BASE });

export default function ThreatIntelligencePage() {
  const [status, setStatus] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [iocs, setIocs] = useState([]);
  const [feeds, setFeeds] = useState([]);
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isEngineRunning, setIsEngineRunning] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateIOC, setShowCreateIOC] = useState(false);

  useEffect(() => {
    loadThreatIntelligenceStatus();
    loadDashboard();
    loadIOCs();
    loadFeeds();
    loadInsights();

    // Actualisation automatique toutes les 60 secondes
    const interval = setInterval(() => {
      if (activeTab === 'dashboard') {
        loadDashboard();
      } else if (activeTab === 'iocs') {
        loadIOCs();
      } else if (activeTab === 'feeds') {
        loadFeeds();
      }
    }, 60000);

    return () => clearInterval(interval);
  }, [activeTab]);

  const loadThreatIntelligenceStatus = async () => {
    try {
      const response = await api.get('/api/threat-intelligence/');
      setStatus(response.data);
      setIsEngineRunning(true); // Assuming operational means running
    } catch (error) {
      console.error('Erreur chargement status TI:', error);
    }
  };

  const loadDashboard = async () => {
    try {
      const response = await api.get('/api/threat-intelligence/dashboard');
      setDashboard(response.data);
    } catch (error) {
      console.error('Erreur chargement dashboard TI:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadIOCs = async () => {
    try {
      const response = await api.post('/api/threat-intelligence/iocs/search', {
        query: searchQuery,
        limit: 50,
        offset: 0
      });
      setIocs(response.data.iocs);
    } catch (error) {
      console.error('Erreur chargement IOCs:', error);
    }
  };

  const loadFeeds = async () => {
    try {
      const response = await api.get('/api/threat-intelligence/feeds');
      setFeeds(response.data.feeds);
    } catch (error) {
      console.error('Erreur chargement feeds:', error);
    }
  };

  const loadInsights = async () => {
    try {
      const response = await api.get('/api/threat-intelligence/insights');
      setInsights(response.data.insights);
    } catch (error) {
      console.error('Erreur chargement insights:', error);
    }
  };

  const toggleEngine = async () => {
    try {
      const endpoint = isEngineRunning ? '/api/threat-intelligence/stop' : '/api/threat-intelligence/start';
      const response = await api.post(endpoint);
      
      if (response.data.status === 'success') {
        setIsEngineRunning(!isEngineRunning);
        loadThreatIntelligenceStatus();
        loadDashboard();
      }
    } catch (error) {
      console.error('Erreur toggle moteur TI:', error);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-blue-600 bg-blue-50 border-blue-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <ExclamationTriangleIcon className="w-4 h-4" />;
      case 'high': return <ShieldExclamationIcon className="w-4 h-4" />;
      case 'medium': return <ClockIcon className="w-4 h-4" />;
      case 'low': return <CheckCircleIcon className="w-4 h-4" />;
      default: return <GlobeAltIcon className="w-4 h-4" />;
    }
  };

  const getIOCTypeIcon = (type) => {
    switch (type) {
      case 'ip_address': return <GlobeAltIcon className="w-4 h-4" />;
      case 'domain': return <ComputerDesktopIcon className="w-4 h-4" />;
      case 'file_hash': return <DocumentTextIcon className="w-4 h-4" />;
      case 'url': return <GlobeAltIcon className="w-4 h-4" />;
      default: return <DocumentTextIcon className="w-4 h-4" />;
    }
  };

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'high': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getFeedStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-red-100 text-red-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="p-6 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Chargement Threat Intelligence...</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Threat Intelligence</h1>
          <p className="text-gray-600 mt-1">Gestion des IOCs, CTI feeds et attribution de menaces</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className={`flex items-center px-3 py-1 rounded-full text-sm ${
            isEngineRunning ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-2 ${
              isEngineRunning ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            {isEngineRunning ? 'Moteur Actif' : 'Moteur Inactif'}
          </div>
          
          <button
            onClick={toggleEngine}
            className={`flex items-center px-4 py-2 rounded-lg font-medium ${
              isEngineRunning 
                ? 'bg-red-600 text-white hover:bg-red-700' 
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isEngineRunning ? (
              <>
                <PauseIcon className="w-4 h-4 mr-2" />
                Arrêter Moteur
              </>
            ) : (
              <>
                <PlayIcon className="w-4 h-4 mr-2" />
                Démarrer Moteur
              </>
            )}
          </button>
        </div>
      </div>

      {/* Status Overview */}
      {status && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{status.total_iocs}</div>
              <div className="text-sm text-gray-600">Total IOCs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{status.active_iocs}</div>
              <div className="text-sm text-gray-600">IOCs Actifs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{status.total_feeds}</div>
              <div className="text-sm text-gray-600">Feeds CTI</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{status.threat_actors}</div>
              <div className="text-sm text-gray-600">Threat Actors</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{status.campaigns}</div>
              <div className="text-sm text-gray-600">Campagnes</div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'dashboard', label: 'Dashboard', icon: ComputerDesktopIcon },
            { key: 'iocs', label: 'IOCs', icon: ShieldExclamationIcon },
            { key: 'feeds', label: 'Feeds CTI', icon: CloudArrowDownIcon },
            { key: 'insights', label: 'Insights', icon: DocumentTextIcon }
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && dashboard && (
        <div className="space-y-6">
          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Vue d'Ensemble</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Statut Moteur:</span>
                  <span className={`font-medium ${
                    dashboard.overview.engine_status === 'active' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {dashboard.overview.engine_status === 'active' ? 'Actif' : 'Inactif'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">IOCs Actifs:</span>
                  <span className="font-medium">{dashboard.overview.active_iocs}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Feeds Actifs:</span>
                  <span className="font-medium">{dashboard.overview.feeds_active}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Queue Enrichissement:</span>
                  <span className="font-medium">{dashboard.overview.enrichment_queue}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistiques IOCs</h3>
              <div className="space-y-3">
                {dashboard.ioc_statistics.by_severity && Object.entries(dashboard.ioc_statistics.by_severity).map(([severity, count]) => (
                  <div key={severity} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(severity)}`}>
                        {getSeverityIcon(severity)}
                        <span className="ml-1 capitalize">{severity}</span>
                      </span>
                    </div>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Activité Récente</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Ajoutés 24h:</span>
                  <span className="font-medium text-green-600">{dashboard.recent_activity.added_last_24h}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Modifiés 24h:</span>
                  <span className="font-medium text-blue-600">{dashboard.recent_activity.updated_last_24h}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Expirent bientôt:</span>
                  <span className="font-medium text-orange-600">{dashboard.recent_activity.expiring_soon}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Faux positifs:</span>
                  <span className="font-medium text-red-600">{dashboard.recent_activity.false_positives}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Recommandations */}
          {dashboard.recommendations && dashboard.recommendations.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-blue-800 mb-4">Recommandations</h3>
              <ul className="space-y-2">
                {dashboard.recommendations.map((recommendation, index) => (
                  <li key={index} className="flex items-start text-blue-700">
                    <CheckCircleIcon className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" />
                    {recommendation}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* IOCs Tab */}
      {activeTab === 'iocs' && (
        <div className="space-y-6">
          {/* Search and Actions */}
          <div className="flex justify-between items-center">
            <div className="relative flex-1 max-w-md">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher IOCs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && loadIOCs()}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex space-x-3">
              <button
                onClick={loadIOCs}
                className="flex items-center px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                <FunnelIcon className="w-4 h-4 mr-2" />
                Rechercher
              </button>
              <button
                onClick={() => setShowCreateIOC(true)}
                className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <PlusIcon className="w-4 h-4 mr-2" />
                Ajouter IOC
              </button>
            </div>
          </div>

          {/* IOCs Table */}
          <div className="bg-white rounded-lg shadow-md">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Indicateurs de Compromission</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      IOC
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Sévérité
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Confiance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Threat Actor
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Première Vue
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {iocs.map((ioc) => (
                    <tr key={ioc.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="flex items-center">
                          {getIOCTypeIcon(ioc.type)}
                          <div className="ml-3">
                            <div className="text-sm font-medium text-gray-900 truncate max-w-xs">
                              {ioc.value}
                            </div>
                            {ioc.threat_type && (
                              <div className="text-sm text-gray-500 capitalize">
                                {ioc.threat_type.replace('_', ' ')}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 capitalize">
                        {ioc.type.replace('_', ' ')}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(ioc.severity)}`}>
                          {getSeverityIcon(ioc.severity)}
                          <span className="ml-1 capitalize">{ioc.severity}</span>
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getConfidenceColor(ioc.confidence)}`}>
                          {ioc.confidence}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {ioc.threat_actor || '-'}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(ioc.first_seen).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        <button className="text-blue-600 hover:text-blue-900">
                          <EyeIcon className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {iocs.length === 0 && (
                <div className="text-center py-12">
                  <ShieldExclamationIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun IOC</h3>
                  <p className="mt-1 text-sm text-gray-500">Commencez par ajouter vos premiers indicateurs.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Feeds Tab */}
      {activeTab === 'feeds' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">Feeds CTI</h3>
            <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              <PlusIcon className="w-4 h-4 mr-2" />
              Ajouter Feed
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {feeds.map((feed) => (
              <div key={feed.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-lg font-semibold text-gray-900 truncate">{feed.name}</h4>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getFeedStatusColor(feed.status)}`}>
                    {feed.status}
                  </span>
                </div>
                
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Provider:</span>
                    <span className="font-medium">{feed.provider}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium uppercase">{feed.feed_type}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">IOCs Importés:</span>
                    <span className="font-medium">{feed.iocs_imported}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Dernière MAJ:</span>
                    <span className="font-medium">
                      {feed.last_update ? new Date(feed.last_update).toLocaleDateString() : 'Jamais'}
                    </span>
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="flex space-x-2">
                    <button className="flex-1 text-xs bg-blue-100 text-blue-700 py-2 px-3 rounded hover:bg-blue-200">
                      Configurer
                    </button>
                    <button className="flex-1 text-xs bg-green-100 text-green-700 py-2 px-3 rounded hover:bg-green-200">
                      Tester
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {feeds.length === 0 && (
            <div className="text-center py-12">
              <CloudArrowDownIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun feed CTI</h3>
              <p className="mt-1 text-sm text-gray-500">Configurez des feeds pour automatiser la collecte d'IOCs.</p>
            </div>
          )}
        </div>
      )}

      {/* Insights Tab */}
      {activeTab === 'insights' && (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-gray-900">Insights Threat Intelligence</h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {insights.map((insight) => (
              <div key={insight.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">{insight.title}</h4>
                    <p className="text-gray-600 text-sm">{insight.description}</p>
                  </div>
                  <div className="ml-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(insight.severity)}`}>
                      {getSeverityIcon(insight.severity)}
                      <span className="ml-1 capitalize">{insight.severity}</span>
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-gray-500">
                    <span className="capitalize">{insight.insight_type}</span>
                    <span className="mx-2">•</span>
                    <span className={`${getConfidenceColor(insight.confidence)} px-2 py-1 rounded`}>
                      {insight.confidence} confiance
                    </span>
                  </div>
                </div>

                {insight.recommendations && insight.recommendations.length > 0 && (
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                    <h5 className="text-sm font-medium text-gray-900 mb-2">Recommandations:</h5>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {insight.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start">
                          <span className="w-1 h-1 bg-gray-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>

          {insights.length === 0 && (
            <div className="text-center py-12">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun insight</h3>
              <p className="mt-1 text-sm text-gray-500">Les insights seront générés automatiquement avec plus de données.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}