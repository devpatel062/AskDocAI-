from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.auth.auth import verify_token
from backend.rag_pipeline.rag import ask_question
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    history: list[str] = []
    token: str


@app.post("/api/ask")
async def ask(req: QueryRequest):
    if not verify_token(req.token):
        raise HTTPException(status_code=401, detail="Unauthorized")

    rag_result = ask_question(req.query, req.history)
    return {
        "response": rag_result["answer"],
        "citations": rag_result["citations"],
    }
