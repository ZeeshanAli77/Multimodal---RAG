import base64
import os
import time
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config import PDF_PATH, PAGE_DIR, VISION_MODEL, GEMINI_API_KEY, check_key, call_with_retry
from ingest import pages_with_figures, render_page_png
from embed_store import store_chunks

PROMPT = (
    "This is a page from the 'Attention Is All You Need' paper. "
    "Describe every figure, diagram and table on it in detail: "
    "labels, arrows, numbers, and what each one shows. "
    "Skip ordinary body text."
)


def describe_png(png_bytes):
    llm = ChatGoogleGenerativeAI(model=f"models/{VISION_MODEL}", google_api_key=GEMINI_API_KEY)
    b64 = base64.b64encode(png_bytes).decode("utf-8")
    message = HumanMessage(content=[
        {"type": "text", "text": PROMPT},
        {"type": "image_url", "image_url": f"data:image/png;base64,{b64}"},
    ])
    return call_with_retry(lambda: llm.invoke([message]).content)


def main():
    check_key()
    os.makedirs(PAGE_DIR, exist_ok=True)
    chunks = []
    for index in pages_with_figures(PDF_PATH):
        page_num = index + 1
        png = render_page_png(PDF_PATH, index)
        path = os.path.join(PAGE_DIR, f"page{page_num}.png")
        with open(path, "wb") as f:
            f.write(png)
        description = describe_png(png)
        chunks.append({
            "text": f"Figure content on page {page_num}: {description}",
            "page": page_num,
            "type": "image",
            "image_path": path,
        })
        print(f"Described page {page_num}")
        time.sleep(8)  # the free tier allows only a few vision requests per minute
    store_chunks(chunks)
    print(f"Stored {len(chunks)} figure chunks.")


if __name__ == "__main__":
    main()