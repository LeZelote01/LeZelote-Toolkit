import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Shield, Brain, Building2, FileText, Settings, ShieldAlert, Search, ClipboardCheck, Code, Smartphone, Cloud, Wifi, Globe, Lock, Eye } from 'lucide-react';
import AssistantPage from './pages/Assistant.jsx';
import PentestPage from './pages/PentestPage.jsx';
import IncidentResponse from './pages/IncidentResponse.jsx';
import DigitalForensics from './pages/DigitalForensics.jsx';
import Compliance from './pages/Compliance.jsx';
import VulnerabilityManagement from './pages/VulnerabilityManagement.jsx';
import BusinessAI from './pages/BusinessAI.jsx';
import CodeAnalysis from './pages/CodeAnalysis.jsx';
import CRM from './pages/CRM.jsx';
import Billing from './pages/Billing.jsx';
import Analytics from './pages/Analytics.jsx';
import Planning from './pages/Planning.jsx';
import Training from './pages/Training.jsx';
import MobileSecurity from './pages/MobileSecurity.jsx';
import CloudSecurity from './pages/CloudSecurity.jsx';
import IoTSecurity from './pages/IoTSecurity.jsx';
import Web3Security from './pages/Web3Security.jsx';
import AISecurity from './pages/AISecurity.jsx';
import NetworkSecurity from './pages/NetworkSecurity.jsx';
import APISecurity from './pages/APISecurity.jsx';
import ContainerSecurity from './pages/ContainerSecurity.jsx';
import IaCSecurityPage from './pages/IaCSecurityPage.jsx';
import SocialEngineeringPage from './pages/SocialEngineeringPage.jsx';
import SecurityOrchestrationPage from './pages/SecurityOrchestrationPage.jsx';
import RiskAssessmentPage from './pages/RiskAssessmentPage.jsx';
import StealthMode from './pages/StealthMode.jsx';
import api from './services/api.js';

// Composants
function Dashboard() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    api.get('/api/')
      .then(res => setStatus(res.data))
      .catch(err => console.error('Error:', err));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        🛡️ CyberSec Toolkit Pro 2025
      </h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">État du Projet</h2>
        {status ? (
          <div className="space-y-2">
            <p><span className="font-medium">Status:</span> {status.status}</p>
            <p><span className="font-medium">Version:</span> {status.version}</p>
            <p><span className="font-medium">Services planifiés:</span> {status.services?.total_planned || 'N/A'}</p>
            <p><span className="font-medium">Services implémentés:</span> <span className="text-green-600 font-bold">{status.services?.implemented || 'N/A'}</span></p>
            <p><span className="font-medium">Phase:</span> {status.services?.phase || 'N/A'}</p>
            
            {status.services?.operational_services && (
              <div className="mt-4 p-3 bg-green-50 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">🎉 Services Opérationnels:</h3>
                <ul className="text-sm text-green-700 space-y-1">
                  {status.services.operational_services.map((service, index) => (
                    <li key={index} className="flex items-center">
                      <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
                      {service}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <p>Chargement du statut...</p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <ServiceCard 
          icon={<Brain className="w-8 h-8" />}
          title="Assistant IA"
          description="Chat cybersécurité expert"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
        <ServiceCard 
          icon={<Shield className="w-8 h-8" />}
          title="Pentesting"
          description="Tests de pénétration OWASP"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
        <ServiceCard 
          icon={<ShieldAlert className="w-8 h-8" />}
          title="Incident Response"
          description="Réponse aux incidents"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
        <ServiceCard 
          icon={<Search className="w-8 h-8" />}
          title="Digital Forensics"
          description="Investigation forensique"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
        <ServiceCard 
          icon={<ClipboardCheck className="w-8 h-8" />}
          title="Compliance"
          description="Gestion conformité"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
        <ServiceCard 
          icon={<ShieldAlert className="w-8 h-8" />}
          title="Vulnerability Management"
          description="Gestion des vulnérabilités"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
        <ServiceCard 
          icon={<Brain className="w-8 h-8" />}
          title="Business AI"
          description="IA décisions business"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
        <ServiceCard 
          icon={<Code className="w-8 h-8" />}
          title="Code Analysis AI"
          description="Analyse sécurisée du code"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
        <ServiceCard 
          icon={<Brain className="w-8 h-8" />}
          title="AI Security"
          description="Sécurité des modèles IA"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
        <ServiceCard 
          icon={<Wifi className="w-8 h-8" />}
          title="Network Security"
          description="Sécurité réseau et scans"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
        <ServiceCard 
          icon={<Lock className="w-8 h-8" />}
          title="API Security"
          description="Tests sécurité API OWASP"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
        <ServiceCard 
          icon={<Settings className="w-8 h-8" />}
          title="Container Security"
          description="Sécurité Docker & Kubernetes"
          status="IMPLÉMENTÉ ✅"
          statusColor="green"
        />
      </div>
    </div>
  );
}

function ServiceCard({ icon, title, description, status, statusColor = "yellow" }) {
  const statusColors = {
    green: "bg-green-100 text-green-800",
    yellow: "bg-yellow-100 text-yellow-800",
    blue: "bg-blue-100 text-blue-800"
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4 text-blue-600">
        {icon}
      </div>
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm mb-3">{description}</p>
      <span className={`inline-block px-2 py-1 text-xs rounded ${statusColors[statusColor]}`}>
        {status}
      </span>
    </div>
  );
}

function Sidebar() {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <Settings className="w-5 h-5" /> },
    { name: 'Assistant IA', path: '/assistant', icon: <Brain className="w-5 h-5" /> },
    { name: 'Pentesting', path: '/pentest', icon: <Shield className="w-5 h-5" /> },
    { name: 'Incident Response', path: '/incident-response', icon: <ShieldAlert className="w-5 h-5" /> },
    { name: 'Digital Forensics', path: '/digital-forensics', icon: <Search className="w-5 h-5" /> },
    { name: 'Compliance', path: '/compliance', icon: <ClipboardCheck className="w-5 h-5" /> },
    { name: 'Vulnerability Mgmt', path: '/vulnerability-management', icon: <ShieldAlert className="w-5 h-5" /> },
    { name: 'Mobile Security', path: '/mobile-security', icon: <Smartphone className="w-5 h-5" /> },
    { name: 'Cloud Security', path: '/cloud-security', icon: <Cloud className="w-5 h-5" /> },
    { name: 'IoT Security', path: '/iot-security', icon: <Wifi className="w-5 h-5" /> },
    { name: 'Web3 Security', path: '/web3-security', icon: <Globe className="w-5 h-5" /> },
    { name: 'AI Security', path: '/ai-security', icon: <Brain className="w-5 h-5" /> },
    { name: 'Network Security', path: '/network-security', icon: <Wifi className="w-5 h-5" /> },
    { name: 'API Security', path: '/api-security', icon: <Lock className="w-5 h-5" /> },
    { name: 'Container Security', path: '/container-security', icon: <Settings className="w-5 h-5" /> },
    { name: 'IaC Security', path: '/iac-security', icon: <Settings className="w-5 h-5" /> },
    { name: 'Social Engineering', path: '/social-engineering', icon: <ShieldAlert className="w-5 h-5" /> },
    { name: 'Security Orchestration', path: '/security-orchestration', icon: <Settings className="w-5 h-5" /> },
    { name: 'Risk Assessment', path: '/risk-assessment', icon: <ShieldAlert className="w-5 h-5" /> },
    { name: 'Stealth Mode', path: '/stealth-mode', icon: <EyeSlash className="w-5 h-5" /> },
    { name: 'CRM', path: '/crm', icon: <Building2 className="w-5 h-5" /> },
    { name: 'Billing', path: '/billing', icon: <FileText className="w-5 h-5" /> },
    { name: 'Analytics', path: '/analytics', icon: <Settings className="w-5 h-5" /> },
    { name: 'Planning', path: '/planning', icon: <Settings className="w-5 h-5" /> },
    { name: 'Training', path: '/training', icon: <Settings className="w-5 h-5" /> },
    { name: 'Business AI', path: '/business-ai', icon: <Building2 className="w-5 h-5" /> },
    { name: 'Code Analysis AI', path: '/code-analysis', icon: <Code className="w-5 h-5" /> }
  ];

  return (
    <div className="w-64 bg-gray-900 text-white min-h-screen p-4">
      <div className="text-xl font-bold mb-8">CyberSec Toolkit</div>
      <nav>
        {navItems.map((item) => (
          <Link
            key={item.name}
            to={item.path}
            className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-800 mb-2"
          >
            {item.icon}
            <span>{item.name}</span>
          </Link>
        ))}
      </nav>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="flex bg-gray-100 min-h-screen">
        <Sidebar />
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/assistant" element={<AssistantPage />} />
            <Route path="/pentest" element={<PentestPage />} />
            <Route path="/incident-response" element={<IncidentResponse />} />
            <Route path="/digital-forensics" element={<DigitalForensics />} />
            <Route path="/compliance" element={<Compliance />} />
            <Route path="/vulnerability-management" element={<VulnerabilityManagement />} />
            <Route path="/business-ai" element={<BusinessAI />} />
            <Route path="/code-analysis" element={<CodeAnalysis />} />
            <Route path="/mobile-security" element={<MobileSecurity />} />
            <Route path="/cloud-security" element={<CloudSecurity />} />
            <Route path="/iot-security" element={<IoTSecurity />} />
            <Route path="/crm" element={<CRM />} />
            <Route path="/billing" element={<Billing />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/planning" element={<Planning />} />
            <Route path="/training" element={<Training />} />
            <Route path="/web3-security" element={<Web3Security />} />
            <Route path="/ai-security" element={<AISecurity />} />
            <Route path="/network-security" element={<NetworkSecurity />} />
            <Route path="/api-security" element={<APISecurity />} />
            <Route path="/container-security" element={<ContainerSecurity />} />
            <Route path="/iac-security" element={<IaCSecurityPage />} />
            <Route path="/social-engineering" element={<SocialEngineeringPage />} />
            <Route path="/security-orchestration" element={<SecurityOrchestrationPage />} />
            <Route path="/risk-assessment" element={<RiskAssessmentPage />} />
            <Route path="/stealth-mode" element={<StealthMode />} />
            <Route path="/reports" element={<div className="p-6">Rapports - À implémenter</div>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;