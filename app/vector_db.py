
import chromadb
from chromadb.config import Settings
from typing import List

# New way to initialize Chroma client (as of mid-2024)
client = chromadb.PersistentClient(path="chromadb_store")

# Create or get collection
collection = client.get_or_create_collection(name="journal_chunks")

def add_chunk_to_db(id: str, embedding: List[float], metadata: dict):
    collection.add(
        ids=[id],
        embeddings=[embedding],
        metadatas=[metadata],
        documents=[metadata["text"]]
    )

def query_chunks(embedding: List[float], k=10):
    return collection.query(
        query_embeddings=[embedding],
        n_results=k
    )

def get_all_by_doc_id(doc_id: str):
    all_data = collection.get(include=["documents", "metadatas"])

    matching_documents = []
    matching_metadatas = []

    for doc, meta in zip(all_data["documents"], all_data["metadatas"]):
        if isinstance(meta, dict) and meta.get("source_doc_id") == doc_id:
            matching_documents.append(doc)
            matching_metadatas.append(meta)

    return {
        "documents": [matching_documents],
        "metadatas": [matching_metadatas]
    }




def get_all_chunks():
    return collection.get()
