
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import requests
import json
from fastapi import Query
from openai import OpenAI
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from app.vector_db import collection
from app.embedding import get_embedding
from app.vector_db import add_chunk_to_db, query_chunks, get_chunks_by_doc_id

load_dotenv()
client = OpenAI()

router = APIRouter()

@router.get("/")
def health_check():
    return {"message": "GenAI API is running"}

# Define the chunk schema
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

# Define the upload request schema
class UploadRequest(BaseModel):
    file_url: Optional[HttpUrl] = None
    chunks: Optional[List[Chunk]] = None
    schema_version: str

# Endpoint to upload chunks
@router.put("/api/upload", status_code=status.HTTP_202_ACCEPTED)
def upload_chunks(request: UploadRequest):
    if not request.file_url and not request.chunks:
        raise HTTPException(status_code=400, detail="Either file_url or chunks must be provided")
    if request.file_url and request.chunks:
        raise HTTPException(status_code=400, detail="Provide either file_url or chunks, not both")

    if not request.schema_version:
        raise HTTPException(status_code=400, detail="schema_version is required")

    chunks = []
    if request.file_url:
        try:
            response = requests.get(request.file_url)
            response.raise_for_status()
            chunks_data = response.json()
            chunks = [Chunk(**chunk) for chunk in chunks_data]
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch file from URL: {str(e)}")
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format in file: {str(e)}")
    else:
        chunks = request.chunks

    try:
        for chunk in chunks:
            embedding = get_embedding(chunk.text)
            metadata_raw = {
                "source_doc_id": chunk.source_doc_id,
                "chunk_index": chunk.chunk_index,
                "section_heading": chunk.section_heading,
                "journal": chunk.journal,
                "publish_year": chunk.publish_year,
                "usage_count": chunk.usage_count,
                "attributes": ",".join(chunk.attributes),
                "link": chunk.link,
                "doi": chunk.doi,
                "text": chunk.text,
                "schema_version": request.schema_version
            }
            metadata = {k: v for k, v in metadata_raw.items() if v is not None}
            add_chunk_to_db(id=chunk.id, embedding=embedding, metadata=metadata)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process chunks: {str(e)}")

    return JSONResponse(
        content={"message": f"{len(chunks)} chunks uploaded successfully."},
        status_code=status.HTTP_202_ACCEPTED
    )

# Search request schema
class SearchRequest(BaseModel):
    query: str
    k: Optional[int] = 10
    min_score: Optional[float] = 0.25

# Endpoint for similarity search
@router.post("/api/similarity_search")
def search_similar_chunks(request: SearchRequest):
    try:
        embedding = get_embedding(request.query)
        results = query_chunks(embedding=embedding, k=request.k)

        # Unpack the first (and only) batch of results
        ids = results['ids'][0]
        docs = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0]

        formatted = []
        for doc_id, doc, metadata, distance in zip(ids, docs, metadatas, distances):
            if not isinstance(metadata, dict):
                print(f"Debug: Invalid metadata format for id {doc_id}: {metadata}")
                continue

            chunk_data = metadata.copy()
            chunk_data["id"] = doc_id
            chunk_data["text"] = doc
            chunk_data["similarity_score"] = round(1 - distance, 3)  # Convert distance to similarity

            # Deserialize attributes from comma-separated string to list
            if "attributes" in chunk_data and isinstance(chunk_data["attributes"], str):
                chunk_data["attributes"] = chunk_data["attributes"].split(",")
            else:
                chunk_data["attributes"] = []

            if chunk_data["similarity_score"] >= request.min_score:
                formatted.append(chunk_data)

        # Sort results by similarity score descending
        formatted = sorted(formatted, key=lambda x: x["similarity_score"], reverse=True)

        return {"matches": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Endpoint to get chunks by journal ID
@router.get("/api/{doc_id}")
def get_document_chunks(doc_id: str):
    try:
        results = get_chunks_by_doc_id(doc_id)
        print(f"Debug: get_chunks_by_doc_id('{doc_id}') results: {results}")

        if not results.get('ids') or not results['ids']:
            raise HTTPException(status_code=404, detail=f"No chunks found for journal_id: {doc_id}")

        formatted = []
        for doc_id, doc, metadata in zip(results['ids'], results['documents'], results['metadatas']):
            if not isinstance(metadata, dict):
                print(f"Debug: Invalid metadata format for id {doc_id}: {metadata}")
                continue
            chunk_data = metadata.copy()
            chunk_data["id"] = doc_id  # Reattach id
            chunk_data["text"] = doc
            if "attributes" in chunk_data and isinstance(chunk_data["attributes"], str) and chunk_data["attributes"]:
                chunk_data["attributes"] = chunk_data["attributes"].split(",")
            else:
                chunk_data["attributes"] = []

            formatted.append(chunk_data)

        if not formatted:
            raise HTTPException(status_code=404, detail=f"No valid chunks found for journal_id: {doc_id}")

        formatted = sorted(formatted, key=lambda x: x.get("chunk_index", 0))

        return {"chunks": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chunks: {str(e)}")
    

# Summary of documents
@router.get("/api/summary/{doc_id}")
def generate_summary(doc_id: str):
    try:
        results = get_chunks_by_doc_id(doc_id)
        if not results.get("documents"):
            raise HTTPException(status_code=404, detail="Document not found")

        # Concatenate all chunk texts
        combined_text = "\n\n".join(results["documents"])

        prompt = f"Summarize the following academic document:\n\n{combined_text}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        summary = response.choices[0].message.content.strip()
        return {"summary": summary}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Comparison endpoint
class CompareRequest(BaseModel):
    doc1_id: str
    doc2_id: str

@router.post("/api/compare")
def compare_documents(request: CompareRequest):
    try:
        # Retrieve chunks for both documents
        chunks1 = get_chunks_by_doc_id(request.doc1_id)
        chunks2 = get_chunks_by_doc_id(request.doc2_id)

        if not chunks1.get("documents") or not chunks2.get("documents"):
            raise HTTPException(status_code=404, detail="One or both documents not found")

        # Combine all text from both documents
        text1 = "\n\n".join(chunks1["documents"])
        text2 = "\n\n".join(chunks2["documents"])

        # Build the comparison prompt
        prompt = f"""Compare the following two academic documents:

        --- Paper A ({request.doc1_id}) ---
        {text1}

        --- Paper B ({request.doc2_id}) ---
        {text2}

        Please generate a structured comparison with the following sections:
        1. Key Similarities
        2. Key Differences
        3. Methods Used
        4. Topics Covered
        5. Conclusions

        Be concise and bullet-point the content under each section.
        """

        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        comparison = response.choices[0].message.content.strip()
        return {"comparison": comparison}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@router.get("/api/debug/list_all_chunks")
def list_all_chunks():
    data = collection.get()
    return {
        "ids": data.get("ids", []),
        "num_chunks": len(data.get("ids", [])),
        "metadatas": data.get("metadatas", [])
    }

