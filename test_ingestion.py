
from services.ingestion_service import ingest_pdf

pdf_path = (
    "C:/Users/Kartik jain/Downloads/DKVMN-KAPS_Dynamic_Key-Value_Memory_Networks_Knowledge_Tracing_With_Students_Knowledge-Absorption_Ability_and_Problem-Solving_Ability.pdf"
)

result = ingest_pdf(pdf_path , course_id="11111111-1111-4111-8111-111111111111",
    scope="global",)

print("PDF ingestion successful!")
print("Document ID:", result["document_id"])
print("Pages:", result["pages"])
print("Chunks saved:", result["chunks"])
print("Status:", result["status"])
