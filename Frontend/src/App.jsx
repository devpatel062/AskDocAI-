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
    <div className="p-6 max-w-2xl mx-auto font-sans">
      <h1 className="text-2xl font-bold mb-4">AskDocAI – Medical Assistant</h1>
      <textarea
        value={query}
        onChange={e => setQuery(e.target.value)}
        className="border rounded w-full p-3 text-lg mb-2"
        placeholder="Type your health-related question..."
      />
      <button
        onClick={handleAsk}
        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
      >
        Ask
      </button>
      <div className="mt-4 p-4 bg-gray-50 border rounded shadow">
        <p className="text-gray-800 whitespace-pre-wrap">{response}</p>
      </div>
    </div>
  );
}

export default App;
