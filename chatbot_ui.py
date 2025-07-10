# import gradio as gr
# import requests
# from openai import OpenAI
# import plotly.express as px
# import os
# from dotenv import load_dotenv
# import requests

# # Load API key from .env
# load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# API_BASE = "http://localhost:8000" 

# def ask_question(question, top_k=5, min_score=0.3):
#     # Step 1: Call similarity search API
#     try:
#         response = requests.post(f"{API_BASE}/api/similarity_search", json={
#             "query": question,
#             "k": top_k,
#             "min_score": min_score
#         })
#         response.raise_for_status()
#         results = response.json().get("matches", [])
#     except Exception as e:
#         return f"Error calling similarity search: {e}", "", None

#     if not results:
#         return "No relevant information found.", "", None

#     # Step 2: Build context with [Source X] tags
#     context = ""
#     for idx, chunk in enumerate(results, start=1):
#         context += f"[Source {idx}] {chunk['text']}\n\n"
#         chunk["source_number"] = idx  # Tag for citation building later

#     # Step 3: Prepare OpenAI prompt
#     prompt = f"""Use the context below to answer the user's question. 
# Cite sources inline using [Source X] format.

# {context}

# Question: {question}
# Answer:"""

#     try:
#         chat_response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.7
#         )
#         answer = chat_response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"OpenAI API error: {e}", "", results

#     # Step 4: Format citation details
#     citations = "Citations:\n"
#     for chunk in results:
#         idx = chunk["source_number"]
#         section = chunk.get("section_heading", "Unknown")
#         doc_id = chunk.get("source_doc_id", "Unknown")
#         journal = chunk.get("journal", "Unknown")
#         year = chunk.get("publish_year", "Unknown")
#         score = chunk.get("similarity_score", 0.0)
#         chunk_idx = chunk.get("chunk_index", "?")
#         link = chunk.get("link", "#")

#         citations += (
#             f"\nSource {idx}:\n"
#             f"- Journal: {journal} (chunk {chunk_idx})\n"
#             f"- Section: {section}\n"
#             f"- Document: {doc_id}\n"
#             f"- Published: {year}\n"
#             f"- Score: {score:.2f}\n"
#             f"- [Link]({link})\n"
#         )

#     return answer, citations, results

# def plot_chart(chunks):
#     if not chunks:
#         return None
#     df = {
#         "ID": [chunk.get("id", "") for chunk in chunks],
#         "Usage Count": [chunk.get("usage_count", 0) for chunk in chunks],
#         "Section": [chunk.get("section_heading", "") for chunk in chunks]
#     }
#     fig = px.bar(df, x="ID", y="Usage Count", hover_data=["Section"], title="Usage Count by Chunk ID")
#     fig.update_layout(xaxis_title="Chunk ID", yaxis_title="Usage Count")
#     return fig


# def get_doc_ids():
#     try:
#         res = requests.get(f"{API_BASE}/api/debug/list_all_chunks")
#         res.raise_for_status()
#         metadatas = res.json().get("metadatas", [])
#         doc_ids = list(set(md["source_doc_id"] for md in metadatas if "source_doc_id" in md))
#         return sorted(doc_ids)
#     except Exception as e:
#         print(f"Error fetching doc IDs: {e}")
#         return []



# def get_summary(doc_id):
#     try:
#         res = requests.get(f"{API_BASE}/api/summary/{doc_id}")
#         res.raise_for_status()
#         return res.json().get("summary", "No summary available.")
#     except Exception as e:
#         return f"Error generating summary: {e}"

# def compare_docs(doc1, doc2):
#     try:
#         res = requests.post(f"{API_BASE}/api/compare", json={
#             "doc1_id": doc1,
#             "doc2_id": doc2
#         })
#         res.raise_for_status()
#         return res.json().get("comparison", "No comparison available.")
#     except Exception as e:
#         return f"Error comparing documents: {e}"



# # doc_ids = get_doc_ids()

# # Gradio UI
# with gr.Blocks() as demo:
#     gr.Markdown("## GenAI Research Assistant")

#     with gr.Tab("Ask a Question"):
#         question = gr.Textbox(label="Ask a question", placeholder="e.g., What are the uses of velvet bean?")
#         submit = gr.Button("Submit")
#         answer = gr.Textbox(label="Answer", lines=5)
#         citations = gr.Textbox(label="Citations", lines=3)
#         show_chart = gr.Button("Show Chart")
#         chart = gr.Plot()
#         chunk_cache = gr.State()

#         submit.click(fn=ask_question, inputs=[question], outputs=[answer, citations, chunk_cache])
#         show_chart.click(fn=plot_chart, inputs=[chunk_cache], outputs=chart)

#     # with gr.Tab("Summarise Document"):
#     #     gr.Markdown("### Select a document to summarise")
#     #     doc_id = gr.Dropdown(choices=doc_ids, label="Select Document to Summarize")
#     #     sum_btn = gr.Button("Summarise")
#     #     summary_out = gr.Markdown(label="Summary")
#     #     sum_btn.click(fn=get_summary, inputs=doc_id, outputs=summary_out)

#     with gr.Tab("Summarise Document"):
#         gr.Markdown("### Select a document to summarise")
#         doc_id = gr.Dropdown(label="Select Document to Summarize", interactive=True)
#         sum_btn = gr.Button("Refresh & Summarise")
#         summary_out = gr.Markdown(label="Summary")

#         def refresh_and_summarise(selected_doc_id):
#             if not selected_doc_id:
#                 return "Please select a document."
#             return get_summary(selected_doc_id)

#         def refresh_doc_ids():
#             return gr.update(choices=get_doc_ids())

#         doc_id.change(fn=refresh_doc_ids, inputs=None, outputs=doc_id)
#         sum_btn.click(fn=refresh_and_summarise, inputs=doc_id, outputs=summary_out)

#     # with gr.Tab("Compare Papers"):
#     #     gr.Markdown("### Select Two Documents to Compare")
#     #     with gr.Row():
#     #         doc1 = gr.Dropdown(choices=doc_ids, label="Paper A", interactive=True)
#     #         doc2 = gr.Dropdown(choices=doc_ids, label="Paper B", interactive=True)
#     #     cmp_btn = gr.Button("Compare")
#     #     cmp_out = gr.Markdown(label="Comparison")
#     #     cmp_btn.click(fn=compare_docs, inputs=[doc1, doc2], outputs=cmp_out)

#     with gr.Tab("Compare Papers"):
#         gr.Markdown("### Select Two Documents to Compare")
#         with gr.Row():
#             doc1 = gr.Dropdown(label="Paper A", interactive=True)
#             doc2 = gr.Dropdown(label="Paper B", interactive=True)

#         cmp_btn = gr.Button("Compare")
#         cmp_out = gr.Markdown(label="Comparison")

#         def refresh_compare_ids():
#             doc_ids = get_doc_ids()
#             return gr.update(choices=doc_ids), gr.update(choices=doc_ids)

#         doc1.change(fn=refresh_compare_ids, inputs=None, outputs=[doc1, doc2])
#         doc2.change(fn=refresh_compare_ids, inputs=None, outputs=[doc1, doc2])

#         cmp_btn.click(fn=compare_docs, inputs=[doc1, doc2], outputs=cmp_out)

# demo.launch()


import gradio as gr
import requests
from openai import OpenAI
import plotly.express as px
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

API_BASE = "http://localhost:8000"

def ask_question(question, top_k=5, min_score=0.3):
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

    context = ""
    for idx, chunk in enumerate(results, start=1):
        context += f"[Source {idx}] {chunk['text']}\n\n"
        chunk["source_number"] = idx

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

def get_doc_ids():
    try:
        res = requests.get(f"{API_BASE}/api/debug/list_all_chunks")
        res.raise_for_status()
        metadatas = res.json().get("metadatas", [])
        doc_ids = list(set(md["source_doc_id"] for md in metadatas if "source_doc_id" in md))
        return sorted(doc_ids)
    except Exception as e:
        print(f"Error fetching doc IDs: {e}")
        return []

def get_summary(doc_id):
    try:
        res = requests.get(f"{API_BASE}/api/summary/{doc_id}")
        res.raise_for_status()
        return res.json().get("summary", "No summary available.")
    except Exception as e:
        return f"Error generating summary: {e}"

def compare_docs(doc1, doc2):
    try:
        res = requests.post(f"{API_BASE}/api/compare", json={
            "doc1_id": doc1,
            "doc2_id": doc2
        })
        res.raise_for_status()
        return res.json().get("comparison", "No comparison available.")
    except Exception as e:
        return f"Error comparing documents: {e}"

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## GenAI Research Assistant")

    with gr.Tab("Ask a Question"):
        question = gr.Textbox(label="Ask a question", placeholder="e.g., What are the uses of velvet bean?")
        submit = gr.Button("Submit")
        answer = gr.Textbox(label="Answer", lines=5)
        citations = gr.Textbox(label="Citations", lines=3)
        show_chart = gr.Button("Show Chart")
        chart = gr.Plot()
        chunk_cache = gr.State()
        submit.click(fn=ask_question, inputs=[question], outputs=[answer, citations, chunk_cache])
        show_chart.click(fn=plot_chart, inputs=[chunk_cache], outputs=chart)

    with gr.Tab("Summarise Document"):
        gr.Markdown("### Select a document to summarise")
        doc_id = gr.Dropdown(label="Select Document to Summarize", interactive=True)
        refresh_docs = gr.Button("Refresh Document List")
        sum_btn = gr.Button("Summarise")
        summary_out = gr.Markdown(label="Summary")

        refresh_docs.click(lambda: gr.update(choices=get_doc_ids()), outputs=doc_id)

        def format_summary(doc_id):
            summary = get_summary(doc_id)
            return f"### Summary\n\n{summary}"

        sum_btn.click(fn=format_summary, inputs=doc_id, outputs=summary_out)

    with gr.Tab("Compare Papers"):
        gr.Markdown("### Select Two Documents to Compare")
        doc1 = gr.Dropdown(label="Paper A", interactive=True)
        doc2 = gr.Dropdown(label="Paper B", interactive=True)
        refresh_cmp = gr.Button("Refresh Document List")
        cmp_btn = gr.Button("Compare")
        cmp_out = gr.Markdown(label="Comparison")

        refresh_cmp.click(lambda: [gr.update(choices=get_doc_ids())]*2, outputs=[doc1, doc2])
        cmp_btn.click(fn=compare_docs, inputs=[doc1, doc2], outputs=cmp_out)

demo.launch()
