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

### Upload file
```bash
PUT /api/upload

{
  "file_url": "http://localhost:8000/static/sample_json.json",
  "schema_version": "1.0"
}```


