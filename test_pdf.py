from ingestion.pdf_loader import load_pdf
from ingestion.text_splitter import split_pages

pdf_path = "C:/Users/Kartik jain/Downloads/Deep_Learning_Complete_Notes.pdf"

pages = load_pdf(pdf_path)
print("pages_extracted : " , len(pages))

chunks = split_pages(pages)
print("total chunks :" , len(chunks))

if chunks:
    print("\nFirst chunk:")
    print(chunks[0]["content"])
    print("\npage_number:" , chunks[0]["page"])
else:
    print("No text extracted. Check whether the PDF is scanned.")