from __future__ import annotations

import torch
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.llms import HuggingFacePipeline
from langchain_community.vectorstores import FAISS

embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

db = FAISS.load_local(
    "./vector_store_pubmed",
    embeddings=embedding_model,
    allow_dangerous_deserialization=True,
)

llm = HuggingFacePipeline.from_model_id(
    model_id="google/flan-t5-large",
    task="text2text-generation",
    model_kwargs={"temperature": 0.3, "max_length": 512},
    device=0 if torch.cuda.is_available() else -1,
)

template = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know.
Keep the answer concise and helpful.

Context: {context}

Question: {question}

Helpful Answer:"""

QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=db.as_retriever(search_kwargs={"k": 3}),
    return_source_documents=True,
    combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT},
)


def ask_question(query: str, history: list[str]) -> dict:
    # Current frontend only sends user queries, not role-paired chat turns.
    chat_history: list = []

    result = qa_chain({"question": query, "chat_history": chat_history})

    citations: list[dict[str, str]] = []
    seen = set()
    for doc in result.get("source_documents", []):
        source = str(doc.metadata.get("source", "unknown"))
        question = str(doc.metadata.get("question", ""))
        key = (source, question)
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            {
                "source": source,
                "question": question,
                "id": str(doc.metadata.get("id", "")),
                "updated_at": str(doc.metadata.get("updated_at", "unknown")),
            }
        )

    return {
        "answer": result.get("answer", "I don't know."),
        "citations": citations,
    }
