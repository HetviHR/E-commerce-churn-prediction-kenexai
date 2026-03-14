import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Database, 
  Megaphone, 
  Users, 
  BrainCircuit,
  Sun,
  Moon
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { isDark, toggleTheme } = useTheme();

  const navItems = [
    { name: 'Data Quality', icon: Database, path: '/' },
    { name: 'Marketing Manager', icon: Megaphone, path: '/marketing' },
    { name: 'Customer Success', icon: Users, path: '/customer-success' },
    { name: 'AI Retention Panel', icon: BrainCircuit, path: '/ai-retention' },
  ];

  return (
    <aside className="w-[280px] h-screen bg-[#0A0D14] flex flex-col py-8 px-6 border-r border-[#1e2230] transition-colors duration-300">
      {/* Logo */}
      <div className="flex items-center gap-4 mb-12">
        <div className="w-12 h-12 rounded-full bg-[#1A1D27] flex flex-shrink-0 items-center justify-center transition-colors">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" fill="#F59E0B" />
            <path d="M2 17L12 22L22 17" stroke="#F59E0B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="#F59E0B" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <circle cx="12" cy="12" r="10" stroke="#F59E0B" strokeWidth="1.5" strokeOpacity="0.5" />
          </svg>
        </div>
        <span className="text-2xl font-bold text-white tracking-wide transition-colors">ChurnAI</span>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-6 flex-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <div 
              key={item.name}
              onClick={() => navigate(item.path)}
              className="flex items-center gap-4 cursor-pointer group"
            >
              <div 
                className={`w-12 h-12 rounded-full flex flex-shrink-0 items-center justify-center transition-all duration-200 ${
                  isActive 
                    ? 'bg-[#6366F1] text-white shadow-[0_0_15px_rgba(99,102,241,0.4)]' 
                    : 'bg-[#1A1D27] text-gray-400 group-hover:bg-[#2A2D39] group-hover:text-white'
                }`}
              >
                <item.icon size={20} strokeWidth={isActive ? 2.5 : 2} />
              </div>
              <span 
                className={`text-sm font-medium transition-colors ${
                  isActive ? 'text-white' : 'text-gray-400 group-hover:text-gray-200'
                }`}
              >
                {item.name}
              </span>
            </div>
          );
        })}
      </nav>

      {/* Theme Toggle */}
      <div className="pt-6 border-t border-[#1e2230]">
        <button 
          onClick={toggleTheme}
          className="w-full flex items-center gap-4 p-3 rounded-2xl bg-[#1A1D27] hover:bg-[#2A2D39] transition-all duration-200 group text-gray-400 hover:text-white"
        >
          <div className="w-10 h-10 rounded-full bg-[#13151D] flex items-center justify-center group-hover:bg-[#0A0D14] transition-colors">
            {isDark ? <Sun size={20} /> : <Moon size={20} className="text-gray-600" />}
          </div>
          <span className="text-sm font-medium">
            {isDark ? 'Light Mode' : 'Dark Mode'}
          </span>
        </button>
      </div>
    </aside>
  );
}
