import React from 'react';

const ServiceCard = ({ 
  icon, 
  title, 
  description, 
  status, 
  phase,
  implemented = false,
  onClick = null 
}) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'implemented': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'planned': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div 
      className={`bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow ${
        onClick ? 'cursor-pointer' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4 text-blue-600">
        {icon}
      </div>
      
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm mb-3">{description}</p>
      
      <div className="flex justify-between items-center">
        <span className={`inline-block px-2 py-1 text-xs rounded ${getStatusColor(status)}`}>
          {implemented ? '✅ Implémenté' : `📋 ${phase || 'Planifié'}`}
        </span>
        
        {implemented && (
          <span className="text-green-600 text-sm font-medium">
            Opérationnel
          </span>
        )}
      </div>
    </div>
  );
};

export default ServiceCard;