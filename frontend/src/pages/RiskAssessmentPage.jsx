import React, { useState, useEffect } from 'react';
import { Shield, TrendingUp, AlertTriangle, CheckCircle, XCircle, BarChart3, FileText, Target, Settings, Activity } from 'lucide-react';

const RiskAssessmentPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [assessments, setAssessments] = useState([]);
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchRiskAssessmentData();
  }, []);

  const fetchRiskAssessmentData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/risk/`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données Risk Assessment:', error);
    }
  };

  const handleAssessmentSubmit = async (assessmentData) => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/risk/assess`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(assessmentData),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Évaluation lancée avec succès! ID: ${result.assessment_id}`);
        fetchAssessments();
      } else {
        throw new Error('Erreur lors du lancement de l\'évaluation');
      }
    } catch (error) {
      console.error('Erreur évaluation risques:', error);
      alert('Erreur lors du lancement de l\'évaluation');
    } finally {
      setLoading(false);
    }
  };

  const fetchAssessments = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/risk/assessments`);
      if (response.ok) {
        const data = await response.json();
        setAssessments(data.assessments || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des évaluations:', error);
    }
  };

  const fetchRisks = async (assessmentId = null) => {
    try {
      let url = `${process.env.REACT_APP_BACKEND_URL}/api/risk/dashboard`;
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setRisks(data.top_risks || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des risques:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'assessments') {
      fetchAssessments();
    } else if (activeTab === 'risks') {
      fetchRisks();
    }
  }, [activeTab]);

  const getRiskLevelColor = (level) => {
    const colors = {
      critical: 'text-red-600 bg-red-100',
      high: 'text-orange-600 bg-orange-100',
      medium: 'text-yellow-600 bg-yellow-100',
      low: 'text-blue-600 bg-blue-100'
    };
    return colors[level] || colors.medium;
  };

  const getStatusColor = (status) => {
    const colors = {
      in_progress: 'text-blue-600 bg-blue-100',
      completed: 'text-green-600 bg-green-100',
      draft: 'text-gray-600 bg-gray-100'
    };
    return colors[status] || colors.draft;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <Activity className="h-8 w-8 text-red-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Risk Assessment</h1>
                <p className="text-gray-600">Évaluation et gestion des risques cybersécurité</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-red-600">{stats.critical_risks || 0}</div>
                <div className="text-sm text-gray-500">Risques critiques</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-600">{stats.total_risks_identified || 0}</div>
                <div className="text-sm text-gray-500">Risques identifiés</div>
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
              { id: 'assessment', name: 'Nouvelle Évaluation', icon: Target },
              { id: 'assessments', name: 'Évaluations', icon: FileText },
              { id: 'risks', name: 'Risques', icon: AlertTriangle },
              { id: 'dashboard', name: 'Dashboard', icon: BarChart3 }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-red-500 text-red-600'
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
                    <p className="text-sm text-gray-600">Évaluations Actives</p>
                    <p className="text-2xl font-bold text-red-600">{stats.active_assessments || 0}</p>
                  </div>
                  <Target className="h-8 w-8 text-red-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Évaluations Terminées</p>
                    <p className="text-2xl font-bold text-green-600">{stats.completed_assessments || 0}</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Risques Critiques</p>
                    <p className="text-2xl font-bold text-red-600">{stats.critical_risks || 0}</p>
                  </div>
                  <XCircle className="h-8 w-8 text-red-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Risques Totaux</p>
                    <p className="text-2xl font-bold text-blue-600">{stats.total_risks_identified || 0}</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-blue-600" />
                </div>
              </div>
            </div>

            {/* Risk Trend */}
            {stats.risk_trend && (
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Tendance des Risques</h3>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-yellow-600">{stats.risk_trend.overall_risk_level}</div>
                      <div className="text-sm text-gray-500">Niveau global</div>
                    </div>
                    <div className="text-center">
                      <div className={`text-2xl font-bold ${
                        stats.risk_trend.trend_direction === 'increasing' ? 'text-red-600' :
                        stats.risk_trend.trend_direction === 'decreasing' ? 'text-green-600' :
                        'text-blue-600'
                      }`}>
                        {stats.risk_trend.trend_direction}
                      </div>
                      <div className="text-sm text-gray-500">Tendance</div>
                    </div>
                  </div>
                  <TrendingUp className={`h-12 w-12 ${
                    stats.risk_trend.trend_direction === 'increasing' ? 'text-red-600' :
                    stats.risk_trend.trend_direction === 'decreasing' ? 'text-green-600' :
                    'text-blue-600'
                  }`} />
                </div>
              </div>
            )}

            {/* Supported Frameworks */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Frameworks Supportés</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {(stats.supported_frameworks || []).map((framework, index) => (
                  <div key={index} className="flex items-center space-x-2 p-3 bg-red-50 rounded-lg">
                    <Shield className="h-5 w-5 text-red-600" />
                    <span className="font-medium text-gray-900">{framework}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Compliance Status */}
            {stats.compliance_status && (
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">État de Conformité</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                  {Object.entries(stats.compliance_status).map(([framework, score]) => (
                    <div key={framework} className="text-center">
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
                            strokeDasharray={`${(score / 100) * 188.4} 188.4`}
                            className={`${
                              score >= 80 ? 'text-green-600' : 
                              score >= 60 ? 'text-yellow-600' : 'text-red-600'
                            }`}
                          />
                        </svg>
                        <span className={`absolute text-sm font-bold ${
                          score >= 80 ? 'text-green-600' : 
                          score >= 60 ? 'text-yellow-600' : 'text-red-600'
                        }`}>{score}%</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-2 uppercase">{framework}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'assessment' && (
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Nouvelle Évaluation des Risques</h3>
            <AssessmentForm onSubmit={handleAssessmentSubmit} loading={loading} />
          </div>
        )}

        {activeTab === 'assessments' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Gestion des Évaluations</h3>
            </div>
            <AssessmentsList assessments={assessments} />
          </div>
        )}

        {activeTab === 'risks' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Registre des Risques</h3>
            </div>
            <RisksList risks={risks} />
          </div>
        )}

        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            <RiskDashboard />
          </div>
        )}
      </div>
    </div>
  );
};

// Composant formulaire d'évaluation
const AssessmentForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    assessment_name: '',
    scope: 'organization',
    target_identifier: '',
    assessment_type: 'comprehensive',
    frameworks: ['NIST'],
    include_threat_modeling: true,
    include_vulnerability_scan: true
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.assessment_name.trim()) {
      alert('Veuillez saisir un nom d\'évaluation');
      return;
    }
    if (!formData.target_identifier.trim()) {
      alert('Veuillez saisir un identifiant cible');
      return;
    }
    onSubmit(formData);
  };

  const toggleFramework = (framework) => {
    const frameworks = formData.frameworks.includes(framework)
      ? formData.frameworks.filter(f => f !== framework)
      : [...formData.frameworks, framework];
    setFormData({...formData, frameworks});
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nom de l'Évaluation
          </label>
          <input
            type="text"
            value={formData.assessment_name}
            onChange={(e) => setFormData({...formData, assessment_name: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            placeholder="Évaluation des risques Q4 2023..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Identifiant Cible
          </label>
          <input
            type="text"
            value={formData.target_identifier}
            onChange={(e) => setFormData({...formData, target_identifier: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            placeholder="Nom du département, projet..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Périmètre
          </label>
          <select
            value={formData.scope}
            onChange={(e) => setFormData({...formData, scope: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            <option value="organization">Organisation</option>
            <option value="department">Département</option>
            <option value="project">Projet</option>
            <option value="asset">Asset Spécifique</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Type d'Évaluation
          </label>
          <select
            value={formData.assessment_type}
            onChange={(e) => setFormData({...formData, assessment_type: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
          >
            <option value="rapid">Rapide (2-5 jours)</option>
            <option value="focused">Ciblée (1-2 semaines)</option>
            <option value="comprehensive">Complète (2-4 semaines)</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Frameworks de Référence
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {['NIST', 'ISO27001', 'FAIR', 'OCTAVE'].map((framework) => (
            <label key={framework} className="flex items-center">
              <input
                type="checkbox"
                checked={formData.frameworks.includes(framework)}
                onChange={() => toggleFramework(framework)}
                className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
              />
              <span className="ml-2 text-sm text-gray-900">{framework}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={formData.include_threat_modeling}
            onChange={(e) => setFormData({...formData, include_threat_modeling: e.target.checked})}
            className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
          />
          <span className="ml-2 text-sm text-gray-900">Inclure la modélisation des menaces</span>
        </label>

        <label className="flex items-center">
          <input
            type="checkbox"
            checked={formData.include_vulnerability_scan}
            onChange={(e) => setFormData({...formData, include_vulnerability_scan: e.target.checked})}
            className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
          />
          <span className="ml-2 text-sm text-gray-900">Inclure l'analyse de vulnérabilités</span>
        </label>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Lancement en cours...</span>
            </>
          ) : (
            <>
              <Target className="h-4 w-4" />
              <span>Lancer l'Évaluation</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};

// Composant liste des évaluations
const AssessmentsList = ({ assessments }) => {
  if (!assessments.length) {
    return (
      <div className="p-8 text-center text-gray-500">
        <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <p>Aucune évaluation disponible</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Évaluation
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Périmètre
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Risques
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Score
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {assessments.map((assessment) => (
            <tr key={assessment.assessment_id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">{assessment.assessment_name}</div>
                <div className="text-sm text-gray-500">{assessment.target_identifier}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  assessment.status === 'completed' ? 'text-green-600 bg-green-100' :
                  assessment.status === 'in_progress' ? 'text-blue-600 bg-blue-100' :
                  'text-gray-600 bg-gray-100'
                }`}>
                  {assessment.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                {assessment.scope}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                {assessment.assessment_type}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {assessment.total_risks && (
                  <div className="flex space-x-1">
                    <span className="text-red-600 font-medium">{assessment.critical_risks}</span>
                    <span>/</span>
                    <span>{assessment.total_risks}</span>
                  </div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                {assessment.overall_risk_score && (
                  <span className={`font-medium ${
                    assessment.overall_risk_score >= 8 ? 'text-red-600' :
                    assessment.overall_risk_score >= 6 ? 'text-orange-600' :
                    assessment.overall_risk_score >= 4 ? 'text-yellow-600' :
                    'text-green-600'
                  }`}>
                    {assessment.overall_risk_score}/10
                  </span>
                )}
                {assessment.progress && (
                  <div className="w-20 bg-gray-200 rounded-full h-2 mt-1">
                    <div 
                      className="bg-red-600 h-2 rounded-full" 
                      style={{ width: `${assessment.progress}%` }}
                    ></div>
                  </div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(assessment.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Composant liste des risques
const RisksList = ({ risks }) => {
  if (!risks.length) {
    return (
      <div className="p-8 text-center text-gray-500">
        <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-400" />
        <p>Aucun risque identifié</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200">
      {risks.map((risk, index) => (
        <div key={index} className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <h4 className="text-lg font-medium text-gray-900">{risk.title}</h4>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  risk.risk_level === 'critical' ? 'text-red-600 bg-red-100' :
                  risk.risk_level === 'high' ? 'text-orange-600 bg-orange-100' :
                  risk.risk_level === 'medium' ? 'text-yellow-600 bg-yellow-100' :
                  'text-blue-600 bg-blue-100'
                }`}>
                  {risk.risk_level.toUpperCase()}
                </span>
                <span className="text-sm text-gray-500">Score: {risk.risk_score}</span>
              </div>
              <p className="text-gray-600 mb-3">{risk.description}</p>
              <div className="flex items-center space-x-6 text-sm text-gray-500 mb-3">
                <span>📂 {risk.category}</span>
                <span>📊 Probabilité: {risk.likelihood}</span>
                <span>💥 Impact: {risk.impact}</span>
              </div>
              {risk.affected_assets && (
                <div className="mb-3">
                  <span className="text-sm font-medium text-gray-700">Assets affectés: </span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {risk.affected_assets.map((asset, i) => (
                      <span key={i} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                        {asset}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Composant dashboard des risques
const RiskDashboard = () => {
  const [dashboard, setDashboard] = useState({});

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/risk/dashboard`);
      if (response.ok) {
        const data = await response.json();
        setDashboard(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement du dashboard:', error);
    }
  };

  if (!dashboard.overview) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Risques Totaux</p>
              <p className="text-2xl font-bold text-blue-600">{dashboard.overview.total_risks}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Critiques</p>
              <p className="text-2xl font-bold text-red-600">{dashboard.overview.critical_risks}</p>
            </div>
            <XCircle className="h-8 w-8 text-red-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Élevés</p>
              <p className="text-2xl font-bold text-orange-600">{dashboard.overview.high_risks}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-orange-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Moyens</p>
              <p className="text-2xl font-bold text-yellow-600">{dashboard.overview.medium_risks}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-yellow-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Score Global</p>
              <p className="text-2xl font-bold text-purple-600">{dashboard.overview.overall_risk_score}</p>
            </div>
            <BarChart3 className="h-8 w-8 text-purple-600" />
          </div>
        </div>
      </div>

      {/* Top Risks */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Risques</h3>
        <div className="space-y-4">
          {dashboard.top_risks?.map((risk, index) => (
            <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-1">
                  <h4 className="font-medium text-gray-900">{risk.title}</h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    risk.risk_level === 'critical' ? 'text-red-600 bg-red-100' :
                    risk.risk_level === 'high' ? 'text-orange-600 bg-orange-100' :
                    'text-yellow-600 bg-yellow-100'
                  }`}>
                    {risk.risk_level.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>📂 {risk.category}</span>
                  <span>📊 {risk.likelihood}</span>
                  <span>💥 {risk.impact}</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-red-600">{risk.risk_score}</div>
                <div className="text-sm text-gray-500">Score</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Risk Categories */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Risques par Catégorie</h3>
        <div className="space-y-4">
          {Object.entries(dashboard.risk_categories || {}).map(([category, data]) => (
            <div key={category} className="flex items-center justify-between">
              <span className="font-medium text-gray-900">{category}</span>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500">{data.count} risques</span>
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      data.avg_score >= 8 ? 'bg-red-500' :
                      data.avg_score >= 6 ? 'bg-orange-500' :
                      data.avg_score >= 4 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${(data.avg_score / 10) * 100}%` }}
                  ></div>
                </div>
                <span className="text-sm font-medium">{data.avg_score}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RiskAssessmentPage;