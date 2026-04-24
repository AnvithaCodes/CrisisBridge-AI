import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Terminal, Search, Filter, Loader2, Database, Shield } from 'lucide-react';
import { motion } from 'framer-motion';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  const fetchLogs = async () => {
    try {
      const response = await axios.get('/api/v1/logs/queries');
      setLogs(response.data); // Backend returns the list directly
    } catch (err) {
      console.error('Failed to fetch logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter(log => 
    log.original_query?.toLowerCase().includes(filter.toLowerCase()) ||
    log.answer?.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="logs-container"
      style={{ maxWidth: '1200px', margin: '0 auto' }}
    >
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h1>System Activity Logs</h1>
          <p className="text-muted mt-2">Audit trail of AI interactions and system events</p>
        </div>
        <div className="flex gap-2">
          <div className="input-group" style={{ position: 'relative' }}>
            <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', opacity: 0.5 }} />
            <input 
              type="text" 
              className="input-field" 
              placeholder="Filter logs..." 
              style={{ paddingLeft: '2.5rem', width: '300px' }}
              value={filter}
              onChange={e => setFilter(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="glass-card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border)', background: 'rgba(255,255,255,0.02)', display: 'grid', gridTemplateColumns: '120px 1fr 1fr 100px', gap: '1rem', fontSize: '0.75rem', fontWeight: '800', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
          <span>Timestamp</span>
          <span>User Query</span>
          <span>AI Response</span>
          <span>Status</span>
        </div>

        <div className="flex flex-col" style={{ maxHeight: 'calc(100vh - 350px)', overflowY: 'auto' }}>
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="animate-spin text-primary" size={32} />
            </div>
          ) : filteredLogs.length === 0 ? (
            <div className="py-20 text-center text-muted">
              <Database size={48} style={{ opacity: 0.1, margin: '0 auto 1rem' }} />
              <p>No activity logs found</p>
            </div>
          ) : (
            filteredLogs.map((log) => (
              <div 
                key={log.id} 
                className="log-row"
                style={{ 
                  display: 'grid', gridTemplateColumns: '120px 1fr 1fr 100px', gap: '1rem', 
                  padding: '1.25rem 1.5rem', borderBottom: '1px solid var(--border)',
                  fontSize: '0.875rem'
                }}
              >
                <span className="text-xs text-muted">
                  {new Date(log.created_at).toLocaleTimeString()}<br/>
                  {new Date(log.created_at).toLocaleDateString()}
                </span>
                <span style={{ color: 'var(--text-main)', fontWeight: '500' }}>{log.original_query}</span>
                <span className="text-muted" style={{ 
                  display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', 
                  overflow: 'hidden', fontSize: '0.8125rem' 
                }}>
                  {log.answer}
                </span>
                <div className="flex items-center gap-2">
                  {log.cache_status === 'hit' ? (
                    <div className="badge" style={{ color: 'var(--success)', borderColor: 'var(--success-glow)' }}>CACHED</div>
                  ) : (
                    <div className="badge" style={{ opacity: 0.5 }}>LIVE</div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      
      <div className="mt-8 grid grid-cols-3 gap-6">
        <div className="glass-card flex items-center gap-4">
          <div className="p-3 rounded-lg" style={{ background: 'rgba(59, 130, 246, 0.1)', color: 'var(--primary)' }}>
            <Terminal size={24} />
          </div>
          <div>
            <h4 style={{ fontSize: '0.875rem' }}>Total Interactions</h4>
            <p className="text-xl font-bold">{logs.length}</p>
          </div>
        </div>
        <div className="glass-card flex items-center gap-4">
          <div className="p-3 rounded-lg" style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' }}>
            <Database size={24} />
          </div>
          <div>
            <h4 style={{ fontSize: '0.875rem' }}>Cache Hit Rate</h4>
            <p className="text-xl font-bold">
              {logs.length > 0 ? Math.round((logs.filter(l => l.cache_status === 'hit').length / logs.length) * 100) : 0}%
            </p>
          </div>
        </div>
        <div className="glass-card flex items-center gap-4">
          <div className="p-3 rounded-lg" style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)' }}>
            <Shield size={24} />
          </div>
          <div>
            <h4 style={{ fontSize: '0.875rem' }}>System Integrity</h4>
            <p className="text-xl font-bold">Optimal</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default Logs;
