# Multimodal RAG - Attention is all you need

A multimodal RAG (Retrieval-Augmented Generation) app that answers questions about the paper **"Attention Is All You Need"** (Vaswani et al., 2017). It searches the paper's text and figures, then uses Gemini to write answers that cite page numbers.

Built with LangChain, Google Gemini, Chroma, PyMuPDF, and Streamlit.

## How it works

1. **Ingest:** PyMuPDF extracts the text from each PDF page.
2. **Chunk:** LangChain's `RecursiveCharacterTextSplitter` cuts the text into overlapping pieces.
3. **Describe figures:** Pages with diagrams are rendered as images. Gemini describes each figure in text, so figures become searchable.
4. **Embed and store:** Gemini embeddings are saved in a local Chroma vector database.
5. **Retrieve and answer:** A question is embedded, the closest chunks are found, and Gemini answers using only those chunks.

## Project structure

```text
Multimodal RAG/
├── app.py              # Streamlit web interface
├── build_index.py      # Builds the text index
├── describe_images.py  # Describes figure pages and adds them to the index
├── chunker.py          # Splits page text into chunks
├── config.py           # Settings and API key loading
├── embed_store.py      # Embeddings and Chroma vector store
├── ingest.py           # PDF reading and page rendering
├── main.py             # Terminal chat interface
├── rag.py              # Retrieval and answer generation
├── data/
│   ├── attention_is_all_you_need.pdf
│   └── pages/          # Rendered figure pages
├── chroma_db/          # Saved vector index
├── .env.example        # Placeholder settings (safe to share)
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.12 or 3.13
- A free Google Gemini API key from https://aistudio.google.com/apikey

## Setup

Clone the repository and open the folder:

```powershell
git clone https://github.com/ZeeshanAli77/Multimodal---RAG.git
cd Multimodal---RAG
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the packages:

```powershell
pip install -r requirements.txt
```

Create your private settings file from the template:

```powershell
copy .env.example .env
```

Open `.env` and replace the placeholder with your real key:

```text
GEMINI_API_KEY=your_real_key_here
CHAT_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-001
VISION_MODEL=gemini-2.5-flash
```

Never commit `.env`. It's listed in `.gitignore`.

## Building the index

The repository includes a prebuilt `chroma_db/` folder, so you can skip this step. To rebuild it from scratch:

```powershell
Remove-Item -Recurse -Force chroma_db, data\pages -ErrorAction SilentlyContinue
python build_index.py
python describe_images.py
```

The free tier has rate limits, so the scripts pause between requests. If you see "Rate limit hit, waiting...", let them finish. If you reach the daily quota, run them again the next day. Chroma keeps what's already saved.

## Running the app

Web interface:

```powershell
streamlit run app.py
```

Then open http://localhost:8501.

Terminal chat:

```powershell
python main.py
```

## Example questions

- What is multi-head attention?
- Why does the Transformer avoid recurrence?
- How is positional encoding done?
- Describe the Transformer architecture diagram.

## Deploying on Streamlit Community Cloud

1. Push this repository to GitHub. Make sure `.env` is not in the repository.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **Create app**, then **Deploy a public app from GitHub**.
4. Set the repository to `ZeeshanAli77/Multimodal---RAG`, the branch to `main`, and the main file path to `app.py`.
5. Open **Advanced settings** and add your secrets in TOML format:

   ```toml
   GEMINI_API_KEY = "your_real_key_here"
   CHAT_MODEL = "gemini-2.5-flash"
   EMBEDDING_MODEL = "gemini-embedding-001"
   VISION_MODEL = "gemini-2.5-flash"
   ```

6. Click **Deploy**. The first build takes a few minutes.

To update the live app, commit and push your changes. Streamlit redeploys automatically.

## Security notes

- API keys belong in `.env` locally and in Streamlit secrets when deployed. Never put them in code or in committed files.
- If a key is ever exposed, delete it in Google AI Studio, create a new one, and update your secrets.
- Gemini's free tier may use submitted content to improve Google's products. This project uses a public paper, so that's fine. For private documents, use a paid plan.

## Limitations

- Figure descriptions come from a vision model, so they can miss fine details.
- Answers are only as good as the retrieved chunks. Retrieval mistakes are the most common cause of wrong answers.
- The free tier limits requests per minute and per day.

## Acknowledgements

- Vaswani et al., ["Attention Is All You Need"](https://arxiv.org/abs/1706.03762) (2017)
- LangChain, Google Gemini, Chroma, PyMuPDF, and Streamlit
