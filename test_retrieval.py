from services.retrieval_service import retrieve_chunks

DOCUMENT_ID = "7cebd009-6fdd-4093-9d22-15dfd50655d3"

question = "What is backpropagation in deep learning?"

results = retrieve_chunks(
    question=question,
    document_id=DOCUMENT_ID,
    top_k=5
)

print(f"\nTotal chunks retrieved: {len(results)}")

for i, chunk in enumerate(results, start=1):
    print(f"\n--- Result {i} ---")
    print("Page:", chunk["page_number"])
    print("Similarity:", round(chunk["similarity"], 4))
    print("Content:", chunk["content"][:500])