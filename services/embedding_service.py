import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("No api key in .env")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 3072

def embed_text(text: str , task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:

    if not text or not text.strip():
        raise ValueError("Text is empty...")

    response = client.models.embed_content(
        model = MODEL_NAME,
        contents= text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=EMBEDDING_DIMENSIONS,
        ),
    )

    if not response.embeddings:
        raise ValueError("Gemini haven't returned the embeddings")

    vector = response.embeddings[0].values

    if len(vector) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
            f"got {len(vector)}"
        )

    return vector