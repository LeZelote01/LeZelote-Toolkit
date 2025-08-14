import React, { useState, useEffect } from 'react';
import { Smartphone, Upload, Shield, AlertTriangle, CheckCircle, Download, Trash2, RefreshCw } from 'lucide-react';

const MobileSecurity = () => {
  const [analyses, setAnalyses] = useState([]);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // État pour l'upload
  const [uploadData, setUploadData] = useState({
    platform: 'android',
    file: null,
    fileName: ''
  });

  // Filtres
  const [filters, setFilters] = useState({
    platform: '',
    status: '',
    severity: ''
  });

  useEffect(() => {
    loadAnalyses();
    loadStats();
  }, [filters]);

  const loadAnalyses = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.platform) params.append('platform', filters.platform);
      if (filters.status) params.append('status', filters.status);
      
      const response = await fetch(`/api/mobile-security/analyses?${params}`);
      const data = await response.json();
      setAnalyses(data);
    } catch (error) {
      console.error('Erreur chargement analyses:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/mobile-security/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadData({
        ...uploadData,
        file: file,
        fileName: file.name
      });
    }
  };

  const handleUpload = async () => {
    if (!uploadData.file) {
      alert('Veuillez sélectionner un fichier');
      return;
    }

    setIsUploading(true);
    
    try {
      // Convertir le fichier en base64
      const base64 = await fileToBase64(uploadData.file);
      
      const request = {
        platform: uploadData.platform,
        source_type: 'file',
        source: base64,
        analysis_options: {
          static_analysis: true,
          dynamic_analysis: false,
          frameworks: ['OWASP_MASVS', 'NIST_Mobile']
        }
      };

      const response = await fetch('/api/mobile-security/analyze/app', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request)
      });

      const result = await response.json();
      
      if (response.ok) {
        alert(`Analyse lancée avec succès! ID: ${result.analysis_id}`);
        setUploadData({ platform: 'android', file: null, fileName: '' });
        loadAnalyses();
      } else {
        throw new Error(result.detail || 'Erreur lors du lancement');
      }
    } catch (error) {
      console.error('Erreur upload:', error);
      alert('Erreur lors du lancement de l\'analyse');
    } finally {
      setIsUploading(false);
    }
  };

  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => {
        // Retirer le préfixe data:type;base64,
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = error => reject(error);
    });
  };

  const viewAnalysisDetails = async (analysisId) => {
    try {
      const response = await fetch(`/api/mobile-security/analysis/${analysisId}`);
      const data = await response.json();
      setCurrentAnalysis(data);
    } catch (error) {
      console.error('Erreur chargement détails:', error);
    }
  };

  const downloadReport = (analysisId, format = 'json') => {
    const url = `/api/mobile-security/analysis/${analysisId}/report?format=${format}`;
    window.open(url, '_blank');
  };

  const deleteAnalysis = async (analysisId) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette analyse ?')) return;
    
    try {
      const response = await fetch(`/api/mobile-security/analysis/${analysisId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        loadAnalyses();
        if (currentAnalysis && currentAnalysis.id === analysisId) {
          setCurrentAnalysis(null);
        }
      }
    } catch (error) {
      console.error('Erreur suppression:', error);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'text-red-600 bg-red-100',
      high: 'text-orange-600 bg-orange-100',
      medium: 'text-yellow-600 bg-yellow-100',
      low: 'text-blue-600 bg-blue-100'
    };
    return colors[severity] || 'text-gray-600 bg-gray-100';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'running':
        return <RefreshCw className="h-5 w-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      default:
        return <RefreshCw className="h-5 w-5 text-gray-400" />;
    }
  };

  const getRiskLevel = (score) => {
    if (score >= 80) return { text: 'Faible', color: 'text-green-600' };
    if (score >= 60) return { text: 'Moyen', color: 'text-yellow-600' };
    if (score >= 40) return { text: 'Élevé', color: 'text-orange-600' };
    return { text: 'Critique', color: 'text-red-600' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-2">Chargement...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Smartphone className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Mobile Security</h1>
            <p className="text-gray-600">Analyse sécurité applications mobiles (Android/iOS)</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={loadAnalyses}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            <RefreshCw className="h-4 w-4 mr-2 inline" />
            Actualiser
          </button>
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Smartphone className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Analyses</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_analyses}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Score Moyen</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.compliance_scores?.avg_owasp_masvs || 0}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-orange-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Vulnérabilités Critiques</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.vulnerabilities?.by_severity?.critical || 0}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Android / iOS</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.platforms?.android?.count || 0} / {stats.platforms?.ios?.count || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Section */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              <Upload className="h-5 w-5 inline mr-2" />
              Nouvelle Analyse
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Plateforme
                </label>
                <select
                  value={uploadData.platform}
                  onChange={(e) => setUploadData({...uploadData, platform: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="android">Android (.apk)</option>
                  <option value="ios">iOS (.ipa)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Fichier Application
                </label>
                <input
                  type="file"
                  accept={uploadData.platform === 'android' ? '.apk' : '.ipa'}
                  onChange={handleFileSelect}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                />
                {uploadData.fileName && (
                  <p className="text-sm text-gray-500 mt-1">Fichier: {uploadData.fileName}</p>
                )}
              </div>

              <button
                onClick={handleUpload}
                disabled={isUploading || !uploadData.file}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {isUploading ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin inline mr-2" />
                    Analyse en cours...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4 inline mr-2" />
                    Lancer l'Analyse
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Filtres */}
          <div className="bg-white shadow rounded-lg p-6 mt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Filtres</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Plateforme
                </label>
                <select
                  value={filters.platform}
                  onChange={(e) => setFilters({...filters, platform: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="">Toutes</option>
                  <option value="android">Android</option>
                  <option value="ios">iOS</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Statut
                </label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({...filters, status: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                >
                  <option value="">Tous</option>
                  <option value="completed">Terminé</option>
                  <option value="running">En cours</option>
                  <option value="failed">Échec</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Analyses List */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                Analyses ({analyses.length})
              </h2>
            </div>
            
            <div className="divide-y divide-gray-200">
              {analyses.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  Aucune analyse trouvée
                </div>
              ) : (
                analyses.map((analysis) => (
                  <div key={analysis.id} className="p-6 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(analysis.status)}
                          <div>
                            <h3 className="text-sm font-medium text-gray-900">
                              {analysis.app_name}
                            </h3>
                            <p className="text-sm text-gray-500">
                              {analysis.platform} • {new Date(analysis.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>
                        
                        {analysis.status === 'completed' && analysis.summary && (
                          <div className="mt-3 flex items-center space-x-4">
                            <span className="text-sm text-gray-600">
                              Score: <span className="font-medium">
                                {analysis.compliance_scores?.Overall || 0}/100
                              </span>
                            </span>
                            <span className="text-sm text-gray-600">
                              Vulnérabilités: <span className="font-medium">
                                {analysis.vulnerabilities_count || 0}
                              </span>
                            </span>
                            <span className={`text-sm font-medium ${getRiskLevel(analysis.compliance_scores?.Overall || 0).color}`}>
                              {getRiskLevel(analysis.compliance_scores?.Overall || 0).text}
                            </span>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {analysis.status === 'completed' && (
                          <>
                            <button
                              onClick={() => viewAnalysisDetails(analysis.id)}
                              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                            >
                              Détails
                            </button>
                            <button
                              onClick={() => downloadReport(analysis.id, 'json')}
                              className="text-green-600 hover:text-green-800 text-sm"
                            >
                              <Download className="h-4 w-4" />
                            </button>
                          </>
                        )}
                        <button
                          onClick={() => deleteAnalysis(analysis.id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Details Modal */}
      {currentAnalysis && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full mx-4 max-h-96 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">
                Détails de l'Analyse - {currentAnalysis.app_name}
              </h2>
              <button
                onClick={() => setCurrentAnalysis(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-80">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Informations</h3>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium">Plateforme:</span> {currentAnalysis.platform}</div>
                    <div><span className="font-medium">Package:</span> {currentAnalysis.package_name}</div>
                    <div><span className="font-medium">Analysé le:</span> {new Date(currentAnalysis.created_at).toLocaleString()}</div>
                  </div>
                </div>
                
                <div>
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Scores de Conformité</h3>
                  <div className="space-y-2 text-sm">
                    {Object.entries(currentAnalysis.compliance_scores || {}).map(([framework, score]) => (
                      <div key={framework}>
                        <span className="font-medium">{framework}:</span> {score}/100
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              {currentAnalysis.vulnerabilities && (
                <div className="mt-6">
                  <h3 className="text-sm font-medium text-gray-900 mb-3">
                    Vulnérabilités ({currentAnalysis.vulnerabilities.length})
                  </h3>
                  <div className="space-y-3 max-h-40 overflow-y-auto">
                    {currentAnalysis.vulnerabilities.slice(0, 10).map((vuln, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(vuln.severity)}`}>
                              {vuln.severity.toUpperCase()}
                            </span>
                            <span className="text-sm font-medium">{vuln.title}</span>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{vuln.description}</p>
                        {vuln.file_path && (
                          <p className="text-xs text-gray-500 mt-1">Fichier: {vuln.file_path}</p>
                        )}
                      </div>
                    ))}
                    {currentAnalysis.vulnerabilities.length > 10 && (
                      <p className="text-sm text-gray-500 text-center">
                        ... et {currentAnalysis.vulnerabilities.length - 10} autres vulnérabilités
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
            
            <div className="px-6 py-4 border-t border-gray-200 flex justify-end space-x-3">
              <button
                onClick={() => downloadReport(currentAnalysis.id, 'pdf')}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm"
              >
                <Download className="h-4 w-4 inline mr-2" />
                Télécharger PDF
              </button>
              <button
                onClick={() => setCurrentAnalysis(null)}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 text-sm"
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MobileSecurity;