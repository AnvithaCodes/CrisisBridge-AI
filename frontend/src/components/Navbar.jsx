import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ShieldAlert, LayoutDashboard, MessageSquare, ShieldCheck, LogOut, Bell, Info } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [notifications, setNotifications] = React.useState([]);
  const [showNotifs, setShowNotifs] = React.useState(false);

  const fetchNotifs = async () => {
    try {
      const response = await axios.get('/api/v1/notifications');
      setNotifications(response.data.notifications);
    } catch (err) {
      console.error('Failed to fetch notifications');
    }
  };

  React.useEffect(() => {
    if (user) {
      fetchNotifs();
      const interval = setInterval(fetchNotifs, 30000); // 30s
      return () => clearInterval(interval);
    }
  }, [user]);

  const markAsRead = async (id) => {
    try {
      await axios.patch(`/api/v1/notifications/${id}/read`);
      fetchNotifs();
    } catch (err) {
      console.error('Failed to mark read');
    }
  };

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
        {user?.role === 'admin' && (
          <Link 
            to="/logs" 
            className={`btn btn-ghost ${isActive('/logs') ? 'active' : ''}`}
          >
            <Info size={18} />
            System Logs
          </Link>
        )}
      </div>

      <div className="user-profile">
        <div style={{ position: 'relative' }}>
          <button 
            className="btn btn-ghost" 
            onClick={() => setShowNotifs(!showNotifs)}
            style={{ padding: '0.5rem', border: 'none' }}
          >
            <Bell size={20} color={notifications.some(n => !n.is_read) ? 'var(--primary)' : 'white'} />
            {notifications.some(n => !n.is_read) && (
              <span style={{ 
                position: 'absolute', top: '4px', right: '4px', 
                width: '8px', height: '8px', background: 'var(--danger)', 
                borderRadius: '50%', border: '2px solid var(--bg-dark)' 
              }}></span>
            )}
          </button>

          <AnimatePresence>
            {showNotifs && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="glass-card"
                style={{
                  position: 'absolute', top: '100%', right: 0, width: '320px',
                  marginTop: '0.5rem', maxHeight: '400px', overflowY: 'auto',
                  padding: '1rem', zIndex: 1000
                }}
              >
                <div className="flex justify-between items-center mb-4">
                  <h4 style={{ fontSize: '0.875rem' }}>Notifications</h4>
                  <button className="text-xs text-primary" style={{ background: 'none', border: 'none' }}>Clear All</button>
                </div>
                <div className="flex flex-col gap-2">
                  {notifications.length === 0 ? (
                    <p className="text-xs text-muted text-center py-4">No notifications</p>
                  ) : (
                    notifications.map(n => (
                      <div 
                        key={n.id} 
                        className="p-3 rounded-lg"
                        style={{ 
                          background: n.is_read ? 'rgba(255,255,255,0.02)' : 'rgba(59, 130, 246, 0.1)',
                          cursor: 'pointer'
                        }}
                        onClick={() => markAsRead(n.id)}
                      >
                        <p className="text-xs font-bold">{n.title}</p>
                        <p className="text-xs text-muted mt-1">{n.message}</p>
                        <p className="text-xs text-muted mt-2" style={{ fontSize: '0.65rem', opacity: 0.5 }}>
                          {new Date(n.created_at).toLocaleTimeString()}
                        </p>
                      </div>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
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
