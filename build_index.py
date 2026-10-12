from config import PDF_PATH, check_key
from ingest import extract_pages
from chunker import chunk_pages
from embed_store import store_chunks


def main():
    check_key()
    pages = extract_pages(PDF_PATH)
    chunks = chunk_pages(pages)
    print(f"Created {len(chunks)} text chunks from {len(pages)} pages.")
    store_chunks(chunks)
    print("Text index saved in the chroma_db folder.")


if __name__ == "__main__":
    main()