import React, { useState, useEffect } from 'react';
import { CheckCircleIcon, ClipboardDocumentListIcon, ChartBarIcon, ExclamationTriangleIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

const Compliance = () => {
  const [assessments, setAssessments] = useState([]);
  const [frameworks, setFrameworks] = useState({});
  const [dashboard, setDashboard] = useState({});
  const [activeTab, setActiveTab] = useState('overview');
  const [serviceStatus, setServiceStatus] = useState({});

  useEffect(() => {
    fetchServiceStatus();
    fetchFrameworks();
    fetchDashboard();
    fetchAssessments();
  }, []);

  const fetchServiceStatus = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/compliance/`);
      const data = await response.json();
      setServiceStatus(data);
    } catch (error) {
      console.error('Erreur récupération status:', error);
    }
  };

  const fetchFrameworks = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/compliance/frameworks`);
      const data = await response.json();
      setFrameworks(data.frameworks || {});
    } catch (error) {
      console.error('Erreur récupération frameworks:', error);
    }
  };

  const fetchDashboard = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL}/api/compliance/dashboard`);
      const data = await response.json();
      setDashboard(data);
    } catch (error) {
      console.error('Erreur récupération dashboard:', error);
    }
  };

  const fetchAssessments = async () => {
    try {
      // Placeholder pour les évaluations actives
      setAssessments([]);
    } catch (error) {
      console.error('Erreur récupération évaluations:', error);
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

  const FrameworkCard = ({ name, info }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <h4 className="font-semibold text-gray-900">{info.name}</h4>
        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">{info.version}</span>
      </div>
      
      <p className="text-sm text-gray-600 mb-3">{info.scope}</p>
      
      <div className="space-y-2 text-xs text-gray-500">
        <div className="flex justify-between">
          <span>Contrôles:</span>
          <span className="font-medium">{info.control_count}</span>
        </div>
        <div className="flex justify-between">
          <span>Fréquence:</span>
          <span className="font-medium">{info.assessment_frequency}</span>
        </div>
        <div className="flex justify-between">
          <span>Juridiction:</span>
          <span className="font-medium">{info.jurisdiction}</span>
        </div>
      </div>
      
      <button className="mt-4 w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors text-sm">
        Lancer Évaluation
      </button>
    </div>
  );

  const ComplianceGauge = ({ percentage, label }) => (
    <div className="text-center">
      <div className="relative inline-flex">
        <svg className="w-20 h-20">
          <circle
            cx="40"
            cy="40"
            r="36"
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            className="text-gray-200"
          />
          <circle
            cx="40"
            cy="40"
            r="36"
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={`${2 * Math.PI * 36}`}
            strokeDashoffset={`${2 * Math.PI * 36 * (1 - percentage / 100)}`}
            className="text-blue-600"
            transform="rotate(-90 40 40)"
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-sm font-semibold text-gray-900">
          {percentage}%
        </span>
      </div>
      <p className="text-sm text-gray-600 mt-2">{label}</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">📋 Compliance Management</h1>
          <p className="text-gray-600 mt-2">
            Gestion de la conformité multi-frameworks avec évaluations automatisées
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
              <div className="text-2xl font-bold text-blue-600">{serviceStatus.active_assessments || 0}</div>
              <div className="text-sm text-gray-600">Évaluations Actives</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{serviceStatus.tracked_controls || 0}</div>
              <div className="text-sm text-gray-600">Contrôles Suivis</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{serviceStatus.open_gaps || 0}</div>
              <div className="text-sm text-gray-600">Lacunes Ouvertes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{serviceStatus.supported_frameworks?.length || 0}</div>
              <div className="text-sm text-gray-600">Frameworks Supportés</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', label: 'Vue d\'ensemble', icon: ChartBarIcon },
              { id: 'frameworks', label: 'Frameworks', icon: ClipboardDocumentListIcon },
              { id: 'assessments', label: 'Évaluations', icon: CheckCircleIcon },
              { id: 'dashboard', label: 'Tableau de Bord', icon: DocumentTextIcon }
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
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Capacités de Conformité</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-gray-700 mb-3">🔧 Fonctionnalités Clés</h4>
                  <ul className="space-y-2">
                    {[
                      'Évaluations multi-frameworks',
                      'Évaluation automatisée',
                      'Analyse des lacunes',
                      'Planification de remédiation',
                      'Surveillance continue',
                      'Génération de rapports',
                      'Gestion des preuves',
                      'Mises à jour réglementaires'
                    ].map((feature, index) => (
                      <li key={index} className="flex items-center text-sm text-gray-600">
                        <div className="w-2 h-2 bg-green-400 rounded-full mr-3"></div>
                        {feature}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-700 mb-3">📋 Frameworks Supportés</h4>
                  <div className="grid grid-cols-2 gap-2">
                    {serviceStatus.supported_frameworks?.map((framework, index) => (
                      <div key={index} className="bg-gray-50 rounded-md p-2 text-center">
                        <span className="text-xs font-medium text-gray-700 uppercase">{framework}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-8">
                <h4 className="font-semibold text-gray-700 mb-3">🎯 Types d'Évaluations</h4>
                <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                  {serviceStatus.assessment_types?.map((type, index) => (
                    <div key={index} className="bg-blue-50 rounded-lg p-3 text-center">
                      <div className="text-blue-600 font-medium text-sm">{type.replace('_', ' ')}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">🚀 Actions Rapides</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                    Nouvelle Évaluation
                  </button>
                  <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
                    Analyser Lacunes
                  </button>
                  <button className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors">
                    Générer Rapport
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'frameworks' && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Frameworks de Conformité</h3>
                <span className="text-sm text-gray-500">{Object.keys(frameworks).length} frameworks disponibles</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.entries(frameworks).map(([key, info]) => (
                  <FrameworkCard key={key} name={key} info={info} />
                ))}
              </div>

              <div className="mt-8 p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-700 mb-3">💡 Combinaisons Recommandées</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 bg-white rounded border">
                    <div>
                      <span className="font-medium">GDPR + ISO 27001</span>
                      <p className="text-sm text-gray-600">Idéal pour les organisations européennes</p>
                    </div>
                    <button className="text-blue-600 hover:text-blue-800 text-sm">Configurer</button>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-white rounded border">
                    <div>
                      <span className="font-medium">NIST + SOC 2</span>
                      <p className="text-sm text-gray-600">Parfait pour les fournisseurs de services US</p>
                    </div>
                    <button className="text-blue-600 hover:text-blue-800 text-sm">Configurer</button>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-white rounded border">
                    <div>
                      <span className="font-medium">ISO 27001 + PCI DSS</span>
                      <p className="text-sm text-gray-600">Essentiel pour e-commerce et paiements</p>
                    </div>
                    <button className="text-blue-600 hover:text-blue-800 text-sm">Configurer</button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'assessments' && (
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Évaluations de Conformité</h3>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
                  Nouvelle Évaluation
                </button>
              </div>

              {assessments.length === 0 ? (
                <div className="text-center py-12">
                  <CheckCircleIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 text-lg">Aucune évaluation en cours</p>
                  <p className="text-gray-400 text-sm">Les évaluations de conformité apparaîtront ici</p>
                  
                  <div className="mt-6 max-w-md mx-auto">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <h4 className="font-semibold text-blue-800 mb-2">Commencer une évaluation</h4>
                      <p className="text-blue-700 text-sm mb-3">
                        Sélectionnez un ou plusieurs frameworks pour démarrer une évaluation automatisée
                      </p>
                      <button className="w-full bg-blue-600 text-white py-2 rounded-md hover:bg-blue-700 transition-colors">
                        Créer Première Évaluation
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {assessments.map((assessment) => (
                    <div key={assessment.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-gray-900">{assessment.name}</h4>
                        <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                          {assessment.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{assessment.description}</p>
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <span>Frameworks: {assessment.frameworks?.join(', ')}</span>
                        <span>Créé: {new Date(assessment.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'dashboard' && (
            <div className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Tableau de Bord Conformité</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <StatusCard
                  title="Total Contrôles"
                  value={dashboard.overview?.total_controls || 0}
                  icon={ClipboardDocumentListIcon}
                  color="bg-blue-500"
                />
                <StatusCard
                  title="Contrôles Conformes"
                  value={dashboard.overview?.compliant_controls || 0}
                  icon={CheckCircleIcon}
                  color="bg-green-500"
                />
                <StatusCard
                  title="Conformité Globale"
                  value={`${dashboard.overview?.compliance_percentage || 0}%`}
                  icon={ChartBarIcon}
                  color="bg-purple-500"
                />
                <StatusCard
                  title="Lacunes Critiques"
                  value={dashboard.overview?.critical_gaps || 0}
                  icon={ExclamationTriangleIcon}
                  color="bg-red-500"
                />
              </div>

              {/* Compliance par Framework */}
              {dashboard.framework_compliance && Object.keys(dashboard.framework_compliance).length > 0 && (
                <div className="mb-8">
                  <h4 className="font-semibold text-gray-700 mb-4">Conformité par Framework</h4>
                  <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    {Object.entries(dashboard.framework_compliance).map(([framework, data]) => (
                      <ComplianceGauge
                        key={framework}
                        percentage={data.percentage || 0}
                        label={framework.toUpperCase()}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* Actions Prioritaires */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-yellow-50 rounded-lg p-4">
                  <h4 className="font-semibold text-yellow-800 mb-3">⚡ Actions Prioritaires</h4>
                  <ul className="space-y-2">
                    {dashboard.priority_actions?.map((action, index) => (
                      <li key={index} className="text-sm text-yellow-700 flex items-start">
                        <span className="w-2 h-2 bg-yellow-400 rounded-full mr-2 mt-2 flex-shrink-0"></span>
                        {action}
                      </li>
                    )) || [
                      <li key="default" className="text-sm text-yellow-700 flex items-start">
                        <span className="w-2 h-2 bg-yellow-400 rounded-full mr-2 mt-2 flex-shrink-0"></span>
                        Lancer une première évaluation de conformité
                      </li>
                    ]}
                  </ul>
                </div>

                <div className="bg-blue-50 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-800 mb-3">💡 Recommandations</h4>
                  <ul className="space-y-2">
                    {dashboard.recommendations?.map((rec, index) => (
                      <li key={index} className="text-sm text-blue-700 flex items-start">
                        <span className="w-2 h-2 bg-blue-400 rounded-full mr-2 mt-2 flex-shrink-0"></span>
                        {rec}
                      </li>
                    )) || [
                      <li key="default1" className="text-sm text-blue-700 flex items-start">
                        <span className="w-2 h-2 bg-blue-400 rounded-full mr-2 mt-2 flex-shrink-0"></span>
                        Planifier des revues trimestrielles de conformité
                      </li>,
                      <li key="default2" className="text-sm text-blue-700 flex items-start">
                        <span className="w-2 h-2 bg-blue-400 rounded-full mr-2 mt-2 flex-shrink-0"></span>
                        Automatiser la collecte de preuves quand possible
                      </li>
                    ]}
                  </ul>
                </div>
              </div>

              {/* Prochaines Échéances */}
              {dashboard.upcoming_assessments && dashboard.upcoming_assessments.length > 0 && (
                <div className="mt-6 bg-gray-50 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-700 mb-3">📅 Prochaines Échéances</h4>
                  <div className="space-y-2">
                    {dashboard.upcoming_assessments.slice(0, 5).map((assessment, index) => (
                      <div key={index} className="flex items-center justify-between bg-white rounded p-2">
                        <span className="text-sm text-gray-700">{assessment.title}</span>
                        <span className="text-xs text-gray-500">
                          {assessment.days_until_due > 0 
                            ? `dans ${assessment.days_until_due} jours` 
                            : 'en retard'
                          }
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Compliance;