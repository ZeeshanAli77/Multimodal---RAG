import os
import time
from dotenv import load_dotenv

load_dotenv()


def get_secret(name, default=None):
    """Read from .env on your PC, or from Streamlit secrets when deployed."""
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return default


GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
CHAT_MODEL = get_secret("CHAT_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = get_secret("EMBEDDING_MODEL", "gemini-embedding-001")
VISION_MODEL = get_secret("VISION_MODEL", "gemini-2.5-flash")

PDF_PATH = "data/Attention is all you need.pdf"
PAGE_DIR = "data/pages"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "attention_paper"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 4


def check_key():
    if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("your_"):
        raise RuntimeError("Put your real GEMINI_API_KEY in the .env file first.")


def call_with_retry(fn, retries=5):
    """Free-tier limits are strict. On a 'too many requests' error, wait and try again."""
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            message = str(e)
            is_rate_limit = "429" in message or "RESOURCE_EXHAUSTED" in message or "quota" in message.lower()
            if is_rate_limit and attempt < retries - 1:
                wait = 30 * (attempt + 1)
                print(f"Rate limit hit, waiting {wait} seconds...")
                time.sleep(wait)
            else:
                raise