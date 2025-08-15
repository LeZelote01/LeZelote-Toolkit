import React, { useState, useEffect } from 'react';
import { Code, Shield, AlertTriangle, CheckCircle, Upload, FileText, Zap, Bug, BarChart3, Eye, Download, Trash2 } from 'lucide-react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
const api = axios.create({ baseURL: API_BASE });

function CodeAnalysis() {
  const [activeTab, setActiveTab] = useState('scanner');
  const [loading, setLoading] = useState(false);
  const [codeAnalysisStatus, setCodeAnalysisStatus] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [codeInput, setCodeInput] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [analysisType, setAnalysisType] = useState('full');
  const [vulnerabilityPatterns, setVulnerabilityPatterns] = useState(null);

  // Charger le statut du service
  useEffect(() => {
    loadCodeAnalysisStatus();
  }, []);

  const loadCodeAnalysisStatus = async () => {
    try {
      const response = await api.get('/api/code-analysis-ai/');
      setCodeAnalysisStatus(response.data);
    } catch (error) {
      console.error('Erreur chargement statut Code Analysis AI:', error);
    }
  };

  const analyzeCode = async () => {
    if (!codeInput.trim() && !selectedFile) {
      alert('Veuillez fournir du code à analyser ou sélectionner un fichier');
      return;
    }

    setLoading(true);
    try {
      const request = {
        analysis_type: analysisType,
        code_content: codeInput || undefined,
        language: selectedLanguage,
        include_dependencies: true
      };

      const response = await api.post('/api/code-analysis-ai/analyze', request);
      setAnalysisResult(response.data);
      setActiveTab('results');
    } catch (error) {
      console.error('Erreur analyse code:', error);
      alert('Erreur lors de l\'analyse: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const runVulnerabilityScan = async () => {
    if (!codeInput.trim()) {
      alert('Veuillez fournir du code à analyser');
      return;
    }

    setLoading(true);
    try {
      const request = {
        code_content: codeInput,
        language: selectedLanguage
      };

      const response = await api.post('/api/code-analysis-ai/scan-vulnerabilities', request);
      setAnalysisResult({ scan_result: response.data });
      setActiveTab('vulnerabilities');
    } catch (error) {
      console.error('Erreur scan vulnérabilités:', error);
      alert('Erreur lors du scan: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setCodeInput(e.target.result);
      };
      reader.readAsText(file);
    }
  };

  const loadVulnerabilityPatterns = async () => {
    try {
      const response = await api.get(`/api/code-analysis-ai/vulnerability-patterns/${selectedLanguage}`);
      setVulnerabilityPatterns(response.data);
    } catch (error) {
      console.error('Erreur chargement patterns:', error);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical': return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case 'high': return <AlertTriangle className="w-4 h-4 text-orange-600" />;
      case 'medium': return <Bug className="w-4 h-4 text-yellow-600" />;
      case 'low': return <Eye className="w-4 h-4 text-blue-600" />;
      default: return <CheckCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center mb-4">
          <div className="bg-indigo-100 p-3 rounded-lg mr-4">
            <Code className="w-8 h-8 text-indigo-600" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Code Analysis AI</h1>
            <p className="text-gray-600">Analyse statique sécurisée du code source avec IA</p>
          </div>
        </div>

        {/* Status Badge */}
        {codeAnalysisStatus && (
          <div className="flex items-center space-x-4 mb-6">
            <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              ✅ Service Opérationnel
            </span>
            <span className="text-sm text-gray-600">
              Langages: {codeAnalysisStatus.supported_languages?.join(', ')}
            </span>
            <span className="text-sm text-gray-600">
              LLM: {codeAnalysisStatus.llm_configured ? '🤖 Configuré' : '📝 Mode simulation'}
            </span>
          </div>
        )}
      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-1 mb-8 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'scanner', label: 'Scanner', icon: <Code className="w-4 h-4" /> },
          { id: 'upload', label: 'Upload', icon: <Upload className="w-4 h-4" /> },
          { id: 'vulnerabilities', label: 'Vulnérabilités', icon: <Shield className="w-4 h-4" /> },
          { id: 'patterns', label: 'Patterns', icon: <Bug className="w-4 h-4" /> },
          { id: 'results', label: 'Résultats', icon: <BarChart3 className="w-4 h-4" /> }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-colors ${
              activeTab === tab.id
                ? 'bg-white text-indigo-600 shadow-sm'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Scanner Tab */}
      {activeTab === 'scanner' && (
        <div className="space-y-6">
          {/* Configuration */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Configuration d'Analyse</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Langage</label>
                <select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  {codeAnalysisStatus?.supported_languages?.map(lang => (
                    <option key={lang} value={lang}>{lang.charAt(0).toUpperCase() + lang.slice(1)}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Type d'Analyse</label>
                <select
                  value={analysisType}
                  onChange={(e) => setAnalysisType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  {codeAnalysisStatus?.analysis_types?.map(type => (
                    <option key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={analyzeCode}
                  disabled={loading}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50"
                >
                  <Zap className="w-4 h-4" />
                  <span>{loading ? 'Analyse...' : 'Analyser'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Code Input */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-800">Code Source</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCodeInput('')}
                  className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Effacer</span>
                </button>
                <button
                  onClick={runVulnerabilityScan}
                  disabled={loading}
                  className="flex items-center space-x-1 px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                >
                  <Shield className="w-4 h-4" />
                  <span>Scan Vulnérabilités</span>
                </button>
              </div>
            </div>
            <textarea
              value={codeInput}
              onChange={(e) => setCodeInput(e.target.value)}
              placeholder={`Collez votre code ${selectedLanguage} ici...`}
              className="w-full h-64 px-4 py-3 border border-gray-300 rounded-md font-mono text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <div className="mt-2 text-sm text-gray-600">
              Lignes: {codeInput.split('\n').length} | Caractères: {codeInput.length}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Actions Rapides</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <button
                onClick={() => {setAnalysisType('security'); analyzeCode();}}
                disabled={loading || !codeInput.trim()}
                className="flex items-center justify-center space-x-2 p-4 border-2 border-red-200 rounded-lg hover:border-red-400 hover:bg-red-50 transition-colors disabled:opacity-50"
              >
                <Shield className="w-5 h-5 text-red-600" />
                <span className="font-medium">Sécurité</span>
              </button>

              <button
                onClick={() => {setAnalysisType('quality'); analyzeCode();}}
                disabled={loading || !codeInput.trim()}
                className="flex items-center justify-center space-x-2 p-4 border-2 border-blue-200 rounded-lg hover:border-blue-400 hover:bg-blue-50 transition-colors disabled:opacity-50"
              >
                <CheckCircle className="w-5 h-5 text-blue-600" />
                <span className="font-medium">Qualité</span>
              </button>

              <button
                onClick={() => {setAnalysisType('performance'); analyzeCode();}}
                disabled={loading || !codeInput.trim()}
                className="flex items-center justify-center space-x-2 p-4 border-2 border-green-200 rounded-lg hover:border-green-400 hover:bg-green-50 transition-colors disabled:opacity-50"
              >
                <Zap className="w-5 h-5 text-green-600" />
                <span className="font-medium">Performance</span>
              </button>

              <button
                onClick={() => {setAnalysisType('dependency'); analyzeCode();}}
                disabled={loading || !codeInput.trim()}
                className="flex items-center justify-center space-x-2 p-4 border-2 border-purple-200 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-colors disabled:opacity-50"
              >
                <FileText className="w-5 h-5 text-purple-600" />
                <span className="font-medium">Dépendances</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Upload de Fichier</h3>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-800 mb-2">
                Glissez-déposez un fichier ou cliquez pour sélectionner
              </h4>
              <p className="text-gray-600 mb-4">
                Formats supportés: .py, .js, .jsx, .ts, .tsx, .java, .c, .cpp, .go, .rs, .php
              </p>
              <input
                type="file"
                onChange={handleFileUpload}
                accept=".py,.js,.jsx,.ts,.tsx,.java,.c,.cpp,.go,.rs,.php"
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="inline-flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 cursor-pointer"
              >
                <Upload className="w-4 h-4" />
                <span>Sélectionner un fichier</span>
              </label>
            </div>

            {selectedFile && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-800">{selectedFile.name}</h4>
                    <p className="text-sm text-gray-600">
                      Taille: {(selectedFile.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                  <button
                    onClick={analyzeCode}
                    disabled={loading}
                    className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50"
                  >
                    <Code className="w-4 h-4" />
                    <span>{loading ? 'Analyse...' : 'Analyser'}</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Sample Code Templates */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Exemples de Code</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                {
                  language: 'python',
                  title: 'Python avec vulnérabilités',
                  code: `# Exemple avec vulnérabilités
import os
import subprocess

password = "admin123"  # Hardcoded password
user_input = input("Enter command: ")

# Command injection vulnerability
result = subprocess.call(user_input, shell=True)

# Code injection vulnerability  
eval(user_input)

print("Command executed")`
                },
                {
                  language: 'javascript',
                  title: 'JavaScript avec XSS',
                  code: `// Exemple avec vulnérabilités XSS
function displayUserData(userData) {
    // XSS vulnerability
    document.getElementById('content').innerHTML = userData;
    
    // Unsafe eval
    eval('var result = ' + userData);
    
    // Weak random
    var sessionId = Math.random().toString();
    
    return sessionId;
}`
                }
              ].map((template, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium text-gray-800">{template.title}</h4>
                    <button
                      onClick={() => {
                        setCodeInput(template.code);
                        setSelectedLanguage(template.language);
                        setActiveTab('scanner');
                      }}
                      className="text-sm text-indigo-600 hover:text-indigo-800"
                    >
                      Utiliser cet exemple
                    </button>
                  </div>
                  <pre className="text-xs text-gray-600 bg-gray-50 p-3 rounded overflow-x-auto">
                    {template.code}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Vulnerabilities Tab */}
      {activeTab === 'vulnerabilities' && (
        <div className="space-y-6">
          {analysisResult?.scan_result ? (
            <div className="space-y-6">
              {/* Summary */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Résumé du Scan</h3>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-800 mb-1">
                      {analysisResult.scan_result.vulnerabilities.length}
                    </div>
                    <div className="text-sm text-gray-600">Total</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-red-600 mb-1">
                      {analysisResult.scan_result.critical_count}
                    </div>
                    <div className="text-sm text-gray-600">Critiques</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-orange-600 mb-1">
                      {analysisResult.scan_result.high_count}
                    </div>
                    <div className="text-sm text-gray-600">Élevées</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-600 mb-1">
                      {analysisResult.scan_result.medium_count}
                    </div>
                    <div className="text-sm text-gray-600">Moyennes</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600 mb-1">
                      {analysisResult.scan_result.low_count}
                    </div>
                    <div className="text-sm text-gray-600">Faibles</div>
                  </div>
                </div>
                <div className="mt-4 text-center">
                  <div className="text-lg font-semibold text-gray-800">
                    Score Sécurité: {analysisResult.scan_result.security_score}/10
                  </div>
                </div>
              </div>

              {/* Vulnerabilities List */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Vulnérabilités Détectées</h3>
                <div className="space-y-4">
                  {analysisResult.scan_result.vulnerabilities.map((vuln, index) => (
                    <div key={index} className="border-l-4 border-red-500 pl-4 py-3 bg-red-50">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getSeverityIcon(vuln.severity)}
                          <h4 className="font-medium text-gray-800">{vuln.vulnerability_type}</h4>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(vuln.severity)}`}>
                            {vuln.severity}
                          </span>
                          {vuln.cwe_id && (
                            <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-xs">
                              {vuln.cwe_id}
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{vuln.description}</p>
                      {vuln.line_number && (
                        <p className="text-xs text-gray-600 mb-2">
                          Ligne {vuln.line_number}: <code className="bg-gray-200 px-1 rounded">{vuln.code_snippet}</code>
                        </p>
                      )}
                      <div className="text-sm">
                        <p className="text-gray-700 mb-1"><strong>Impact:</strong> {vuln.impact}</p>
                        <p className="text-gray-700"><strong>Remédiation:</strong> {vuln.remediation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <Shield className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Aucun scan de vulnérabilités disponible. Lancez un scan depuis l'onglet Scanner.</p>
            </div>
          )}
        </div>
      )}

      {/* Patterns Tab */}
      {activeTab === 'patterns' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-800">Patterns de Vulnérabilités</h3>
            <button
              onClick={loadVulnerabilityPatterns}
              className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
            >
              <Bug className="w-4 h-4" />
              <span>Charger patterns {selectedLanguage}</span>
            </button>
          </div>

          {vulnerabilityPatterns ? (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h4 className="font-semibold text-gray-800 mb-4">
                Patterns pour {vulnerabilityPatterns.language} ({vulnerabilityPatterns.total_patterns} patterns)
              </h4>
              <div className="space-y-4">
                {vulnerabilityPatterns.patterns.map((pattern, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h5 className="font-medium text-gray-800">{pattern.type}</h5>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(pattern.severity)}`}>
                          {pattern.severity}
                        </span>
                        {pattern.cwe && (
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                            {pattern.cwe}
                          </span>
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{pattern.description}</p>
                    <div className="bg-gray-50 p-3 rounded mb-2">
                      <code className="text-xs text-gray-800">{pattern.pattern}</code>
                    </div>
                    <p className="text-sm text-green-700">
                      <strong>Remédiation:</strong> {pattern.remediation}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <Bug className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Cliquez sur "Charger patterns" pour voir les patterns de vulnérabilités.</p>
            </div>
          )}
        </div>
      )}

      {/* Results Tab */}
      {activeTab === 'results' && (
        <div className="space-y-6">
          {!analysisResult ? (
            <div className="bg-white rounded-lg shadow-md p-6 text-center">
              <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Aucune analyse disponible. Lancez une analyse depuis l'onglet Scanner.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Analysis Summary */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">Résultats d'Analyse</h3>
                  <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-600">
                      Temps: {analysisResult.execution_time_ms}ms
                    </span>
                    <span className="text-sm text-gray-600">
                      Recommandations: {analysisResult.recommendations_count}
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-red-600 mb-1">
                      {analysisResult.analysis.overall_security_score}/10
                    </div>
                    <div className="text-sm text-gray-600">Score Sécurité</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600 mb-1">
                      {analysisResult.analysis.overall_quality_score}/10
                    </div>
                    <div className="text-sm text-gray-600">Score Qualité</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-gray-800 mb-1">
                      {analysisResult.analysis.vulnerability_findings?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Vulnérabilités</div>
                  </div>
                </div>
              </div>

              {/* Code Metrics */}
              {analysisResult.analysis.code_metrics && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h4 className="font-semibold text-gray-800 mb-4">Métriques du Code</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-xl font-bold text-gray-800">
                        {analysisResult.analysis.code_metrics.lines_of_code}
                      </div>
                      <div className="text-sm text-gray-600">Lignes de code</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl font-bold text-gray-800">
                        {analysisResult.analysis.code_metrics.cyclomatic_complexity}
                      </div>
                      <div className="text-sm text-gray-600">Complexité</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl font-bold text-gray-800">
                        {analysisResult.analysis.code_metrics.function_count}
                      </div>
                      <div className="text-sm text-gray-600">Fonctions</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl font-bold text-gray-800">
                        {analysisResult.analysis.code_metrics.duplication_percentage?.toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Duplication</div>
                    </div>
                  </div>
                </div>
              )}

              {/* AI Recommendations */}
              {analysisResult.analysis.ai_recommendations && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h4 className="font-semibold text-gray-800 mb-4">Recommandations IA</h4>
                  <div className="space-y-3">
                    {analysisResult.analysis.ai_recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 bg-indigo-50 rounded-lg">
                        <CheckCircle className="w-5 h-5 text-indigo-600 mt-0.5" />
                        <span className="text-sm text-gray-700">{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Security Recommendations */}
              {analysisResult.analysis.security_recommendations && (
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h4 className="font-semibold text-gray-800 mb-4">Recommandations Sécurité</h4>
                  <div className="space-y-3">
                    {analysisResult.analysis.security_recommendations.map((rec, index) => (
                      <div key={index} className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                        <Shield className="w-5 h-5 text-red-600 mt-0.5" />
                        <span className="text-sm text-gray-700">{rec}</span>
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
            <Code className="w-6 h-6 text-indigo-600 animate-pulse" />
            <span className="text-gray-800">Analyse du code en cours...</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default CodeAnalysis;