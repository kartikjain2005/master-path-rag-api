from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_pages(pages):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 800,
        chunk_overlap = 100
    )

    chunks = []
    for page in pages :
        page_chunks = splitter.split_text(page["content"])

        for chunk_text in page_chunks:
            chunks.append({
                "content" : chunk_text,
                "page":page["page"]
            })
    return chunks