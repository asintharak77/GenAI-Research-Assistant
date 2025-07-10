# Ingestion Pipeline for Journal Files

This document outlines the ingestion pipeline for detecting, processing, and storing journal files in a vector database (ChromaDB). The pipeline meets the following requirements:
- Detect newly uploaded journal files (`.json`).
- Chunk content into coherent segments.
- Generate embeddings for each chunk.
- Attach minimal metadata: `id`, `source_doc_id`, `section_heading`, `journal`, `publish_year`, `usage_count`, `attributes`.
- Write results to a vector database.

The pipeline addresses previous issues, such as ChromaDB metadata errors (`"Invalid metadata format: source_doc_id"`) and limited similarity search results, ensuring all chunks are stored correctly and retrievable for queries like `"What are the uses of velvet bean?"`.

## Pseudocode

```pseudo
// Ingestion Pipeline for Journal Files
// Requirements: Detect new journal files, chunk content, generate embeddings, attach metadata, write to vector database

// Constants
STATIC_DIR = "app/static"  // Directory where journal files are uploaded
VECTOR_DB_NAME = "journal_chunks"
DISTANCE_METRIC = "cosine"
SCHEMA_VERSION = "1.0"

// Initialize vector database client
client = InitializeVectorDBClient("chromadb_store")
collection = client.GetOrCreateCollection(name=VECTOR_DB_NAME, metadata={"hnsw:space": DISTANCE_METRIC})

// Initialize embedding model
embedding_model = LoadEmbeddingModel("all-MiniLM-L6-v2")

// Function: Ingestion Pipeline
Function RunIngestionPipeline():
    // Step 1: Detect newly uploaded journal files
    new_files = MonitorDirectory(STATIC_DIR, file_extension=".json")
    If new_files is empty:
        Log("No new journal files detected")
        Return

    // Step 2: Process each new file
    For each file in new_files:
        Try:
            // Read and parse JSON file
            journal_data = ReadJSONFile(file)
            If journal_data is invalid:
                LogError("Invalid JSON format in file: " + file)
                Continue

            // Step 3: Chunk the content
            chunks = ChunkContent(journal_data)
            If chunks is empty:
                LogError("No chunks created for file: " + file)
                Continue

            // Step 4: Generate embeddings and attach metadata
            processed_chunks = []
            For each chunk in chunks:
                // Generate embedding
                embedding = embedding_model.GenerateEmbedding(chunk.text)
                
                // Create metadata
                metadata = {
                    source_doc_id: chunk.source_doc_id,
                    section_heading: chunk.section_heading,
                    journal: chunk.journal,
                    publish_year: chunk.publish_year,
                    usage_count: chunk.usage_count,
                    attributes: Join(chunk.attributes, ","),
                    schema_version: SCHEMA_VERSION
                }
                // "id" is stored separately via `ids`, and "text" is stored as `documents`

                // Remove null values from metadata
                metadata = FilterNullValues(metadata)
                
                processed_chunks.Append({
                    id: chunk.id,
                    embedding: embedding,
                    metadata: metadata,
                    text: chunk.text
                })

            // Step 5: Write to vector database
            For each processed_chunk in processed_chunks:
                Try:
                    collection.Add(
                        ids: [processed_chunk.id],
                        embeddings: [processed_chunk.embedding],
                        metadatas: [processed_chunk.metadata],
                        documents: [processed_chunk.text]
                    )
                    Log("Added chunk " + processed_chunk.id + " to vector database")
                Catch error:
                    LogError("Failed to add chunk " + processed_chunk.id + ": " + error)
                    Continue

            Log("Successfully processed file: " + file)
        Catch error:
            LogError("Failed to process file: " + file + ": " + error)
            Continue

// Function: Monitor directory for new files
Function MonitorDirectory(directory, file_extension):
    // Check directory for files with specified extension
    all_files = ListFiles(directory, file_extension)
    // Load previously processed files from a log (e.g., database or file)
    processed_files = LoadProcessedFilesLog()
    // Return files that haven’t been processed
    Return all_files.Filter(file => NotIn(file, processed_files))

// Function: Chunk content into coherent segments
Function ChunkContent(journal_data):
    chunks = []
    For each section in journal_data.sections:
        // Split section text into segments based on size or semantic boundaries
        section_chunks = SplitText(section.text, max_size=500, separator="paragraph")
        For index, chunk_text in Enumerate(section_chunks):
            chunk = {
                id: GenerateUniqueID(journal_data.source_doc_id + "_" + section.heading + "_" + index),
                source_doc_id: journal_data.source_doc_id,
                chunk_index: index + 1,
                section_heading: section.heading,
                journal: journal_data.journal,
                publish_year: journal_data.publish_year,
                usage_count: journal_data.usage_count or 0,
                attributes: ExtractAttributes(chunk_text),
                link: journal_data.link,
                doi: journal_data.doi,
                text: chunk_text
            }
            chunks.Append(chunk)
    Return chunks

// Function: Extract attributes from text
Function ExtractAttributes(text):
    // Use NLP or rule-based method to extract keywords/tags
    attributes = AnalyzeTextForKeywords(text)
    Return attributes

// Function: Generate unique ID
Function GenerateUniqueID(base_string):
    // Combine base_string with timestamp or UUID
    Return base_string + "_" + GenerateUUID()

// Function: Filter null values from metadata
Function FilterNullValues(metadata):
    Return {key: value for key, value in metadata if value is not null}
```

## Code Explanation

**1. Detect Newly Uploaded Journal Files**
The MonitorDirectory() function scans a directory (STATIC_DIR) for .json files that haven’t been processed before. It compares against a log of previously ingested files to ensures that duplicate or already ingested files are skipped

**2. Chunk Content into Coherent Segments**
The ChunkContent() function takes each journal's content and splits it into coherent chunks. It extracts content based on semantic boundaries. This section also preserves metadata.

**3. Generate Embeddings**
Each chunk’s text is passed to an embedding model. Here, raw text is converted into a numerical vector representation. This enables semantic search later via vector similarity like cosine similarity.

**4. Attach Metadata per Chunk**
Minimal metadata is assembled into a dictionary for each chunk. Metadata includes: id, source_doc_id, section_heading, journal, publish_year, usage_count, attributes, and schema_version. The dictionary is cleaned using FilterNullValues() to remove empty or invalid fields before storing.

**5. Write Results to Vector Database (ChromaDB)**
Each chunk is added to the journal_chunks collection in ChromaDB. 






> **Note**:  
> `id` and `text` are not stored inside `metadata`.  
> - `id` is stored using the `ids` parameter.  
> - `text` is stored using the `documents` parameter.  
> - Both are reattached manually during retrieval (e.g., similarity search) for accurate formatting and citation in responses.
