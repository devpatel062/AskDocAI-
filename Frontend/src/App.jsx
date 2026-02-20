import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, User, Bot, Loader2, Stethoscope, Sparkles } from 'lucide-react';

function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]); 
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

    const currentQuery = query;
    setQuery('');
    setIsLoading(true);

    // Optimistically add user message
    setMessages(prev => [...prev, { role: 'user', content: currentQuery }]);

    try {
      const res = await axios.post('http://localhost:8000/api/ask', {
        query: currentQuery,
        history: history,
        token: 'secure_token_123'
      });

      const answer = res.data.response;
      
      setMessages(prev => [...prev, { role: 'bot', content: answer }]);
      setHistory(prev => [...prev, currentQuery]);
    } catch (error) {
      console.error("Error fetching response:", error);
      setMessages(prev => [...prev, { role: 'bot', content: "Sorry, something went wrong. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-50 font-sans text-slate-900">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-center shadow-sm sticky top-0 z-10">
        <div className="flex items-center gap-2 text-blue-600">
          <Stethoscope className="w-8 h-8" />
          <h1 className="text-2xl font-bold tracking-tight text-slate-800">AskDocAI</h1>
        </div>
      </header>

      {/* Chat Area */}
      <main className="flex-1 overflow-y-auto p-4 md:p-6 scroll-smooth">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.length === 0 ? (
             <div className="text-center mt-20 opacity-70">
                <div className="bg-blue-100 p-4 rounded-full w-20 h-20 mx-auto flex items-center justify-center mb-4">
                  <Sparkles className="w-10 h-10 text-blue-600" />
                </div>
                <h2 className="text-xl font-semibold text-slate-700">How can I help you today?</h2>
                <p className="text-slate-500 mt-2">Ask any medical question to get started.</p>
             </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`flex gap-4 ${
                  msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-emerald-500 text-white'
                  }`}
                >
                  {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>

                <div
                  className={`max-w-[80%] rounded-2xl px-5 py-3 shadow-sm border ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white border-blue-600 rounded-tr-none'
                      : 'bg-white text-slate-800 border-slate-200 rounded-tl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed">
                    {msg.content}
                  </p>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex gap-4 items-start animate-fade-in">
               <div className="w-10 h-10 rounded-full bg-emerald-500 text-white flex items-center justify-center flex-shrink-0 shadow-sm">
                  <Bot size={20} />
               </div>
               <div className="bg-white border border-slate-200 rounded-2xl rounded-tl-none px-5 py-4 shadow-sm flex items-center gap-2">
                 <Loader2 className="w-5 h-5 text-slate-400 animate-spin" />
                 <span className="text-slate-500 text-sm">Thinking...</span>
               </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Area */}
      <footer className="bg-white border-t border-slate-200 p-4 sticky bottom-0 z-10">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleAsk} className="relative flex items-center">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a medical question..."
              className="w-full pl-5 pr-14 py-4 rounded-xl border border-slate-300 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all shadow-sm placeholder:text-slate-400 text-slate-700"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={!query.trim() || isLoading}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
            >
              <Send size={20} />
            </button>
          </form>
          <p className="text-center text-xs text-slate-400 mt-2">
            AI can make mistakes. Please consult a professional for medical advice.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;

