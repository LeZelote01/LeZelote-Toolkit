import React, { useState, useEffect } from 'react';
import { Brain, ShieldCheck, AlertTriangle, Clock, TrendingUp, FileText, Play, ChevronRight } from 'lucide-react';
import api from '../services/api.js';

const AISecurity = () => {
  const [status, setStatus] = useState(null);
  const [evaluations, setEvaluations] = useState([]);
  const [newEvaluation, setNewEvaluation] = useState({
    model_type: 'llm',
    model_name: '',
    model_endpoint: '',
    test_suite: ['prompt_injection', 'adversarial_attack', 'bias_evaluation']
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStatus();
    fetchEvaluations();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await api.get('/api/ai-security/');
      setStatus(response.data);
    } catch (error) {
      console.error('Erreur récupération status:', error);
    }
  };

  const fetchEvaluations = async () => {
    try {
      const response = await api.get('/api/ai-security/evaluations');
      setEvaluations(response.data.evaluations || []);
    } catch (error) {
      console.error('Erreur récupération évaluations:', error);
    }
  };

  const startEvaluation = async () => {
    if (!newEvaluation.model_name) {
      alert('Nom du modèle requis');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/ai-security/evaluate', newEvaluation);
      setNewEvaluation({
        model_type: 'llm',
        model_name: '',
        model_endpoint: '',
        test_suite: ['prompt_injection', 'adversarial_attack', 'bias_evaluation']
      });
      fetchEvaluations();
    } catch (error) {
      console.error('Erreur lancement évaluation:', error);
      alert('Erreur lors du lancement de l\'évaluation');
    }
    setLoading(false);
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'text-red-600 bg-red-50',
      high: 'text-orange-600 bg-orange-50',
      medium: 'text-yellow-600 bg-yellow-50',
      low: 'text-blue-600 bg-blue-50',
      info: 'text-gray-600 bg-gray-50'
    };
    return colors[severity] || colors.info;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <Brain className="mr-3 h-8 w-8 text-purple-600" />
          AI Security
        </h1>
        <p className="text-gray-600">
          Évaluation de sécurité et robustesse des modèles d'intelligence artificielle
        </p>
      </div>

      {/* Status */}
      {status && (
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Status du Service</h2>
              <div className="flex items-center space-x-6">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  status.status === 'operational' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  <ShieldCheck className="w-4 h-4 mr-1" />
                  {status.status === 'operational' ? 'Opérationnel' : 'Indisponible'}
                </span>
                <span className="text-sm text-gray-600">
                  Évaluations actives: {status.active_evaluations}
                </span>
                <span className="text-sm text-gray-600">
                  Évaluations terminées: {status.completed_evaluations}
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-600 mb-1">Frameworks supportés</div>
              <div className="text-xs space-x-2">
                {status.security_frameworks?.map(framework => (
                  <span key={framework} className="bg-white px-2 py-1 rounded text-gray-700">
                    {framework}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Nouvelle Évaluation */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Play className="w-5 h-5 mr-2 text-purple-600" />
            Nouvelle Évaluation IA
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type de Modèle
              </label>
              <select
                value={newEvaluation.model_type}
                onChange={(e) => setNewEvaluation(prev => ({...prev, model_type: e.target.value}))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="llm">Large Language Model (LLM)</option>
                <option value="image_classification">Classification d'images</option>
                <option value="nlp">Natural Language Processing</option>
                <option value="computer_vision">Computer Vision</option>
                <option value="recommendation">Système de recommandation</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nom du Modèle *
              </label>
              <input
                type="text"
                value={newEvaluation.model_name}
                onChange={(e) => setNewEvaluation(prev => ({...prev, model_name: e.target.value}))}
                placeholder="ex: GPT-4, BERT, ResNet-50..."
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Endpoint API (optionnel)
              </label>
              <input
                type="url"
                value={newEvaluation.model_endpoint}
                onChange={(e) => setNewEvaluation(prev => ({...prev, model_endpoint: e.target.value}))}
                placeholder="https://api.example.com/model"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tests à Effectuer
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { value: 'prompt_injection', label: 'Prompt Injection' },
                  { value: 'adversarial_attack', label: 'Attaques Adversariales' },
                  { value: 'bias_evaluation', label: 'Évaluation des Biais' },
                  { value: 'fairness_testing', label: 'Test d\'Équité' },
                  { value: 'robustness_testing', label: 'Test de Robustesse' },
                  { value: 'privacy_leakage', label: 'Fuite de Données' }
                ].map(test => (
                  <label key={test.value} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={newEvaluation.test_suite.includes(test.value)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setNewEvaluation(prev => ({
                            ...prev,
                            test_suite: [...prev.test_suite, test.value]
                          }));
                        } else {
                          setNewEvaluation(prev => ({
                            ...prev,
                            test_suite: prev.test_suite.filter(t => t !== test.value)
                          }));
                        }
                      }}
                      className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">{test.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <button
              onClick={startEvaluation}
              disabled={loading || !newEvaluation.model_name}
              className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Clock className="w-4 h-4 mr-2 animate-spin" />
                  Démarrage...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Lancer l'Évaluation
                </>
              )}
            </button>
          </div>
        </div>

        {/* Évaluations Récentes */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-gray-600" />
            Évaluations Récentes
          </h3>
          
          {evaluations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Aucune évaluation pour le moment</p>
              <p className="text-sm">Lancez votre première évaluation AI</p>
            </div>
          ) : (
            <div className="space-y-4">
              {evaluations.slice(0, 5).map((evaluation) => (
                <div key={evaluation.evaluation_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium text-gray-900">
                      {evaluation.model_name || 'Modèle anonyme'}
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      evaluation.status === 'completed' ? 'bg-green-100 text-green-800' :
                      evaluation.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      evaluation.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {evaluation.status === 'completed' ? 'Terminé' :
                       evaluation.status === 'running' ? 'En cours' :
                       evaluation.status === 'failed' ? 'Échoué' : evaluation.status}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600 mb-2">
                    Type: {evaluation.model_type} • 
                    Durée: {Math.round(evaluation.duration)}s
                  </div>
                  
                  {evaluation.security_score && (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="text-sm">
                          Score: <span className="font-medium">{evaluation.security_score}/100</span>
                        </div>
                        {evaluation.vulnerabilities_found > 0 && (
                          <div className="text-sm text-orange-600">
                            {evaluation.vulnerabilities_found} vulnérabilités
                          </div>
                        )}
                      </div>
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Métriques Global */}
      {status && status.average_scores && (
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
            Métriques Globales
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {status.average_scores.security}/10
              </div>
              <div className="text-sm text-gray-600">Score Sécurité Moyen</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {status.average_scores.robustness}/10
              </div>
              <div className="text-sm text-gray-600">Score Robustesse Moyen</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {status.average_scores.fairness}/10
              </div>
              <div className="text-sm text-gray-600">Score Équité Moyen</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AISecurity;