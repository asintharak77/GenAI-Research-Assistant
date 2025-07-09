import os
import chromadb
from typing import List, Dict

# Ensure ChromaDB directory exists
os.makedirs("chromadb_store", exist_ok=True)

# Initialize Chroma client
client = chromadb.PersistentClient(path="chromadb_store")
collection = client.get_or_create_collection(name="journal_chunks", metadata={"hnsw:space": "cosine"})

def add_chunk_to_db(id: str, embedding: List[float], metadata: Dict):
    print(f"Embedding preview for {id}: {embedding[:5]}")  # Debug line
    collection.add(
        ids=[id],
        embeddings=[embedding],
        metadatas=[metadata],
        documents=[metadata["text"]]
    )

def query_chunks(embedding: List[float], k: int):
    results = collection.query(
        query_embeddings=[embedding],
        n_results=k,
        include=["distances", "metadatas", "documents"]  # include everything needed
    )
    print(f"Search raw results: {results}")  # for debugging
    return results

def get_chunks_by_doc_id(doc_id: str):
    results = collection.get(
        where={"source_doc_id": doc_id}
    )
    print(f"Debug: get_chunks_by_doc_id('{doc_id}') results: {results}")
    return results

