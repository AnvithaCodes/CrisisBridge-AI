import React, { useState } from 'react';
import axios from 'axios';
import { ShieldCheck, Search, AlertTriangle, ShieldAlert, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Safety = () => {
  const [floor, setFloor] = useState(3);
  const [zone, setZone] = useState('east_wing');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCheck = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('/api/v1/safety/check', { floor, zone });
      setResult(response.data);
    } catch (err) {
      alert("Safety check failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getStatusVisuals = (level) => {
    switch (level) {
      case 'safe':
        return {
          color: '#10b981',
          icon: <ShieldCheck size={48} />,
          bg: 'rgba(16, 185, 129, 0.1)',
          label: 'SAFE STATUS'
        };
      case 'warning':
        return {
          color: '#f59e0b',
          icon: <AlertTriangle size={48} />,
          bg: 'rgba(245, 158, 11, 0.1)',
          label: 'CAUTION ADVISED'
        };
      case 'evacuate':
        return {
          color: '#ef4444',
          icon: <ShieldAlert size={48} />,
          bg: 'rgba(239, 68, 68, 0.1)',
          label: 'IMMEDIATE EVACUATION'
        };
      default:
        return { color: '#94a3b8', icon: <Search size={48} />, bg: 'rgba(255,255,255,0.05)', label: 'UNKNOWN' };
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      style={{ maxWidth: '600px', margin: '0 auto' }}
    >
      <div className="mb-8">
        <h1>Safety Status Check</h1>
        <p className="text-muted mt-2">Verify if your current location is affected by any active incidents.</p>
      </div>

      <div className="glass-card">
        <form onSubmit={handleCheck}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
            <div className="input-group">
              <label>Your Floor</label>
              <input 
                type="number" 
                className="input-field" 
                value={floor}
                onChange={(e) => setFloor(parseInt(e.target.value))}
                required
              />
            </div>
            <div className="input-group">
              <label>Zone / Wing</label>
              <select 
                className="input-field"
                value={zone}
                onChange={(e) => setZone(e.target.value)}
              >
                <option value="lobby">Lobby</option>
                <option value="east_wing">East Wing</option>
                <option value="west_wing">West Wing</option>
                <option value="restaurant">Restaurant</option>
              </select>
            </div>
          </div>
          <button type="submit" className="btn btn-primary w-full" disabled={loading}>
            {loading ? <Loader2 className="animate-spin" size={20} /> : <><Search size={20} /> Check Safety Status</>}
          </button>
        </form>
      </div>

      <AnimatePresence>
        {result && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-8"
          >
            {(() => {
              const visuals = getStatusVisuals(result.safety_level);
              return (
                <div 
                  className="glass-card" 
                  style={{ 
                    border: `2px solid ${visuals.color}`,
                    background: visuals.bg,
                    textAlign: 'center',
                    padding: '3rem 2rem'
                  }}
                >
                  <div style={{ color: visuals.color, marginBottom: '1.5rem', display: 'inline-block' }}>
                    {visuals.icon}
                  </div>
                  <h2 style={{ color: visuals.color, marginBottom: '1rem' }}>{visuals.label}</h2>
                  <h3 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>{result.message}</h3>
                  <p className="text-muted">{result.recommended_action}</p>

                  {result.nearby_incidents.length > 0 && (
                    <div className="mt-8 pt-6" style={{ borderTop: '1px solid var(--border)' }}>
                      <p className="text-sm font-bold uppercase mb-4" style={{ color: visuals.color }}>Active Incidents in your vicinity:</p>
                      <div className="flex flex-col gap-2">
                        {result.nearby_incidents.map((inc, i) => (
                          <div key={i} className="text-sm bg-white/5 p-3 rounded-lg flex justify-between items-center">
                            <span>{inc.title}</span>
                            <span className="text-xs uppercase font-bold" style={{ color: visuals.color }}>{inc.severity}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })()}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default Safety;
