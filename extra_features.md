# Optional Stretch Features Implemented

The following optional enhancements were implemented beyond the core requirements:

## Gradio Frontend UI
A fully functional Gradio-based chatbot interface is provided, allowing users to:
- Ask questions in natural language
- Internally call /api/similarity_search endpoint
- Display OpenAI-generated answers
- Show citations and usage insights
- Generate summary of documents selected
- Compare two different documents

## Content Generation via OpenAI
The system uses OpenAI's GPT for advanced content generation:
- Generate answers using semantically matched chunks
- Embed inline citations like [Source 1] in the answer
- Return full citation metadata (document, section, year, score, link)

## Summarize Academic Documents
Users can generate concise summaries of entire academic documents by selecting a source document ID
- Utilizes OpenAI GPT to understand and summarize the full content
- Works on all uploaded or ingested documents
- Helps quickly grasp the key ideas and findings of a paper

## Compare Two Academic Documents
This feature allows users to compare two selected documents side-by-side, with AI-generated analysis covering:
* Key Similarities
* Key Differences
* Methods Used
* Topics Covered
* Conclusions
Perfect for evaluating research papers, identifying overlaps, or understanding methodological contrasts.