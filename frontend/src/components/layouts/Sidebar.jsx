import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Shield, Brain, Building2, FileText, Settings,
  Activity, Lock, Zap, Globe, Smartphone
} from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();

  const navigationItems = [
    { name: 'Dashboard', path: '/', icon: <Settings className="w-5 h-5" /> },
    
    // Services Cybersécurité
    { 
      name: 'Cybersécurité', 
      icon: <Shield className="w-5 h-5" />,
      children: [
        { name: 'Audit Sécurité', path: '/security/audit' },
        { name: 'Pentesting', path: '/security/pentest' },
        { name: 'Incident Response', path: '/security/incident' },
        { name: 'Forensics', path: '/security/forensics' },
        { name: 'Compliance', path: '/security/compliance' },
        { name: 'Monitoring', path: '/security/monitoring' }
      ]
    },
    
    // Services IA
    { 
      name: 'Intelligence IA', 
      icon: <Brain className="w-5 h-5" />,
      children: [
        { name: 'Assistant IA', path: '/ai/assistant' },
        { name: 'Cyber AI', path: '/ai/cyber' },
        { name: 'IA Prédictive', path: '/ai/predictive' },
        { name: 'Automatisation', path: '/ai/automation' }
      ]
    },
    
    // Services Business
    { 
      name: 'Business Tools', 
      icon: <Building2 className="w-5 h-5" />,
      children: [
        { name: 'CRM', path: '/business/crm' },
        { name: 'Facturation', path: '/business/billing' },
        { name: 'Analytics', path: '/business/analytics' },
        { name: 'Planning', path: '/business/planning' }
      ]
    },
    
    { name: 'Rapports', path: '/reports', icon: <FileText className="w-5 h-5" /> }
  ];

  return (
    <div className="w-64 bg-gray-900 text-white min-h-screen p-4">
      <div className="text-xl font-bold mb-8 text-center">
        🛡️ CyberSec Toolkit Pro 2025
      </div>
      
      <nav className="space-y-2">
        {navigationItems.map((item) => (
          <div key={item.name}>
            {item.children ? (
              <div>
                <div className="flex items-center space-x-3 p-3 text-gray-300 font-medium">
                  {item.icon}
                  <span>{item.name}</span>
                </div>
                <div className="ml-4 space-y-1">
                  {item.children.map((child) => (
                    <Link
                      key={child.name}
                      to={child.path}
                      className={`block p-2 pl-8 rounded text-sm hover:bg-gray-800 ${
                        location.pathname === child.path ? 'bg-gray-800 text-blue-400' : ''
                      }`}
                    >
                      {child.name}
                    </Link>
                  ))}
                </div>
              </div>
            ) : (
              <Link
                to={item.path}
                className={`flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-800 ${
                  location.pathname === item.path ? 'bg-gray-800 text-blue-400' : ''
                }`}
              >
                {item.icon}
                <span>{item.name}</span>
              </Link>
            )}
          </div>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;