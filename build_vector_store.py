import pandas as pd
from llama_index.core import VectorStoreIndex, Document
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
import chromadb
import streamlit as st
import os

# Securely get OpenAI API key
api_key = st.secrets["openai"]["key"] if "openai" in st.secrets else os.getenv("OPENAI_API_KEY")

# Read and clean the CSV
df = pd.read_csv("faq_chatbot_ready.csv", on_bad_lines='skip')
df = df.dropna(subset=["question", "answer"])  # ❗ This is the fix

# Prepare documents
documents = [
    Document(
        text=row["answer"],
        metadata={"question": row["question"]}
    )
    for _, row in df.iterrows()
]

# Setup Chroma and vector store
chroma_client = chromadb.PersistentClient(path="./llamachromadb")
collection = chroma_client.get_or_create_collection("rcsilib")
vector_store = ChromaVectorStore(chroma_collection=collection)

# Indexing with embedding model
embedding = OpenAIEmbedding(api_key=api_key)
index = VectorStoreIndex.from_documents(
    documents, vector_store=vector_store, embed_model=embedding
)

print("✅ Indexing completed.")
