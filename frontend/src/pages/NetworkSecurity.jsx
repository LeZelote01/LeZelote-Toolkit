import React, { useState, useEffect } from 'react';
import { Wifi, Shield, Search, Globe, AlertTriangle, Clock, Server, Activity, ChevronRight } from 'lucide-react';
import api from '../services/api.js';

const NetworkSecurity = () => {
  const [status, setStatus] = useState(null);
  const [scans, setScans] = useState([]);
  const [newScan, setNewScan] = useState({
    scan_type: 'port_scan',
    target: {
      ip_range: '',
      specific_hosts: []
    },
    scan_options: {
      port_range: '1-1000',
      os_detection: true,
      service_detection: true,
      stealth_mode: false
    }
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchStatus();
    fetchScans();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await api.get('/api/network-security/');
      setStatus(response.data);
    } catch (error) {
      console.error('Erreur récupération status:', error);
    }
  };

  const fetchScans = async () => {
    try {
      const response = await api.get('/api/network-security/scans');
      setScans(response.data.scans || []);
    } catch (error) {
      console.error('Erreur récupération scans:', error);
    }
  };

  const startScan = async () => {
    if (!newScan.target.ip_range && newScan.target.specific_hosts.length === 0) {
      alert('Veuillez spécifier une cible (plage IP ou hôtes spécifiques)');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/network-security/scan', newScan);
      setNewScan({
        scan_type: 'port_scan',
        target: {
          ip_range: '',
          specific_hosts: []
        },
        scan_options: {
          port_range: '1-1000',
          os_detection: true,
          service_detection: true,
          stealth_mode: false
        }
      });
      fetchScans();
    } catch (error) {
      console.error('Erreur lancement scan:', error);
      alert('Erreur lors du lancement du scan');
    }
    setLoading(false);
  };

  const getScanTypeLabel = (type) => {
    const labels = {
      port_scan: 'Scan de Ports',
      host_discovery: 'Découverte d\'Hôtes',
      service_detection: 'Détection Services',
      os_detection: 'Détection OS',
      vulnerability_scan: 'Scan Vulnérabilités',
      full_scan: 'Scan Complet',
      stealth_scan: 'Scan Furtif',
      udp_scan: 'Scan UDP'
    };
    return labels[type] || type;
  };

  const getScanStatusColor = (status) => {
    const colors = {
      completed: 'bg-green-100 text-green-800',
      running: 'bg-blue-100 text-blue-800',
      failed: 'bg-red-100 text-red-800',
      starting: 'bg-yellow-100 text-yellow-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center">
          <Wifi className="mr-3 h-8 w-8 text-blue-600" />
          Network Security
        </h1>
        <p className="text-gray-600">
          Scan et analyse de sécurité réseau avec découverte d'hôtes et détection de vulnérabilités
        </p>
      </div>

      {/* Status */}
      {status && (
        <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg p-6 mb-8">
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
                  Nmap: {status.nmap_available ? '✅ Disponible' : '❌ Indisponible'}
                </span>
                <span className="text-sm text-gray-600">
                  Scans actifs: {status.active_scans}
                </span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">
                {status.total_hosts_scanned}
              </div>
              <div className="text-sm text-gray-600">Hôtes scannés au total</div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Nouveau Scan */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Search className="w-5 h-5 mr-2 text-blue-600" />
            Nouveau Scan Réseau
          </h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type de Scan
              </label>
              <select
                value={newScan.scan_type}
                onChange={(e) => setNewScan(prev => ({...prev, scan_type: e.target.value}))}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="port_scan">Scan de Ports</option>
                <option value="host_discovery">Découverte d'Hôtes</option>
                <option value="service_detection">Détection Services</option>
                <option value="os_detection">Détection OS</option>
                <option value="vulnerability_scan">Scan Vulnérabilités</option>
                <option value="full_scan">Scan Complet</option>
                <option value="stealth_scan">Scan Furtif</option>
                <option value="udp_scan">Scan UDP</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cible (Plage IP) *
              </label>
              <input
                type="text"
                value={newScan.target.ip_range}
                onChange={(e) => setNewScan(prev => ({
                  ...prev,
                  target: {...prev.target, ip_range: e.target.value}
                }))}
                placeholder="ex: 192.168.1.0/24, 10.0.0.1-10.0.0.100"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Plage de Ports
              </label>
              <input
                type="text"
                value={newScan.scan_options.port_range}
                onChange={(e) => setNewScan(prev => ({
                  ...prev,
                  scan_options: {...prev.scan_options, port_range: e.target.value}
                }))}
                placeholder="ex: 1-1000, 80,443,22"
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div className="space-y-3">
              <label className="block text-sm font-medium text-gray-700">
                Options de Scan
              </label>
              
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newScan.scan_options.os_detection}
                    onChange={(e) => setNewScan(prev => ({
                      ...prev,
                      scan_options: {...prev.scan_options, os_detection: e.target.checked}
                    }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Détection OS</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newScan.scan_options.service_detection}
                    onChange={(e) => setNewScan(prev => ({
                      ...prev,
                      scan_options: {...prev.scan_options, service_detection: e.target.checked}
                    }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Détection Services</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newScan.scan_options.stealth_mode}
                    onChange={(e) => setNewScan(prev => ({
                      ...prev,
                      scan_options: {...prev.scan_options, stealth_mode: e.target.checked}
                    }))}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Mode Furtif</span>
                </label>
              </div>
            </div>

            <button
              onClick={startScan}
              disabled={loading || (!newScan.target.ip_range)}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <Clock className="w-4 h-4 mr-2 animate-spin" />
                  Démarrage...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2" />
                  Lancer Scan
                </>
              )}
            </button>
          </div>
        </div>

        {/* Scans Récents */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Activity className="w-5 h-5 mr-2 text-gray-600" />
            Scans Récents
          </h3>
          
          {scans.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Wifi className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Aucun scan pour le moment</p>
              <p className="text-sm">Lancez votre premier scan réseau</p>
            </div>
          ) : (
            <div className="space-y-4">
              {scans.slice(0, 5).map((scan) => (
                <div key={scan.scan_id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="font-medium text-gray-900">
                      {getScanTypeLabel(scan.scan_type)}
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getScanStatusColor(scan.status)}`}>
                      {scan.status === 'completed' ? 'Terminé' :
                       scan.status === 'running' ? 'En cours' :
                       scan.status === 'failed' ? 'Échoué' : scan.status}
                    </span>
                  </div>
                  
                  <div className="text-sm text-gray-600 mb-2">
                    Cible: {scan.target_range || scan.target} • 
                    Durée: {Math.round(scan.duration || 0)}s
                  </div>
                  
                  {scan.hosts_discovered !== undefined && (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="text-sm">
                          <Server className="w-4 h-4 inline mr-1" />
                          {scan.hosts_discovered} hôtes
                        </div>
                        {scan.vulnerabilities_found > 0 && (
                          <div className="text-sm text-orange-600">
                            <AlertTriangle className="w-4 h-4 inline mr-1" />
                            {scan.vulnerabilities_found} vulnérabilités
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

      {/* Services et OS Populaires */}
      {status && (status.top_services || status.top_os) && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          {status.top_services && Object.keys(status.top_services).length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Globe className="w-5 h-5 mr-2 text-green-600" />
                Services Détectés
              </h3>
              
              <div className="space-y-2">
                {Object.entries(status.top_services).slice(0, 5).map(([service, count]) => (
                  <div key={service} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{service}</span>
                    <span className="text-sm font-medium text-gray-900">{count} instances</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {status.top_os && Object.keys(status.top_os).length > 0 && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <Server className="w-5 h-5 mr-2 text-blue-600" />
                Systèmes Détectés
              </h3>
              
              <div className="space-y-2">
                {Object.entries(status.top_os).slice(0, 5).map(([os, count]) => (
                  <div key={os} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">{os}</span>
                    <span className="text-sm font-medium text-gray-900">{count} instances</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default NetworkSecurity;