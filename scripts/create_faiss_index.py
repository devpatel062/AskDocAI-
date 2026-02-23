from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

DATA_PATH = Path("./data/medical_data.json")
OUTPUT_DIR = Path("./vector_store_pubmed")


def load_documents(data_path: Path) -> list[Document]:
    if not data_path.exists():
        print(f"Warning: {data_path} not found. Using default sample data.")
        return [
            Document(
                page_content="Question: What are common viral infection symptoms?\n"
                "Answer: Fever and headache are common symptoms of viral infections.",
                metadata={"source": "sample_data", "id": "sample-1"},
            ),
            Document(
                page_content="Question: What is diabetes?\n"
                "Answer: Diabetes is a condition that affects insulin regulation.",
                metadata={"source": "sample_data", "id": "sample-2"},
            ),
        ]

    with data_path.open("r", encoding="utf-8") as f:
        data: list[dict[str, Any]] = json.load(f)

    docs: list[Document] = []
    for idx, entry in enumerate(data):
        question = (entry.get("question") or "").strip()
        answer = (entry.get("answer") or "").strip()
        if not question or not answer:
            continue

        text = f"Question: {question}\nAnswer: {answer}"
        metadata = {
            "id": str(entry.get("id") or f"doc-{idx + 1}"),
            "source": entry.get("source") or "medical_data.json",
            "updated_at": entry.get("updated_at") or "unknown",
            "question": question,
        }
        docs.append(Document(page_content=text, metadata=metadata))

    return docs


def main() -> None:
    docs = load_documents(DATA_PATH)
    if not docs:
        raise ValueError(f"No valid QA pairs found in {DATA_PATH}")

    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(docs, embedding_model)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    db.save_local(str(OUTPUT_DIR))

    print(f"Indexed {len(docs)} documents")
    print("✅ FAISS vector store created in:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
