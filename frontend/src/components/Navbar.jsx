import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldAlert, LayoutDashboard, MessageSquare, ShieldCheck, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="logo">
        <ShieldAlert size={28} color="#3b82f6" />
        <span>CrisisBridge AI</span>
      </div>
      
      <div className="nav-links">
        <Link 
          to="/dashboard" 
          className={`btn btn-ghost ${isActive('/dashboard') ? 'active' : ''}`}
        >
          <LayoutDashboard size={18} />
          Dashboard
        </Link>
        <Link 
          to="/chat" 
          className={`btn btn-ghost ${isActive('/chat') ? 'active' : ''}`}
        >
          <MessageSquare size={18} />
          AI Assistant
        </Link>
        <Link 
          to="/safety" 
          className={`btn btn-ghost ${isActive('/safety') ? 'active' : ''}`}
        >
          <ShieldCheck size={18} />
          Safety Check
        </Link>
      </div>

      <div className="user-profile">
        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
          {user?.username?.[0]?.toUpperCase() || 'A'}
        </div>
        <button className="btn btn-ghost" onClick={logout} style={{ padding: '0.5rem', border: 'none' }}>
          <LogOut size={18} />
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
