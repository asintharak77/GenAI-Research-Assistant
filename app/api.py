from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from app.embedding import get_embedding
from app.vector_db import add_chunk_to_db
from app.vector_db import get_all_chunks

router = APIRouter()

@router.get("/")
def health_check():
    return {"message": "GenAI API is running"}

# Define the input schema using Pydantic
class Chunk(BaseModel):
    id: str
    source_doc_id: str
    chunk_index: int
    section_heading: str
    journal: str
    publish_year: int
    usage_count: int
    attributes: List[str]
    link: Optional[str] = None
    doi: Optional[str] = None
    text: str

# Endpoint to upload chunks
@router.put("/api/upload")
def upload_chunks(chunks: List[Chunk]):
    for chunk in chunks:
        try:
            embedding = get_embedding(chunk.text)

            metadata_raw = {
                "id": chunk.id,
                "source_doc_id": chunk.source_doc_id,
                "chunk_index": chunk.chunk_index,
                "section_heading": chunk.section_heading,
                "journal": chunk.journal,
                "publish_year": chunk.publish_year,
                "usage_count": chunk.usage_count,
                "attributes": ", ".join(chunk.attributes),
                "link": chunk.link,
                "doi": chunk.doi,
                "text": chunk.text
            }
            metadata = {k: v for k, v in metadata_raw.items() if v is not None}
            add_chunk_to_db(id=chunk.id, embedding=embedding, metadata=metadata)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse({"message": f"{len(chunks)} chunks uploaded successfully."})

# Endpoint to similarity search
from fastapi import Query
from app.vector_db import query_chunks

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5

@router.post("/api/similarity_search")
def search_similar_chunks(request: SearchRequest):
    try:
        embedding = get_embedding(request.query)
        results = query_chunks(embedding=embedding, k=request.top_k)

        # Return formatted matches
        formatted = []
        for doc, metadata, score in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
            metadata["text"] = doc
            metadata["similarity_score"] = round(score, 3)
            formatted.append(metadata)

        return {"matches": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint to get all chunks by document ID
from app.vector_db import get_all_by_doc_id

@router.get("/api/{journal_id}")
def get_chunks_by_journal(journal_id: str):
    print("🔍 Looking for doc_id:", journal_id)
    try:
        results = get_all_by_doc_id(doc_id=journal_id.strip())

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        # Combine document text with metadata only if metadata is a dict
        chunks = []
        for doc, meta in zip(documents, metadatas):
            if isinstance(meta, dict):
                combined = meta.copy()
                combined["text"] = doc
                chunks.append(combined)

        # Sort the chunks by chunk_index
        chunks = sorted(chunks, key=lambda x: x.get("chunk_index", 0))

        return {"chunks": chunks}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# endpoint to print all entries
@router.get("/api/debug/show_all")
def debug_show_all():
    results = get_all_chunks()
    return results

@router.get("/api/debug/list_doc_ids")
def list_all_doc_ids():
    from app.vector_db import collection
    data = collection.get()
    
    doc_ids = []
    for meta in data.get("metadatas", [[]])[0]:
        if isinstance(meta, dict):
            doc_ids.append(meta.get("source_doc_id"))
    return {"stored_source_doc_ids": doc_ids}
