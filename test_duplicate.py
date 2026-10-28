
from services.ingestion_service import ingest_pdf

PDF_PATH = r"C:/Users/Kartik jain/Downloads/DKVMN-KAPS_Dynamic_Key-Value_Memory_Networks_Knowledge_Tracing_With_Students_Knowledge-Absorption_Ability_and_Problem-Solving_Ability.pdf"

COURSE_ID = "11111111-1111-4111-8111-111111111111"

try:
    result = ingest_pdf(
        file_path=PDF_PATH,
        course_id=COURSE_ID,
        scope="global",
        owner_user_id=None,
    )
    print("Unexpected result:", result)

except ValueError as error:
    print("Duplicate check result:")
    print(error)
