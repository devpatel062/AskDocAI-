import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [history, setHistory] = useState([]);

  const handleAsk = async () => {
    const res = await axios.post('http://localhost:8000/api/ask', {
      query,
      history,
      token: 'secure_token_123'
    });
    setResponse(res.data.response);
    setHistory([...history, query]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white flex items-center justify-center px-4">
  <div className="bg-white p-10 rounded-3xl shadow-xl max-w-3xl w-full font-sans border border-gray-200">
    <h1 className="text-4xl font-bold text-blue-800 mb-8 text-center tracking-tight">
      🩺 AskDocAI – Your Medical Assistant
    </h1>

    <textarea
      value={query}
      onChange={e => setQuery(e.target.value)}
      rows={8}
      className="w-full p-6 border border-gray-300 rounded-2xl text-lg text-gray-800 shadow focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-300"
      placeholder="Ask any medical question, e.g., 'How does insulin affect blood sugar?'"
    />

    <div className="flex justify-center mt-6">
      <button
        onClick={handleAsk}
        className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-10 rounded-full transition-all duration-300 transform hover:scale-105 hover:shadow-lg active:scale-95 active:shadow-sm"
      >
        ✨ Ask Now
      </button>
    </div>

    {response && (
      <div className="mt-8 p-6 bg-blue-50 border border-blue-200 rounded-xl shadow-sm">
        <h2 className="font-semibold text-gray-700 mb-2">Answer:</h2>
        <p className="text-gray-900 whitespace-pre-wrap leading-relaxed">{response}</p>
      </div>
    )}
  </div>
</div>

  );
}

export default App;
