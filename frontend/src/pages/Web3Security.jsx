import React, { useState, useEffect } from 'react';
import { 
  Code, 
  Search, 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Activity,
  Globe,
  Zap,
  DollarSign,
  Settings,
  MapPin,
  RefreshCw,
  Download,
  Trash2,
  Play,
  Pause,
  FileText,
  Layers,
  TrendingUp
} from 'lucide-react';

const Web3Security = () => {
  const [audits, setAudits] = useState([]);
  const [currentAudit, setCurrentAudit] = useState(null);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [gasAnalysis, setGasAnalysis] = useState([]);
  const [isAuditing, setIsAuditing] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // État pour nouvel audit
  const [auditConfig, setAuditConfig] = useState({
    chain: 'ethereum',
    contract_address: '',
    source_code: '',
    contract_type: 'general',
    audit_scope: ['reentrancy', 'overflow', 'access_control', 'front_running']
  });

  // Filtres
  const [filters, setFilters] = useState({
    chain: '',
    contract_type: '',
    status: '',
    severity: ''
  });

  // Exemples de code pour tests
  const sampleContracts = {
    token: `pragma solidity ^0.8.0;

contract SampleToken {
    mapping(address => uint256) public balances;
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    function transfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount);
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
    
    function withdraw() public {
        uint256 amount = balances[msg.sender];
        msg.sender.call{value: amount}("");
        balances[msg.sender] = 0;
    }
}`,
    defi: `pragma solidity ^0.8.0;

contract DeFiProtocol {
    mapping(address => uint256) public stakes;
    uint256 public rewardRate = 100;
    
    function stake(uint256 amount) public {
        stakes[msg.sender] += amount;
    }
    
    function calculateReward() public view returns (uint256) {
        return stakes[msg.sender] * rewardRate * block.timestamp;
    }
    
    function emergencyWithdraw() public {
        require(tx.origin == owner);
        payable(msg.sender).transfer(address(this).balance);
    }
}`,
    nft: `pragma solidity ^0.8.0;

contract SimpleNFT {
    mapping(uint256 => string) public tokenURI;
    mapping(uint256 => address) public ownerOf;
    uint256 public nextTokenId;
    
    function mint(address to) public {
        uint256 tokenId = nextTokenId++;
        ownerOf[tokenId] = to;
        tokenURI[tokenId] = "ipfs://example";
    }
    
    function setTokenURI(uint256 tokenId, string memory uri) public {
        require(ownerOf[tokenId] == msg.sender);
        tokenURI[tokenId] = uri;
    }
}`
  };

  useEffect(() => {
    loadAudits();
    loadStats();
  }, [filters]);

  const loadAudits = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.chain) params.append('chain', filters.chain);
      if (filters.contract_type) params.append('contract_type', filters.contract_type);
      if (filters.status) params.append('status', filters.status);
      
      const response = await fetch(`/api/web3-security/audits?${params}`);
      const data = await response.json();
      setAudits(data.audits || []);
    } catch (error) {
      console.error('Erreur chargement audits:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/web3-security/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    }
  };

  const startAudit = async () => {
    if (isAuditing) return;
    
    if (!auditConfig.contract_address && !auditConfig.source_code) {
      alert('Veuillez fournir une adresse de contrat ou du code source');
      return;
    }
    
    setIsAuditing(true);
    try {
      const response = await fetch('/api/web3-security/audit/contract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(auditConfig)
      });

      if (response.ok) {
        const result = await response.json();
        setCurrentAudit(result);
        
        // Polling pour suivre le progrès
        pollAuditStatus(result.audit_id);
        loadAudits();
      } else {
        const error = await response.json();
        throw new Error(error.detail);
      }
    } catch (error) {
      console.error('Erreur audit:', error);
      alert('Erreur lors du démarrage de l\'audit: ' + error.message);
    }
  };

  const pollAuditStatus = (auditId) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/web3-security/audit/${auditId}/status`);
        const status = await response.json();
        
        setCurrentAudit(status);
        
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          setIsAuditing(false);
          loadAudits();
          
          if (status.status === 'completed') {
            loadAuditDetails(auditId);
          }
        }
      } catch (error) {
        console.error('Erreur polling:', error);
        clearInterval(interval);
        setIsAuditing(false);
      }
    }, 2000);
  };

  const loadAuditDetails = async (auditId) => {
    try {
      // Charger les vulnérabilités
      const vulnResponse = await fetch(`/api/web3-security/audit/${auditId}/vulnerabilities`);
      const vulnData = await vulnResponse.json();
      setVulnerabilities(vulnData.vulnerabilities || []);

      // Charger l'analyse de gas
      const gasResponse = await fetch(`/api/web3-security/audit/${auditId}/gas-analysis`);
      const gasData = await gasResponse.json();
      setGasAnalysis(gasData.gas_analysis || []);
    } catch (error) {
      console.error('Erreur chargement détails:', error);
    }
  };

  const loadSampleContract = (type) => {
    setAuditConfig(prev => ({
      ...prev,
      source_code: sampleContracts[type],
      contract_type: type,
      contract_address: ''
    }));
  };

  const deleteAudit = async (auditId) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet audit ?')) return;
    
    try {
      await fetch(`/api/web3-security/audit/${auditId}`, { method: 'DELETE' });
      loadAudits();
      if (currentAudit?.audit_id === auditId) {
        setCurrentAudit(null);
        setVulnerabilities([]);
        setGasAnalysis([]);
      }
    } catch (error) {
      console.error('Erreur suppression:', error);
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'text-red-600 bg-red-50',
      high: 'text-orange-600 bg-orange-50',
      medium: 'text-yellow-600 bg-yellow-50',
      low: 'text-blue-600 bg-blue-50'
    };
    return colors[severity] || 'text-gray-600 bg-gray-50';
  };

  const getChainIcon = (chain) => {
    return <Globe className="w-4 h-4" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <Code className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Web3 Security</h1>
              <p className="text-gray-600">Audit de sécurité pour smart contracts</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={loadAudits}
              className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-100"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Statistiques */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <Search className="w-5 h-5 text-blue-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Total Audits</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_audits}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <Code className="w-5 h-5 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Contrats</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_contracts}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Vulnérabilités</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_vulnerabilities}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <Shield className="w-5 h-5 text-indigo-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Score Moyen</p>
                <p className="text-2xl font-bold text-gray-900">{stats.average_security_score}%</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Configuration nouvel audit */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Nouvel Audit Smart Contract</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Blockchain
            </label>
            <select
              value={auditConfig.chain}
              onChange={(e) => setAuditConfig(prev => ({ ...prev, chain: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="ethereum">Ethereum</option>
              <option value="bsc">Binance Smart Chain</option>
              <option value="polygon">Polygon</option>
              <option value="arbitrum">Arbitrum</option>
              <option value="optimism">Optimism</option>
              <option value="avalanche">Avalanche</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type de contrat
            </label>
            <select
              value={auditConfig.contract_type}
              onChange={(e) => setAuditConfig(prev => ({ ...prev, contract_type: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="general">Général</option>
              <option value="token">Token ERC-20</option>
              <option value="nft">NFT</option>
              <option value="defi">DeFi Protocol</option>
              <option value="dao">DAO</option>
            </select>
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Adresse du contrat (optionnel)
          </label>
          <input
            type="text"
            value={auditConfig.contract_address}
            onChange={(e) => setAuditConfig(prev => ({ ...prev, contract_address: e.target.value }))}
            placeholder="0x..."
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">
              Code source Solidity
            </label>
            <div className="flex space-x-2">
              <button
                onClick={() => loadSampleContract('token')}
                className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded"
              >
                Token
              </button>
              <button
                onClick={() => loadSampleContract('defi')}
                className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded"
              >
                DeFi
              </button>
              <button
                onClick={() => loadSampleContract('nft')}
                className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded"
              >
                NFT
              </button>
            </div>
          </div>
          <textarea
            value={auditConfig.source_code}
            onChange={(e) => setAuditConfig(prev => ({ ...prev, source_code: e.target.value }))}
            placeholder="pragma solidity ^0.8.0;..."
            rows={8}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm"
          />
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Scope d'audit
          </label>
          <div className="flex flex-wrap gap-2">
            {['reentrancy', 'overflow', 'access_control', 'front_running', 'time_manipulation', 'unchecked_call', 'tx_origin'].map(scope => (
              <label key={scope} className="flex items-center">
                <input
                  type="checkbox"
                  checked={auditConfig.audit_scope.includes(scope)}
                  onChange={(e) => {
                    const scopes = e.target.checked
                      ? [...auditConfig.audit_scope, scope]
                      : auditConfig.audit_scope.filter(s => s !== scope);
                    setAuditConfig(prev => ({ ...prev, audit_scope: scopes }));
                  }}
                  className="mr-2"
                />
                <span className="text-sm">{scope}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={startAudit}
            disabled={isAuditing}
            className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {isAuditing ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Audit en cours...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Démarrer l'audit
              </>
            )}
          </button>
        </div>
      </div>

      {/* Audit en cours */}
      {currentAudit && isAuditing && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <RefreshCw className="w-5 h-5 text-blue-600 animate-spin mr-3" />
            <div>
              <p className="font-medium text-blue-900">Audit en cours</p>
              <p className="text-sm text-blue-700">
                {currentAudit.message} - Progression: {currentAudit.progress || 0}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Liste des audits */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Historique des audits</h2>
            
            {/* Filtres */}
            <div className="flex space-x-2">
              <select
                value={filters.chain}
                onChange={(e) => setFilters(prev => ({ ...prev, chain: e.target.value }))}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                <option value="">Toutes chaînes</option>
                <option value="ethereum">Ethereum</option>
                <option value="bsc">BSC</option>
                <option value="polygon">Polygon</option>
              </select>
              
              <select
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                <option value="">Tous statuts</option>
                <option value="completed">Terminé</option>
                <option value="failed">Échoué</option>
              </select>
            </div>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Audit
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Vulnérabilités
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {audits.map((audit) => (
                <tr key={audit.audit_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getChainIcon(audit.chain)}
                      <div className="ml-3">
                        <div className="text-sm font-medium text-gray-900">
                          {audit.chain} - {audit.contract_type}
                        </div>
                        <div className="text-sm text-gray-500">
                          {audit.contract_address ? audit.contract_address.substring(0, 10) + '...' : 'Code source'}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      audit.status === 'completed' ? 'bg-green-100 text-green-800' :
                      audit.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {audit.status === 'completed' && <CheckCircle className="w-3 h-3 mr-1" />}
                      {audit.status === 'failed' && <AlertTriangle className="w-3 h-3 mr-1" />}
                      {audit.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {audit.security_score !== undefined && (
                      <div className="flex items-center">
                        <Shield className="w-4 h-4 mr-1 text-gray-400" />
                        <span className="text-sm text-gray-900">{audit.security_score}%</span>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {audit.vulnerabilities_found || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(audit.start_time).toLocaleString('fr-FR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      {audit.status === 'completed' && (
                        <button
                          onClick={() => loadAuditDetails(audit.audit_id)}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          <MapPin className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => deleteAudit(audit.audit_id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {audits.length === 0 && (
          <div className="text-center py-12">
            <Code className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun audit</h3>
            <p className="mt-1 text-sm text-gray-500">
              Lancez votre premier audit de smart contract pour commencer.
            </p>
          </div>
        )}
      </div>

      {/* Vulnérabilités détectées */}
      {vulnerabilities.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Vulnérabilités détectées ({vulnerabilities.length})
            </h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Vulnérabilité
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Sévérité
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Localisation
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Remédiation
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {vulnerabilities.map((vuln) => (
                  <tr key={vuln.id}>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        {vuln.title}
                      </div>
                      <div className="text-sm text-gray-500">
                        {vuln.description}
                      </div>
                      {vuln.swc_id && (
                        <div className="text-xs text-gray-400 mt-1">
                          {vuln.swc_id}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(vuln.severity)}`}>
                        {vuln.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {vuln.location}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {vuln.remediation}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Analyse de gas */}
      {gasAnalysis.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Analyse de consommation Gas ({gasAnalysis.length} fonctions)
            </h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Fonction
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Gas estimé
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Optimisation
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Suggestions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {gasAnalysis.map((analysis, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Zap className="w-4 h-4 text-yellow-500 mr-2" />
                        <span className="text-sm font-medium text-gray-900">
                          {analysis.function_name}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <DollarSign className="w-4 h-4 text-green-500 mr-1" />
                        <span className="text-sm text-gray-900">
                          {analysis.estimated_gas.toLocaleString()}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        analysis.optimization_potential > 20 ? 'bg-red-100 text-red-800' :
                        analysis.optimization_potential > 10 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {analysis.optimization_potential}%
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <ul className="text-sm text-gray-600 space-y-1">
                        {analysis.suggestions.map((suggestion, idx) => (
                          <li key={idx} className="flex items-start">
                            <TrendingUp className="w-3 h-3 text-blue-500 mr-1 mt-0.5 flex-shrink-0" />
                            {suggestion}
                          </li>
                        ))}
                      </ul>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Web3Security;