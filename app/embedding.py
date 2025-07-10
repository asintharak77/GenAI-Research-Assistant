# OPEN AI API call for embeddings

import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_embedding(text: str) -> list:
    response = openai.embeddings.create(
        input=[text], 
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding
    print(f"Generated embedding: {embedding[:5]}") 
    return embedding


# --------------------

# # Sentence Transformers for embeddings

# from sentence_transformers import SentenceTransformer

# # Load the pre-trained embedding model (small & fast)
# model = SentenceTransformer("all-MiniLM-L6-v2")

# def get_embedding(text: str) -> list:
#     embedding = model.encode(text)
#     print(f"Generated embedding: {embedding[:5]}")
#     return embedding.tolist()
