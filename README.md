
# RAG-Based AI Tutor

A Retrieval-Augmented Generation (RAG) API for an AI Tutor system. It retrieves relevant information from uploaded PDF documents and uses a Large Language Model (LLM) to generate context-aware answers.

## Features

- PDF document ingestion
- Text extraction and chunking
- Google Gemini embeddings
- Vector search using Supabase and pgvector
- Context-aware answer generation
- Source references in responses
- Global and student-specific document retrieval
- API authentication using a bearer token
- FastAPI backend

## Tech Stack

- Python
- FastAPI
- Google Gemini API
- Supabase
- PostgreSQL with pgvector
- PyPDF

## Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd minor_project_rags_implementation
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a reference.

Fill in your own API keys and configuration values. Never commit real secrets to GitHub.

### 5. Run the API

```bash
uvicorn main:app --reload
```

### 6. Open API documentation

Visit:

http://127.0.0.1:8000/docs

## API Endpoints

- `GET /health` — Check API health
- `POST /api/rag/v1/query` — Ask a question using retrieved document context
- `POST /api/rag/v1/documents/ingest` — Upload and ingest a PDF document

## Security Notes

- Keep `.env` and all API keys private.
- Use authenticated, authorized student and course IDs.
- Do not expose the RAG API secret in frontend code.

## Project Status

Core ingestion, retrieval, and answer generation have been tested. Further integration, testing, and production hardening are ongoing.
