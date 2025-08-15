import React, { useState, useEffect } from 'react';
import { Shield, Users, Mail, Phone, AlertTriangle, CheckCircle, BarChart3, Eye, TrendingUp, Target, Settings } from 'lucide-react';

const SocialEngineeringPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [campaigns, setCampaigns] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({});

  useEffect(() => {
    fetchSocialEngineeringData();
  }, []);

  const fetchSocialEngineeringData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social-engineering/`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des données Social Engineering:', error);
    }
  };

  const handleCampaignSubmit = async (campaignData) => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social-engineering/campaign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(campaignData),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Campagne créée avec succès! ID: ${result.campaign_id}`);
        fetchCampaigns();
      } else {
        throw new Error('Erreur lors de la création de la campagne');
      }
    } catch (error) {
      console.error('Erreur création campagne:', error);
      alert('Erreur lors de la création de la campagne');
    } finally {
      setLoading(false);
    }
  };

  const fetchCampaigns = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social-engineering/campaigns`);
      if (response.ok) {
        const data = await response.json();
        setCampaigns(data.campaigns || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des campagnes:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social-engineering/templates`);
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des templates:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'campaigns') {
      fetchCampaigns();
    } else if (activeTab === 'templates') {
      fetchTemplates();
    }
  }, [activeTab]);

  const getCampaignStatusColor = (status) => {
    const colors = {
      active: 'text-green-600 bg-green-100',
      completed: 'text-blue-600 bg-blue-100',
      scheduled: 'text-yellow-600 bg-yellow-100',
      stopped: 'text-red-600 bg-red-100'
    };
    return colors[status] || colors.scheduled;
  };

  const getSuccessRateColor = (successRate) => {
    if (successRate >= 30) return 'text-red-600';
    if (successRate >= 20) return 'text-orange-600';
    if (successRate >= 10) return 'text-yellow-600';
    return 'text-green-600';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Users className="h-8 w-8 text-orange-600" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Social Engineering</h1>
                <p className="text-gray-600">Simulations phishing et tests de sensibilisation</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <div className="text-2xl font-bold text-orange-600">{stats.active_campaigns || 0}</div>
                <div className="text-sm text-gray-500">Campagnes actives</div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-blue-600">{stats.total_targets_tested || 0}</div>
                <div className="text-sm text-gray-500">Cibles testées</div>
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
              { id: 'campaign', name: 'Nouvelle Campagne', icon: Target },
              { id: 'campaigns', name: 'Campagnes', icon: Mail },
              { id: 'templates', name: 'Templates', icon: Settings },
              { id: 'analytics', name: 'Analytics', icon: BarChart3 }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`${
                  activeTab === tab.id
                    ? 'border-orange-500 text-orange-600'
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
                    <p className="text-sm text-gray-600">Campagnes Actives</p>
                    <p className="text-2xl font-bold text-orange-600">{stats.active_campaigns || 0}</p>
                  </div>
                  <Target className="h-8 w-8 text-orange-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Campagnes Terminées</p>
                    <p className="text-2xl font-bold text-green-600">{stats.completed_campaigns || 0}</p>
                  </div>
                  <CheckCircle className="h-8 w-8 text-green-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Taux de Succès</p>
                    <p className={`text-2xl font-bold ${getSuccessRateColor(stats.overall_success_rate || 0)}`}>
                      {stats.overall_success_rate || 0}%
                    </p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-blue-600" />
                </div>
              </div>
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Cibles Testées</p>
                    <p className="text-2xl font-bold text-blue-600">{stats.total_targets_tested || 0}</p>
                  </div>
                  <Users className="h-8 w-8 text-blue-600" />
                </div>
              </div>
            </div>

            {/* Campaign Types */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Types de Campagnes</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {(stats.campaign_types || []).map((type, index) => (
                  <div key={index} className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                    <Mail className="h-5 w-5 text-orange-600" />
                    <span className="font-medium text-gray-900 capitalize">{type.replace('_', ' ')}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Awareness Improvement */}
            {stats.awareness_improvement && (
              <div className="bg-white p-6 rounded-lg shadow-sm border">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Amélioration Sensibilisation</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-red-600">{stats.awareness_improvement.initial_click_rate}%</div>
                    <div className="text-sm text-gray-500">Taux initial</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">{stats.awareness_improvement.current_click_rate}%</div>
                    <div className="text-sm text-gray-500">Taux actuel</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">+{stats.awareness_improvement.improvement_percentage}%</div>
                    <div className="text-sm text-gray-500">Amélioration</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'campaign' && (
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Nouvelle Campagne Social Engineering</h3>
            <CampaignForm onSubmit={handleCampaignSubmit} loading={loading} />
          </div>
        )}

        {activeTab === 'campaigns' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Gestion des Campagnes</h3>
            </div>
            <CampaignsList campaigns={campaigns} />
          </div>
        )}

        {activeTab === 'templates' && (
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Templates de Phishing</h3>
            </div>
            <TemplatesList templates={templates} />
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <AnalyticsDashboard />
          </div>
        )}
      </div>
    </div>
  );
};

// Composant formulaire de campagne
const CampaignForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    campaign_name: '',
    target_type: 'email_list',
    targets: [],
    template_type: 'phishing_email',
    campaign_duration: 7,
    difficulty_level: 'medium',
    training_mode: true
  });

  const [targetInput, setTargetInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.campaign_name.trim()) {
      alert('Veuillez saisir un nom de campagne');
      return;
    }
    if (formData.targets.length === 0) {
      alert('Veuillez ajouter au moins une cible');
      return;
    }
    onSubmit(formData);
  };

  const addTarget = () => {
    if (targetInput.trim() && !formData.targets.includes(targetInput.trim())) {
      setFormData({
        ...formData,
        targets: [...formData.targets, targetInput.trim()]
      });
      setTargetInput('');
    }
  };

  const removeTarget = (target) => {
    setFormData({
      ...formData,
      targets: formData.targets.filter(t => t !== target)
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nom de la Campagne
          </label>
          <input
            type="text"
            value={formData.campaign_name}
            onChange={(e) => setFormData({...formData, campaign_name: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="Nom de la campagne..."
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Type de Template
          </label>
          <select
            value={formData.template_type}
            onChange={(e) => setFormData({...formData, template_type: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="phishing_email">Email de Phishing</option>
            <option value="fake_login">Page de Connexion Factice</option>
            <option value="usb_drop">USB Drop</option>
            <option value="phone_vishing">Vishing (Appel)</option>
            <option value="spear_phishing">Spear Phishing</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Durée (jours)
          </label>
          <input
            type="number"
            value={formData.campaign_duration}
            onChange={(e) => setFormData({...formData, campaign_duration: parseInt(e.target.value)})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            min="1"
            max="30"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Niveau de Difficulté
          </label>
          <select
            value={formData.difficulty_level}
            onChange={(e) => setFormData({...formData, difficulty_level: e.target.value})}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="easy">Facile</option>
            <option value="medium">Moyen</option>
            <option value="hard">Difficile</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Cibles
        </label>
        <div className="flex space-x-2 mb-2">
          <input
            type="email"
            value={targetInput}
            onChange={(e) => setTargetInput(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
            placeholder="email@exemple.com"
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTarget())}
          />
          <button
            type="button"
            onClick={addTarget}
            className="bg-orange-600 text-white px-4 py-2 rounded-md hover:bg-orange-700"
          >
            Ajouter
          </button>
        </div>
        <div className="flex flex-wrap gap-2">
          {formData.targets.map((target, index) => (
            <span
              key={index}
              className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-sm flex items-center space-x-1"
            >
              <span>{target}</span>
              <button
                type="button"
                onClick={() => removeTarget(target)}
                className="text-orange-600 hover:text-orange-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      </div>

      <div className="flex items-center">
        <input
          type="checkbox"
          id="training_mode"
          checked={formData.training_mode}
          onChange={(e) => setFormData({...formData, training_mode: e.target.checked})}
          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
        />
        <label htmlFor="training_mode" className="ml-2 block text-sm text-gray-900">
          Mode formation (éducatif)
        </label>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="bg-orange-600 text-white px-6 py-2 rounded-md hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Création en cours...</span>
            </>
          ) : (
            <>
              <Target className="h-4 w-4" />
              <span>Créer la Campagne</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
};

// Composant liste des campagnes
const CampaignsList = ({ campaigns }) => {
  if (!campaigns.length) {
    return (
      <div className="p-8 text-center text-gray-500">
        <Target className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <p>Aucune campagne disponible</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Campagne
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Type
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Cibles
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Taux de Succès
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Date
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {campaigns.map((campaign) => (
            <tr key={campaign.campaign_id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-gray-900">{campaign.campaign_name}</div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  campaign.status === 'active' ? 'text-green-600 bg-green-100' :
                  campaign.status === 'completed' ? 'text-blue-600 bg-blue-100' :
                  campaign.status === 'scheduled' ? 'text-yellow-600 bg-yellow-100' :
                  'text-red-600 bg-red-100'
                }`}>
                  {campaign.status}
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                {campaign.template_type.replace('_', ' ')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {campaign.targets_count}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm">
                <span className={`font-medium ${
                  campaign.current_metrics.success_rate >= 30 ? 'text-red-600' :
                  campaign.current_metrics.success_rate >= 20 ? 'text-orange-600' :
                  campaign.current_metrics.success_rate >= 10 ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {campaign.current_metrics.success_rate}%
                </span>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(campaign.created_at).toLocaleDateString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// Composant liste des templates
const TemplatesList = ({ templates }) => {
  if (!templates.length) {
    return (
      <div className="p-8 text-center text-gray-500">
        <Settings className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <p>Aucun template disponible</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
      {templates.map((template, index) => (
        <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900">{template.name}</h4>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
              template.difficulty === 'easy' ? 'text-green-600 bg-green-100' :
              template.difficulty === 'medium' ? 'text-yellow-600 bg-yellow-100' :
              'text-red-600 bg-red-100'
            }`}>
              {template.difficulty}
            </span>
          </div>
          <p className="text-gray-600 text-sm mb-3">{template.description}</p>
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span className="capitalize">{template.category}</span>
            <span className={`font-medium ${
              template.success_rate >= 30 ? 'text-red-600' :
              template.success_rate >= 20 ? 'text-orange-600' :
              'text-green-600'
            }`}>
              {template.success_rate}% succès
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};

// Composant analytics
const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState({});

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/social-engineering/analytics`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des analytics:', error);
    }
  };

  if (!analytics.overview) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Campagnes Totales</p>
              <p className="text-2xl font-bold text-orange-600">{analytics.overview.total_campaigns}</p>
            </div>
            <Target className="h-8 w-8 text-orange-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Cibles Testées</p>
              <p className="text-2xl font-bold text-blue-600">{analytics.overview.total_targets}</p>
            </div>
            <Users className="h-8 w-8 text-blue-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Taux Moyen</p>
              <p className="text-2xl font-bold text-red-600">{analytics.overview.avg_success_rate}%</p>
            </div>
            <TrendingUp className="h-8 w-8 text-red-600" />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Amélioration</p>
              <p className="text-2xl font-bold text-green-600">+{analytics.overview.awareness_improvement}%</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-600" />
          </div>
        </div>
      </div>

      {/* Success Rates by Template */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Efficacité par Type de Template</h3>
        <div className="space-y-4">
          {Object.entries(analytics.success_rates_by_template || {}).map(([template, rate]) => (
            <div key={template} className="flex items-center justify-between">
              <span className="font-medium text-gray-900 capitalize">{template.replace('_', ' ')}</span>
              <div className="flex items-center space-x-2">
                <div className="w-32 bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      rate >= 30 ? 'bg-red-500' : rate >= 20 ? 'bg-orange-500' : 'bg-yellow-500'
                    }`}
                    style={{ width: `${Math.min(rate, 100)}%` }}
                  ></div>
                </div>
                <span className={`text-sm font-medium ${
                  rate >= 30 ? 'text-red-600' : rate >= 20 ? 'text-orange-600' : 'text-yellow-600'
                }`}>
                  {rate}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* User Behavior */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Comportement des Utilisateurs</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-red-600">{analytics.user_behavior?.immediate_clickers}%</div>
            <div className="text-sm text-gray-500">Cliquent immédiatement</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-yellow-600">{analytics.user_behavior?.delayed_clickers}%</div>
            <div className="text-sm text-gray-500">Cliquent après réflexion</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{analytics.user_behavior?.reporters}%</div>
            <div className="text-sm text-gray-500">Signalent le phishing</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SocialEngineeringPage;