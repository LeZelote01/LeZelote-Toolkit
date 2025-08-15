import React, { useState, useEffect } from 'react';
import { ArrowRightIcon, ShieldIcon, EyeSlashIcon, GlobeAltIcon, LockClosedIcon, CpuChipIcon, ClockIcon } from '@heroicons/react/24/outline';

const StealthMode = () => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [sessionConfig, setSessionConfig] = useState({
    level: 'medium',
    tor_enabled: true,
    vpn_chaining: false,
    signature_evasion: true,
    anti_forensics: true,
    decoy_traffic: false,
    mac_spoofing: false,
    process_hiding: true,
    memory_cleaning: true,
    log_anonymization: true,
    dns_over_https: true,
    timing_variation_min: 1.0,
    timing_variation_max: 30.0
  });
  const [operation, setOperation] = useState({
    operation_type: 'port_scan',
    target: '',
    params: {}
  });
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [networkIdentity, setNetworkIdentity] = useState(null);

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    loadStealthStats();
    loadNetworkIdentity();
  }, []);

  const loadStealthStats = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stealth-mode/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    }
  };

  const loadNetworkIdentity = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/stealth-mode/network/identity`);
      if (response.ok) {
        const data = await response.json();
        setNetworkIdentity(data.network_identity);
      }
    } catch (error) {
      console.error('Erreur chargement identité réseau:', error);
    }
  };

  const createStealthSession = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/stealth-mode/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionConfig),
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentSession(data);
        loadStealthStats();
        alert(`Session stealth créée avec succès ! ID: ${data.session_id}`);
      } else {
        const error = await response.json();
        alert(`Erreur: ${error.detail}`);
      }
    } catch (error) {
      alert(`Erreur réseau: ${error.message}`);
    }
    setLoading(false);
  };

  const executeStealthOperation = async () => {
    if (!currentSession || !operation.target) {
      alert('Veuillez créer une session et spécifier une cible');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/stealth-mode/operations/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: currentSession.session_id,
          ...operation
        }),
      });

      if (response.ok) {
        const data = await response.json();
        alert('Opération stealth terminée avec succès !');
        console.log('Résultats:', data);
      } else {
        const error = await response.json();
        alert(`Erreur: ${error.detail}`);
      }
    } catch (error) {
      alert(`Erreur réseau: ${error.message}`);
    }
    setLoading(false);
  };

  const terminateSession = async () => {
    if (!currentSession) return;

    setLoading(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/stealth-mode/sessions/${currentSession.session_id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setCurrentSession(null);
        loadStealthStats();
        alert('Session terminée et traces nettoyées');
      }
    } catch (error) {
      alert(`Erreur: ${error.message}`);
    }
    setLoading(false);
  };

  const stealthLevels = [
    { value: 'low', label: 'Faible', desc: 'Obfuscation basique', color: 'text-yellow-600' },
    { value: 'medium', label: 'Moyen', desc: 'Obfuscation avancée + anti-forensics', color: 'text-orange-600' },
    { value: 'high', label: 'Élevé', desc: 'Obfuscation maximale + évasion complète', color: 'text-red-600' },
    { value: 'ghost', label: 'Fantôme', desc: 'Mode indétectable total', color: 'text-purple-600' }
  ];

  const operationTypes = [
    { value: 'port_scan', label: 'Scan de Ports' },
    { value: 'vulnerability_scan', label: 'Scan de Vulnérabilités' },
    { value: 'web_crawl', label: 'Exploration Web' },
    { value: 'api_test', label: 'Test API' }
  ];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <EyeSlashIcon className="h-8 w-8 text-purple-600" />
          <h1 className="text-3xl font-bold text-gray-900">Mode Furtif Avancé</h1>
          <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
            Stealth Mode
          </span>
        </div>
        <p className="text-gray-600">
          Système d'obfuscation réseau, d'évasion de signatures et de protection anti-forensique 
          pour des opérations cybersécurité totalement indétectables.
        </p>
      </div>

      {/* Statistiques Globales */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <ShieldIcon className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Sessions Actives</p>
                <p className="text-2xl font-bold text-gray-900">{stats.general_statistics?.active_sessions || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <CpuChipIcon className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Opérations</p>
                <p className="text-2xl font-bold text-gray-900">{stats.general_statistics?.total_active_operations || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <GlobeAltIcon className="h-6 w-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Identité Réseau</p>
                <p className="text-sm font-bold text-gray-900">
                  {networkIdentity?.anonymity_level || 'Standard'}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-red-500">
            <div className="flex items-center">
              <div className="p-2 bg-red-100 rounded-lg">
                <LockClosedIcon className="h-6 w-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Score Sécurité</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.overall_security_score || 0}/100
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Configuration Session Stealth */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Configuration Session Stealth</h2>
          
          {/* Niveau de Furtivité */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Niveau de Furtivité
            </label>
            <div className="grid grid-cols-2 gap-3">
              {stealthLevels.map((level) => (
                <div
                  key={level.value}
                  className={`p-3 border-2 rounded-lg cursor-pointer transition-all ${
                    sessionConfig.level === level.value
                      ? 'border-purple-500 bg-purple-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSessionConfig({...sessionConfig, level: level.value})}
                >
                  <div className={`font-medium ${level.color}`}>{level.label}</div>
                  <div className="text-xs text-gray-600 mt-1">{level.desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Options Avancées */}
          <div className="mb-6">
            <h3 className="text-sm font-medium text-gray-700 mb-3">Options Avancées</h3>
            <div className="grid grid-cols-2 gap-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={sessionConfig.tor_enabled}
                  onChange={(e) => setSessionConfig({...sessionConfig, tor_enabled: e.target.checked})}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="ml-2 text-sm text-gray-700">Tor</span>
              </label>
              
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={sessionConfig.vpn_chaining}
                  onChange={(e) => setSessionConfig({...sessionConfig, vpn_chaining: e.target.checked})}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="ml-2 text-sm text-gray-700">VPN Chaining</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={sessionConfig.signature_evasion}
                  onChange={(e) => setSessionConfig({...sessionConfig, signature_evasion: e.target.checked})}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="ml-2 text-sm text-gray-700">Évasion Signatures</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={sessionConfig.anti_forensics}
                  onChange={(e) => setSessionConfig({...sessionConfig, anti_forensics: e.target.checked})}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="ml-2 text-sm text-gray-700">Anti-Forensics</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={sessionConfig.decoy_traffic}
                  onChange={(e) => setSessionConfig({...sessionConfig, decoy_traffic: e.target.checked})}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="ml-2 text-sm text-gray-700">Trafic Decoy</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={sessionConfig.mac_spoofing}
                  onChange={(e) => setSessionConfig({...sessionConfig, mac_spoofing: e.target.checked})}
                  className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                />
                <span className="ml-2 text-sm text-gray-700">MAC Spoofing</span>
              </label>
            </div>
          </div>

          {/* Contrôles Session */}
          <div className="flex gap-3">
            {!currentSession ? (
              <button
                onClick={createStealthSession}
                disabled={loading}
                className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
              >
                {loading ? 'Création...' : 'Créer Session Stealth'}
              </button>
            ) : (
              <button
                onClick={terminateSession}
                disabled={loading}
                className="flex-1 bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
              >
                {loading ? 'Terminaison...' : 'Terminer Session'}
              </button>
            )}
          </div>

          {/* Info Session Active */}
          {currentSession && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                <span className="text-sm font-medium text-green-800">Session Active</span>
              </div>
              <p className="text-xs text-green-700 mt-1">
                ID: {currentSession.session_id}
              </p>
              <p className="text-xs text-green-700">
                Niveau: {currentSession.configuration?.level}
              </p>
            </div>
          )}
        </div>

        {/* Exécution Opérations Stealth */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Opérations Stealth</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type d'Opération
            </label>
            <select
              value={operation.operation_type}
              onChange={(e) => setOperation({...operation, operation_type: e.target.value})}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {operationTypes.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cible
            </label>
            <input
              type="text"
              value={operation.target}
              onChange={(e) => setOperation({...operation, target: e.target.value})}
              placeholder="exemple.com, 192.168.1.1, etc."
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>

          <button
            onClick={executeStealthOperation}
            disabled={loading || !currentSession || !operation.target}
            className="w-full bg-purple-600 text-white py-3 px-4 rounded-lg hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              'Exécution en cours...'
            ) : (
              <>
                Exécuter Opération Stealth
                <ArrowRightIcon className="h-4 w-4" />
              </>
            )}
          </button>

          {/* Identité Réseau Actuelle */}
          {networkIdentity && (
            <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-3">Identité Réseau Actuelle</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">IP apparente:</span>
                  <div className="font-mono bg-white px-2 py-1 rounded border text-xs">
                    {networkIdentity.ip_address || 'Masquée'}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Pays:</span>
                  <div className="font-mono bg-white px-2 py-1 rounded border text-xs">
                    {networkIdentity.country || 'Inconnu'}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Tor:</span>
                  <div className={`px-2 py-1 rounded text-xs ${
                    networkIdentity.tor_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {networkIdentity.tor_active ? 'Actif' : 'Inactif'}
                  </div>
                </div>
                <div>
                  <span className="text-gray-600">Niveau:</span>
                  <div className="font-mono bg-white px-2 py-1 rounded border text-xs">
                    {networkIdentity.security_level || 'Standard'}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Avertissements Sécurité */}
      <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <ClockIcon className="h-5 w-5 text-yellow-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Avertissements de Sécurité
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <ul className="list-disc pl-5 space-y-1">
                <li>Utilisez le mode stealth uniquement dans un cadre légal et autorisé</li>
                <li>Les traces sont automatiquement nettoyées mais restez vigilant</li>
                <li>Certaines techniques peuvent être détectées par des systèmes avancés</li>
                <li>Respectez les délais entre opérations pour éviter la détection</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StealthMode;