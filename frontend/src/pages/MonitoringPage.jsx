import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  PlayIcon, 
  PauseIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ChartBarIcon,
  EyeIcon,
  CogIcon,
  DocumentTextIcon,
  BellIcon,
  ServerIcon,
  CpuChipIcon,
  CircleStackIcon
} from '@heroicons/react/24/outline';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const api = axios.create({ baseURL: API_BASE });

export default function MonitoringPage() {
  const [status, setStatus] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [realtimeMetrics, setRealtimeMetrics] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');

  useEffect(() => {
    loadMonitoringStatus();
    loadDashboard();
    loadRealtimeMetrics();
    loadAlerts();
    loadRules();

    // Actualisation automatique toutes les 30 secondes
    const interval = setInterval(() => {
      if (activeTab === 'dashboard') {
        loadDashboard();
        loadRealtimeMetrics();
      } else if (activeTab === 'alerts') {
        loadAlerts();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [activeTab]);

  const loadMonitoringStatus = async () => {
    try {
      const response = await api.get('/api/monitoring/');
      setStatus(response.data);
      setIsMonitoring(response.data.is_monitoring_active);
    } catch (error) {
      console.error('Erreur chargement status monitoring:', error);
    }
  };

  const loadDashboard = async () => {
    try {
      const response = await api.get('/api/monitoring/dashboard');
      setDashboard(response.data);
    } catch (error) {
      console.error('Erreur chargement dashboard:', error);
    }
  };

  const loadRealtimeMetrics = async () => {
    try {
      const response = await api.get('/api/monitoring/metrics/realtime');
      setRealtimeMetrics(response.data.metrics);
    } catch (error) {
      console.error('Erreur chargement métriques temps réel:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadAlerts = async () => {
    try {
      const response = await api.post('/api/monitoring/alerts/search', {
        limit: 20,
        offset: 0
      });
      setAlerts(response.data.alerts);
    } catch (error) {
      console.error('Erreur chargement alertes:', error);
    }
  };

  const loadRules = async () => {
    try {
      const response = await api.get('/api/monitoring/rules');
      setRules(response.data.rules);
    } catch (error) {
      console.error('Erreur chargement règles:', error);
    }
  };

  const toggleMonitoring = async () => {
    try {
      const endpoint = isMonitoring ? '/api/monitoring/stop' : '/api/monitoring/start';
      const response = await api.post(endpoint);
      
      if (response.data.status === 'success') {
        setIsMonitoring(!isMonitoring);
        loadMonitoringStatus();
        loadDashboard();
      }
    } catch (error) {
      console.error('Erreur toggle monitoring:', error);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-50';
      case 'high': return 'text-orange-600 bg-orange-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-blue-600 bg-blue-50';
      case 'info': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <XCircleIcon className="w-5 h-5" />;
      case 'high': return <ExclamationTriangleIcon className="w-5 h-5" />;
      case 'medium': return <ClockIcon className="w-5 h-5" />;
      case 'low': return <CheckCircleIcon className="w-5 h-5" />;
      default: return <BellIcon className="w-5 h-5" />;
    }
  };

  const getMetricIcon = (metricName) => {
    switch (metricName) {
      case 'cpu_usage': return <CpuChipIcon className="w-5 h-5" />;
      case 'memory_usage': return <CircleStackIcon className="w-5 h-5" />;
      case 'disk_usage': return <ServerIcon className="w-5 h-5" />;
      default: return <ChartBarIcon className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="p-6 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Chargement du monitoring...</p>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Monitoring 24/7</h1>
          <p className="text-gray-600 mt-1">Surveillance temps réel et gestion des alertes</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className={`flex items-center px-3 py-1 rounded-full text-sm ${
            isMonitoring ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-2 ${
              isMonitoring ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            {isMonitoring ? 'Actif' : 'Inactif'}
          </div>
          
          <button
            onClick={toggleMonitoring}
            className={`flex items-center px-4 py-2 rounded-lg font-medium ${
              isMonitoring 
                ? 'bg-red-600 text-white hover:bg-red-700' 
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            {isMonitoring ? (
              <>
                <PauseIcon className="w-4 h-4 mr-2" />
                Arrêter Monitoring
              </>
            ) : (
              <>
                <PlayIcon className="w-4 h-4 mr-2" />
                Démarrer Monitoring
              </>
            )}
          </button>
        </div>
      </div>

      {/* Status Overview */}
      {status && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{status.active_alerts}</div>
              <div className="text-sm text-gray-600">Alertes Actives</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{status.monitoring_rules}</div>
              <div className="text-sm text-gray-600">Règles Monitoring</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{status.uptime}</div>
              <div className="text-sm text-gray-600">Uptime</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${
                status.system_health?.monitoring?.status === 'healthy' ? 'text-green-600' : 'text-red-600'
              }`}>
                {status.system_health?.monitoring?.status === 'healthy' ? '✓' : '✗'}
              </div>
              <div className="text-sm text-gray-600">Santé Système</div>
            </div>
          </div>
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { key: 'dashboard', label: 'Dashboard', icon: ChartBarIcon },
            { key: 'alerts', label: 'Alertes', icon: BellIcon },
            { key: 'metrics', label: 'Métriques', icon: CpuChipIcon },
            { key: 'rules', label: 'Règles', icon: CogIcon }
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
                  <span className="text-gray-600">Status Monitoring:</span>
                  <span className={`font-medium ${
                    dashboard.overview.monitoring_status === 'active' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {dashboard.overview.monitoring_status === 'active' ? 'Actif' : 'Inactif'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Alertes 24h:</span>
                  <span className="font-medium">{dashboard.overview.alerts_last_24h}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Alertes Critiques:</span>
                  <span className="font-medium text-red-600">{dashboard.overview.critical_active_alerts}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Métriques Collectées:</span>
                  <span className="font-medium">{dashboard.overview.metrics_collected}</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Répartition Alertes</h3>
              <div className="space-y-3">
                {Object.entries(dashboard.alerts_summary.by_severity).map(([severity, count]) => (
                  <div key={severity} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(severity)}`}>
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
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Alertes Traitées:</span>
                  <span className="font-medium">{dashboard.performance.alerts_processed}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Règles Évaluées:</span>
                  <span className="font-medium">{dashboard.performance.rules_evaluated}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Uptime:</span>
                  <span className="font-medium text-green-600">{dashboard.overview.uptime}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Actions Prioritaires */}
          {dashboard.priority_actions.length > 0 && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-yellow-800 mb-4">Actions Prioritaires</h3>
              <ul className="space-y-2">
                {dashboard.priority_actions.map((action, index) => (
                  <li key={index} className="flex items-start text-yellow-700">
                    <ExclamationTriangleIcon className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" />
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Recommandations */}
          {dashboard.recommendations.length > 0 && (
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

      {/* Alerts Tab */}
      {activeTab === 'alerts' && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Alertes Récentes</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Alerte
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sévérité
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Source
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Détectée
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{alert.title}</div>
                      <div className="text-sm text-gray-500 truncate max-w-xs">
                        {alert.description || 'Pas de description'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(alert.severity)}`}>
                        {getSeverityIcon(alert.severity)}
                        <span className="ml-1 capitalize">{alert.severity}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        alert.status === 'active' ? 'bg-red-100 text-red-800' :
                        alert.status === 'acknowledged' ? 'bg-yellow-100 text-yellow-800' :
                        alert.status === 'resolved' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {alert.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900 capitalize">
                      {alert.source}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {new Date(alert.detected_at).toLocaleString()}
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
            {alerts.length === 0 && (
              <div className="text-center py-12">
                <BellIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune alerte</h3>
                <p className="mt-1 text-sm text-gray-500">Toutes les alertes sont résolues.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Metrics Tab */}
      {activeTab === 'metrics' && realtimeMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Object.entries(realtimeMetrics).map(([metricName, metricData]) => (
            <div key={metricName} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                  {getMetricIcon(metricName)}
                  <span className="ml-2 capitalize">{metricName.replace('_', ' ')}</span>
                </h3>
                {metricData.length > 0 && (
                  <span className="text-2xl font-bold text-blue-600">
                    {Math.round(metricData[metricData.length - 1]?.value || 0)}
                    {metricName.includes('usage') ? '%' : ''}
                  </span>
                )}
              </div>
              <div className="space-y-2">
                {metricData.slice(-5).map((point, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span className="text-gray-500">
                      {new Date(point.timestamp).toLocaleTimeString()}
                    </span>
                    <span className="font-medium">
                      {Math.round(point.value)}{metricName.includes('usage') ? '%' : ''}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Rules Tab */}
      {activeTab === 'rules' && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Règles de Monitoring</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Règle
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Condition
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sévérité
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {rules.map((rule) => (
                  <tr key={rule.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">{rule.name}</div>
                      <div className="text-sm text-gray-500">{rule.description}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      <code className="bg-gray-100 px-2 py-1 rounded text-xs">
                        {rule.condition}
                      </code>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(rule.severity)}`}>
                        {getSeverityIcon(rule.severity)}
                        <span className="ml-1 capitalize">{rule.severity}</span>
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        rule.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {rule.enabled ? 'Activée' : 'Désactivée'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      <button className="text-blue-600 hover:text-blue-900">
                        <CogIcon className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {rules.length === 0 && (
              <div className="text-center py-12">
                <CogIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Aucune règle</h3>
                <p className="mt-1 text-sm text-gray-500">Aucune règle de monitoring configurée.</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}