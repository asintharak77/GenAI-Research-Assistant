import gradio as gr
import requests
from openai import OpenAI
import plotly.express as px
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

API_BASE = "http://localhost:8000"  # your FastAPI server

def ask_question(question, top_k=5, min_score=0.3):
    # Step 1: Call similarity search API
    try:
        response = requests.post(f"{API_BASE}/api/similarity_search", json={
            "query": question,
            "k": top_k,
            "min_score": min_score
        })
        response.raise_for_status()
        results = response.json().get("matches", [])
    except Exception as e:
        return f"Error calling similarity search: {e}", "", None

    if not results:
        return "No relevant information found.", "", None

    # Step 2: Build context with [Source X] tags
    context = ""
    for idx, chunk in enumerate(results, start=1):
        context += f"[Source {idx}] {chunk['text']}\n\n"
        chunk["source_number"] = idx  # Tag for citation building later

    # Step 3: Prepare OpenAI prompt
    prompt = f"""Use the context below to answer the user's question. 
Cite sources inline using [Source X] format.

{context}

Question: {question}
Answer:"""

    try:
        chat_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        answer = chat_response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI API error: {e}", "", results

    # Step 4: Format citation details
    citations = "Citations:\n"
    for chunk in results:
        idx = chunk["source_number"]
        section = chunk.get("section_heading", "Unknown")
        doc_id = chunk.get("source_doc_id", "Unknown")
        journal = chunk.get("journal", "Unknown")
        year = chunk.get("publish_year", "Unknown")
        score = chunk.get("similarity_score", 0.0)
        chunk_idx = chunk.get("chunk_index", "?")
        link = chunk.get("link", "#")

        citations += (
            f"\nSource {idx}:\n"
            f"- Journal: {journal} (chunk {chunk_idx})\n"
            f"- Section: {section}\n"
            f"- Document: {doc_id}\n"
            f"- Published: {year}\n"
            f"- Score: {score:.2f}\n"
            f"- [Link]({link})\n"
        )

    return answer, citations, results

def plot_chart(chunks):
    if not chunks:
        return None
    df = {
        "ID": [chunk.get("id", "") for chunk in chunks],
        "Usage Count": [chunk.get("usage_count", 0) for chunk in chunks],
        "Section": [chunk.get("section_heading", "") for chunk in chunks]
    }
    fig = px.bar(df, x="ID", y="Usage Count", hover_data=["Section"], title="Usage Count by Chunk ID")
    fig.update_layout(xaxis_title="Chunk ID", yaxis_title="Usage Count")
    return fig


# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 🤖 GenAI Research Assistant Chatbot")

    question = gr.Textbox(label="Ask a question", placeholder="e.g., What are the uses of velvet bean?")
    submit = gr.Button("Submit")

    answer = gr.Textbox(label="Answer", lines=5)
    citations = gr.Textbox(label="Citations", lines=3)
    show_chart = gr.Button("Show Chart")
    chart = gr.Plot()

    chunk_cache = gr.State()

    submit.click(fn=ask_question, inputs=[question], outputs=[answer, citations, chunk_cache])
    show_chart.click(fn=plot_chart, inputs=[chunk_cache], outputs=chart)

demo.launch()
