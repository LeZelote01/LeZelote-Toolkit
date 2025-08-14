import React, { useState, useEffect } from 'react';
import { 
  Wifi, 
  Search, 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Activity,
  Globe,
  Router,
  Smartphone,
  Monitor,
  Settings,
  MapPin,
  RefreshCw,
  Download,
  Trash2,
  Play,
  Pause
} from 'lucide-react';

const IoTSecurity = () => {
  const [scans, setScans] = useState([]);
  const [currentScan, setCurrentScan] = useState(null);
  const [devices, setDevices] = useState([]);
  const [vulnerabilities, setVulnerabilities] = useState([]);
  const [isScanning, setIsScanning] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // État pour nouveau scan
  const [scanConfig, setScanConfig] = useState({
    target: {
      ip_range: '192.168.1.0/24',
      specific_devices: []
    },
    protocols: ['mqtt', 'coap', 'http', 'https'],
    scan_type: 'discovery',
    scan_options: {}
  });

  // Filtres
  const [filters, setFilters] = useState({
    scan_type: '',
    status: '',
    device_type: '',
    protocol: ''
  });

  useEffect(() => {
    loadScans();
    loadStats();
  }, [filters]);

  const loadScans = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.scan_type) params.append('scan_type', filters.scan_type);
      if (filters.status) params.append('status', filters.status);
      
      const response = await fetch(`/api/iot-security/scans?${params}`);
      const data = await response.json();
      setScans(data.scans || []);
    } catch (error) {
      console.error('Erreur chargement scans:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/iot-security/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    }
  };

  const startScan = async () => {
    if (isScanning) return;
    
    setIsScanning(true);
    try {
      const response = await fetch('/api/iot-security/scan/device', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scanConfig)
      });

      if (response.ok) {
        const result = await response.json();
        setCurrentScan(result);
        
        // Polling pour suivre le progrès
        pollScanStatus(result.scan_id);
        loadScans();
      } else {
        throw new Error('Erreur lors du démarrage du scan');
      }
    } catch (error) {
      console.error('Erreur scan:', error);
      alert('Erreur lors du démarrage du scan: ' + error.message);
    }
  };

  const pollScanStatus = (scanId) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`/api/iot-security/scan/${scanId}/status`);
        const status = await response.json();
        
        setCurrentScan(status);
        
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          setIsScanning(false);
          loadScans();
          
          if (status.status === 'completed') {
            loadScanDetails(scanId);
          }
        }
      } catch (error) {
        console.error('Erreur polling:', error);
        clearInterval(interval);
        setIsScanning(false);
      }
    }, 2000);
  };

  const loadScanDetails = async (scanId) => {
    try {
      // Charger les dispositifs
      const devicesResponse = await fetch(`/api/iot-security/scan/${scanId}/devices`);
      const devicesData = await devicesResponse.json();
      setDevices(devicesData.devices || []);

      // Charger les vulnérabilités
      const vulnResponse = await fetch(`/api/iot-security/scan/${scanId}/vulnerabilities`);
      const vulnData = await vulnResponse.json();
      setVulnerabilities(vulnData.vulnerabilities || []);
    } catch (error) {
      console.error('Erreur chargement détails:', error);
    }
  };

  const deleteScan = async (scanId) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce scan ?')) return;
    
    try {
      await fetch(`/api/iot-security/scan/${scanId}`, { method: 'DELETE' });
      loadScans();
      if (currentScan?.scan_id === scanId) {
        setCurrentScan(null);
        setDevices([]);
        setVulnerabilities([]);
      }
    } catch (error) {
      console.error('Erreur suppression:', error);
    }
  };

  const getDeviceIcon = (deviceType) => {
    const icons = {
      camera: Monitor,
      router: Router,
      sensor: Activity,
      smart_plug: Settings,
      smart_bulb: Globe,
      unknown: Wifi
    };
    const Icon = icons[deviceType] || Wifi;
    return <Icon className="w-4 h-4" />;
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
            <div className="p-2 bg-purple-100 rounded-lg">
              <Wifi className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">IoT Security</h1>
              <p className="text-gray-600">Analyse de sécurité des dispositifs IoT</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={loadScans}
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
                <p className="text-sm font-medium text-gray-600">Total Scans</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_scans}</p>
              </div>
            </div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="flex items-center">
              <Wifi className="w-5 h-5 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Dispositifs</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_devices}</p>
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
              <Shield className="w-5 h-5 text-purple-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-600">Score Sécurité</p>
                <p className="text-2xl font-bold text-gray-900">{stats.security_score}%</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Configuration nouveau scan */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Nouveau Scan IoT</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Plage IP à scanner
            </label>
            <input
              type="text"
              value={scanConfig.target.ip_range}
              onChange={(e) => setScanConfig(prev => ({
                ...prev,
                target: { ...prev.target, ip_range: e.target.value }
              }))}
              placeholder="192.168.1.0/24"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type de scan
            </label>
            <select
              value={scanConfig.scan_type}
              onChange={(e) => setScanConfig(prev => ({ ...prev, scan_type: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="discovery">Découverte</option>
              <option value="vulnerability">Vulnérabilités</option>
              <option value="configuration">Configuration</option>
              <option value="protocol_analysis">Analyse protocoles</option>
            </select>
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Protocoles à analyser
          </label>
          <div className="flex flex-wrap gap-2">
            {['mqtt', 'coap', 'modbus', 'http', 'https', 'ssh', 'telnet'].map(protocol => (
              <label key={protocol} className="flex items-center">
                <input
                  type="checkbox"
                  checked={scanConfig.protocols.includes(protocol)}
                  onChange={(e) => {
                    const protocols = e.target.checked
                      ? [...scanConfig.protocols, protocol]
                      : scanConfig.protocols.filter(p => p !== protocol);
                    setScanConfig(prev => ({ ...prev, protocols }));
                  }}
                  className="mr-2"
                />
                <span className="text-sm">{protocol.toUpperCase()}</span>
              </label>
            ))}
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={startScan}
            disabled={isScanning}
            className="inline-flex items-center px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
          >
            {isScanning ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Scan en cours...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Démarrer le scan
              </>
            )}
          </button>
        </div>
      </div>

      {/* Scan en cours */}
      {currentScan && isScanning && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <RefreshCw className="w-5 h-5 text-blue-600 animate-spin mr-3" />
            <div>
              <p className="font-medium text-blue-900">Scan en cours</p>
              <p className="text-sm text-blue-700">
                {currentScan.message} - Progression: {currentScan.progress || 0}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Liste des scans */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Historique des scans</h2>
            
            {/* Filtres */}
            <div className="flex space-x-2">
              <select
                value={filters.scan_type}
                onChange={(e) => setFilters(prev => ({ ...prev, scan_type: e.target.value }))}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                <option value="">Tous types</option>
                <option value="discovery">Découverte</option>
                <option value="vulnerability">Vulnérabilités</option>
                <option value="configuration">Configuration</option>
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
                  Scan
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Dispositifs
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
              {scans.map((scan) => (
                <tr key={scan.scan_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <Search className="w-4 h-4 text-gray-400 mr-2" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {scan.scan_type}
                        </div>
                        <div className="text-sm text-gray-500">
                          {scan.target?.ip_range || scan.target_range || 'Cibles spécifiques'}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      scan.status === 'completed' ? 'bg-green-100 text-green-800' :
                      scan.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {scan.status === 'completed' && <CheckCircle className="w-3 h-3 mr-1" />}
                      {scan.status === 'failed' && <AlertTriangle className="w-3 h-3 mr-1" />}
                      {scan.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {scan.devices_discovered || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {scan.vulnerabilities_found || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(scan.start_time).toLocaleString('fr-FR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      {scan.status === 'completed' && (
                        <button
                          onClick={() => loadScanDetails(scan.scan_id)}
                          className="text-purple-600 hover:text-purple-900"
                        >
                          <MapPin className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => deleteScan(scan.scan_id)}
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

        {scans.length === 0 && (
          <div className="text-center py-12">
            <Search className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun scan</h3>
            <p className="mt-1 text-sm text-gray-500">
              Lancez votre premier scan IoT pour découvrir les dispositifs sur votre réseau.
            </p>
          </div>
        )}
      </div>

      {/* Détails du scan sélectionné */}
      {devices.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Dispositifs découverts ({devices.length})
            </h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Dispositif
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Protocoles
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ports ouverts
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {devices.map((device) => (
                  <tr key={device.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {getDeviceIcon(device.device_type)}
                        <div className="ml-3">
                          <div className="text-sm font-medium text-gray-900">
                            {device.ip_address}
                          </div>
                          {device.manufacturer && (
                            <div className="text-sm text-gray-500">
                              {device.manufacturer} {device.model}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {device.device_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex flex-wrap gap-1">
                        {device.protocols.map(protocol => (
                          <span key={protocol} className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
                            {protocol}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {device.open_ports.join(', ')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Vulnérabilités */}
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
                    Protocole
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
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(vuln.severity)}`}>
                        {vuln.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {vuln.protocol}
                      {vuln.port && `:${vuln.port}`}
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
    </div>
  );
};

export default IoTSecurity;