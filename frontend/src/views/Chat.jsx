import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Zap, Loader2, Square } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

const Chat = () => {
  const [messages, setMessages] = useState([
    { id: 1, role: 'ai', content: 'Hello! I am your CrisisBridge Assistant. How can I help you ensure safety today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [lastQueryLogId, setLastQueryLogId] = useState(null);
  const scrollRef = useRef(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setLoading(false);
      setMessages(prev => [...prev, { 
        id: Date.now(), 
        role: 'ai', 
        content: '_Request cancelled by user._' 
      }]);
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = { id: Date.now(), role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    const userQuery = input;
    setInput('');
    setLoading(true);

    // Initialize AbortController
    abortControllerRef.current = new AbortController();

    try {
      const response = await axios.post('/api/v1/query', 
        { query: userQuery },
        { signal: abortControllerRef.current.signal }
      );
      const aiMsg = {
        id: Date.now() + 1,
        role: 'ai',
        content: response.data.answer,
        isCached: response.data.cache_status === 'hit',
        sources: response.data.sources
      };
      setMessages(prev => [...prev, aiMsg]);
      setLastQueryLogId(response.data.query_log_id);
    } catch (err) {
      if (axios.isCancel(err)) {
        console.log('Request cancelled');
      } else {
        setMessages(prev => [...prev, { id: Date.now() + 1, role: 'ai', content: 'Sorry, I encountered an error. Please try again.' }]);
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  return (
    <div className="flex flex-col" style={{ maxWidth: '900px', margin: '0 auto', height: 'calc(100vh - 180px)' }}>
      <div className="mb-6 flex justify-between items-end">
        <div>
          <h1>AI Crisis Assistant <span style={{ fontSize: '0.75rem', opacity: 0.5, verticalAlign: 'middle' }}>v1.2-live</span></h1>
          <p className="text-muted mt-2">Expert emergency guidance powered by RAG</p>
        </div>
      </div>

      <div 
        ref={scrollRef}
        className="glass-card" 
        style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '1.5rem', padding: '1.5rem' }}
      >
        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                alignSelf: msg.role === 'ai' ? 'flex-start' : 'flex-end',
                maxWidth: '85%',
                display: 'flex',
                gap: '1rem',
                flexDirection: msg.role === 'ai' ? 'row' : 'row-reverse'
              }}
            >
              <div style={{ 
                width: '36px', height: '36px', borderRadius: '50%', 
                background: msg.role === 'ai' ? 'linear-gradient(135deg, var(--primary), #60a5fa)' : 'rgba(255,255,255,0.1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                boxShadow: msg.role === 'ai' ? '0 4px 12px var(--primary-glow)' : 'none'
              }}>
                {msg.role === 'ai' ? <Bot size={20} color="white" /> : <User size={20} color="white" />}
              </div>
              
              <div 
                className="chat-bubble"
                style={{
                  background: msg.role === 'ai' ? 'rgba(255,255,255,0.03)' : 'var(--primary)',
                  color: 'white',
                  border: msg.role === 'ai' ? '1px solid var(--border)' : 'none'
                }}
              >
                {msg.role === 'ai' ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
                
                {msg.isCached && (
                  <div className="flex items-center gap-1 text-xs mt-3" style={{ color: 'var(--success)', fontWeight: '600' }}>
                    <Zap size={10} fill="currentColor" />
                    Instant Response
                  </div>
                )}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 text-xs text-muted" style={{ borderTop: '1px solid var(--border)' }}>
                    Sources: {msg.sources.join(', ')}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {loading && (
          <div className="flex items-center gap-3 text-muted ml-12">
            <Loader2 className="animate-spin" size={16} />
            <span className="text-sm">Assistant is thinking...</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSend} style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
        <input 
          type="text" 
          className="input-field" 
          placeholder={loading ? "Processing your request..." : "Ask a question (e.g., 'What are the fire safety steps?')"}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          required
          disabled={loading}
          style={{ height: '3.5rem', cursor: loading ? 'not-allowed' : 'text' }}
        />
        
        {loading ? (
          <button 
            type="button" 
            className="btn btn-danger" 
            onClick={handleStop}
            style={{ width: '3.5rem', height: '3.5rem', padding: 0, flexShrink: 0, borderRadius: '0.75rem' }}
            title="Stop Response"
          >
            <Square size={20} fill="white" />
          </button>
        ) : (
          <button type="submit" className="btn btn-primary" style={{ width: '3.5rem', height: '3.5rem', padding: 0, flexShrink: 0 }}>
            <Send size={20} />
          </button>
        )}
      </form>
    </div>
  );
};

export default Chat;
