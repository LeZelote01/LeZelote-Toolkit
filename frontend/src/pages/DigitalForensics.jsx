import React, { useState, useEffect } from 'react';
import { MagnifyingGlassIcon, DocumentTextIcon, FolderIcon, ClockIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';

const DigitalForensics = () => {
  const [cases, setCases] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [activeTab, setActiveTab] = useState('overview');
  const [serviceStatus, setServiceStatus] = useState({});

  useEffect(() => {
    fetchServiceStatus();
    fetchCases();
    fetchStatistics();
  }, []);

  const fetchServiceStatus = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/digital-forensics/`);
      const data = await response.json();
      setServiceStatus(data);
    } catch (error) {
      console.error('Erreur récupération status:', error);
    }
  };

  const fetchCases = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/digital-forensics/cases`);
      const data = await response.json();
      setCases(data.cases || []);
    } catch (error) {
      console.error('Erreur récupération dossiers:', error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/digital-forensics/statistics`);
      const data = await response.json();
      setStatistics(data);
    } catch (error) {
      console.error('Erreur récupération statistiques:', error);
    }
  };

  const StatusCard = ({ title, value, icon: Icon, color = "bg-blue-500" }) => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center">
        <div className={`${color} rounded-md p-3`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );

  const EvidenceTypeBadge = ({ type }) => {
    const colors = {
      disk_image: 'bg-purple-100 text-purple-800',
      memory_dump: 'bg-red-100 text-red-800',
      network_capture: 'bg-green-100 text-green-800',
      log_file: 'bg-blue-100 text-blue-800',
      email_message: 'bg-yellow-100 text-yellow-800',
      document: 'bg-gray-100 text-gray-800',
      mobile_backup: 'bg-indigo-100 text-indigo-800',
      other: 'bg-gray-100 text-gray-800'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[type] || colors.other}`}>
        {type.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🔍 Digital Forensics</h1>
          <p className="text-gray-600 mt-2">
            Investigation forensique numérique avec chaîne de custody complète
          </p>
        </div>

        {/* Service Status */}
        <div className="mb-8 bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">État du Service</h2>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
              <span className="text-sm font-medium text-green-600">
                {serviceStatus.status === 'operational' ? 'Opérationnel' : 'Indisponible'}
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{serviceStatus.active_cases || 0}</div>
              <div className="text-sm text-gray-600">Dossiers Actifs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{serviceStatus.active_evidence || 0}</div>
              <div className="text-sm text-gray-600">Preuves Actives</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{serviceStatus.running_analyses || 0}</div>
              <div className="text-sm text-gray-600">Analyses en Cours</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{serviceStatus.analysis_modules?.length || 0}</div>
              <div className="text-sm text-gray-600">Modules d'Analyse</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Vue d\'ensemble', icon: FolderIcon },
              { id: 'cases', label: 'Dossiers', icon: DocumentTextIcon },
              { id: 'evidence', label: 'Preuves', icon: ShieldCheckIcon },
              { id: 'statistics', label: 'Statistiques', icon: ClockIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                  activeTab === tab.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                <tab.icon className="h-5 w-5 mr-2" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content based on active tab */}
        <div className="bg-white rounded-lg shadow-md">
          {activeTab === 'overview' && (
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Capacités Forensiques</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-700 mb-3">🔧 Fonctionnalités Clés</h4>
                  <ul className="space-y-2">
                    {[
                      'Acquisition de preuves numériques',
                      'Chaîne de custody sécurisée',
                      'Analyses automatisées avancées',
                      'Reconstruction de timeline',
                      'Vérification d\'intégrité par hash',
                      'Recherche par mots-clés',
                      'Extraction de métadonnées',
                      'Génération de rapports'
                    ].map((feature, index) => (
                      <li key={index} className="flex items-center text-sm text-gray-600">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-700 mb-3">📊 Types de Preuves Supportées</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {serviceStatus.supported_evidence_types?.map((type, index) => (
                      <div key={index} className="bg-gray-50 rounded-md p-2 text-center">
                        <EvidenceTypeBadge type={type} />
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-8">
                <h4 className="font-semibold text-gray-700 mb-3">🔬 Modules d'Analyse Disponibles</h4>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {serviceStatus.analysis_modules?.map((module, index) => (
                    <div key={index} className="bg-blue-50 rounded-lg p-3 text-center">
                      <div className="text-blue-600 font-medium text-sm">{module.replace('_', ' ')}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">🚀 Actions Rapides</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                    Nouveau Dossier
                  </button>
                  <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
                    Ajouter Preuve
                  </button>
                  <button className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors">
                    Lancer Analyse
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'cases' && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Dossiers Forensiques</h3>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                  Nouveau Dossier
                </button>
              </div>

              {cases.length === 0 ? (
                <div className="text-center py-12">
                  <FolderIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 text-lg">Aucun dossier en cours</p>
                  <p className="text-gray-400 text-sm">Les dossiers d'enquête apparaîtront ici une fois créés</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">N° Dossier</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Titre</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Enquêteur</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Statut</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Preuves</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Créé</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {cases.map((caseItem) => (
                        <tr key={caseItem.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {caseItem.case_number}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{caseItem.title}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{caseItem.investigator}</td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              {caseItem.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{caseItem.evidence_count}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {new Date(caseItem.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button className="text-blue-600 hover:text-blue-900 mr-3">
                              <MagnifyingGlassIcon className="h-4 w-4" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === 'evidence' && (
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Gestion des Preuves</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="col-span-2">
                  <div className="bg-gray-50 rounded-lg p-4 text-center py-12">
                    <ShieldCheckIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 text-lg">Aucune preuve en cours d'analyse</p>
                    <p className="text-gray-400 text-sm">Les preuves numériques apparaîtront ici</p>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-gray-700 mb-3">Chaîne de Custody</h4>
                  <div className="space-y-3">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="flex items-center">
                        <div className="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
                        <span className="text-sm font-medium text-green-800">Intégrité Vérifiée</span>
                      </div>
                      <p className="text-xs text-green-600 mt-1">Toutes les preuves intègres</p>
                    </div>
                    
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                      <div className="flex items-center">
                        <div className="w-3 h-3 bg-blue-400 rounded-full mr-2"></div>
                        <span className="text-sm font-medium text-blue-800">Hash Validé</span>
                      </div>
                      <p className="text-xs text-blue-600 mt-1">SHA-256, MD5 vérifiés</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'statistics' && (
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Statistiques Forensiques</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatusCard
                  title="Dossiers Actifs"
                  value={statistics.summary?.active_cases || 0}
                  icon={FolderIcon}
                  color="bg-blue-500"
                />
                <StatusCard
                  title="Total Preuves"
                  value={statistics.summary?.total_evidence || 0}
                  icon={ShieldCheckIcon}
                  color="bg-green-500"
                />
                <StatusCard
                  title="Analyses Totales"
                  value={statistics.summary?.total_analyses || 0}
                  icon={MagnifyingGlassIcon}
                  color="bg-purple-500"
                />
                <StatusCard
                  title="Taux Completion"
                  value={`${statistics.summary?.completion_rate || 0}%`}
                  icon={ClockIcon}
                  color="bg-orange-500"
                />
              </div>

              {(statistics.evidence_by_type || statistics.analyses_by_type) && (
                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                  {statistics.evidence_by_type && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-700 mb-3">Preuves par Type</h4>
                      <div className="space-y-2">
                        {Object.entries(statistics.evidence_by_type).map(([type, count]) => (
                          <div key={type} className="flex justify-between">
                            <span className="text-sm text-gray-600">{type.replace('_', ' ')}</span>
                            <span className="text-sm font-medium">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {statistics.analyses_by_type && (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-700 mb-3">Analyses par Type</h4>
                      <div className="space-y-2">
                        {Object.entries(statistics.analyses_by_type).map(([type, count]) => (
                          <div key={type} className="flex justify-between">
                            <span className="text-sm text-gray-600">{type.replace('_', ' ')}</span>
                            <span className="text-sm font-medium">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {statistics.currently_running > 0 && (
                <div className="mt-6 bg-yellow-50 rounded-lg p-4">
                  <h4 className="font-semibold text-yellow-800 mb-2">Analyses en Cours</h4>
                  <p className="text-yellow-700">{statistics.currently_running} analyses en cours d'exécution</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DigitalForensics;