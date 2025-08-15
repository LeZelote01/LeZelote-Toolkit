import React, { useState, useEffect } from 'react';
import { Shield, PlayCircle, Settings, Clock, CheckCircle, XCircle, AlertTriangle, BarChart3, Zap, GitBranch } from 'lucide-react';

const SecurityOrchestrationPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [playbooks, setPlaybooks] = useState([]);
  const [executions, setExecutions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchSOARData();
  }, []);

  const fetchSOARData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/soar/`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données SOAR:', error);
    }
  };

  const handlePlaybookExecution = async (executionData) => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/soar/playbook/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(executionData),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Playbook exécuté avec succès! ID: ${result.execution_id}`);
        fetchExecutions();
      } else {
        throw new Error('Erreur lors de l\'exécution du playbook');
      }
    } catch (error) {
      console.error('Erreur exécution playbook:', error);
      alert('Erreur lors de l\'exécution du playbook');
    } finally {
      setLoading(false);
    }
  };

  const fetchPlaybooks = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/soar/playbooks`);
      if (response.ok) {
        const data = await response.json();
        setPlaybooks(data.playbooks || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des playbooks:', error);
    }
  };

  const fetchExecutions = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/soar/executions`);
      if (response.ok) {
        const data = await response.json();
        setExecutions(data.executions || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des exécutions:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'playbooks') {
      fetchPlaybooks();
    } else if (activeTab === 'executions') {
      fetchExecutions();
    }
  }, [activeTab]);

  const getStatusColor = (status) => {
    const colors = {
      running: 'text-blue-600 bg-blue-100',
      completed: 'text-green-600 bg-green-100',
      failed: 'text-red-600 bg-red-100',
      cancelled: 'text-gray-600 bg-gray-100'
    };
    return colors[status] || colors.cancelled;
  };

  const getPriorityColor = (priority) => {
    const colors = {
      critical: 'text-red-600 bg-red-100',
      high: 'text-orange-600 bg-orange-100',
      medium: 'text-yellow-600 bg-yellow-100',
      low: 'text-blue-600 bg-blue-100'
    };
    return colors[priority] || colors.medium;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Zap className="h-8 w-8 text-purple-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Security Orchestration (SOAR)</h1>
                <p className="text-gray-600">Automatisation et orchestration de la réponse aux incidents</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-purple-600">{stats.active_executions || 0}</div>
                <div className="text-sm text-gray-500">Exécutions actives</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-green-600">{stats.success_rate || 0}%</div>
                <div className="text-sm text-gray-500">Taux de succès</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8" aria-label="Tabs">
            {[
              { id: 'overview', name: 'Vue d\'ensemble', icon: Shield },
              { id: 'playbooks', name: 'Playbooks', icon: GitBranch },
              { id: 'execute', name: 'Exécuter', icon: PlayCircle },
              { id: 'executions', name: 'Exécutions', icon: Clock },
              { id: 'analytics', name: 'Analytics', icon: BarChart3 }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
              >
                <tab.icon className="h-5 w-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Exécutions Actives</p>
                    <p className="text-2xl font-bold text-purple-600">{stats.active_executions || 0}</p>
                  </div>
                  <Clock className="h-8 w-8 text-purple-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Exécutions Terminées</p>
                    <p className="text-2xl font-bold text-green-600">{stats.completed_executions || 0}</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Playbooks Totaux</p>
                    <p className="text-2xl font-bold text-blue-600">{stats.total_playbooks || 0}</p>
                  </div>
                  <GitBranch className="h-8 w-8 text-blue-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Temps Moyen</p>
                    <p className="text-2xl font-bold text-orange-600">{stats.avg_execution_time || '0 min'}</p>
                  </div>
                  <Clock className="h-8 w-8 text-orange-600" />
                </div>
              </div>
            </div>

            {/* Automation Coverage */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Couverture d'Automatisation</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {Object.entries(stats.automation_coverage || {}).map(([category, percentage]) => (
                  <div key={category} className="text-center">
                    <div className="relative inline-flex items-center justify-center w-20 h-20">
                      <svg className="w-20 h-20 transform -rotate-90">
                        <circle
                          cx="40"
                          cy="40"
                          r="30"
                          stroke="currentColor"
                          strokeWidth="6"
                          fill="transparent"
                          className="text-gray-200"
                        />
                        <circle
                          cx="40"
                          cy="40"
                          r="30"
                          stroke="currentColor"
                          strokeWidth="6"
                          fill="transparent"
                          strokeDasharray={`${(percentage / 100) * 188.4} 188.4`}
                          className="text-purple-600"
                        />
                      </svg>
                      <span className="absolute text-sm font-bold text-purple-600">{percentage}%</span>
                    </div>
                    <p className="text-sm text-gray-600 mt-2 capitalize">{category.replace('_', ' ')}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Supported Integrations */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Intégrations Supportées</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {(stats.supported_integrations || []).map((integration, index) => (
                  <div key={index} className="flex items-center space-x-2 p-3 bg-purple-50 rounded-lg">
                    <Zap className="h-5 w-5 text-purple-600" />
                    <span className="font-medium text-gray-900">{integration}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Efficiency Metrics */}
            {stats.efficiency_metrics && (
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Métriques d'Efficacité</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">{stats.efficiency_metrics.time_saved_hours}h</div>
                    <div className="text-sm text-gray-500">Temps économisé</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">{stats.efficiency_metrics.manual_tasks_automated}</div>
                    <div className="text-sm text-gray-500">Tâches automatisées</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600">{stats.efficiency_metrics.false_positive_reduction}%</div>
                    <div className="text-sm text-gray-500">Réduction faux positifs</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'playbooks' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Playbooks Disponibles</h3>
            </div>
            <PlaybooksList playbooks={playbooks} onExecute={handlePlaybookExecution} />
          </div>
        )}

        {activeTab === 'execute' && (
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Exécuter un Playbook</h3>
            <PlaybookExecutionForm onSubmit={handlePlaybookExecution} loading={loading} playbooks={playbooks} />
          </div>
        )}

        {activeTab === 'executions' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Historique des Exécutions</h3>
            </div>
            <ExecutionsList executions={executions} />
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <SOARAnalytics />
          </div>
        )}
      </div>
    </div>
  );
};

// Composant liste des playbooks
const PlaybooksList = ({ playbooks, onExecute }) => {
  if (!playbooks.length) {
    return (
      <div className="p-8 text-center text-gray-500">
        <GitBranch className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <p>Aucun playbook disponible</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200">
      {playbooks.map((playbook) => (
        <div key={playbook.playbook_id} className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <h4 className="text-lg font-medium text-gray-900">{playbook.name}</h4>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  playbook.status === 'active' ? 'text-green-600 bg-green-100' : 'text-gray-600 bg-gray-100'
                }`}>
                  {playbook.status}
                </span>
              </div>
              <p className="text-gray-600 mb-3">{playbook.description}</p>
              <div className="flex items-center space-x-6 text-sm text-gray-500 mb-3">
                <span>📂 {playbook.category}</span>
                <span>⏱️ {playbook.estimated_duration}</span>
                <span>📊 {playbook.success_rate}% succès</span>
                <span>▶️ {playbook.executions_count} exécutions</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {playbook.trigger_conditions?.map((condition, index) => (
                  <span key={index} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                    {condition}
                  </span>
                ))}
              </div>
            </div>
            <div className="ml-6">
              <button
                onClick={() => onExecute({
                  playbook_id: playbook.playbook_id,
                  execution_mode: 'manual',
                  priority: 'medium'
                })}
                disabled={playbook.status !== 'active'}
                className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <PlayCircle className="h-4 w-4" />
                <span>Exécuter</span>
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Composant formulaire d'exécution
const PlaybookExecutionForm = ({ onSubmit, loading, playbooks }) => {
  const [formData, setFormData] = useState({
    playbook_id: '',
    incident_id: '',
    execution_mode: 'manual',
    priority: 'medium',
    input_parameters: {}
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.playbook_id) {
      alert('Veuillez sélectionner un playbook');
      return;
    }
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Playbook
          </label>
          <select
            value={formData.playbook_id}
            onChange={(e) => setFormData({...formData, playbook_id: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            required
          >
            <option value="">Sélectionner un playbook...</option>
            {playbooks.filter(p => p.status === 'active').map((playbook) => (
              <option key={playbook.playbook_id} value={playbook.playbook_id}>
                {playbook.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            ID Incident (optionnel)
          </label>
          <input
            type="text"
            value={formData.incident_id}
            onChange={(e) => setFormData({...formData, incident_id: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            placeholder="INC-2023-001234"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Mode d'Exécution
          </label>
          <select
            value={formData.execution_mode}
            onChange={(e) => setFormData({...formData, execution_mode: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="manual">Manuel</option>
            <option value="automatic">Automatique</option>
            <option value="scheduled">Programmé</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Priorité
          </label>
          <select
            value={formData.priority}
            onChange={(e) => setFormData({...formData, priority: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            <option value="low">Basse</option>
            <option value="medium">Moyenne</option>
            <option value="high">Haute</option>
            <option value="critical">Critique</option>
          </select>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Exécution en cours...</span>
            </>
          ) : (
            <>
              <PlayCircle className="h-4 w-4" />
              <span>Exécuter le Playbook</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};

// Composant liste des exécutions
const ExecutionsList = ({ executions }) => {
  if (!executions.length) {
    return (
      <div className="p-8 text-center text-gray-500">
        <Clock className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <p>Aucune exécution disponible</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Playbook
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Priorité
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Progression
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Durée
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {executions.map((execution) => (
            <tr key={execution.execution_id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">{execution.playbook_name}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  execution.status === 'running' ? 'text-blue-600 bg-blue-100' :
                  execution.status === 'completed' ? 'text-green-600 bg-green-100' :
                  execution.status === 'failed' ? 'text-red-600 bg-red-100' :
                  'text-gray-600 bg-gray-100'
                }`}>
                  {execution.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  execution.priority === 'critical' ? 'text-red-600 bg-red-100' :
                  execution.priority === 'high' ? 'text-orange-600 bg-orange-100' :
                  execution.priority === 'medium' ? 'text-yellow-600 bg-yellow-100' :
                  'text-blue-600 bg-blue-100'
                }`}>
                  {execution.priority}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {execution.steps_completed}/{execution.steps_total}
                {execution.progress && (
                  <div className="w-20 bg-gray-200 rounded-full h-2 mt-1">
                    <div 
                      className="bg-purple-600 h-2 rounded-full" 
                      style={{ width: `${execution.progress}%` }}
                    ></div>
                  </div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {execution.duration}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(execution.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Composant analytics SOAR
const SOARAnalytics = () => {
  const [analytics, setAnalytics] = useState({});

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/soar/analytics`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des analytics:', error);
    }
  };

  if (!analytics.overview) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Exécutions Totales</p>
              <p className="text-2xl font-bold text-purple-600">{analytics.overview.total_executions}</p>
            </div>
            <PlayCircle className="h-8 w-8 text-purple-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Taux de Succès</p>
              <p className="text-2xl font-bold text-green-600">{analytics.overview.success_rate}%</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Temps Économisé</p>
              <p className="text-2xl font-bold text-blue-600">{analytics.overview.time_saved_hours}h</p>
            </div>
            <Clock className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Tâches Automatisées</p>
              <p className="text-2xl font-bold text-orange-600">{analytics.overview.manual_tasks_automated}</p>
            </div>
            <Zap className="h-8 w-8 text-orange-600" />
          </div>
        </div>
      </div>

      {/* Playbook Usage */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Utilisation des Playbooks</h3>
        <div className="space-y-4">
          {Object.entries(analytics.playbook_usage || {}).map(([playbook, data]) => (
            <div key={playbook} className="flex items-center justify-between">
              <span className="font-medium text-gray-900">{playbook}</span>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500">{data.executions} exécutions</span>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-purple-600 h-2 rounded-full"
                    style={{ width: `${data.success_rate}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium text-purple-600">{data.success_rate}%</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Time Savings */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Économies de Temps</h3>
        <div className="space-y-4">
          {Object.entries(analytics.time_savings || {}).map(([process, data]) => (
            <div key={process} className="border rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-medium text-gray-900 capitalize">{process.replace('_', ' ')}</h4>
                <span className="text-lg font-bold text-green-600">{data.savings}% économisé</span>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Temps manuel: </span>
                  <span className="font-medium">{data.manual_time} min</span>
                </div>
                <div>
                  <span className="text-gray-500">Temps automatisé: </span>
                  <span className="font-medium">{data.automated_time} min</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Integration Health */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Santé des Intégrations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(analytics.integration_health || {}).map(([integration, status]) => (
            <div key={integration} className="flex items-center justify-between p-3 border rounded-lg">
              <span className="font-medium text-gray-900 capitalize">{integration.replace('_', ' ')}</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                status === 'healthy' ? 'text-green-600 bg-green-100' :
                status === 'degraded' ? 'text-yellow-600 bg-yellow-100' :
                'text-red-600 bg-red-100'
              }`}>
                {status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SecurityOrchestrationPage;