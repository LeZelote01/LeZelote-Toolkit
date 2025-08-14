import React, { useState, useEffect } from 'react';
import { Cloud, Shield, AlertTriangle, CheckCircle, Download, Trash2, RefreshCw, Settings, Globe } from 'lucide-react';
import axios from '../services/api';

const CloudSecurity = () => {
  const [audits, setAudits] = useState([]);
  const [currentAudit, setCurrentAudit] = useState(null);
  const [findings, setFindings] = useState([]);
  const [isLaunching, setIsLaunching] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // État pour lancer un audit
  const [auditConfig, setAuditConfig] = useState({
    provider: 'aws',
    credentials: {
      aws: {
        access_key: '',
        secret_key: '',
        region: 'us-east-1'
      },
      azure: {
        subscription_id: '',
        tenant_id: '',
        client_id: '',
        client_secret: ''
      },
      gcp: {
        project_id: '',
        service_account_key: ''
      }
    },
    scope: {
      services: ['compute', 'storage', 'networking', 'iam'],
      frameworks: ['CIS-AWS', 'NIST', 'SOC2']
    },
    options: {
      deep_scan: false,
      export_format: 'json'
    }
  });

  // Filtres pour les findings
  const [filters, setFilters] = useState({
    audit_id: '',
    severity: '',
    service: '',
    page: 1,
    page_size: 20
  });

  useEffect(() => {
    loadAudits();
    loadStats();
  }, []);

  useEffect(() => {
    if (filters.audit_id) {
      loadFindings();
    }
  }, [filters]);

  const loadAudits = async () => {
    try {
      const response = await axios.get('/api/cloud-security/audits');
      setAudits(response.data || []);
    } catch (error) {
      console.error('Erreur chargement audits:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get('/api/cloud-security/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    }
  };

  const loadFindings = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.audit_id) params.append('audit_id', filters.audit_id);
      if (filters.severity) params.append('severity', filters.severity);
      if (filters.service) params.append('service', filters.service);
      params.append('page', filters.page);
      params.append('page_size', filters.page_size);

      const response = await axios.get(`/api/cloud-security/findings?${params}`);
      setFindings(response.data || []);
    } catch (error) {
      console.error('Erreur chargement findings:', error);
    }
  };

  const launchAudit = async () => {
    setIsLaunching(true);
    
    try {
      const response = await fetch('/api/cloud-security/audit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(auditConfig)
      });

      const result = await response.json();
      
      if (response.ok) {
        alert(`Audit lancé avec succès! ID: ${result.audit_id}`);
        loadAudits();
        // Reset credentials for security
        setAuditConfig({
          ...auditConfig,
          credentials: {
            aws: { access_key: '', secret_key: '', region: auditConfig.credentials.aws.region },
            azure: { subscription_id: '', tenant_id: '', client_id: '', client_secret: '' },
            gcp: { project_id: '', service_account_key: '' }
          }
        });
      } else {
        throw new Error(result.detail || 'Erreur lors du lancement');
      }
    } catch (error) {
      console.error('Erreur lancement audit:', error);
      alert('Erreur lors du lancement de l\'audit');
    } finally {
      setIsLaunching(false);
    }
  };

  const viewAuditDetails = async (auditId) => {
    try {
      setCurrentAudit({ id: auditId });
      setFilters({ ...filters, audit_id: auditId });
    } catch (error) {
      console.error('Erreur chargement détails:', error);
    }
  };

  const downloadReport = (auditId, format = 'json') => {
    const url = `/api/cloud-security/reports?audit_id=${auditId}&format=${format}`;
    window.open(url, '_blank');
  };

  const deleteAudit = async (auditId) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet audit ?')) return;
    
    try {
      const response = await fetch(`/api/cloud-security/audit/${auditId}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        loadAudits();
        if (currentAudit && currentAudit.id === auditId) {
          setCurrentAudit(null);
          setFindings([]);
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

  const getProviderIcon = (provider) => {
    const icons = {
      aws: '☁️',
      azure: '🔷',
      gcp: '🌐',
      multi: '🌍'
    };
    return icons[provider] || '☁️';
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
          <Cloud className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Cloud Security</h1>
            <p className="text-gray-600">Audit de sécurité multi-cloud (AWS, Azure, GCP)</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={loadAudits}
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
              <Cloud className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Total Audits</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_audits || 0}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Score Moyen</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.average_compliance_score || 0}%
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-orange-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Findings Critiques</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.critical_findings || 0}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="flex items-center">
              <Globe className="h-8 w-8 text-purple-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">Providers</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.providers_audited || 0}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Audit */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">
              <Settings className="h-5 w-5 inline mr-2" />
              Nouvel Audit
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Provider Cloud
                </label>
                <select
                  value={auditConfig.provider}
                  onChange={(e) => setAuditConfig({...auditConfig, provider: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="aws">{getProviderIcon('aws')} Amazon AWS</option>
                  <option value="azure">{getProviderIcon('azure')} Microsoft Azure</option>
                  <option value="gcp">{getProviderIcon('gcp')} Google Cloud</option>
                  <option value="multi">{getProviderIcon('multi')} Multi-Cloud</option>
                </select>
              </div>

              {/* Credentials AWS */}
              {auditConfig.provider === 'aws' && (
                <div className="space-y-3">
                  <h3 className="text-sm font-medium text-gray-900">Credentials AWS</h3>
                  <input
                    type="text"
                    placeholder="Access Key ID"
                    value={auditConfig.credentials.aws.access_key}
                    onChange={(e) => setAuditConfig({
                      ...auditConfig,
                      credentials: {
                        ...auditConfig.credentials,
                        aws: { ...auditConfig.credentials.aws, access_key: e.target.value }
                      }
                    })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  />
                  <input
                    type="password"
                    placeholder="Secret Access Key"
                    value={auditConfig.credentials.aws.secret_key}
                    onChange={(e) => setAuditConfig({
                      ...auditConfig,
                      credentials: {
                        ...auditConfig.credentials,
                        aws: { ...auditConfig.credentials.aws, secret_key: e.target.value }
                      }
                    })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  />
                  <select
                    value={auditConfig.credentials.aws.region}
                    onChange={(e) => setAuditConfig({
                      ...auditConfig,
                      credentials: {
                        ...auditConfig.credentials,
                        aws: { ...auditConfig.credentials.aws, region: e.target.value }
                      }
                    })}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                  >
                    <option value="us-east-1">US East (N. Virginia)</option>
                    <option value="us-west-2">US West (Oregon)</option>
                    <option value="eu-west-1">Europe (Ireland)</option>
                    <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                  </select>
                </div>
              )}

              {/* Services à auditer */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Services à Auditer
                </label>
                <div className="space-y-2">
                  {['compute', 'storage', 'networking', 'iam'].map((service) => (
                    <label key={service} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={auditConfig.scope.services.includes(service)}
                        onChange={(e) => {
                          const services = e.target.checked
                            ? [...auditConfig.scope.services, service]
                            : auditConfig.scope.services.filter(s => s !== service);
                          setAuditConfig({
                            ...auditConfig,
                            scope: { ...auditConfig.scope, services }
                          });
                        }}
                        className="mr-2"
                      />
                      <span className="text-sm capitalize">{service}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Frameworks */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Frameworks de Conformité
                </label>
                <div className="space-y-2">
                  {['CIS-AWS', 'NIST', 'SOC2', 'GDPR'].map((framework) => (
                    <label key={framework} className="flex items-center">
                      <input
                        type="checkbox"
                        checked={auditConfig.scope.frameworks.includes(framework)}
                        onChange={(e) => {
                          const frameworks = e.target.checked
                            ? [...auditConfig.scope.frameworks, framework]
                            : auditConfig.scope.frameworks.filter(f => f !== framework);
                          setAuditConfig({
                            ...auditConfig,
                            scope: { ...auditConfig.scope, frameworks }
                          });
                        }}
                        className="mr-2"
                      />
                      <span className="text-sm">{framework}</span>
                    </label>
                  ))}
                </div>
              </div>

              <button
                onClick={launchAudit}
                disabled={isLaunching || !auditConfig.credentials[auditConfig.provider].access_key}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {isLaunching ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin inline mr-2" />
                    Audit en cours...
                  </>
                ) : (
                  <>
                    <Cloud className="h-4 w-4 inline mr-2" />
                    Lancer l'Audit
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Audits List */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow rounded-lg">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                Audits ({audits.length})
              </h2>
            </div>
            
            <div className="divide-y divide-gray-200">
              {audits.length === 0 ? (
                <div className="p-6 text-center text-gray-500">
                  Aucun audit trouvé
                </div>
              ) : (
                audits.map((audit) => (
                  <div key={audit.id} className="p-6 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(audit.status)}
                          <div>
                            <h3 className="text-sm font-medium text-gray-900 flex items-center">
                              {getProviderIcon(audit.provider)}
                              <span className="ml-2">{audit.provider.toUpperCase()} Audit</span>
                            </h3>
                            <p className="text-sm text-gray-500">
                              {new Date(audit.created_at).toLocaleDateString()} •{' '}
                              {audit.scope?.services?.join(', ') || 'Services non spécifiés'}
                            </p>
                          </div>
                        </div>
                        
                        {audit.status === 'completed' && audit.summary && (
                          <div className="mt-3 flex items-center space-x-4">
                            <span className="text-sm text-gray-600">
                              Score: <span className="font-medium">
                                {audit.summary.compliance_score || 0}%
                              </span>
                            </span>
                            <span className="text-sm text-gray-600">
                              Findings: <span className="font-medium">
                                {audit.summary.total_findings || 0}
                              </span>
                            </span>
                            <span className="text-sm text-gray-600">
                              Critiques: <span className="font-medium text-red-600">
                                {audit.summary.critical_findings || 0}
                              </span>
                            </span>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {audit.status === 'completed' && (
                          <>
                            <button
                              onClick={() => viewAuditDetails(audit.id)}
                              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                            >
                              Détails
                            </button>
                            <button
                              onClick={() => downloadReport(audit.id, 'json')}
                              className="text-green-600 hover:text-green-800 text-sm"
                            >
                              <Download className="h-4 w-4" />
                            </button>
                          </>
                        )}
                        <button
                          onClick={() => deleteAudit(audit.id)}
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

          {/* Findings */}
          {currentAudit && findings.length > 0 && (
            <div className="bg-white shadow rounded-lg mt-6">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">
                  Findings - Audit {currentAudit.id}
                </h3>
                <div className="flex items-center space-x-4 mt-2">
                  <select
                    value={filters.severity}
                    onChange={(e) => setFilters({...filters, severity: e.target.value})}
                    className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                  >
                    <option value="">Toutes les sévérités</option>
                    <option value="critical">Critique</option>
                    <option value="high">Élevée</option>
                    <option value="medium">Moyenne</option>
                    <option value="low">Faible</option>
                  </select>
                  <select
                    value={filters.service}
                    onChange={(e) => setFilters({...filters, service: e.target.value})}
                    className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                  >
                    <option value="">Tous les services</option>
                    <option value="compute">Compute</option>
                    <option value="storage">Storage</option>
                    <option value="networking">Networking</option>
                    <option value="iam">IAM</option>
                  </select>
                </div>
              </div>
              
              <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                {findings.map((finding) => (
                  <div key={finding.id} className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(finding.severity)}`}>
                            {finding.severity.toUpperCase()}
                          </span>
                          <span className="text-sm font-medium text-gray-900">{finding.service}</span>
                        </div>
                        <h4 className="text-sm font-medium text-gray-900 mb-1">
                          {finding.title}
                        </h4>
                        <p className="text-sm text-gray-600 mb-2">{finding.description}</p>
                        {finding.resource_id && (
                          <p className="text-xs text-gray-500">
                            Ressource: {finding.resource_id}
                          </p>
                        )}
                        {finding.frameworks && (
                          <p className="text-xs text-gray-500">
                            Frameworks: {finding.frameworks.join(', ')}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CloudSecurity;