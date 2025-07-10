# Optional Stretch Features Implemented

The following optional enhancements were implemented beyond the core requirements:

## Gradio Frontend UI
A fully functional Gradio-based chatbot interface is provided, allowing users to:
- Ask questions in natural language
- Internally call /api/similarity_search endpoint
- Display OpenAI-generated answers
- Show citations and usage insights

## Content Generation via OpenAI
The system uses OpenAI's GPT to:
- Generate answers using semantically matched chunks
- Embed inline citations like [Source 1] in the answer
- Return full citation metadata (document, section, year, score, link)