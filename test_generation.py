from services.retrieval_service import retrieve_chunks
from services.generation_service import generate_answer

DOCUMENT_ID = "7cebd009-6fdd-4093-9d22-15dfd50655d3"

COURSE_ID = "11111111-1111-4111-8111-111111111111"

# Global document ke liye student_id None reh sakta hai
STUDENT_ID = None

question = "What learning rate and number of iterations were used for DKVMN?"

# Step 1: Relevant chunks retrieve karo
chunks = retrieve_chunks(
    question=question,
    course_id=COURSE_ID,
    student_id=STUDENT_ID,
    document_id=DOCUMENT_ID,
    top_k=5,
)

print(f"\nRetrieved chunks: {len(chunks)}")
print("\nGenerating answer...\n")

# Step 2: Gemini se answer generate karao
answer = generate_answer(
    question=question,
    context_chunks=chunks
)

print("QUESTION:", question)
print("\nANSWER:\n")
print(answer)

print("\n--- RETRIEVED CONTEXT ---\n")

for i, chunk in enumerate(chunks, start=1):
    print(f"Chunk {i}")
    print(f"Page: {chunk.get('page_number')}")
    print(f"Content: {chunk.get('content')}")
    print("-" * 50)


for i, chunk in enumerate(chunks, start=1):
    print(
        f"Chunk {i} | "
        f"Page: {chunk.get('page_number')} | "
        f"Similarity: {chunk.get('similarity')}"
    )
