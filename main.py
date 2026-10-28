import os
import secrets
from uuid import UUID

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from services.retrieval_service import retrieve_chunks
from services.generation_service import generate_answer

import tempfile
from pathlib import Path

from fastapi import File, Form, UploadFile
from services.ingestion_service import ingest_pdf

load_dotenv()

app = FastAPI(
    title="Master Path RAG Service",
    version="1.0.0",
)
bearer_scheme = HTTPBearer()


class QueryRequest(BaseModel):
    student_id: str
    course_id: str
    question: str = Field(min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=10)


def verify_api_key(authorization: str | None) -> None:
    expected_key = os.getenv("RAG_API_KEY")

    if not expected_key:
        print("RAG_API_KEY is not configured.")
        raise HTTPException(
            status_code=500,
            detail="Service authentication is not configured.",
        )

    expected_header = f"Bearer {expected_key}"

    if (
        authorization is None
        or not secrets.compare_digest(
            authorization.strip(),
            expected_header,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid service credential.",
        )


@app.get("/health")
def health():
    return {"status": "ok"}





@app.post("/api/rag/v1/documents/ingest")
def ingest_document(
    course_id: str = Form(...),
    scope: str = Form(...),
    owner_user_id: str | None = Form(default=None),
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    verify_api_key(f"Bearer {credentials.credentials}")

    try:
        course_id = str(UUID(course_id))

        if scope not in ("global", "student"):
            raise HTTPException(
                status_code=400,
                detail="scope must be 'global' or 'student'.",
            )

        if scope == "global":
            if owner_user_id is not None:
                raise HTTPException(
                    status_code=400,
                    detail="Global documents must not have an owner_user_id.",
                )
        else:
            if not owner_user_id:
                raise HTTPException(
                    status_code=400,
                    detail="owner_user_id is required for student documents.",
                )
            owner_user_id = str(UUID(owner_user_id))

        if not file.filename or not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Please upload a PDF file.",
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / Path(file.filename).name

            with pdf_path.open("wb") as destination:
                while True:
                    chunk = file.file.read(1024 * 1024)
                    if not chunk:
                        break
                    destination.write(chunk)

            result = ingest_pdf(
                file_path=str(pdf_path),
                course_id=course_id,
                scope=scope,
                owner_user_id=owner_user_id,
            )

        return result

    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        print(f"Document ingestion failed: {type(error).__name__}: {error}")
        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed.",
        ) from error
    finally:
        file.file.close()



@app.post("/api/rag/v1/query")
def query_rag(
    request: QueryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    verify_api_key(f"Bearer {credentials.credentials}")

    try:
        student_id = str(UUID(request.student_id))
        course_id = str(UUID(request.course_id))
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail="student_id and course_id must be valid UUIDs.",
        ) from error

    try:
        chunks = retrieve_chunks(
            question=request.question,
            course_id=course_id,
            student_id=student_id,
            top_k=request.top_k,
        )

        if not chunks:
            return {
                "answer": (
                    "The available course materials do not contain "
                    "enough evidence to answer this question."
                ),
                "sources": [],
                "retrieval": {
                    "used_global_documents": False,
                    "used_student_documents": False,
                },
            }

        answer = generate_answer(
            question=request.question,
            context_chunks=chunks,
        )

        sources = [
            {
                "document_id": chunk.get("document_id"),
                "title": chunk.get("title"),
                "page_number": chunk.get("page_number"),
                "chunk_id": chunk.get("chunk_id"),
                "content": chunk.get("content", "")[:500],
            }
            for chunk in chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
            "retrieval": {
                "used_global_documents": any(
                    chunk.get("scope") == "global"
                    for chunk in chunks
                ),
                "used_student_documents": any(
                    chunk.get("scope") == "student"
                    for chunk in chunks
                ),
            },
        }

    except HTTPException:
        raise

    except Exception as error:
        # Server terminal mein actual error log hoga.
        print(f"RAG query failed: {type(error).__name__}: {error}")
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while answering the question.",
        ) from error
