import React, { useState, useEffect } from 'react';
import { Globe, Shield, Code, Lock, AlertTriangle, Clock, CheckCircle, XCircle, ChevronRight } from 'lucide-react';
import api from '../services/api.js';

const APISecurity = () => {
  const [status, setStatus] = useState(null);
  const [tests, setTests] = useState([]);
  const [newTest, setNewTest] = useState({
    base_url: '',
    api_type: 'rest',
    test_suite: ['owasp_api_top10', 'authentication', 'authorization'],
    endpoints: [],
    test_options: {
      max_depth: 3,
      include_documentation_search: true,
      rate_limit_testing: true
    }
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStatus();
    fetchTests();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await api.get('/api/api-security/');
      setStatus(response.data);
    } catch (error) {
      console.error('Erreur récupération status:', error);
    }
  };

  const fetchTests = async () => {
    try {
      const response = await api.get('/api/api-security/tests');
      setTests(response.data.tests || []);
    } catch (error) {
      console.error('Erreur récupération tests:', error);
    }
  };

  const startTest = async () => {
    if (!newTest.base_url) {
      alert('URL de base de l\'API requise');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/api-security/test', newTest);
      setNewTest({
        base_url: '',
        api_type: 'rest',
        test_suite: ['owasp_api_top10', 'authentication', 'authorization'],
        endpoints: [],
        test_options: {
          max_depth: 3,
          include_documentation_search: true,
          rate_limit_testing: true
        }
      });
      fetchTests();
    } catch (error) {
      console.error('Erreur lancement test:', error);
      alert('Erreur lors du lancement du test');
    }
    setLoading(false);
  };

  const getAPITypeLabel = (type) => {
    const labels = {
      rest: 'REST API',
      graphql: 'GraphQL',
      soap: 'SOAP',
      grpc: 'gRPC',
      webhook: 'Webhook'
    };
    return labels[type] || type;
  };

  const getTestStatusColor = (status) => {
    const colors = {
      completed: 'bg-green-100 text-green-800',
      running: 'bg-blue-100 text-blue-800',
      failed: 'bg-red-100 text-red-800',
      starting: 'bg-yellow-100 text-yellow-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getOWASPCompliance = (complianceStats) => {
    if (!complianceStats || Object.keys(complianceStats).length === 0) return null;
    
    const total = Object.keys(complianceStats).length;
    const compliant = Object.values(complianceStats).filter(c => c.compliant === c.total).length;
    return Math.round((compliant / total) * 100);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <Code className="mr-3 h-8 w-8 text-green-600" />
          API Security
        </h1>
        <p className="text-gray-600">
          Test de sécurité des APIs selon les standards OWASP API Security Top 10
        </p>
      </div>

      {/* Status */}
      {status && (
        <div className="bg-gradient-to-r from-green-50 to-teal-50 rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Status du Service</h2>
              <div className="flex items-center space-x-6">
                <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                  status.status === 'operational' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  <Shield className="w-4 h-4 mr-1" />
                  {status.status === 'operational' ? 'Opérationnel' : 'Indisponible'}
                </span>
                <span className="text-sm text-gray-600">
                  Tests actifs: {status.active_tests}
                </span>
                <span className="text-sm text-gray-600">
                  Tests terminés: {status.completed_tests}
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-600 mb-1">Conformité OWASP</div>
              {status.owasp_compliance_stats && (
                <div className="text-lg font-bold text-green-600">
                  {getOWASPCompliance(status.owasp_compliance_stats) || 'N/A'}%
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Nouveau Test */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Lock className="w-5 h-5 mr-2 text-green-600" />
            Nouveau Test API
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                URL de Base de l'API *
              </label>
              <input
                type="url"
                value={newTest.base_url}
                onChange={(e) => setNewTest(prev => ({...prev, base_url: e.target.value}))}
                placeholder="https://api.example.com/v1"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type d'API
              </label>
              <select
                value={newTest.api_type}
                onChange={(e) => setNewTest(prev => ({...prev, api_type: e.target.value}))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="rest">REST API</option>
                <option value="graphql">GraphQL</option>
                <option value="soap">SOAP</option>
                <option value="grpc">gRPC</option>
                <option value="webhook">Webhook</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tests à Effectuer
              </label>
              <div className="grid grid-cols-1 gap-2">
                {[
                  { value: 'owasp_api_top10', label: 'OWASP API Top 10' },
                  { value: 'authentication', label: 'Tests d\'Authentification' },
                  { value: 'authorization', label: 'Tests d\'Autorisation' },
                  { value: 'injection', label: 'Tests d\'Injection' },
                  { value: 'rate_limiting', label: 'Tests de Limitation' },
                  { value: 'data_validation', label: 'Validation des Données' },
                  { value: 'cors', label: 'Configuration CORS' },
                  { value: 'ssl_tls', label: 'Tests SSL/TLS' }
                ].map(test => (
                  <label key={test.value} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={newTest.test_suite.includes(test.value)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setNewTest(prev => ({
                            ...prev,
                            test_suite: [...prev.test_suite, test.value]
                          }));
                        } else {
                          setNewTest(prev => ({
                            ...prev,
                            test_suite: prev.test_suite.filter(t => t !== test.value)
                          }));
                        }
                      }}
                      className="rounded border-gray-300 text-green-600 focus:ring-green-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">{test.label}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">
                Options de Test
              </label>
              
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newTest.test_options.include_documentation_search}
                    onChange={(e) => setNewTest(prev => ({
                      ...prev,
                      test_options: {...prev.test_options, include_documentation_search: e.target.checked}
                    }))}
                    className="rounded border-gray-300 text-green-600 focus:ring-green-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Recherche de documentation</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newTest.test_options.rate_limit_testing}
                    onChange={(e) => setNewTest(prev => ({
                      ...prev,
                      test_options: {...prev.test_options, rate_limit_testing: e.target.checked}
                    }))}
                    className="rounded border-gray-300 text-green-600 focus:ring-green-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Tests de limitation de débit</span>
                </label>
              </div>

              <div>
                <label className="block text-sm text-gray-700 mb-1">
                  Profondeur maximale de découverte
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={newTest.test_options.max_depth}
                  onChange={(e) => setNewTest(prev => ({
                    ...prev,
                    test_options: {...prev.test_options, max_depth: parseInt(e.target.value)}
                  }))}
                  className="w-20 p-2 border border-gray-300 rounded focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>

            <button
              onClick={startTest}
              disabled={loading || !newTest.base_url}
              className="w-full bg-green-600 text-white py-3 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Clock className="w-4 h-4 mr-2 animate-spin" />
                  Démarrage...
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4 mr-2" />
                  Lancer Test API
                </>
              )}
            </button>
          </div>
        </div>

        {/* Tests Récents */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Globe className="w-5 h-5 mr-2 text-gray-600" />
            Tests Récents
          </h3>
          
          {tests.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Code className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Aucun test pour le moment</p>
              <p className="text-sm">Lancez votre premier test API</p>
            </div>
          ) : (
            <div className="space-y-4">
              {tests.slice(0, 5).map((test) => (
                <div key={test.test_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium text-gray-900 truncate">
                      {new URL(test.base_url).hostname}
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTestStatusColor(test.status)}`}>
                      {test.status === 'completed' ? 'Terminé' :
                       test.status === 'running' ? 'En cours' :
                       test.status === 'failed' ? 'Échoué' : test.status}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600 mb-2">
                    {getAPITypeLabel(test.api_type)} • 
                    Durée: {Math.round(test.duration || 0)}s
                  </div>
                  
                  {test.endpoints_tested !== undefined && (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="text-sm">
                          <CheckCircle className="w-4 h-4 inline mr-1 text-green-500" />
                          {test.endpoints_tested} endpoints
                        </div>
                        {test.vulnerabilities_found > 0 && (
                          <div className="text-sm text-orange-600">
                            <AlertTriangle className="w-4 h-4 inline mr-1" />
                            {test.vulnerabilities_found} vulnérabilités
                          </div>
                        )}
                        {test.security_score && (
                          <div className="text-sm text-blue-600">
                            Score: {test.security_score}/100
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

      {/* OWASP Categories */}
      {status && status.owasp_categories_supported && (
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-orange-600" />
            OWASP API Security Top 10 (2023)
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {status.owasp_categories_supported.map((category, index) => (
              <div key={category} className="flex items-center p-3 bg-gray-50 rounded-lg">
                <div className="w-8 h-8 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center text-sm font-bold mr-3">
                  {index + 1}
                </div>
                <div className="text-sm font-medium text-gray-700">
                  {category}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Métriques */}
      {status && status.average_scores && (
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Métriques Globales</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {status.average_scores.security}/100
              </div>
              <div className="text-sm text-gray-600">Score Sécurité Moyen</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {status.average_scores.authentication}/100
              </div>
              <div className="text-sm text-gray-600">Score Authentification Moyen</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default APISecurity;