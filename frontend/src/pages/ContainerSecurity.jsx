import React, { useState, useEffect } from 'react';
import api from '../services/api';

const ContainerSecurity = () => {
    const [status, setStatus] = useState(null);
    const [scans, setScans] = useState([]);
    const [loading, setLoading] = useState(false);
    const [scanForm, setScanForm] = useState({
        image_name: '',
        scan_type: 'vulnerability',
        include_runtime: false
    });
    const [activeTab, setActiveTab] = useState('scanner');
    const [selectedScan, setSelectedScan] = useState(null);
    const [vulnerabilities, setVulnerabilities] = useState([]);

    useEffect(() => {
        fetchStatus();
        fetchScans();
    }, []);

    const fetchStatus = async () => {
        try {
            const response = await api.get('/api/container-security/');
            setStatus(response.data);
        } catch (error) {
            console.error('Erreur récupération status:', error);
        }
    };

    const fetchScans = async () => {
        try {
            const response = await api.get('/api/container-security/scans');
            setScans(response.data.scans || []);
        } catch (error) {
            console.error('Erreur récupération scans:', error);
        }
    };

    const startScan = async (e) => {
        e.preventDefault();
        if (!scanForm.image_name.trim()) return;

        setLoading(true);
        try {
            const response = await api.post('/api/container-security/scan-image', scanForm);
            
            // Simuler le scan en cours
            setTimeout(() => {
                fetchScans();
                setScanForm({ image_name: '', scan_type: 'vulnerability', include_runtime: false });
                setLoading(false);
            }, 2000);
            
        } catch (error) {
            console.error('Erreur lancement scan:', error);
            setLoading(false);
        }
    };

    const fetchVulnerabilities = async (scanId) => {
        try {
            const response = await api.get(`/api/container-security/vulns?scan_id=${scanId}`);
            setVulnerabilities(response.data.vulnerabilities || []);
        } catch (error) {
            console.error('Erreur récupération vulnérabilités:', error);
        }
    };

    const getSeverityColor = (severity) => {
        const colors = {
            critical: 'text-red-800 bg-red-100',
            high: 'text-orange-800 bg-orange-100',
            medium: 'text-yellow-800 bg-yellow-100',
            low: 'text-blue-800 bg-blue-100',
            negligible: 'text-gray-800 bg-gray-100'
        };
        return colors[severity] || colors.low;
    };

    const StatusCard = () => (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold flex items-center">
                    🐳 Container Security
                    <span className={`ml-3 px-2 py-1 rounded-full text-xs font-medium ${
                        status?.status === 'operational' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                        {status?.status || 'Unknown'}
                    </span>
                </h2>
            </div>
            
            {status && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">{status.completed_scans}</div>
                        <div className="text-sm text-gray-500">Scans Terminés</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">{status.total_images_scanned}</div>
                        <div className="text-sm text-gray-500">Images Scannées</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">{status.total_vulnerabilities_found}</div>
                        <div className="text-sm text-gray-500">Vulnérabilités</div>
                    </div>
                    <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">{status.scan_performance?.success_rate || 'N/A'}</div>
                        <div className="text-sm text-gray-500">Taux de Succès</div>
                    </div>
                </div>
            )}
        </div>
    );

    const ScannerTab = () => (
        <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold mb-4">Nouveau Scan d'Image</h3>
                <form onSubmit={startScan} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Nom de l'image
                        </label>
                        <input
                            type="text"
                            value={scanForm.image_name}
                            onChange={(e) => setScanForm({...scanForm, image_name: e.target.value})}
                            placeholder="nginx:latest, postgres:13, myapp:1.0.0"
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                            required
                        />
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Type de scan
                        </label>
                        <select
                            value={scanForm.scan_type}
                            onChange={(e) => setScanForm({...scanForm, scan_type: e.target.value})}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                            <option value="vulnerability">Vulnérabilités</option>
                            <option value="configuration">Configuration</option>
                            <option value="runtime">Runtime Analysis</option>
                        </select>
                    </div>
                    
                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            id="include_runtime"
                            checked={scanForm.include_runtime}
                            onChange={(e) => setScanForm({...scanForm, include_runtime: e.target.checked})}
                            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <label htmlFor="include_runtime" className="ml-2 text-sm text-gray-700">
                            Inclure l'analyse runtime
                        </label>
                    </div>
                    
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <span className="flex items-center justify-center">
                                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                                </svg>
                                Scan en cours...
                            </span>
                        ) : (
                            'Lancer le scan'
                        )}
                    </button>
                </form>
            </div>

            {/* Fonctionnalités supportées */}
            {status && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-4">Fonctionnalités Supportées</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <h4 className="font-medium text-gray-700">Détection</h4>
                            <div className="space-y-1 text-sm">
                                {Object.entries(status.features).map(([key, enabled]) => (
                                    <div key={key} className="flex items-center">
                                        <span className={`w-2 h-2 rounded-full mr-2 ${enabled ? 'bg-green-500' : 'bg-gray-300'}`}></span>
                                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className="space-y-2">
                            <h4 className="font-medium text-gray-700">Formats & Standards</h4>
                            <div className="text-sm">
                                <div className="mb-2">
                                    <span className="font-medium">Formats:</span>
                                    <div className="ml-2">{status.supported_formats?.join(', ')}</div>
                                </div>
                                <div>
                                    <span className="font-medium">Conformité:</span>
                                    <div className="ml-2">{status.compliance_standards?.join(', ')}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    const HistoryTab = () => (
        <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b">
                <h3 className="text-lg font-semibold">Historique des Scans</h3>
            </div>
            <div className="divide-y">
                {scans.length === 0 ? (
                    <div className="p-6 text-center text-gray-500">
                        Aucun scan effectué pour le moment
                    </div>
                ) : (
                    scans.map((scan) => (
                        <div key={scan.scan_id} className="p-6 hover:bg-gray-50">
                            <div className="flex items-center justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center space-x-3">
                                        <h4 className="font-medium text-gray-900">{scan.image_name}</h4>
                                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                            scan.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                        }`}>
                                            {scan.status}
                                        </span>
                                    </div>
                                    <div className="mt-1 text-sm text-gray-500">
                                        Scan {scan.scan_type} • {new Date(scan.created_at).toLocaleString()}
                                    </div>
                                    {scan.vulnerabilities_found > 0 && (
                                        <div className="mt-2 flex space-x-4 text-sm">
                                            {Object.entries(scan.severity_breakdown).map(([severity, count]) => (
                                                count > 0 && (
                                                    <span key={severity} className={`px-2 py-1 rounded ${getSeverityColor(severity)}`}>
                                                        {count} {severity}
                                                    </span>
                                                )
                                            ))}
                                        </div>
                                    )}
                                </div>
                                <div className="flex items-center space-x-3">
                                    <div className="text-right">
                                        <div className="text-lg font-semibold text-gray-900">
                                            {scan.vulnerabilities_found}
                                        </div>
                                        <div className="text-xs text-gray-500">vulnérabilités</div>
                                    </div>
                                    <button
                                        onClick={() => {
                                            setSelectedScan(scan);
                                            fetchVulnerabilities(scan.scan_id);
                                        }}
                                        className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
                                    >
                                        Détails
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );

    const VulnerabilitiesTab = () => (
        <div className="space-y-6">
            {selectedScan && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold mb-4">
                        Vulnérabilités - {selectedScan.image_name}
                    </h3>
                    
                    <div className="grid grid-cols-4 gap-4 mb-6">
                        {Object.entries(selectedScan.severity_breakdown).map(([severity, count]) => (
                            <div key={severity} className="text-center">
                                <div className={`text-2xl font-bold ${
                                    severity === 'critical' ? 'text-red-600' :
                                    severity === 'high' ? 'text-orange-600' :
                                    severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                                }`}>
                                    {count}
                                </div>
                                <div className="text-sm text-gray-500 capitalize">{severity}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="bg-white rounded-lg shadow">
                <div className="p-6 border-b">
                    <h3 className="text-lg font-semibold">Liste des Vulnérabilités</h3>
                </div>
                <div className="divide-y">
                    {vulnerabilities.length === 0 ? (
                        <div className="p-6 text-center text-gray-500">
                            Sélectionnez un scan pour voir les vulnérabilités
                        </div>
                    ) : (
                        vulnerabilities.map((vuln, index) => (
                            <div key={index} className="p-6">
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-3 mb-2">
                                            <h4 className="font-medium text-gray-900">{vuln.cve_id}</h4>
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(vuln.severity)}`}>
                                                {vuln.severity}
                                            </span>
                                            {vuln.cvss_score && (
                                                <span className="text-sm text-gray-500">
                                                    CVSS: {vuln.cvss_score}
                                                </span>
                                            )}
                                        </div>
                                        <p className="text-gray-700 mb-2">{vuln.description}</p>
                                        <div className="text-sm text-gray-500">
                                            Package: <span className="font-medium">{vuln.package}</span> 
                                            ({vuln.installed_version})
                                            {vuln.fixed_version && (
                                                <span className="text-green-600 ml-2">
                                                    → Fix: {vuln.fixed_version}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <StatusCard />
            
            {/* Navigation Tabs */}
            <div className="border-b border-gray-200 mb-6">
                <nav className="-mb-px flex space-x-8">
                    {[
                        { id: 'scanner', name: 'Scanner', icon: '🔍' },
                        { id: 'history', name: 'Historique', icon: '📋' },
                        { id: 'vulnerabilities', name: 'Vulnérabilités', icon: '🐛' }
                    ].map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                                activeTab === tab.id
                                    ? 'border-blue-500 text-blue-600'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            <span className="mr-2">{tab.icon}</span>
                            {tab.name}
                        </button>
                    ))}
                </nav>
            </div>

            {/* Tab Content */}
            {activeTab === 'scanner' && <ScannerTab />}
            {activeTab === 'history' && <HistoryTab />}
            {activeTab === 'vulnerabilities' && <VulnerabilitiesTab />}
        </div>
    );
};

export default ContainerSecurity;