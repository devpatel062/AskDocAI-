# AskDocAI - Learning Path & Implementation Guide 🚀

For someone who just forked this project, here's a structured way to understand and implement everything.

---

## 📚 Start Here: Reading Order

### **Phase 1: Understand the Project (15 minutes)**

1. **[README.md](README.md)** ← Start here
   - What is AskDocAI?
   - Tech stack overview
   - High-level architecture diagram

2. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** ← Then read this
   - Visual system architecture
   - Data flow diagram
   - Request lifecycle with timing

3. **[ARCHITECTURE.md](ARCHITECTURE.md)** ← Optional deep dive
   - Application flow diagram
   - Component hierarchy
   - Interaction patterns

### **Phase 2: Setup the Project (30 minutes)**

4. Run the automated setup script:
   ```bash
   bash setup.sh
   # OR follow manual setup in COMPLETE_PROJECT_GUIDE.md
   ```

5. Start both servers:
   ```bash
   # Terminal 1: Backend
   source .venv/bin/activate
   uvicorn backend.main:app --reload
   
   # Terminal 2: Frontend
   cd Frontend
   npm run dev
   ```

6. Test in browser: `http://localhost:5173`

### **Phase 3: Understand the Code (1-2 hours)**

7. **[COMPLETE_PROJECT_GUIDE.md](COMPLETE_PROJECT_GUIDE.md)** ← Read this in detail
   - Every file explained
   - Data flow walkthrough
   - Step-by-step setup
   - Common tasks & how-tos

8. Read the actual code files:
   - `backend/main.py` - API routes
   - `backend/auth/auth.py` - Authentication
   - `backend/rag_pipeline/rag.py` - RAG logic (most important!)
   - `Frontend/src/App.jsx` - Chat UI

### **Phase 4: Troubleshoot Issues (As needed)**

9. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** ← When something breaks
   - Common errors and fixes
   - Debugging tips
   - Quick checklist

---

## 🎯 Learning Objectives

By the end of this guide, you should understand:

### **Architecture Understanding**
- [ ] What is RAG (Retrieval-Augmented Generation)?
- [ ] How FAISS vector database works
- [ ] How embedding models convert text to vectors
- [ ] How LLMs generate answers from context
- [ ] Client-server communication flow

### **Technical Knowledge**
- [ ] FastAPI basics (routes, models, middleware)
- [ ] React hooks (useState, useEffect)
- [ ] How axios makes HTTP requests
- [ ] What Tailwind CSS does
- [ ] Python virtual environments

### **Practical Skills**
- [ ] Can start backend and frontend servers
- [ ] Can import medical data from XML
- [ ] Can create FAISS vector index
- [ ] Can debug API errors using curl
- [ ] Can read and understand backend logs

---

## 🏗️ Code Structure Deep Dive

### **Backend Architecture**

```
backend/
├── main.py
│   ├── FastAPI app initialization
│   ├── CORS middleware setup
│   ├── QueryRequest model definition
│   └── @app.post("/api/ask") endpoint
│       ├── verify_token()
│       └── ask_question()
│
├── auth/
│   └── auth.py
│       └── verify_token(token: str) -> bool
│
└── rag_pipeline/
    └── rag.py
        ├── embedding_model (SentenceTransformer)
        ├── db (FAISS vector store)
        ├── llm (Flan-T5-Large)
        ├── QA_CHAIN_PROMPT (template)
        ├── qa_chain (LangChain)
        └── ask_question(query, history)
            ├── embed query
            ├── search FAISS
            ├── prepare context
            ├── call LLM
            ├── extract citations
            └── return result dict
```

### **Frontend Architecture**

```
Frontend/
├── src/
│   ├── main.jsx (Entry point)
│   │   └── ReactDOM.createRoot(App)
│   │
│   ├── App.jsx (Main component)
│   │   ├── State: query, messages, history, isLoading
│   │   ├── useEffect hooks for auto-scroll
│   │   ├── handleAsk() function
│   │   │   ├── POST to /api/ask
│   │   │   ├── Handle response
│   │   │   └── Update messages
│   │   │
│   │   ├── Header (title + icon)
│   │   ├── Chat area (messages)
│   │   │   ├── Welcome message (empty state)
│   │   │   └── Message bubbles (user/bot)
│   │   └── Input form
│   │       ├── Text input
│   │       ├── Send button
│   │       └── Loading spinner
│   │
│   ├── App.css (Component styles)
│   ├── index.css (Global styles)
│   └── assets/ (Images, fonts)
│
├── package.json (Dependencies)
├── vite.config.js (Build config)
├── tailwind.config.js (CSS config)
├── postcss.config.js (CSS processing)
└── eslint.config.js (Code quality)
```

---

## 🔄 Data Flow: Step-by-Step

### **Initialization (On Backend Startup)**

```python
# backend/rag_pipeline/rag.py executes at import time

# 1. Load Embedding Model (first time: ~30 seconds, 500MB download)
embedding_model = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
# Result: Object that converts text to 384-dimensional vectors

# 2. Load FAISS Index (1-5 seconds)
db = FAISS.load_local(
    "./vector_store_pubmed",
    embeddings=embedding_model
)
# Result: Fast search index over all documents

# 3. Load LLM (first time: ~2-5 seconds, 750MB download)
llm = HuggingFacePipeline.from_model_id(
    model_id="google/flan-t5-large",
    task="text2text-generation",
    model_kwargs={"temperature": 0.3, "max_length": 512},
    device=0 if torch.cuda.is_available() else -1,
)
# Result: Language model for generating answers

# 4. Create Prompt Template
QA_CHAIN_PROMPT = PromptTemplate.from_template("""
Use the following pieces of context to answer the question at the end.
...
Context: {context}
Question: {question}
Helpful Answer:""")

# 5. Create RAG Chain
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=db.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT},
)
# Result: Ready to process queries
```

### **Query Processing (Per User Question)**

```python
# User Types: "What is diabetes?"
# Frontend sends POST to /api/ask

@app.post("/api/ask")
async def ask(req: QueryRequest):  # Query, history, token
    
    # 1. Authentication Check
    if not verify_token(req.token):  # ← Check token
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # 2. RAG Pipeline
    rag_result = ask_question(req.query, req.history)
    
    # 3. Return Response
    return {
        "response": rag_result["answer"],
        "citations": rag_result["citations"],
    }

def ask_question(query: str, history: list[str]) -> dict:
    
    # A. Embed the User Query
    # Input: "What is diabetes?"
    query_embedding = embedding_model.embed_query(query)
    # Output: [0.23, -0.45, 0.12, ..., 0.87]  (384 floats)
    
    # B. Vector Similarity Search in FAISS
    # Compare query_embedding against all indexed documents
    results = db.similarity_search(query_embedding, k=3)
    # Output: List of 3 most similar documents
    # [
    #   Document("Question: What is diabetes?", metadata={...}),
    #   Document("Question: What are diabetes symptoms?", metadata={...}),
    #   Document("Question: How is diabetes treated?", metadata={...}),
    # ]
    
    # C. Format Context for LLM
    context_text = "\n\n".join([
        f"Question: {doc.metadata['question']}\n" +
        f"Answer: {doc.page_content}"
        for doc in results
    ])
    # Output: String with 3 Q&A pairs
    
    # D. Call LLM with Prompt + Context
    final_prompt = f"""Use the following context:
{context_text}

Answer this question: {query}

Helpful Answer:"""
    
    # LLM takes prompt and generates answer
    answer = llm(final_prompt)
    # Output: "Diabetes is a chronic condition that affects..."
    
    # E. Extract Citations from Retrieved Documents
    citations = []
    for doc in results:
        citations.append({
            "source": doc.metadata.get("source"),
            "question": doc.metadata.get("question"),
            "id": doc.metadata.get("id"),
            "updated_at": doc.metadata.get("updated_at"),
        })
    # Output: List of source documents used
    
    # F. Return Complete Result
    return {
        "answer": answer,
        "citations": citations,
    }
```

### **Response Display (Frontend Updates)**

```javascript
// Backend returns:
{
  "response": "Diabetes is a chronic...",
  "citations": [{source: "...", question: "...", ...}]
}

// Frontend processes:
const res = await axios.post("http://localhost:8000/api/ask", {...});

// 1. Add bot message to chat
setMessages(prev => [...prev, {
    role: 'bot',
    content: res.data.response
}]);

// 2. Could display citations (currently not shown, can add)
console.log(res.data.citations);

// 3. Add to history for context-awareness
setHistory(prev => [...prev, currentQuery]);

// 4. Re-render UI (automatic with React)
// User sees the new message in chat
```

---

## 🛠️ Common Modifications

### **Modify #1: Change the LLM Model**

```python
# backend/rag_pipeline/rag.py, line ~15
# Before:
llm = HuggingFacePipeline.from_model_id(
    model_id="google/flan-t5-large",  # ← 750MB, 10-15s per query
    ...
)

# After (faster):
llm = HuggingFacePipeline.from_model_id(
    model_id="google/flan-t5-base",  # ← 250MB, 3-5s per query
    ...
)

# Or (better quality):
llm = HuggingFacePipeline.from_model_id(
    model_id="google/flan-t5-xl",  # ← 3GB, slower but better
    ...
)
```

**Then restart backend:**
```bash
# Kill existing: Ctrl+C
# Restart:
uvicorn backend.main:app --reload
```

### **Modify #2: Retrieve More Context**

```python
# backend/rag_pipeline/rag.py, line ~30
# Before:
retriever=db.as_retriever(search_kwargs={"k": 3}),  # Top-3 docs

# After (more context, slower):
retriever=db.as_retriever(search_kwargs={"k": 5}),  # Top-5 docs

# Or (less context, faster):
retriever=db.as_retriever(search_kwargs={"k": 1}),  # Top-1 doc
```

### **Modify #3: Display Citations in Frontend**

```javascript
// Frontend/src/App.jsx
// In the handleAsk function, after setting messages:

const res = await axios.post('http://localhost:8000/api/ask', {
    query: currentQuery,
    history: history,
    token: 'secure_token_123'
});

const answer = res.data.response;

// Add this to display citations:
const citations = res.data.citations;
let citationText = "";
if (citations && citations.length > 0) {
    citationText = "\n\nSources:\n" + 
        citations.map(c => `- ${c.source}: "${c.question}"`).join("\n");
}

setMessages(prev => [...prev, { 
    role: 'bot', 
    content: answer + citationText  // Include citations
}]);
```

### **Modify #4: Add Actual User Authentication**

```python
# backend/auth/auth.py
from datetime import datetime, timedelta
import jwt

SECRET_KEY = "your-secret-key-change-me"

def create_token(user_id: str, expires_in_hours: int = 24) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return True  # Token is valid
    except jwt.ExpiredSignatureError:
        return False  # Token expired
    except jwt.InvalidTokenError:
        return False  # Token invalid

# Usage in frontend:
# 1. User logs in (implement login API)
# 2. Backend returns JWT token
# 3. Frontend stores token
# 4. Frontend sends token with each /api/ask request
# 5. Backend verifies token before processing
```

Install JWT library:
```bash
pip install python-jose[cryptography]
```

### **Modify #5: Add Database for Chat History**

```python
# backend/main.py
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite database
DATABASE_URL = "sqlite:///./askdocai.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define Chat Message model
class ChatMessage(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    role = Column(String)  # "user" or "bot"
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Save messages to database
@app.post("/api/ask")
async def ask(req: QueryRequest):
    if not verify_token(req.token):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    db_session = SessionLocal()
    
    # Save user message
    db_session.add(ChatMessage(
        user_id="user123",  # Get from token
        role="user",
        content=req.query
    ))
    
    # Get RAG response
    rag_result = ask_question(req.query, req.history)
    
    # Save bot message
    db_session.add(ChatMessage(
        user_id="user123",
        role="bot",
        content=rag_result["answer"]
    ))
    
    db_session.commit()
    db_session.close()
    
    return {
        "response": rag_result["answer"],
        "citations": rag_result["citations"],
    }
```

---

## 📚 Learning Resources

### **For Understanding RAG:**
- [What is RAG?](https://python.langchain.com/docs/use_cases/question_answering/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)

### **For FastAPI:**
- [FastAPI Official Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Pydantic Models](https://docs.pydantic.dev/)

### **For React:**
- [React Hooks Documentation](https://react.dev/reference/react)
- [Axios HTTP Client](https://axios-http.com/)

### **For Deployment:**
- [Docker Container Setup](https://docs.docker.com/)
- [Heroku Deployment](https://devcenter.heroku.com/)
- [AWS EC2 Setup](https://docs.aws.amazon.com/ec2/)

---

## ✅ Success Checklist

After completing this guide, you should be able to:

- [ ] Explain what RAG is and why it's useful
- [ ] Describe the data flow from user query to response
- [ ] List all the files and their purposes
- [ ] Start both backend and frontend servers
- [ ] Ask a question and get an answer with citations
- [ ] Modify the LLM model being used
- [ ] Understand how embeddings and vector search work
- [ ] Read and understand the backend logs
- [ ] Debug a broken connection using curl
- [ ] Modify the frontend to display different information
- [ ] Add new features (like citations display)
- [ ] Deploy the application to a server

---

## 🎓 Next Steps

### **Level 1: Understand (You are here)**
- Read all documentation
- Run the application
- Test with different queries

### **Level 2: Customize**
- Add your own medical data
- Modify the appearance
- Change LLM parameters
- Add new features

### **Level 3: Extend**
- Add user authentication
- Implement chat history database
- Add response streaming
- Deploy to production

### **Level 4: Optimize**
- Fine-tune retrieval
- Add caching
- Optimize embedding model
- Set up monitoring

---

## 💡 Pro Tips

1. **Save Model Downloads**: First run takes time to download. Subsequent runs are fast.
2. **Use GPU**: If available, inference is 5-10x faster with CUDA.
3. **Smaller Models**: For testing, use `flan-t5-base` instead of `flan-t5-large`.
4. **Monitor Logs**: Always check terminal output - it shows exactly what's happening.
5. **Test Components**: Test embedding, FAISS, and LLM separately with Python REPL.
6. **Use curl**: Skip browser complexity and test API directly with curl.
7. **Read Errors**: Python and JavaScript errors are very descriptive - read them fully.
8. **Version Control**: Commit working states before making changes.
9. **Documentation**: Update docs when you modify code.
10. **Community**: Star the repo if you find it useful, and consider contributing!

---

**Congratulations! You now have a complete understanding of AskDocAI! 🎉**

Next, try one of these:
1. Import your own medical data
2. Change to a different LLM model
3. Deploy to the cloud
4. Add a new feature

Happy learning! 🚀
