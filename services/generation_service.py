import os
from dotenv import load_dotenv
from google import genai
import time    

start_time = time.time()
print("Sending request to Gemini...")


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY .env mein nahi mili.")

client = genai.Client(api_key=api_key)

MODEL_NAME ="gemini-3.5-flash"


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    if not question or not question.strip():
        raise ValueError("Question empty nahi hona chahiye.")

    if not context_chunks:
        return "Is document mein answer dene ke liye relevant information nahi mili."

    # Retrieved chunks ko context mein convert karo
    context_parts = []

    for chunk in context_chunks:
        page = chunk.get("page_number", "Unknown")
        content = chunk.get("content", "")

        context_parts.append(
            f"[Page {page}]\n{content}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are an AI Tutor.

Answer the student's question using ONLY the provided context.

Rules:
1. Explain the answer in simple language.
2. Do not invent facts that are not supported by the context.
3. If the context does not contain the answer, clearly say so.
4. Mention the relevant page numbers when possible.

CONTEXT:
{context}

STUDENT QUESTION:
{question}

ANSWER:
"""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config = {
                "http_options":{"timeout" : 60000}
            }
        )
        print(f"response recieved in {time.time() - start_time:.1f} seconds")
    except Exception as e:
        print(f"Generation failed after {time.time() - start_time:.1f} seconds")
        print(f"Error: {e}")
        raise
    answer = response.text

    if not answer:
        raise ValueError("Gemini ne koi answer return nahi kiya.")

    return answer.strip()