# GenAI-Research-Assistant

This is a research assistant tool powered by OpenAI embeddings and LLMs. It ingests academic journal chunks, stores them in a vector database (ChromaDB), and provides a Gradio chatbot UI to ask questions with contextual answers, proper citations, and usage charts.

## Features

* Upload journal chunks via URL or JSON  
* Semantic search using OpenAI embeddings  
* Gradio chatbot UI with:  
  * Q & A with tehe help of LLM
  * Source citations (with similarity score and links)  
  * Usage count chart (Plotly)  
* Vector search via ChromaDB  
* FastAPI backend with RESTful endpoints


## Project Structure

```
├── app/
│ ├── api.py # FastAPI endpoints
│ ├── main.py # App entry point
│ ├── embedding.py # Embedding logic (OpenAI)
│ ├── vector_db.py # ChromaDB integration
│ └── static/
│ └── sample_json.json # Sample input data
├── chatbot_ui.py # Gradio chatbot frontend
├── ingestion_design.md # Pseudocode + logic for ingestion
├── requirements.txt # Dependencies
├── estimates.csv # Time estimates (optional)
└── .gitignore
```

---

## Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/genai-research-assistant.git
cd genai-research-assistant
```

### 2. Create Virtual Environment & Install Requirements

```bash
conda create -n genai python=3.11
conda activate genai
pip install -r requirements.txt
```

### 3. Add Your OpenAI API Key

Create a .env file in the root directory.
```bash
OPENAI_API_KEY=your-openai-api-key
```

## Running the Application

### 1. Start FastAPI backend
```bash
uvicorn app.main:app --reload
```

### 2. Launch the Gradio chatbot UI
```bash
python chatbot_ui.py
```

## Sample Usage

### 1. a. Upload file
```bash
PUT /api/upload

{
  "file_url": "http://localhost:8000/static/sample_json.json",
  "schema_version": "1.0"
}
```

### 1. b. Upload chunk
```bash
PUT /api/upload

{
    "chunks": [
        {
            "id": document_id,
            "source_doc_id": ...,
            "chunk_index": 1,
            "section_heading": ...,
            "journal": ...,
            "publish_year": ...,
            "usage_count": ...,
            "attributes": ...,
            "link": ...,
            "text": "..."
        }
    ],
    "schema_version": "1.0"
}
```

### 2. Similarity search
```bash
POST /api/similarity_search

{
  "query": "What are the uses of velvet bean?",
  "k": 3,
  "min_score": 0.25
}
```

### 3. Get Chunks by Journal
```bash
GET /api/{journal_id}
```
Example:
GET /api/extension_brief_mucuna.pdf


## Chatbot Features
- Answer questions using semantically matched journal content
- Citations include: source, section, journal, year, score
- Interactive usage chart (Plotly)

## Sample JSON
Located at: ```app/static/sample_json.json```

## Ingestion Pipeline Design
For design pseudocode and explanations of:
- Chunking logic
- Metadata schema
- Embedding generation
- Storage flow in ChromaDB

Choice of VectorDB is also discussed here.

Refer to: ```ingestion_design.md```

## Extra features

I have explored some of the optional stretch features.
- Frontend UI using Gradio that lets users ask a natural-language question, calls /similarity_search, sends results to an LLM, and displays the generated answer.

## Requirements
Dependencies are listed in ```requirements.txt```

## Demo Video


