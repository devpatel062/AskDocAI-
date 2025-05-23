from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.llms import HuggingFacePipeline
from langchain.chains import ConversationalRetrievalChain
import torch

from langchain_community.embeddings import SentenceTransformerEmbeddings
embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

db = FAISS.load_local("./vector_store_pubmed", embeddings=embedding_model, allow_dangerous_deserialization=True)

llm = HuggingFacePipeline.from_model_id(
    model_id="meta-llama/Llama-2-7b-chat-hf",
    task="text-generation",
    device=0 if torch.cuda.is_available() else -1
)

qa_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=db.as_retriever())

def ask_question(query, history):
    chat_history = [(h, "") for h in history]
    return qa_chain.run({"question": query, "chat_history": chat_history})

