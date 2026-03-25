#!/bin/bash

# AskDocAI - Complete Setup Script
# Run this script to set up the entire project from scratch

set -e  # Exit on error

echo "🏥 AskDocAI - Complete Setup Script"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo -e "${YELLOW}Step 1: Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
echo ""

# Step 2: Create virtual environment
echo -e "${YELLOW}Step 2: Setting up Python virtual environment...${NC}"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi
source .venv/bin/activate
echo ""

# Step 3: Install Python dependencies
echo -e "${YELLOW}Step 3: Installing Python dependencies...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null
pip install -r requirements.txt > /dev/null 2>&1 || {
    echo "📦 Installing dependencies (this may take a few minutes)..."
    pip install fastapi uvicorn langchain langchain-community sentence-transformers torch transformers faiss-cpu
}
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# Step 4: Create FAISS index if it doesn't exist
echo -e "${YELLOW}Step 4: Creating FAISS vector index...${NC}"
if [ ! -d "vector_store_pubmed" ] || [ -z "$(ls -A vector_store_pubmed)" ]; then
    echo "📊 Building FAISS index (this may take a minute)..."
    python scripts/create_faiss_index.py
    echo -e "${GREEN}✓ FAISS vector index created${NC}"
else
    echo -e "${GREEN}✓ FAISS vector index already exists${NC}"
fi
echo ""

# Step 5: Check Node.js
echo -e "${YELLOW}Step 5: Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Skipping frontend setup."
    echo "    Please install Node.js 16+ manually and run:"
    echo "    cd Frontend && npm install"
else
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"
    
    # Step 6: Install frontend dependencies
    echo -e "${YELLOW}Step 6: Installing frontend dependencies...${NC}"
    cd Frontend
    if [ -d "node_modules" ]; then
        echo -e "${GREEN}✓ Frontend dependencies already installed${NC}"
    else
        echo "📦 Installing npm packages..."
        npm install > /dev/null 2>&1
        echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    fi
    cd ..
fi
echo ""

# Summary
echo "=================================="
echo -e "${GREEN}✅ Setup complete!${NC}"
echo "=================================="
echo ""
echo "📖 Next Steps:"
echo ""
echo "1️⃣  Start the Backend Server:"
echo "    source .venv/bin/activate"
echo "    uvicorn backend.main:app --reload"
echo "    → Backend will run at http://127.0.0.1:8000"
echo ""
echo "2️⃣  Start the Frontend (in another terminal):"
echo "    cd Frontend"
echo "    npm run dev"
echo "    → Frontend will run at http://localhost:5173"
echo ""
echo "3️⃣  Open http://localhost:5173 in your browser"
echo ""
echo "4️⃣  Ask a medical question!"
echo ""
echo "📚 Documentation:"
echo "   - COMPLETE_PROJECT_GUIDE.md - Detailed explanation of everything"
echo "   - QUICK_REFERENCE.md - Visual guides and diagrams"
echo "   - ARCHITECTURE.md - System design"
echo "   - README.md - Quick start"
echo ""
echo "🔧 Configuration:"
echo "   Backend: backend/main.py"
echo "   Auth: backend/auth/auth.py"
echo "   RAG: backend/rag_pipeline/rag.py"
echo "   Frontend: Frontend/src/App.jsx"
echo ""
echo "Happy coding! 🚀"
