from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
import os

# Sample documents
docs = [
    "Fever and headache are common symptoms of viral infections.",
    "Diabetes is a condition that affects insulin regulation.",
    "The heart pumps blood through the circulatory system.",
    "COVID-19 is a respiratory illness caused by a virus."
]

# Load embedding model
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Create FAISS index
db = FAISS.from_texts(docs, embedding_model)

# Save index to vector_store_pubmed directory
output_dir = "./vector_store_pubmed"
os.makedirs(output_dir, exist_ok=True)
db.save_local(output_dir)

print("✅ FAISS vector store created in:", output_dir)
