import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users as UsersIcon, ShieldAlert, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user: currentUser } = useAuth();

  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/v1/users');
      setUsers(response.data);
    } catch (err) {
      console.error('Failed to fetch users', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId, newRole) => {
    try {
      await axios.patch(`/api/v1/users/${userId}/role`, { role: newRole });
      // Update local state to reflect change without full reload
      setUsers(users.map(u => u.id === userId ? { ...u, role: newRole } : u));
    } catch (err) {
      alert('Failed to update role. Only admins can do this.');
    }
  };

  if (currentUser?.role !== 'admin') {
    return (
      <div className="flex items-center justify-center" style={{ minHeight: '50vh' }}>
        <div className="glass-card text-center" style={{ padding: '3rem' }}>
          <ShieldAlert size={48} className="text-danger mx-auto mb-4" />
          <h2>Access Denied</h2>
          <p className="text-muted mt-2">Only administrators can manage users.</p>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="dashboard-container"
      style={{ maxWidth: '1000px', margin: '0 auto' }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ padding: '1rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '1rem' }}>
          <UsersIcon size={32} color="#3b82f6" />
        </div>
        <div>
          <h1>User Management</h1>
          <p className="text-muted">Manage roles and permissions for all personnel</p>
        </div>
      </div>

      <div className="glass-card" style={{ padding: '0' }}>
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="animate-spin text-primary" size={32} />
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ padding: '1.5rem 1rem', color: 'var(--text-muted)' }}>Name</th>
                <th style={{ padding: '1.5rem 1rem', color: 'var(--text-muted)' }}>Email</th>
                <th style={{ padding: '1.5rem 1rem', color: 'var(--text-muted)' }}>Username</th>
                <th style={{ padding: '1.5rem 1rem', color: 'var(--text-muted)' }}>Role</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '1rem' }} className="font-bold">{u.full_name || 'N/A'}</td>
                  <td style={{ padding: '1rem' }} className="text-muted">{u.email}</td>
                  <td style={{ padding: '1rem' }}>@{u.username}</td>
                  <td style={{ padding: '1rem' }}>
                    <select 
                      className="input-field"
                      style={{ padding: '0.5rem', width: 'auto', minWidth: '120px' }}
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      disabled={u.id === currentUser.id} // Cannot change own role
                    >
                      <option value="guest">Guest</option>
                      <option value="staff">Staff</option>
                      <option value="admin">Admin</option>
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </motion.div>
  );
};

export default Users;
