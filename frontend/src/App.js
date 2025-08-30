import React, { useState } from 'react';
import Navigation from './components/Navigation';
import ChatPage from './components/ChatPage';
import Features from './components/Features';

function App() {
  // Current page state
  const [currentPage, setCurrentPage] = useState('chat');

  // Render current page
  const renderPage = () => {
    switch (currentPage) {
      case 'features':
        return <Features />;
      case 'chat':
      default:
        return <ChatPage />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Navigation 
        currentPage={currentPage}
        onNavigate={setCurrentPage}
        user={null} // No user authentication
        onLogout={() => {}} // No logout needed
      />
      {renderPage()}
    </div>
  );
}

export default App;
