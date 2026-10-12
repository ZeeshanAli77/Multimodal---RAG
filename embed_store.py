import time
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config import EMBEDDING_MODEL, CHROMA_DIR, COLLECTION_NAME, GEMINI_API_KEY, check_key


def get_embeddings():
    check_key()
    return GoogleGenerativeAIEmbeddings(
        model=f"models/{EMBEDDING_MODEL}",
        google_api_key=GEMINI_API_KEY,
    )


def get_vectorstore():
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def store_chunks(chunks, batch_size=50):
    """Wrap each chunk in a LangChain Document and save it to Chroma."""
    store = get_vectorstore()
    docs = [
        Document(
            page_content=c["text"],
            metadata={
                "page": c["page"],
                "type": c["type"],
                "image_path": c.get("image_path", ""),
            },
        )
        for c in chunks
    ]
    # Fixed IDs mean re-running the script updates chunks instead of duplicating them
    ids = [f"{c['type']}-{c['page']}-{i}" for i, c in enumerate(chunks)]

    for start in range(0, len(docs), batch_size):
        store.add_documents(
            docs[start:start + batch_size],
            ids=ids[start:start + batch_size],
        )
        time.sleep(2)  # pause between batches for the free-tier limit