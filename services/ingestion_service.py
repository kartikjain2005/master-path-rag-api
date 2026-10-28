
import hashlib
from pathlib import Path
from uuid import UUID

from ingestion.pdf_loader import load_pdf
from ingestion.text_splitter import split_pages
from services.embedding_service import embed_text
from database.supabase_client import supabase


def calculate_file_hash(file_path: Path) -> str:
    """PDF ka SHA-256 fingerprint calculate karta hai."""
    sha256 = hashlib.sha256()

    with file_path.open("rb") as pdf_file:
        for block in iter(lambda: pdf_file.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def ingest_pdf(
    file_path: str,
    course_id: str,
    scope: str,
    owner_user_id: str | None = None,
) -> dict:

    if scope not in ("global", "student"):
        raise ValueError("scope must be 'global' or 'student'")

    UUID(course_id)

    if scope == "global" and owner_user_id is not None:
        raise ValueError(
            "The owner_user_id of a global document should be None"
        )

    if scope == "student":
        if not owner_user_id:
            raise ValueError(
                "The owner_user_id is required for student documents."
            )
        UUID(owner_user_id)

    pdf_path = Path(file_path)

    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF file nahi mili: {file_path}")

    file_hash = calculate_file_hash(pdf_path)

    # Same file, course aur access scope pehle se hai?
    duplicate_query = (
        supabase.table("documents")
        .select("id, status, file_hash")
        .eq("file_hash", file_hash)
        .eq("course_id", course_id)
        .eq("scope", scope)
    )

    if scope == "global":
        duplicate_query = duplicate_query.is_("owner_user_id", "null")
    else:
        duplicate_query = duplicate_query.eq(
            "owner_user_id", owner_user_id
        )

    existing = duplicate_query.limit(1).execute()

    if existing.data:
        document = existing.data[0]
        raise ValueError(
            f"Duplicate PDF: document already exists "
            f"(id={document['id']}, status={document['status']}). "
            "Existing document ko dobara ingest nahi kiya."
        )

    pages = load_pdf(str(pdf_path))

    if not pages:
        raise ValueError("PDF se readable text nahi mila.")

    chunks = split_pages(pages)

    if not chunks:
        raise ValueError("PDF se koi chunks generate nahi hue.")

    document_response = (
        supabase.table("documents")
        .insert({
            "title": pdf_path.stem,
            "file_name": pdf_path.name,
            "file_hash": file_hash,
            "status": "processing",
            "course_id": course_id,
            "scope": scope,
            "owner_user_id": owner_user_id,
        })
        .execute()
    )

    document_id = document_response.data[0]["id"]

    try:
        chunk_records = []

        for index, chunk in enumerate(chunks):
            vector = embed_text(
                chunk["content"],
                task_type="RETRIEVAL_DOCUMENT",
            )

            chunk_records.append({
                "document_id": document_id,
                "chunk_index": index,
                "content": chunk["content"],
                "page_number": chunk["page"],
                "embedding": vector,
            })

        batch_size = 50

        for start in range(0, len(chunk_records), batch_size):
            batch = chunk_records[start:start + batch_size]
            supabase.table("document_chunks").insert(batch).execute()

        supabase.table("documents").update({
            "status": "ready"
        }).eq("id", document_id).execute()

        return {
            "document_id": document_id,
            "pages": len(pages),
            "chunks": len(chunks),
            "status": "ready",
            "scope": scope,
            "course_id": course_id,
            "owner_user_id": owner_user_id,
        }

    except Exception:
        # Failed ingestion ke partial chunks aur document clean karo.
        try:
            supabase.table("documents").delete().eq(
                "id", document_id
            ).execute()
        except Exception:
            # Cleanup fail ho toh document ko failed mark karne ki koshish.
            supabase.table("documents").update({
                "status": "failed"
            }).eq("id", document_id).execute()

        raise
