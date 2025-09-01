import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDiamond, faComments, faInfoCircle } from '@fortawesome/free-solid-svg-icons';

const Navigation = ({ currentPage, onNavigate, user, onLogout }) => {
  const navItems = [
    { id: 'chat', label: 'Demo', icon: faComments },
    { id: 'features', label: 'Project Details', icon: faInfoCircle },
  ];

  return (
    <nav className="bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center cursor-pointer" onClick={() => onNavigate('chat')}>
            <FontAwesomeIcon icon={faDiamond} className="text-2xl mr-3" />
            <span className="text-xl font-bold">Fashion Assistant</span>
          </div>

          {/* Navigation Items */}
          <div className="flex items-center space-x-6">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`flex items-center px-3 py-2 rounded-lg transition-colors duration-200 ${
                  currentPage === item.id 
                    ? 'bg-white bg-opacity-20 text-white' 
                    : 'text-purple-100 hover:text-white hover:bg-white hover:bg-opacity-10'
                }`}
              >
                <FontAwesomeIcon icon={item.icon} className="mr-2" />
                {item.label}
              </button>
            ))}
            
            {/* User Info */}
            {user && (
              <div className="flex items-center space-x-3 ml-6">
                <span className="text-purple-100">Welcome, {user.name}</span>
                <button 
                  onClick={onLogout}
                  className="text-purple-100 hover:text-white px-3 py-1 rounded border border-purple-300 hover:border-white transition-colors"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
