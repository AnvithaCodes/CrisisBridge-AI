import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { Send, HeadphonesIcon, User as UserIcon, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const CHAT_API_BASE = 'http://localhost:8002';
const WS_BASE = 'ws://localhost:8002/ws/chat';

const LiveChat = () => {
  const { user } = useAuth();
  const [activeSessions, setActiveSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [ws, setWs] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const isGuest = user?.role === 'guest';

  // Fetch active sessions for staff/admin
  useEffect(() => {
    if (!isGuest && !currentSessionId) {
      const fetchSessions = async () => {
        try {
          const res = await axios.get(`${CHAT_API_BASE}/chat/active`);
          setActiveSessions(res.data.sessions || []);
        } catch (err) {
          console.error("Failed to fetch active sessions", err);
        }
      };
      fetchSessions();
      const interval = setInterval(fetchSessions, 5000);
      return () => clearInterval(interval);
    }
  }, [isGuest, currentSessionId]);

  // Scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // WebSocket connection logic
  const connectWebSocket = (sessionId) => {
    if (ws) ws.close();

    const senderId = user.username;
    const senderRole = user.role;
    const websocket = new WebSocket(`${WS_BASE}/${sessionId}?sender_id=${senderId}&sender_role=${senderRole}`);

    websocket.onopen = () => {
      console.log('Connected to chat session:', sessionId);
      setCurrentSessionId(sessionId);
      setLoading(false);
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'history') {
        setMessages(data.messages);
      } else if (['message', 'user_joined', 'user_left'].includes(data.event)) {
        setMessages(prev => [...prev, data]);
      } else if (data.event === 'error') {
        alert(`Error: ${data.message}`);
      }
    };

    websocket.onclose = () => {
      console.log('Disconnected from chat');
      setCurrentSessionId(null);
      setWs(null);
    };

    setWs(websocket);
  };

  const startNewSession = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${CHAT_API_BASE}/chat/start`, { user_id: user.username });
      connectWebSocket(res.data.session_id);
    } catch (err) {
      console.error("Failed to start session", err);
      alert("Failed to start chat session.");
      setLoading(false);
    }
  };

  const leaveSession = () => {
    if (ws) {
      ws.close();
    }
    setCurrentSessionId(null);
    setMessages([]);
  };

  const closeSessionAsAdmin = async (sessionId) => {
    try {
      await axios.patch(`${CHAT_API_BASE}/chat/session/${sessionId}/close`);
      leaveSession();
      alert("Session closed.");
    } catch (err) {
      console.error(err);
      alert("Failed to close session.");
    }
  };

  const deleteSession = async (sessionId) => {
    if (!window.confirm("Are you sure you want to permanently delete this session?")) return;
    try {
      await axios.delete(`${CHAT_API_BASE}/chat/session/${sessionId}`);
      setActiveSessions(prev => prev.filter(s => s.session_id !== sessionId));
    } catch (err) {
      console.error("Failed to delete session", err);
      alert("Failed to delete session.");
    }
  };

  const sendMessage = (e) => {
    e.preventDefault();
    if (!input.trim() || !ws) return;

    ws.send(JSON.stringify({
      sender_id: user.username,
      sender_role: user.role,
      message: input
    }));
    setInput('');
  };

  return (
    <div className="dashboard-container" style={{ maxWidth: '1000px', margin: '0 auto', height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.5rem', flexShrink: 0 }}>
        <div style={{ padding: '1rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '1rem' }}>
          <HeadphonesIcon size={32} color="#3b82f6" />
        </div>
        <div>
          <h1>Live Support</h1>
          <p className="text-muted">Real-time connection to {isGuest ? 'hotel staff' : 'guests in need'}</p>
        </div>
      </div>

      <div className="glass-card" style={{ flex: 1, display: 'flex', overflow: 'hidden', padding: 0 }}>
        {/* Sidebar for Staff */}
        {!isGuest && !currentSessionId && (
          <div style={{ width: '100%', padding: '1.5rem', overflowY: 'auto' }}>
            <h3>Active Guest Sessions</h3>
            {activeSessions.length === 0 ? (
              <p className="text-muted mt-4">No active guest sessions at the moment.</p>
            ) : (
              <div className="mt-4 flex flex-col gap-3">
                {activeSessions.map((session, i) => (
                  <div key={i} className="flex justify-between items-center p-4 rounded-lg" style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border)' }}>
                    <div>
                      <h4 className="text-md font-semibold">Session: <span className="text-muted text-sm font-mono">{session.session_id.split('-')[0]}</span></h4>
                      <p className="text-sm text-muted mt-1">Active Users: <span className="text-white">{session.active_users}</span></p>
                    </div>
                    <div className="flex gap-2">
                      <button className="btn btn-primary btn-sm" onClick={() => connectWebSocket(session.session_id)}>
                        Join Chat
                      </button>
                      {user?.role === 'admin' && (
                        <button className="btn btn-danger btn-sm" onClick={() => deleteSession(session.session_id)}>
                          Delete
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Guest Start Screen */}
        {isGuest && !currentSessionId && (
          <div className="flex flex-col items-center justify-center w-full" style={{ padding: '3rem' }}>
            <HeadphonesIcon size={64} className="text-muted mb-4" />
            <h2 className="mb-2">Need Human Assistance?</h2>
            <p className="text-muted text-center mb-6 max-w-md">
              Connect directly with our 24/7 staff for immediate help. Once connected, a staff member will join the chat shortly.
            </p>
            <button 
              className="btn btn-primary flex items-center gap-2" 
              onClick={startNewSession}
              disabled={loading}
            >
              {loading ? <Loader2 className="animate-spin" /> : <HeadphonesIcon size={20} />}
              Start Support Chat
            </button>
          </div>
        )}

        {/* Active Chat Interface */}
        {currentSessionId && (
          <div className="flex flex-col w-full h-full">
            <div className="p-4 flex justify-between items-center" style={{ borderBottom: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)' }}>
              <div>
                <h3 className="text-sm">Session Connected</h3>
                <p className="text-xs text-muted text-mono">{currentSessionId}</p>
              </div>
              <div className="flex gap-2">
                <button className="btn btn-ghost btn-sm" onClick={leaveSession}>
                  Leave
                </button>
                {user?.role === 'admin' && (
                  <button className="btn btn-danger btn-sm" onClick={() => closeSessionAsAdmin(currentSessionId)}>
                    End Chat
                  </button>
                )}
              </div>
            </div>

            <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-3">
              {messages.map((msg, i) => {
                if (['user_joined', 'user_left'].includes(msg.event)) {
                  return (
                    <div key={i} className="text-center w-full my-2">
                      <span className="text-xs text-muted px-3 py-1 rounded-full" style={{ background: 'rgba(255,255,255,0.05)' }}>
                        {msg.message}
                      </span>
                    </div>
                  );
                }

                const isMe = msg.sender_id === user.username;
                return (
                  <div 
                    key={i} 
                    className="flex gap-2 max-w-[80%]" 
                    style={{ 
                      alignSelf: isMe ? 'flex-end' : 'flex-start',
                      flexDirection: isMe ? 'row-reverse' : 'row' 
                    }}
                  >
                    <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0" style={{ background: isMe ? 'var(--primary)' : 'rgba(255,255,255,0.1)' }}>
                      <UserIcon size={14} color="white" />
                    </div>
                    <div>
                      <div className={`text-xs mb-1 ${isMe ? 'text-right text-blue-200' : 'text-left text-muted font-semibold'}`}>
                        {msg.sender_id} <span className="uppercase opacity-50 ml-1" style={{ fontSize: '0.65rem' }}>({msg.sender_role})</span>
                      </div>
                      <div className="shadow-lg" style={{ 
                        padding: '0.75rem 1rem',
                        borderRadius: isMe ? '1rem 0.25rem 1rem 1rem' : '0.25rem 1rem 1rem 1rem',
                        background: isMe ? 'var(--primary)' : 'rgba(255,255,255,0.08)',
                        color: 'white',
                        fontSize: '0.95rem',
                        lineHeight: '1.4',
                        border: isMe ? 'none' : '1px solid rgba(255,255,255,0.1)'
                      }}>
                        {msg.message}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            <div className="p-4" style={{ borderTop: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)' }}>
              <form onSubmit={sendMessage} className="flex gap-2">
                <input 
                  type="text" 
                  className="input-field flex-1" 
                  placeholder="Type your message..." 
                  value={input}
                  onChange={e => setInput(e.target.value)}
                />
                <button type="submit" className="btn btn-primary" style={{ padding: '0 1.5rem' }}>
                  <Send size={18} />
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveChat;
