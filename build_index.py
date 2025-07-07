import pandas as pd
from llama_index.core import VectorStoreIndex, Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import os

# Load your OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not set in environment variables.")

embedding = OpenAIEmbedding(api_key=api_key)

# Load the CSV file and convert each row to a Document
df = pd.read_csv("faq_chatbot_ready.csv", on_bad_lines="skip")

documents = [
    Document(text=f"Q: {row['question']}\nA: {row['answer']}")
    for _, row in df.iterrows()
]

# Initialize and store in ChromaDB
chroma_client = chromadb.PersistentClient(path="./llamachromadb")
collection = chroma_client.get_or_create_collection("rcsilib")
vector_store = ChromaVectorStore(chroma_collection=collection)

# Build the index
index = VectorStoreIndex.from_documents(documents, embed_model=embedding, vector_store=vector_store)

print("✅ Indexing completed. Your FAQs are now ready to be retrieved by the chatbot.")
