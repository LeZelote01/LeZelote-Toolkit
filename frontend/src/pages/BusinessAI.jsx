import React, { useState, useEffect } from 'react';
import { Brain, TrendingUp, DollarSign, AlertTriangle, Target, BarChart3, PieChart, ArrowRight, CheckCircle, Clock, Star } from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const api = axios.create({ baseURL: API_BASE });

function BusinessAI() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [businessStatus, setBusinessStatus] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [metricsData, setMetricsData] = useState(null);
  const [roiScenarios, setRoiScenarios] = useState(null);

  // Charger le statut du service
  useEffect(() => {
    loadBusinessStatus();
  }, []);

  const loadBusinessStatus = async () => {
    try {
      const response = await api.get('/api/business-ai/');
      setBusinessStatus(response.data);
    } catch (error) {
      console.error('Erreur chargement statut Business AI:', error);
    }
  };

  const runBusinessAnalysis = async (analysisType) => {
    setLoading(true);
    try {
      const request = {
        analysis_type: analysisType,
        business_context: {
          company_type: "cybersecurity_consulting",
          size: "medium",
          focus_areas: ["security_consulting", "incident_response", "training"]
        },
        time_period: 30,
        strategic_objectives: ["growth", "efficiency", "risk_mitigation"]
      };

      const response = await api.post('/api/business-ai/analyze', request);
      setAnalysisResult(response.data.analysis);
      setActiveTab('results');
    } catch (error) {
      console.error('Erreur analyse business:', error);
      alert('Erreur lors de l\'analyse business: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/business-ai/metrics');
      setMetricsData(response.data);
    } catch (error) {
      console.error('Erreur chargement métriques:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadROIScenarios = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/business-ai/roi-scenarios');
      setRoiScenarios(response.data);
    } catch (error) {
      console.error('Erreur chargement ROI:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <div className="bg-purple-100 p-3 rounded-lg mr-4">
            <Brain className="w-8 h-8 text-purple-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Business AI</h1>
            <p className="text-gray-600">Intelligence artificielle pour décisions business stratégiques</p>
          </div>
        </div>

        {/* Status Badge */}
        {businessStatus && (
          <div className="flex items-center space-x-4 mb-6">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              businessStatus.analytics_ready ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
              {businessStatus.analytics_ready ? '✅ Opérationnel' : '⚠️ En préparation'}
            </span>
            <span className="text-sm text-gray-600">
              LLM: {businessStatus.llm_configured ? '🤖 Configuré' : '📝 Mode simulation'}
            </span>
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-8 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'dashboard', label: 'Dashboard', icon: <BarChart3 className="w-4 h-4" /> },
          { id: 'analysis', label: 'Analyses', icon: <Brain className="w-4 h-4" /> },
          { id: 'metrics', label: 'Métriques', icon: <PieChart className="w-4 h-4" /> },
          { id: 'roi', label: 'ROI', icon: <DollarSign className="w-4 h-4" /> },
          { id: 'results', label: 'Résultats', icon: <Target className="w-4 h-4" /> }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-white text-purple-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Santé Business</h3>
                <TrendingUp className="w-6 h-6 text-green-500" />
              </div>
              <div className="text-3xl font-bold text-green-600 mb-2">87.5/100</div>
              <p className="text-sm text-gray-600">Score global en amélioration (+5.2 ce mois)</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Revenus Mensuels</h3>
                <DollarSign className="w-6 h-6 text-blue-500" />
              </div>
              <div className="text-3xl font-bold text-blue-600 mb-2">125k€</div>
              <p className="text-sm text-gray-600">Objectif: 150k€ (+16.7% à atteindre)</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Risques Actifs</h3>
                <AlertTriangle className="w-6 h-6 text-orange-500" />
              </div>
              <div className="text-3xl font-bold text-orange-600 mb-2">3</div>
              <p className="text-sm text-gray-600">Niveau de risque: Moyen (65/100)</p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Actions Rapides</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <button
                onClick={() => runBusinessAnalysis('performance')}
                disabled={loading}
                className="flex items-center justify-center space-x-2 p-4 border-2 border-purple-200 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-colors disabled:opacity-50"
              >
                <BarChart3 className="w-5 h-5 text-purple-600" />
                <span className="font-medium">Analyse Performance</span>
              </button>

              <button
                onClick={() => runBusinessAnalysis('roi')}
                disabled={loading}
                className="flex items-center justify-center space-x-2 p-4 border-2 border-green-200 rounded-lg hover:border-green-400 hover:bg-green-50 transition-colors disabled:opacity-50"
              >
                <DollarSign className="w-5 h-5 text-green-600" />
                <span className="font-medium">Calcul ROI</span>
              </button>

              <button
                onClick={() => runBusinessAnalysis('risk_business')}
                disabled={loading}
                className="flex items-center justify-center space-x-2 p-4 border-2 border-orange-200 rounded-lg hover:border-orange-400 hover:bg-orange-50 transition-colors disabled:opacity-50"
              >
                <AlertTriangle className="w-5 h-5 text-orange-600" />
                <span className="font-medium">Évaluation Risques</span>
              </button>

              <button
                onClick={() => runBusinessAnalysis('optimization')}
                disabled={loading}
                className="flex items-center justify-center space-x-2 p-4 border-2 border-blue-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-colors disabled:opacity-50"
              >
                <Target className="w-5 h-5 text-blue-600" />
                <span className="font-medium">Optimisation</span>
              </button>
            </div>
          </div>

          {/* Services Features */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Fonctionnalités Disponibles</h3>
            {businessStatus && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(businessStatus.features).map(([feature, available]) => (
                  <div key={feature} className="flex items-center space-x-3">
                    <CheckCircle className={`w-5 h-5 ${available ? 'text-green-500' : 'text-gray-300'}`} />
                    <span className={`capitalize ${available ? 'text-gray-800' : 'text-gray-400'}`}>
                      {feature.replace(/_/g, ' ')}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Analysis Tab */}
      {activeTab === 'analysis' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Types d'Analyses Disponibles</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                {
                  type: 'performance',
                  title: 'Analyse de Performance',
                  description: 'Évaluation complète des KPIs business et métriques opérationnelles',
                  icon: <BarChart3 className="w-6 h-6 text-blue-600" />,
                  color: 'blue'
                },
                {
                  type: 'roi',
                  title: 'Calcul ROI & Investissements',
                  description: 'Scénarios de retour sur investissement et projections financières',
                  icon: <DollarSign className="w-6 h-6 text-green-600" />,
                  color: 'green'
                },
                {
                  type: 'risk_business',
                  title: 'Évaluation des Risques',
                  description: 'Identification et quantification des risques business',
                  icon: <AlertTriangle className="w-6 h-6 text-orange-600" />,
                  color: 'orange'
                },
                {
                  type: 'optimization',
                  title: 'Optimisation Stratégique',
                  description: 'Recommandations d\'amélioration et opportunités de croissance',
                  icon: <Target className="w-6 h-6 text-purple-600" />,
                  color: 'purple'
                }
              ].map(analysis => (
                <div key={analysis.type} className="border rounded-lg p-6 hover:shadow-md transition-shadow">
                  <div className="flex items-start space-x-4">
                    <div className={`bg-${analysis.color}-100 p-3 rounded-lg`}>
                      {analysis.icon}
                    </div>
                    <div className="flex-1">
                      <h4 className="text-lg font-semibold text-gray-800 mb-2">{analysis.title}</h4>
                      <p className="text-gray-600 text-sm mb-4">{analysis.description}</p>
                      <button
                        onClick={() => runBusinessAnalysis(analysis.type)}
                        disabled={loading}
                        className={`flex items-center space-x-2 px-4 py-2 bg-${analysis.color}-600 text-white rounded-md hover:bg-${analysis.color}-700 transition-colors disabled:opacity-50`}
                      >
                        {loading ? <Clock className="w-4 h-4 animate-spin" /> : analysis.icon}
                        <span>{loading ? 'Analyse en cours...' : 'Lancer l\'analyse'}</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Metrics Tab */}
      {activeTab === 'metrics' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-800">Métriques Business</h3>
            <button
              onClick={loadMetrics}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors disabled:opacity-50"
            >
              {loading ? <Clock className="w-4 h-4 animate-spin" /> : <PieChart className="w-4 h-4" />}
              <span>Actualiser Métriques</span>
            </button>
          </div>

          {metricsData ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {metricsData.metrics.map((metric, index) => (
                  <div key={index} className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-semibold text-gray-800 capitalize">
                        {metric.metric_name.replace(/_/g, ' ')}
                      </h4>
                      <span className={`text-sm px-2 py-1 rounded-full ${
                        metric.trend === 'increasing' ? 'bg-green-100 text-green-800' :
                        metric.trend === 'decreasing' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {metric.trend}
                      </span>
                    </div>
                    <div className="text-2xl font-bold text-gray-800 mb-1">
                      {metric.current_value} {metric.unit}
                    </div>
                    {metric.target_value && (
                      <div className="text-sm text-gray-600">
                        Objectif: {metric.target_value} {metric.unit}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {metricsData.benchmark_comparison && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h4 className="font-semibold text-gray-800 mb-4">Comparaison Benchmarks Industrie</h4>
                  <div className="space-y-4">
                    {Object.entries(metricsData.benchmark_comparison).map(([key, benchmark]) => (
                      <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <span className="font-medium capitalize">{key.replace(/_/g, ' ')}</span>
                        <div className="flex items-center space-x-4">
                          <span>Vous: {benchmark.current}</span>
                          <span>Industrie: {benchmark.industry_average}</span>
                          <span className={`px-2 py-1 rounded text-sm ${
                            benchmark.performance === 'above' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {benchmark.performance === 'above' ? '↗️ Au-dessus' : '↘️ En-dessous'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <PieChart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Cliquez sur "Actualiser Métriques" pour charger les données</p>
            </div>
          )}
        </div>
      )}

      {/* ROI Tab */}
      {activeTab === 'roi' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-800">Scénarios ROI</h3>
            <button
              onClick={loadROIScenarios}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              {loading ? <Clock className="w-4 h-4 animate-spin" /> : <DollarSign className="w-4 h-4" />}
              <span>Calculer ROI</span>
            </button>
          </div>

          {roiScenarios ? (
            <div className="space-y-6">
              {roiScenarios.best_roi && (
                <div className="bg-gradient-to-r from-green-50 to-green-100 border border-green-200 rounded-lg p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <Star className="w-6 h-6 text-green-600" />
                    <h4 className="text-lg font-semibold text-green-800">Meilleur Scénario ROI</h4>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <div className="text-sm text-green-600 mb-1">Investissement</div>
                      <div className="text-xl font-bold text-green-800">
                        {roiScenarios.best_roi.initial_investment.toLocaleString()}€
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-green-600 mb-1">ROI</div>
                      <div className="text-xl font-bold text-green-800">
                        {roiScenarios.best_roi.roi_percentage}%
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-green-600 mb-1">Retour</div>
                      <div className="text-xl font-bold text-green-800">
                        {roiScenarios.best_roi.payback_period_months} mois
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-green-600 mb-1">VAN</div>
                      <div className="text-xl font-bold text-green-800">
                        {roiScenarios.best_roi.net_present_value.toLocaleString()}€
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {roiScenarios.roi_scenarios.map((scenario, index) => (
                  <div key={index} className="bg-white rounded-lg shadow-md p-6">
                    <h4 className="font-semibold text-gray-800 mb-4">{scenario.investment_name}</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Investissement initial</span>
                        <span className="font-medium">{scenario.initial_investment.toLocaleString()}€</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Bénéfices annuels</span>
                        <span className="font-medium text-green-600">{scenario.annual_benefits.toLocaleString()}€</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Coûts annuels</span>
                        <span className="font-medium text-red-600">{scenario.annual_costs.toLocaleString()}€</span>
                      </div>
                      <hr />
                      <div className="flex justify-between text-lg font-semibold">
                        <span>ROI</span>
                        <span className="text-green-600">{scenario.roi_percentage}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Période de retour</span>
                        <span>{scenario.payback_period_months} mois</span>
                      </div>
                      <div className="flex justify-between">
                        <span>VAN</span>
                        <span className={scenario.net_present_value > 0 ? 'text-green-600' : 'text-red-600'}>
                          {scenario.net_present_value.toLocaleString()}€
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <DollarSign className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Cliquez sur "Calculer ROI" pour voir les scénarios d'investissement</p>
            </div>
          )}
        </div>
      )}

      {/* Results Tab */}
      {activeTab === 'results' && (
        <div className="space-y-6">
          {!analysisResult ? (
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <Brain className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Aucune analyse disponible. Lancez une analyse depuis l'onglet "Analyses".</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Header Results */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">Résultats d'analyse</h3>
                  <span className="text-sm text-gray-600">
                    {new Date(analysisResult.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center space-x-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600 mb-1">
                      {analysisResult.business_health_score}/100
                    </div>
                    <div className="text-sm text-gray-600">Score Santé Business</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-800 mb-1">
                      {analysisResult.recommendations.length}
                    </div>
                    <div className="text-sm text-gray-600">Recommandations</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-800 mb-1">
                      {analysisResult.roi_calculations.length}
                    </div>
                    <div className="text-sm text-gray-600">Scénarios ROI</div>
                  </div>
                </div>
              </div>

              {/* AI Insights */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h4 className="font-semibold text-gray-800 mb-4 flex items-center">
                  <Brain className="w-5 h-5 mr-2 text-purple-600" />
                  Insights IA
                </h4>
                <div className="prose max-w-none text-gray-700 whitespace-pre-line">
                  {analysisResult.ai_insights}
                </div>
              </div>

              {/* Recommendations */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h4 className="font-semibold text-gray-800 mb-4">Recommandations Stratégiques</h4>
                <div className="space-y-4">
                  {analysisResult.recommendations.map((rec, index) => (
                    <div key={index} className="border-l-4 border-purple-500 pl-4 py-2">
                      <div className="flex items-center justify-between mb-2">
                        <h5 className="font-medium text-gray-800">{rec.title}</h5>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          rec.priority === 'high' ? 'bg-red-100 text-red-800' :
                          rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {rec.priority}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{rec.description}</p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>Complexité: {rec.implementation_complexity}</span>
                        <span>Délai: {rec.estimated_timeline}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Growth Opportunities */}
              {analysisResult.growth_opportunities && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h4 className="font-semibold text-gray-800 mb-4">Opportunités de Croissance</h4>
                  <div className="space-y-2">
                    {analysisResult.growth_opportunities.map((opportunity, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                        <ArrowRight className="w-5 h-5 text-green-600 mt-0.5" />
                        <span className="text-sm text-gray-700">{opportunity}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-4">
            <Clock className="w-6 h-6 text-purple-600 animate-spin" />
            <span className="text-gray-800">Analyse en cours...</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default BusinessAI;