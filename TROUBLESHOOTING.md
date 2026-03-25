# AskDocAI - Troubleshooting Guide 🔧

This guide helps you resolve common issues when setting up or running AskDocAI.

---

## 📋 Table of Contents

1. [Installation Issues](#installation-issues)
2. [Backend Issues](#backend-issues)
3. [Frontend Issues](#frontend-issues)
4. [Runtime Issues](#runtime-issues)
5. [Performance Issues](#performance-issues)
6. [Data & Vector Store Issues](#data--vector-store-issues)
7. [Debugging Tips](#debugging-tips)

---

## 🔴 Installation Issues

### Issue: Python command not found

**Error Message:**
```
command not found: python
```

**Solution:**
```bash
# Check what's installed
which python3
which python

# Use python3 explicitly
python3 --version
python3 -m venv .venv

# Or create an alias
alias python=python3
```

**If Python not installed:**
- macOS: `brew install python3`
- Ubuntu/Debian: `sudo apt-get install python3 python3-venv`
- Windows: Download from https://www.python.org/downloads/

---

### Issue: Virtual environment not activating

**Error Message:**
```
bash: .venv/bin/activate: No such file or directory
```

**Solution:**
```bash
# Recreate virtual environment
rm -rf .venv
python3 -m venv .venv

# Activate correctly
source .venv/bin/activate

# Verify activation (should show (.venv) prefix)
which python
```

**On Windows:**
```bash
.venv\Scripts\activate
```

---

### Issue: pip install fails with "No module named 'pip'"

**Solution:**
```bash
# Ensure you're in the virtual environment
source .venv/bin/activate

# Reinstall pip
python -m ensurepip --upgrade

# Try installing again
pip install -r requirements.txt
```

---

### Issue: "ModuleNotFoundError" after installing

**Error Message:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
Make sure the virtual environment is **activated**:

```bash
# Check if activated (should see (.venv) prefix)
$ source .venv/bin/activate
(.venv) $ python -c "import fastapi; print('OK')"  # Should print OK
```

**If you see the error after activation:**
```bash
# Reinstall
pip install fastapi uvicorn

# Or reinstall everything
pip install -r requirements.txt
```

---

### Issue: Node modules won't install

**Error Message:**
```
npm ERR! Could not resolve dependency
```

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules
rm -rf Frontend/node_modules
rm -f Frontend/package-lock.json

# Reinstall
cd Frontend
npm install
```

If still failing:
```bash
# Check Node version
node --version  # Should be 16+

# Try removing version constraints
npm install --legacy-peer-deps
```

---

## 🔴 Backend Issues

### Issue: Uvicorn server won't start

**Error Message:**
```
ERROR: Application startup failed
```

**Solution:**

1. **Check if port is already in use:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn backend.main:app --port 8001
```

2. **Check Python import errors:**
```bash
# Try to import the module manually
python -c "from backend import main; print('OK')"

# If error, shows the specific problem
```

3. **Verify file structure:**
```bash
# These files must exist:
ls backend/main.py
ls backend/auth/auth.py
ls backend/rag_pipeline/rag.py
```

4. **Check for syntax errors:**
```bash
# Validate Python syntax
python -m py_compile backend/main.py
python -m py_compile backend/auth/auth.py
python -m py_compile backend/rag_pipeline/rag.py
```

---

### Issue: "ModuleNotFoundError: No module named 'backend'"

**Solution:**

The backend module must be discoverable. Make sure you're running from the **project root**:

```bash
# Wrong - running from backend/ folder
cd backend
uvicorn main:app  # ❌ Fails

# Correct - running from project root
cd /Users/devpatel062/Documents/clone/AskDocAI
uvicorn backend.main:app --reload  # ✓ Works
```

---

### Issue: Frontend can't reach backend (CORS error)

**Error in Browser Console:**
```
Access to XMLHttpRequest at 'http://localhost:8000/api/ask' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**Solution:**

This is already configured in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**If still failing:**

1. Check backend is actually running:
```bash
curl http://localhost:8000/docs
# Should return HTML, not "Connection refused"
```

2. Check frontend is using correct URL:
```javascript
// Should be:
axios.post('http://localhost:8000/api/ask', ...)

// NOT:
axios.post('http://127.0.0.1:8000/api/ask', ...)  // Different host!
```

3. Restart backend after changes:
```bash
# Kill existing server
ps aux | grep uvicorn
kill -9 <PID>

# Restart
uvicorn backend.main:app --reload
```

---

### Issue: "Unauthorized" error on every request

**Error Message:**
```json
{"detail": "Unauthorized"}
```

**Solution:**

The token must match exactly. In `backend/auth/auth.py`:
```python
def verify_token(token: str) -> bool:
    return token == "secure_token_123"  # ← Must match exactly
```

**Make sure frontend sends correct token:**
```javascript
// In Frontend/src/App.jsx (line ~35)
axios.post('http://localhost:8000/api/ask', {
    query: currentQuery,
    history: history,
    token: 'secure_token_123'  // ← Must match backend
})
```

**For development**, you can disable auth temporarily:
```python
# backend/auth/auth.py - for testing only!
def verify_token(token: str) -> bool:
    return True  # Always return True (NEVER do this in production!)
```

---

## 🔴 Frontend Issues

### Issue: Frontend won't start with `npm run dev`

**Error Message:**
```
command not found: npm
```

**Solution:**

Install Node.js from https://nodejs.org/ (version 16+)

```bash
# Verify installation
node --version
npm --version

# Then try again
cd Frontend
npm run dev
```

---

### Issue: Vite dev server crashes

**Error Message:**
```
error when starting dev server:
Error: listen EADDRINUSE: address already in use :::5173
```

**Solution:**

Port 5173 is already in use:

```bash
# Find what's using it
lsof -i :5173

# Kill it
kill -9 <PID>

# Or use different port
npm run dev -- --port 5174
```

---

### Issue: Tailwind styles not applying

**Problem:** CSS classes don't work, page looks unstyled

**Solution:**

1. Check that Tailwind config exists:
```bash
ls Frontend/tailwind.config.js
ls Frontend/postcss.config.js
```

2. Restart dev server:
```bash
cd Frontend
npm run dev  # Kill and restart
```

3. Clear browser cache:
```
DevTools → Network → Uncheck "Disable cache" → Refresh
```

4. Rebuild Tailwind:
```bash
cd Frontend
npx tailwindcss -i ./src/index.css -o ./dist/output.css
```

---

### Issue: React component not updating after API response

**Problem:** Chat doesn't show bot's response

**Solution:**

Check browser console (F12):

1. **Network tab**: Did request finish successfully (200 status)?
2. **Console tab**: Any JavaScript errors?
3. **Check state management** in `Frontend/src/App.jsx`:

```javascript
// Make sure API response is handled:
try {
    const res = await axios.post('http://localhost:8000/api/ask', {...});
    const answer = res.data.response;
    
    // These state updates are critical:
    setMessages(prev => [...prev, { role: 'bot', content: answer }]);
    setHistory(prev => [...prev, currentQuery]);
} catch (error) {
    console.error("Error:", error);
    setMessages(prev => [...prev, { role: 'bot', content: "Error occurred" }]);
}
```

---

## 🔴 Runtime Issues

### Issue: Queries return "I don't know." for every question

**Problem:** Backend is returning empty answers

**Causes & Solutions:**

**1. FAISS index doesn't exist or is empty:**
```bash
# Check if it exists
ls -la vector_store_pubmed/

# If empty or missing, recreate:
python scripts/create_faiss_index.py
```

**2. medical_data.json doesn't exist:**
```bash
# Check
ls -la data/medical_data.json

# If missing, create sample or import real data:
python scripts/create_faiss_index.py  # Creates sample
# OR
python scripts/import_medquad.py --input ./MedQuAD-master --output data/medical_data.json
python scripts/create_faiss_index.py
```

**3. LLM not responding properly:**
```bash
# Test that models can load:
python -c "
from langchain_community.embeddings import SentenceTransformerEmbeddings
e = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')
result = e.embed_query('test')
print(f'Embedding works: {len(result)} dimensions')
"

python -c "
from langchain_community.llms import HuggingFacePipeline
llm = HuggingFacePipeline.from_model_id(
    model_id='google/flan-t5-large',
    task='text2text-generation'
)
result = llm('What is 2+2?')
print(f'LLM works: {result}')
"
```

---

### Issue: Very slow responses (30+ seconds)

**Expected:** 5-20 seconds per response
**Actual:** 30+ seconds

**Causes & Solutions:**

**1. Using wrong device (CPU instead of GPU):**
```bash
# Check if GPU is available
python -c "import torch; print(torch.cuda.is_available())"

# If False, you're using CPU (slow)
# Install GPU version:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install faiss-gpu  # Instead of faiss-cpu
```

**2. Using large model:**
```python
# In backend/rag_pipeline/rag.py, use smaller model:
# Change from:
llm = HuggingFacePipeline.from_model_id(
    model_id="google/flan-t5-large",  # ← Large
    ...
)

# To:
llm = HuggingFacePipeline.from_model_id(
    model_id="google/flan-t5-base",  # ← Faster
    ...
)
```

**3. Too many documents being retrieved:**
```python
# In backend/rag_pipeline/rag.py:
retriever=db.as_retriever(
    search_kwargs={"k": 1}  # Reduce from 3 to 1
)
```

**4. Model loading on every request (shouldn't happen):**

Check that embedding_model, db, and llm are defined **outside** the `ask_question()` function (they should be module-level, loaded once at startup).

---

### Issue: Out of Memory error

**Error Message:**
```
RuntimeError: CUDA out of memory
or
MemoryError: Unable to allocate ...
```

**Solutions:**

**1. Reduce batch size:**
```python
# In backend/rag_pipeline/rag.py
llm = HuggingFacePipeline.from_model_id(
    ...,
    model_kwargs={
        "temperature": 0.3,
        "max_length": 256,  # ← Reduce from 512
    }
)
```

**2. Use smaller model:**
```python
model_id="google/flan-t5-base"  # Instead of flan-t5-large
```

**3. Reduce retrieval context:**
```python
retriever=db.as_retriever(search_kwargs={"k": 1})  # Instead of k=3
```

**4. Disable GPU:**
```python
device=-1  # Use CPU instead (slower but less memory)
```

---

## 🔴 Data & Vector Store Issues

### Issue: Vector store folder is huge (>1GB)

**Solution:**

That's normal for large datasets. To reduce size:

1. **Use fewer documents** when creating index:
```bash
python scripts/create_faiss_index.py --limit 1000
```

2. **Use smaller embedding model:**
```python
# In backend/rag_pipeline/rag.py
embedding_model = SentenceTransformerEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # ← Smaller
)
```

---

### Issue: "Vector store format error" or "index.faiss corrupted"

**Solution:**

Recreate the vector store:

```bash
# Backup old store
mv vector_store_pubmed vector_store_pubmed.backup

# Recreate
python scripts/create_faiss_index.py

# If that works, delete backup
rm -rf vector_store_pubmed.backup
```

---

### Issue: Imported MedQuAD but index creation fails

**Error:**
```
ValueError: No valid QA pairs found
```

**Solution:**

1. Verify data was imported:
```bash
# Check file exists and has content
ls -lh data/medical_data.json
wc -l data/medical_data.json

# View first entry
python -c "import json; data=json.load(open('data/medical_data.json')); print(data[0])"
```

2. If empty, re-import:
```bash
# Make sure MedQuAD path is correct
ls MedQuAD-master/*.xml  # Should list XML files

# Re-import with verbose output
python scripts/import_medquad.py --input ./MedQuAD-master --output data/medical_data.json
```

---

## 🔴 Debugging Tips

### Enable verbose logging

**Backend:**
```python
# Add to backend/main.py at the top
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add to /api/ask endpoint:
@app.post("/api/ask")
async def ask(req: QueryRequest):
    logger.info(f"Received query: {req.query}")
    logger.info(f"Token: {req.token}")
    
    if not verify_token(req.token):
        logger.error("Token verification failed")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    logger.info("Starting RAG pipeline...")
    rag_result = ask_question(req.query, req.history)
    logger.info(f"Generated answer: {rag_result['answer'][:100]}...")
    
    return {
        "response": rag_result["answer"],
        "citations": rag_result["citations"],
    }
```

**Frontend:**
```javascript
// In Frontend/src/App.jsx, add logging
const handleAsk = async (e) => {
    console.log("🔵 [APP] User query:", query);
    
    try {
        console.log("📤 [API] Sending request to backend...");
        const res = await axios.post('http://localhost:8000/api/ask', {
            query: currentQuery,
            history: history,
            token: 'secure_token_123'
        });
        
        console.log("📥 [API] Response received:", res.data);
        const answer = res.data.response;
        console.log("✅ [APP] Answer:", answer);
        
        setMessages(prev => [...prev, { role: 'bot', content: answer }]);
    } catch (error) {
        console.error("❌ [ERROR]", error.response?.data || error.message);
    }
};
```

---

### Test components individually

**Test backend in isolation:**
```bash
# Test embedding
python -c "
from backend.rag_pipeline.rag import embedding_model
result = embedding_model.embed_query('test')
print(f'✓ Embedding: {len(result)} dims')
"

# Test FAISS
python -c "
from backend.rag_pipeline.rag import db
results = db.similarity_search('diabetes')
print(f'✓ Found {len(results)} documents')
"

# Test LLM
python -c "
from backend.rag_pipeline.rag import llm
answer = llm('What is 2+2?')
print(f'✓ LLM: {answer}')
"

# Test full RAG
python -c "
from backend.rag_pipeline.rag import ask_question
result = ask_question('What is diabetes?', [])
print(f'Answer: {result[\"answer\"]}')
print(f'Citations: {result[\"citations\"]}')
"
```

**Test frontend in isolation:**
```bash
cd Frontend
npm run lint  # Check for errors
npm run build  # Test production build
```

---

### Check system resources

```bash
# CPU/Memory
top
# or
ps aux | grep uvicorn
ps aux | grep node

# Disk
du -sh vector_store_pubmed/
du -sh Frontend/node_modules/

# Network
netstat -an | grep 8000
netstat -an | grep 5173
```

---

## 🎯 Quick Checklist

Use this to diagnose issues:

```
Backend Issues:
☐ Python 3.8+? python3 --version
☐ Virtual env activated? source .venv/bin/activate
☐ Dependencies installed? pip list | grep fastapi
☐ FAISS index exists? ls vector_store_pubmed/index.faiss
☐ Backend running? curl http://localhost:8000/docs
☐ No syntax errors? python -m py_compile backend/main.py

Frontend Issues:
☐ Node 16+? node --version
☐ Dependencies installed? npm list react
☐ Dev server running? npm run dev
☐ Frontend accessible? curl http://localhost:5173
☐ No build errors? npm run build

Integration Issues:
☐ Backend port 8000? lsof -i :8000
☐ Frontend port 5173? lsof -i :5173
☐ CORS enabled? Check backend/main.py
☐ Token matches? Check frontend query vs auth.py
☐ API response valid JSON? curl -X POST http://localhost:8000/api/ask ...
```

---

## 📞 Still Stuck?

1. **Check the logs**:
   - Backend terminal: Shows errors with full traceback
   - Browser DevTools (F12): Shows CORS, network, JavaScript errors

2. **Read the docs**:
   - [COMPLETE_PROJECT_GUIDE.md](COMPLETE_PROJECT_GUIDE.md)
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

3. **Test in isolation**:
   - Run backend without frontend
   - Use `curl` to test API directly
   - Check each component loads correctly

4. **Check Stack Overflow** or GitHub issues with similar errors

5. **Review your installation** following the setup guide step-by-step

Good luck! 🚀
