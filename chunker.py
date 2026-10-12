from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP


def chunk_pages(pages):
    """Split each page into overlapping chunks, keeping the page number."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = []
    for p in pages:
        text = " ".join(p["text"].split())
        for piece in splitter.split_text(text):
            chunks.append({"text": piece, "page": p["page"], "type": "text"})
    return chunks