import React from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import DataQuality from './pages/DataQuality';
import Marketing from './pages/Marketing';
import CustomerSuccess from './pages/CustomerSuccess';
import AIRetention from './pages/AIRetention';
import { ThemeProvider } from './context/ThemeContext';

function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  const getActiveItem = () => {
    switch (location.pathname) {
      case '/': return 'Data Quality';
      case '/marketing': return 'Marketing Manager';
      case '/customer-success': return 'Customer Success';
      case '/ai-retention': return 'AI Retention Panel';
      default: return 'Data Quality';
    }
  };

  const handleNavigate = (item) => {
    switch (item) {
      case 'Data Quality': navigate('/'); break;
      case 'Marketing Manager': navigate('/marketing'); break;
      case 'Customer Success': navigate('/customer-success'); break;
      case 'AI Retention Panel': navigate('/ai-retention'); break;
      default: navigate('/'); break;
    }
  };

  return (
    <div className="flex min-h-screen bg-[#0A0D14] text-white transition-colors duration-300 light:bg-[#F8FAFC] light:text-[#0F172A]">
      <Sidebar activeItem={getActiveItem()} setActiveItem={handleNavigate} />
      <main className="flex-1 p-8 h-screen overflow-y-auto w-full">
        <Routes>
          <Route path="/" element={<DataQuality />} />
          <Route path="/marketing" element={<Marketing />} />
          <Route path="/customer-success" element={<CustomerSuccess />} />
          <Route path="/ai-retention" element={<AIRetention />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
