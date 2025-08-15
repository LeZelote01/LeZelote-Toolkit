import React, { useState, useEffect } from 'react';
import { Shield, FileText, AlertTriangle, CheckCircle, XCircle, Settings, Search, Filter, Download, Upload, GitBranch, Cloud } from 'lucide-react';

const IaCSecurityPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [scans, setScans] = useState([]);
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchIaCSecurityData();
  }, []);

  const fetchIaCSecurityData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/iac-security/`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données IaC Security:', error);
    }
  };

  const handleScanSubmit = async (scanData) => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/iac-security/scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(scanData),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Scan IaC lancé avec succès! ID: ${result.scan_id}`);
        fetchScans();
      } else {
        throw new Error('Erreur lors du lancement du scan');
      }
    } catch (error) {
      console.error('Erreur scan IaC:', error);
      alert('Erreur lors du lancement du scan');
    } finally {
      setLoading(false);
    }
  };

  const fetchScans = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/iac-security/scans`);
      if (response.ok) {
        const data = await response.json();
        setScans(data.scans || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des scans:', error);
    }
  };

  const fetchFindings = async (scanId = null) => {
    try {
      let url = `${process.env.REACT_APP_BACKEND_URL}/api/iac-security/findings`;
      if (scanId) url += `?scan_id=${scanId}`;
      
      const response = await fetch(url);
      if (response.ok) {
        const data = await response.json();
        setFindings(data.findings || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des findings:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'scans') {
      fetchScans();
    } else if (activeTab === 'findings') {
      fetchFindings();
    }
  }, [activeTab]);

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'text-red-600 bg-red-100',
      high: 'text-orange-600 bg-orange-100',
      medium: 'text-yellow-600 bg-yellow-100',
      low: 'text-blue-600 bg-blue-100',
      info: 'text-gray-600 bg-gray-100'
    };
    return colors[severity] || colors.info;
  };

  const getSeverityBadge = (severity) => (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(severity)}`}>
      {severity.toUpperCase()}
    </span>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Cloud className="h-8 w-8 text-blue-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">IaC Security</h1>
                <p className="text-gray-600">Infrastructure as Code Security Analysis</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-600">{stats.total_files_scanned || 0}</div>
                <div className="text-sm text-gray-500">Fichiers analysés</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-red-600">{stats.total_findings || 0}</div>
                <div className="text-sm text-gray-500">Problèmes détectés</div>
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
              { id: 'scan', name: 'Nouveau Scan', icon: Search },
              { id: 'scans', name: 'Historique Scans', icon: FileText },
              { id: 'findings', name: 'Problèmes', icon: AlertTriangle },
              { id: 'rules', name: 'Règles', icon: Settings }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
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
                    <p className="text-sm text-gray-600">Scans Actifs</p>
                    <p className="text-2xl font-bold text-blue-600">{stats.active_scans || 0}</p>
                  </div>
                  <Search className="h-8 w-8 text-blue-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Scans Terminés</p>
                    <p className="text-2xl font-bold text-green-600">{stats.completed_scans || 0}</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Problèmes Critiques</p>
                    <p className="text-2xl font-bold text-red-600">{stats.severity_breakdown?.critical || 0}</p>
                  </div>
                  <XCircle className="h-8 w-8 text-red-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Taux de Succès</p>
                    <p className="text-2xl font-bold text-blue-600">{stats.scan_performance?.success_rate || '0%'}</p>
                  </div>
                  <Shield className="h-8 w-8 text-blue-600" />
                </div>
              </div>
            </div>

            {/* Supported Frameworks */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Frameworks Supportés</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {(stats.supported_iac_types || []).map((type, index) => (
                  <div key={index} className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                    <GitBranch className="h-5 w-5 text-blue-600" />
                    <span className="font-medium text-gray-900 capitalize">{type}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Security Frameworks */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Standards de Sécurité</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {(stats.security_frameworks || []).map((framework, index) => (
                  <div key={index} className="flex items-center space-x-2 p-3 bg-blue-50 rounded-lg">
                    <Shield className="h-5 w-5 text-blue-600" />
                    <span className="font-medium text-gray-900">{framework}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'scan' && (
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Nouveau Scan IaC</h3>
            <IaCSecurityScanForm onSubmit={handleScanSubmit} loading={loading} />
          </div>
        )}

        {activeTab === 'scans' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Historique des Scans</h3>
            </div>
            <ScansHistory scans={scans} onViewDetails={fetchFindings} />
          </div>
        )}

        {activeTab === 'findings' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Problèmes de Sécurité IaC</h3>
            </div>
            <FindingsList findings={findings} />
          </div>
        )}

        {activeTab === 'rules' && (
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Règles de Sécurité IaC</h3>
            <RulesList />
          </div>
        )}
      </div>
    </div>
  );
};

// Composant formulaire de scan
const IaCSecurityScanForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    source_type: 'text',
    source_content: '',
    iac_type: 'terraform',
    scan_options: {}
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.source_content.trim()) {
      alert('Veuillez fournir le contenu à analyser');
      return;
    }
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Type de Source
          </label>
          <select
            value={formData.source_type}
            onChange={(e) => setFormData({...formData, source_type: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="text">Texte/Code</option>
            <option value="file_upload">Upload Fichier</option>
            <option value="git_repo">Dépôt Git</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Type IaC
          </label>
          <select
            value={formData.iac_type}
            onChange={(e) => setFormData({...formData, iac_type: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="terraform">Terraform</option>
            <option value="cloudformation">CloudFormation</option>
            <option value="ansible">Ansible</option>
            <option value="kubernetes">Kubernetes</option>
            <option value="helm">Helm</option>
            <option value="docker-compose">Docker Compose</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Contenu à Analyser
        </label>
        <textarea
          value={formData.source_content}
          onChange={(e) => setFormData({...formData, source_content: e.target.value})}
          placeholder={formData.source_type === 'git_repo' ? 'URL du dépôt Git...' : 'Collez votre code IaC ici...'}
          rows={10}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Analyse en cours...</span>
            </>
          ) : (
            <>
              <Search className="h-4 w-4" />
              <span>Lancer le Scan</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};

// Composant historique des scans
const ScansHistory = ({ scans, onViewDetails }) => {
  if (!scans.length) {
    return (
      <div className="p-8 text-center text-gray-500">
        <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <p>Aucun scan disponible</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type IaC
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Fichiers
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Problèmes
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Score
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {scans.map((scan) => (
            <tr key={scan.scan_id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="flex items-center">
                  <GitBranch className="h-5 w-5 text-blue-600 mr-2" />
                  <span className="font-medium text-gray-900 capitalize">{scan.iac_type}</span>
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  scan.status === 'completed' ? 'text-green-600 bg-green-100' : 'text-yellow-600 bg-yellow-100'
                }`}>
                  {scan.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(scan.created_at).toLocaleDateString()}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {scan.files_analyzed}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {scan.findings_count}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <span className={`font-medium ${
                  scan.compliance_score >= 80 ? 'text-green-600' : 
                  scan.compliance_score >= 60 ? 'text-yellow-600' : 'text-red-600'
                }`}>
                  {scan.compliance_score}%
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Composant liste des findings
const FindingsList = ({ findings }) => {
  if (!findings.length) {
    return (
      <div className="p-8 text-center text-gray-500">
        <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-400" />
        <p>Aucun problème détecté</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200">
      {findings.map((finding, index) => (
        <div key={index} className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <h4 className="text-lg font-medium text-gray-900">{finding.title}</h4>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  finding.severity === 'critical' ? 'text-red-600 bg-red-100' :
                  finding.severity === 'high' ? 'text-orange-600 bg-orange-100' :
                  finding.severity === 'medium' ? 'text-yellow-600 bg-yellow-100' :
                  'text-blue-600 bg-blue-100'
                }`}>
                  {finding.severity.toUpperCase()}
                </span>
              </div>
              <p className="text-gray-600 mb-2">{finding.description}</p>
              <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                <span>📁 {finding.file_path}</span>
                {finding.line_number && <span>📍 Ligne {finding.line_number}</span>}
                {finding.resource_name && <span>🔧 {finding.resource_name}</span>}
              </div>
              {finding.remediation && (
                <div className="bg-blue-50 p-3 rounded-md">
                  <p className="text-sm text-blue-800">
                    <strong>Remédiation:</strong> {finding.remediation}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

// Composant liste des règles
const RulesList = () => {
  const [rules, setRules] = useState([]);

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/iac-security/rules`);
      if (response.ok) {
        const data = await response.json();
        setRules(data.rules || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des règles:', error);
    }
  };

  return (
    <div className="space-y-4">
      {rules.map((rule, index) => (
        <div key={index} className="border rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-gray-900">{rule.name}</h4>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              rule.severity === 'critical' ? 'text-red-600 bg-red-100' :
              rule.severity === 'high' ? 'text-orange-600 bg-orange-100' :
              rule.severity === 'medium' ? 'text-yellow-600 bg-yellow-100' :
              'text-blue-600 bg-blue-100'
            }`}>
              {rule.severity.toUpperCase()}
            </span>
          </div>
          <p className="text-gray-600 mb-2">{rule.description}</p>
          <div className="flex items-center space-x-4 text-sm">
            <span className="text-gray-500">ID: {rule.rule_id}</span>
            <span className="text-gray-500">Catégorie: {rule.category}</span>
            <div className="flex space-x-1">
              {rule.applicable_types?.map((type, i) => (
                <span key={i} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                  {type}
                </span>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default IaCSecurityPage;