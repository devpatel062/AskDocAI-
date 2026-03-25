# AskDocAI - Complete Project Guide for New Forks 🏥

Welcome! This guide explains the **entire AskDocAI project**, how it works, what each file does, and how to set it up from scratch.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [End-to-End Data Flow](#end-to-end-data-flow)
5. [Detailed File Explanations](#detailed-file-explanations)
6. [Step-by-Step Setup Guide](#step-by-step-setup-guide)
7. [Common Tasks & How-Tos](#common-tasks--how-tos)

---

## 🎯 Project Overview

**AskDocAI** is an AI-powered Question-Answering system designed specifically for medical documents. It uses a **Retrieval-Augmented Generation (RAG)** pipeline to:

1. **Retrieve** relevant medical information from a vector database
2. **Generate** accurate, contextual answers using an LLM
3. **Cite sources** from the retrieved documents

### Key Features

✅ **RAG Architecture** - Combines vector search with generative AI to reduce hallucinations  
✅ **Source Citations** - Provides metadata about which documents were used  
✅ **Conversational Ready** - Maintains chat history for follow-up questions  
✅ **Medical Domain** - Optimized for MedQuAD and medical text  
✅ **Secure API** - Token-based authentication  

---

## 🛠️ Technology Stack

### Frontend
- **React 19** - UI framework with hooks for state management
- **Vite** - Ultra-fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS for styling
- **Axios** - HTTP client for API calls
- **Lucide React** - Beautiful, consistent icons

### Backend
- **FastAPI** - Modern, fast Python web framework
- **LangChain** - Orchestration framework for AI chains
- **FAISS** - Facebook's vector similarity search library
- **Sentence Transformers** - `all-MiniLM-L6-v2` for embeddings
- **Hugging Face** - `google/flan-t5-large` for answer generation

---

## 📂 Project Structure Explained

```
AskDocAI/
├── ARCHITECTURE.md                    # High-level architecture diagrams
├── README.md                          # Quick start guide
├── COMPLETE_PROJECT_GUIDE.md          # THIS FILE - comprehensive explanation
├── requirements.txt                   # Python dependencies (empty - install manually)
│
├── backend/                           # Backend API Server
│   ├── main.py                        # FastAPI entry point, routes, CORS setup
│   ├── auth/
│   │   └── auth.py                    # Token verification (dummy implementation)
│   └── rag_pipeline/
│       └── rag.py                     # RAG logic, LLM, vector store, embeddings
│
├── Frontend/                          # React SPA (Single Page Application)
│   ├── src/
│   │   ├── main.jsx                   # React app entry point
│   │   ├── App.jsx                    # Main component (chat interface)
│   │   ├── App.css                    # Global component styles
│   │   ├── index.css                  # Global CSS
│   │   └── assets/                    # Images, fonts, etc.
│   ├── public/                        # Static files served directly
│   ├── package.json                   # Frontend dependencies & scripts
│   ├── vite.config.js                 # Vite build configuration
│   ├── tailwind.config.js             # Tailwind CSS configuration
│   ├── postcss.config.js              # PostCSS plugins (Tailwind)
│   └── eslint.config.js               # Code linting rules
│
├── scripts/                           # Utility scripts (one-time setup)
│   ├── create_faiss_index.py          # Creates vector database from JSON
│   └── import_medquad.py              # Converts MedQuAD XML to JSON format
│
├── data/                              # Data directory (initially empty)
│   └── (medical_data.json created here by import script)
│
└── vector_store_pubmed/               # FAISS vector database
    ├── index.faiss                    # Binary vector index
    └── (other FAISS metadata files)
```

---

## 🔄 End-to-End Data Flow

### 1. **Data Preparation Phase** (One-time setup)

```
MedQuAD XML Files
       ↓
   import_medquad.py (parses XML)
       ↓
data/medical_data.json (Question-Answer pairs as JSON)
       ↓
   create_faiss_index.py (embeds & indexes)
       ↓
vector_store_pubmed/ (FAISS vector database)
```

**What happens:**
- XML files are parsed to extract `<question>` and `<answer>` pairs
- Data is converted to JSON with metadata (source, id, timestamp)
- Each Q&A pair is converted to text: `"Question: X\nAnswer: Y"`
- Text is embedded using `all-MiniLM-L6-v2` model
- Embeddings are indexed in FAISS for fast similarity search

### 2. **Request-Response Flow** (Happens on each user query)

```
User Types Question in Frontend
       ↓ (React state update)
User Clicks "Send" Button
       ↓ (POST /api/ask)
┌─────────────────────────────────────┐
│      BACKEND - FastAPI Server       │
│  1. verify_token() - Check auth     │
│  2. ask_question() - RAG Pipeline   │
│     a. Embed user query             │
│     b. Search FAISS for top-3 docs  │
│     c. Send context to LLM          │
│     d. Generate answer              │
│     e. Extract citations            │
│  3. Return response + citations     │
└─────────────────────────────────────┘
       ↓ (JSON response)
Frontend Receives Response
       ↓ (React state update)
Display Answer + Citations to User
```

**Example Request:**
```json
{
  "query": "What are symptoms of diabetes?",
  "history": [],
  "token": "secure_token_123"
}
```

**Example Response:**
```json
{
  "response": "Diabetes symptoms include increased thirst, frequent urination, and fatigue...",
  "citations": [
    {
      "source": "medquad:diabetes.xml",
      "question": "What are the main symptoms of diabetes?",
      "id": "doc-123",
      "updated_at": "2024-01-15"
    }
  ]
}
```

---

## 📄 Detailed File Explanations

### **Backend Files**

#### `backend/main.py` (FastAPI Entry Point)

**Purpose:** REST API server that connects frontend to RAG logic

```python
# Key parts:
1. FastAPI() - Creates the app
2. CORSMiddleware - Allows frontend (different port) to call backend
3. QueryRequest Model - Validates incoming requests
4. /api/ask endpoint - POST route that:
   - Takes user query, chat history, and token
   - Calls verify_token() for authentication
   - Calls ask_question() from RAG pipeline
   - Returns answer and citations
```

**When it runs:**
```bash
uvicorn backend.main:app --reload
# Starts server at http://127.0.0.1:8000
```

---

#### `backend/auth/auth.py` (Authentication)

**Purpose:** Verify user tokens (simple implementation)

```python
def verify_token(token: str) -> bool:
    # Current: Dummy check (token == "secure_token_123")
    # Production: Should use JWT or similar
    return token == "secure_token_123"
```

**How to upgrade for production:**
1. Use **JWT tokens** instead of hardcoded strings
2. Sign tokens with a secret key
3. Verify signature and expiration
4. Consider libraries like `python-jose`

---

#### `backend/rag_pipeline/rag.py` (The Core Logic)

**Purpose:** Contains the entire RAG pipeline

```python
# Step 1: Load Embedding Model
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
# Converts text to 384-dimensional vectors
# (~22MB download on first use)

# Step 2: Load Vector Database
db = FAISS.load_local("./vector_store_pubmed", embeddings=embedding_model)
# Loads indexed document embeddings for fast search

# Step 3: Load LLM (Language Model)
llm = HuggingFacePipeline.from_model_id(
    model_id="google/flan-t5-large",
    task="text2text-generation",
    model_kwargs={"temperature": 0.3, "max_length": 512},
    device=0 if torch.cuda.is_available() else -1  # Use GPU if available
)
# T5 model good for question-answering tasks (~750MB)

# Step 4: Create Prompt
template = """Use the following pieces of context...
Context: {context}
Question: {question}
Helpful Answer:"""

# Step 5: Create Chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=db.as_retriever(search_kwargs={"k": 3}),  # Retrieve top-3 docs
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT}
)

# Step 6: Process Query
def ask_question(query: str, history: list[str]) -> dict:
    # Run the chain with user question
    result = qa_chain({"question": query, "chat_history": []})
    
    # Extract citations from source documents
    citations = []
    for doc in result.get("source_documents", []):
        citations.append({
            "source": doc.metadata.get("source"),
            "question": doc.metadata.get("question"),
            "id": doc.metadata.get("id"),
            "updated_at": doc.metadata.get("updated_at")
        })
    
    return {
        "answer": result.get("answer"),
        "citations": citations
    }
```

**Flow inside `ask_question():`**

1. **Embed Query** - Convert user's question to a 384-dim vector
2. **Vector Search** - Find 3 most similar documents in FAISS
3. **Prepare Context** - Combine the 3 retrieved documents
4. **Prompt LLM** - Send context + question to T5 model
5. **Generate Answer** - T5 generates answer based on context
6. **Extract Metadata** - Collect source info from retrieved docs
7. **Return Result** - Answer + citations back to frontend

---

### **Frontend Files**

#### `Frontend/src/main.jsx` (React Entry Point)

**Purpose:** Mounts React app to the DOM

```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

**When it runs:** Loads `/Frontend/index.html` which contains `<div id="root"></div>` and script reference

---

#### `Frontend/src/App.jsx` (Main Chat Interface)

**Purpose:** The entire user interface component

```javascript
// State Management:
const [query, setQuery] = useState('');              // Current user input
const [messages, setMessages] = useState([]);        // Chat history display
const [history, setHistory] = useState([]);          // Query history for API
const [isLoading, setIsLoading] = useState(false);   // Loading indicator

// Key Functions:
handleAsk(e) {
  // 1. Get user's query
  // 2. Add to messages (optimistic update)
  // 3. POST to /api/ask with query + token
  // 4. Add bot response to messages
  // 5. Add query to history
  // 6. Handle errors
}

scrollToBottom() {
  // Auto-scroll to latest message (UX)
}

// UI Structure:
Header with "AskDocAI" title and icon
Main chat area with message bubbles
  - User messages (blue, right-aligned)
  - Bot responses (green, left-aligned)
  - Icons for user/bot distinction
Input form at bottom
  - Text input field
  - Send button
  - Loading spinner
```

**Message Format:**
```javascript
{
  role: 'user' or 'bot',
  content: 'actual message text'
}
```

---

#### `Frontend/src/App.css` & `Frontend/src/index.css`

**Purpose:** Component-specific and global styles

- Uses **Tailwind CSS** classes (defined in JSX)
- Custom CSS for animations and special effects
- Responsive design breakpoints

---

#### `Frontend/package.json`

**Purpose:** Define dependencies and build scripts

```json
{
  "scripts": {
    "dev": "vite",              // npm run dev - starts dev server
    "build": "vite build",      // npm run build - production build
    "lint": "eslint .",         // npm run lint - check code quality
    "preview": "vite preview"   // npm run preview - test production build
  },
  "dependencies": {
    "react": "^19.1.0",         // UI framework
    "axios": "^1.13.5",         // HTTP client
    "lucide-react": "^0.574.0", // React icon library
    "react-dom": "^19.1.0"      // React DOM rendering
  }
}
```

---

#### `Frontend/vite.config.js`

**Purpose:** Configure Vite build tool

```javascript
// Tells Vite:
// - Use React plugin for JSX transformation
// - Dev server settings
// - Build output format
```

#### `Frontend/tailwind.config.js`

**Purpose:** Customize Tailwind CSS

```javascript
// Defines:
// - Color schemes
// - Typography settings
// - Custom components
// - Theme extensions
```

#### `Frontend/postcss.config.js`

**Purpose:** PostCSS configuration for CSS processing

```javascript
// Enables Tailwind CSS processing through PostCSS
```

---

### **Scripts**

#### `scripts/import_medquad.py` (Data Importer)

**Purpose:** Convert MedQuAD XML format to our JSON format

```python
# Input: MedQuAD XML files (hierarchical medical Q&A)
# Process:
#   1. Parse XML with ElementTree
#   2. Extract <question> and <answer> elements
#   3. Find source URL or filename
#   4. Deduplicate Q&A pairs
#   5. Build JSON structure with metadata

# Output: data/medical_data.json
# Format:
[
  {
    "question": "What is diabetes?",
    "answer": "Diabetes is a chronic condition...",
    "source": "medquad:diabetes.xml",
    "updated_at": "unknown"
  },
  ...
]

# Usage:
python scripts/import_medquad.py \
  --input ./MedQuAD-master \
  --output data/medical_data.json \
  --limit 1000  # Optional: limit records
```

---

#### `scripts/create_faiss_index.py` (Vector Indexing)

**Purpose:** Create FAISS vector database from JSON data

```python
# Input: data/medical_data.json
# Process:
#   1. Load JSON file
#   2. Convert each Q&A to text: "Question: X\nAnswer: Y"
#   3. Embed text using SentenceTransformer
#   4. Create FAISS index from embeddings
#   5. Save to vector_store_pubmed/

# Output: vector_store_pubmed/
# Contains:
#   - index.faiss (binary vector index)
#   - index.pkl (serialized metadata)
#   - docstore.pkl (document storage)
#   - etc.

# Usage:
python scripts/create_faiss_index.py

# Auto-generates sample data if medical_data.json not found
```

---

## 🚀 Step-by-Step Setup Guide

### **Prerequisites**

- Python 3.8+
- Node.js 16+ and npm
- ~2GB disk space (for models)
- 4GB+ RAM recommended
- Optional: GPU (CUDA) for faster inference

---

### **Backend Setup**

#### Step 1: Create Python Virtual Environment

```bash
cd /Users/devpatel062/Documents/clone/AskDocAI
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### Step 2: Install Python Dependencies

Since `requirements.txt` is empty, install manually:

```bash
pip install fastapi uvicorn
pip install langchain langchain-community
pip install sentence-transformers torch
pip install faiss-cpu  # Use faiss-gpu if you have NVIDIA GPU
```

Or create a `requirements.txt`:
```
fastapi==0.104.1
uvicorn==0.24.0
langchain==0.1.0
langchain-community==0.0.10
sentence-transformers==2.2.2
torch==2.0.0
faiss-cpu==1.7.4
```

#### Step 3: Prepare Data

**Option A: Use sample data (test only)**
```bash
python scripts/create_faiss_index.py
# Creates sample vector store automatically
```

**Option B: Import MedQuAD**
```bash
# 1. Download MedQuAD from GitHub:
git clone https://github.com/abachaa/MedQuAD.git

# 2. Convert to JSON:
python scripts/import_medquad.py --input ./MedQuAD --output data/medical_data.json

# 3. Create vector index:
python scripts/create_faiss_index.py
```

#### Step 4: Start Backend Server

```bash
uvicorn backend.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

Test it:
```bash
# In another terminal:
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is diabetes?",
    "history": [],
    "token": "secure_token_123"
  }'
```

---

### **Frontend Setup**

#### Step 1: Install Node Dependencies

```bash
cd Frontend
npm install
```

#### Step 2: Start Dev Server

```bash
npm run dev
```

Expected output:
```
VITE v6.3.5  ready in 123 ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

#### Step 3: Open in Browser

Navigate to `http://localhost:5173/`

You should see:
- AskDocAI header with stethoscope icon
- Welcome message
- Input field to ask questions

---

### **Complete Setup Checklist**

- [ ] Created `.venv` virtual environment
- [ ] Installed Python dependencies
- [ ] Created/indexed medical data
- [ ] Backend running at `http://localhost:8000`
- [ ] Frontend running at `http://localhost:5173`
- [ ] Can send test query without errors
- [ ] Response appears in chat and citations show

---

## 🎯 Common Tasks & How-Tos

### **Task 1: Add Your Own Medical Documents**

1. Create JSON file in `data/` with structure:
```json
[
  {
    "question": "What is X?",
    "answer": "X is...",
    "source": "your_source.pdf",
    "updated_at": "2024-03-25"
  }
]
```

2. Rebuild index:
```bash
python scripts/create_faiss_index.py
```

3. Restart backend server

---

### **Task 2: Customize the LLM Model**

Edit `backend/rag_pipeline/rag.py`:

```python
# Change model:
llm = HuggingFacePipeline.from_model_id(
    model_id="mistral-7b",  # Different model
    task="text2text-generation",
    model_kwargs={"temperature": 0.3, "max_length": 512},
    device=0 if torch.cuda.is_available() else -1,
)
```

Available options:
- `google/flan-t5-large` (default, ~750MB)
- `google/flan-t5-xl` (larger, better quality)
- `mistral-7b` (requires more VRAM)
- `gpt2` (smaller, faster)

---

### **Task 3: Improve Token Authentication**

Update `backend/auth/auth.py`:

```python
from datetime import datetime, timedelta
import jwt

SECRET_KEY = "your-secret-key-here"

def create_token(user_id: str):
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> bool:
    try:
        jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return True
    except:
        return False
```

Install JWT library:
```bash
pip install python-jose[cryptography]
```

---

### **Task 4: Deploy to Production**

**Backend (using Gunicorn):**
```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -b 0.0.0.0:8000
```

**Frontend (build for production):**
```bash
cd Frontend
npm run build
# Creates optimized build in dist/
```

**Deployment options:**
- AWS EC2, ECS
- Heroku
- DigitalOcean
- Railway
- Vercel (frontend only)

---

### **Task 5: Monitor Performance**

Add logging to `backend/main.py`:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/ask")
async def ask(req: QueryRequest):
    logger.info(f"Query received: {req.query[:50]}...")
    start_time = time.time()
    
    # ... existing code ...
    
    elapsed = time.time() - start_time
    logger.info(f"Response generated in {elapsed:.2f}s")
    return response
```

---

## 🔍 Key Concepts Explained

### **What is RAG (Retrieval-Augmented Generation)?**

Traditional LLM workflow:
```
User Query → LLM → Answer (might hallucinate)
```

RAG workflow:
```
User Query → Vector Search → Retrieve Context → LLM + Context → Grounded Answer
```

**Benefits:**
- Factually accurate answers
- Source attribution
- Works with proprietary/recent data
- Reduces hallucinations

---

### **What is FAISS?**

Facebook AI Similarity Search - super fast vector similarity search

```
1. Store embeddings (vectors) in efficient data structure
2. User query gets embedded to same vector space
3. Find most similar existing vectors (nearest neighbors)
4. Return corresponding documents
```

Time complexity: O(1) to O(log n) instead of O(n)

---

### **What are Embeddings?**

Numerical representation of text meaning

```
"What is diabetes?" → [0.23, -0.45, 0.12, ..., 0.87]  (384 dimensions)
                        ↓
                 Captures semantic meaning
                        ↓
              Similar questions = similar vectors
```

Model: `all-MiniLM-L6-v2` (12 layers, 22M parameters, 384-dim output)

---

### **Temperature in LLM**

Controls randomness of generation:

```
temperature = 0.1  → Deterministic, factual (good for QA)
temperature = 0.5  → Balanced
temperature = 1.0+ → Creative, variable (good for brainstorming)
```

Current setting: `0.3` (factual but slightly creative)

---

## 📊 API Reference

### **POST /api/ask**

**Request:**
```json
{
  "query": "What are diabetes symptoms?",
  "history": ["What is diabetes?"],
  "token": "secure_token_123"
}
```

**Response (Success):**
```json
{
  "response": "Diabetes symptoms include...",
  "citations": [
    {
      "source": "medquad:diabetes.xml",
      "question": "What are the symptoms of diabetes?",
      "id": "doc-1",
      "updated_at": "2024-01-15"
    }
  ]
}
```

**Response (Error):**
```json
{
  "detail": "Unauthorized"
}
```

**Status Codes:**
- `200` - Success
- `401` - Invalid token
- `422` - Invalid request format
- `500` - Server error

---

## 🐛 Troubleshooting

### **Issue: "ModuleNotFoundError: No module named 'langchain'"**

**Solution:**
```bash
source .venv/bin/activate
pip install langchain langchain-community
```

### **Issue: "FAISS index not found"**

**Solution:**
```bash
python scripts/create_faiss_index.py
# Generates sample data if data/medical_data.json missing
```

### **Issue: "Connection refused" on http://localhost:8000**

**Solution:**
```bash
# Check if backend is running
ps aux | grep uvicorn

# If not running, start it:
uvicorn backend.main:app --reload
```

### **Issue: Frontend can't reach backend**

**Check:**
1. Backend running on `http://localhost:8000`?
2. Frontend making requests to `http://localhost:8000/api/ask`?
3. CORS enabled in `backend/main.py`? (Already configured with `allow_origins=["*"]`)

### **Issue: Slow inference (>30s per query)**

**Solutions:**
1. Use smaller model: `google/flan-t5-base` instead of `flan-t5-large`
2. Reduce `max_length` in model_kwargs
3. Use GPU: Install `faiss-gpu` and `torch[cuda]`
4. Reduce number of retrieved documents: `search_kwargs={"k": 1}`

---

## 📚 Learning Resources

- **FastAPI:** https://fastapi.tiangolo.com/
- **LangChain:** https://python.langchain.com/
- **React:** https://react.dev/
- **FAISS:** https://github.com/facebookresearch/faiss
- **Sentence Transformers:** https://www.sbert.net/

---

## 🤝 Making Improvements

### Potential Enhancements

1. **Better Auth** - JWT tokens, user accounts, rate limiting
2. **Database** - PostgreSQL for persistent chat history
3. **UI Improvements** - Citations panel, copy buttons, feedback
4. **Streaming API** - Stream answers as they're generated
5. **Multi-turn Context** - Better handling of conversation history
6. **RAG Optimization** - Hybrid search, re-ranking, query expansion
7. **Monitoring** - Logging, error tracking, performance metrics
8. **Caching** - Redis to cache common queries
9. **Multi-language** - Support for non-English queries
10. **Mobile App** - React Native version

---

## 📝 Summary

**What you now know:**

✅ Project is a RAG-based medical Q&A system  
✅ Frontend (React) talks to Backend (FastAPI)  
✅ Backend uses LangChain to orchestrate: Embedding → Vector Search → LLM  
✅ Data flows: MedQuAD XML → JSON → Embeddings → FAISS Index → Search Results  
✅ Each component can be modified independently  
✅ Setup involves 3 main scripts: data import, indexing, and running servers  

**Next steps:**

1. Run setup commands
2. Test with a simple query
3. Explore code and understand each piece
4. Modify and experiment
5. Deploy or contribute!

---

**Good luck! Happy coding! 🚀**
