from services.embedding_service import embed_text
from database.supabase_client import supabase
from uuid import UUID


def retrieve_chunks(
    question: str,
    course_id: str,
    student_id: str | None = None,
    document_id: str | None = None,
    top_k: int = 5,
):
    if not question or not question.strip():
        raise ValueError("Question empty nahi hona chahiye.")

    UUID(course_id)

    if student_id is not None:
        UUID(student_id)

    if document_id is not None:
        UUID(document_id)

    top_k = max(1, min(top_k, 20))

    # User ke question ki embedding banao
    query_vector = embed_text(
        question,
        task_type="RETRIEVAL_QUERY"
    )

    # Supabase se relevant chunks search karo
    response = supabase.rpc(
        "match_document_chunks",
        {
            "query_embedding": query_vector,
            "match_count": top_k,
            "filter_document_id": document_id,
            "filter_course_id": course_id,
            "filter_student_id": student_id,
        }
    ).execute()

    return response.data