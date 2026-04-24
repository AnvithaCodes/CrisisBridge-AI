import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertOctagon, MapPin, Clock, Users, Activity, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const [incidents, setIncidents] = useState([]);
  const [stats, setStats] = useState({ active: 0, resolved: 0 });
  const [loading, setLoading] = useState(true);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportData, setReportData] = useState({
    title: '',
    incident_type: 'fire',
    severity: 'medium',
    description: '',
    floor: 1,
    zone: 'lobby'
  });
  const { user } = useAuth();

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get('/api/v1/incidents');
      setIncidents(response.data.incidents);
      setStats({
        active: response.data.active_count,
        resolved: response.data.resolved_today || 0
      });
    } catch (err) {
      console.error('Failed to fetch incidents', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const handlePanic = async () => {
    if (!window.confirm("This will trigger a CRITICAL emergency alert. Continue?")) return;
    try {
      await axios.post('/api/v1/incidents/report', {
        incident_type: 'security',
        severity: 'critical',
        title: 'PANIC BUTTON TRIGGERED',
        description: `User ${user.full_name} initiated emergency panic alert.`,
        floor: user.current_floor || 1,
        room: user.current_room || 'Lobby',
        zone: user.current_zone || 'Main',
        reporter_id: user.id
      });
      fetchDashboardData();
      alert("🚨 Emergency reported! Help is on the way.");
    } catch (err) {
      alert("Failed to report emergency.");
    }
  };

  const submitReport = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/v1/incidents/report', {
        ...reportData,
        reporter_id: user.id
      });
      setShowReportModal(false);
      setReportData({
        title: '',
        incident_type: 'fire',
        severity: 'medium',
        description: '',
        floor: user.current_floor || 1,
        zone: user.current_zone || 'lobby'
      });
      fetchDashboardData();
    } catch (err) {
      alert("Failed to submit report.");
    }
  };

  const getSeverityColor = (sev) => {
    switch (sev) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      default: return '#94a3b8';
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="dashboard-container"
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2.5rem' }}>
        <div>
          <h1>Live Incident Dashboard</h1>
          <p className="text-muted mt-2">Real-time emergency monitoring and coordination</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button className="btn btn-ghost" onClick={() => setShowReportModal(true)} style={{ padding: '1rem 1.5rem' }}>
            <Activity size={20} />
            REPORT INCIDENT
          </button>
          <button className="btn btn-danger pulse-red" onClick={handlePanic} style={{ padding: '1rem 2rem', fontSize: '1rem' }}>
            <AlertOctagon size={24} />
            PANIC BUTTON
          </button>
        </div>
      </div>

      <AnimatePresence>
        {showReportModal && (
          <div className="modal-overlay" style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', 
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
            backdropFilter: 'blur(8px)'
          }}>
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="glass-card" 
              style={{ width: '100%', maxWidth: '500px', padding: '2rem' }}
            >
              <h2 style={{ marginBottom: '1.5rem' }}>Report Incident</h2>
              <form onSubmit={submitReport} className="flex flex-col gap-4">
                <div className="input-group">
                  <label>Title</label>
                  <input 
                    className="input-field" 
                    placeholder="Brief summary..." 
                    value={reportData.title}
                    onChange={e => setReportData({...reportData, title: e.target.value})}
                    required
                  />
                </div>
                <div className="flex gap-4">
                  <div className="input-group flex-1">
                    <label>Type</label>
                    <select 
                      className="input-field"
                      value={reportData.incident_type}
                      onChange={e => setReportData({...reportData, incident_type: e.target.value})}
                    >
                      <option value="fire">Fire</option>
                      <option value="medical">Medical</option>
                      <option value="security">Security</option>
                      <option value="infrastructure">Infrastructure</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                  <div className="input-group flex-1">
                    <label>Severity</label>
                    <select 
                      className="input-field"
                      value={reportData.severity}
                      onChange={e => setReportData({...reportData, severity: e.target.value})}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                      <option value="critical">Critical</option>
                    </select>
                  </div>
                </div>
                <div className="input-group">
                  <label>Description</label>
                  <textarea 
                    className="input-field" 
                    rows="3" 
                    placeholder="What happened?"
                    value={reportData.description}
                    onChange={e => setReportData({...reportData, description: e.target.value})}
                  />
                </div>
                <div className="flex gap-4 mt-4">
                  <button type="button" className="btn btn-ghost flex-1" onClick={() => setShowReportModal(false)}>CANCEL</button>
                  <button type="submit" className="btn btn-primary flex-1">SUBMIT REPORT</button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '2rem' }}>
        {/* Main Feed */}
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity size={20} className="text-primary" />
            <h3 style={{ fontSize: '1.25rem' }}>Active Incidents</h3>
          </div>
          
          <AnimatePresence mode="popLayout">
            {loading ? (
              <div className="glass-card flex items-center justify-center" style={{ height: '200px' }}>
                <Loader2 className="animate-spin text-primary" size={32} />
              </div>
            ) : incidents.length === 0 ? (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass-card"
              >
                <p className="text-muted" style={{ textAlign: 'center' }}>No active incidents reported. All systems clear.</p>
              </motion.div>
            ) : (
              incidents.map((inc) => (
                <motion.div 
                  key={inc.id}
                  layout
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  className="glass-card"
                  style={{ borderLeft: `6px solid ${getSeverityColor(inc.severity)}` }}
                >
                  <div className="flex justify-between items-start">
                    <div className="flex flex-col">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold uppercase tracking-wider" style={{ color: getSeverityColor(inc.severity) }}>
                          {inc.incident_type}
                        </span>
                        <div className="badge">{inc.severity}</div>
                      </div>
                      <h4 className="mt-2" style={{ fontSize: '1.125rem' }}>{inc.title}</h4>
                      <p className="text-sm text-muted mt-2">{inc.description}</p>
                      
                      <div className="flex gap-4 mt-4 text-xs text-muted">
                        <span className="flex items-center gap-1">
                          <MapPin size={12} />
                          Floor {inc.floor}, {inc.zone}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock size={12} />
                          {new Date(inc.reported_at).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                    <div className="badge" style={{ border: 'none', background: 'rgba(255,255,255,0.05)' }}>
                      {inc.status}
                    </div>
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>
        </div>

        {/* Sidebar */}
        <div className="flex flex-col gap-6">
          <div className="glass-card">
            <h3>Quick Stats</h3>
            <div className="mt-6 flex flex-col gap-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted">Active Alerts</span>
                <span className="font-bold text-xl" style={{ color: incidents.length > 0 ? 'var(--danger)' : 'var(--success)' }}>
                  {stats.active}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted">Resolved Today</span>
                <span className="font-bold text-xl text-primary">{stats.resolved}</span>
              </div>
            </div>
          </div>

          <div className="glass-card">
            <h3 className="flex items-center gap-2">
              <Users size={18} className="text-primary" />
              Staff Online
            </h3>
            <div className="mt-4 flex flex-col gap-3">
              {[
                { name: 'John Doe', role: 'Security Manager', online: true },
                { name: 'Sarah Chen', role: 'Chief Medical', online: true },
                { name: 'Mike Ross', role: 'Floor Warden', online: false },
              ].map((staff, i) => (
                <div key={i} className="flex items-center gap-3 py-1">
                  <div className="status-dot" style={{ background: staff.online ? 'var(--success)' : 'var(--border)', boxShadow: staff.online ? '0 0 8px var(--success)' : 'none' }}></div>
                  <div className="flex flex-col">
                    <p className="text-sm font-medium leading-none">{staff.name}</p>
                    <p className="text-xs text-muted mt-1">{staff.role}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Dashboard;
