# Multimodal RAG - Attention is all you need

Live app: https://multimodal---rag-wsewrcjdtnnckphovqfnyu.streamlit.app/

A multimodal RAG (Retrieval-Augmented Generation) app that answers questions about the paper "Attention Is All You Need" (Vaswani et al., 2017). It searches both the paper's text and its figures, then uses Google Gemini to write answers that cite the page numbers they came from.

Built with LangChain, Google Gemini, Chroma, PyMuPDF, and Streamlit.

Table of contents
What the app does
How it works
Project structure
Tech stack
Requirements
Local setup
Building the index
Running the app
Example questions
Deploying on Streamlit Community Cloud
Updating the live app
Configuration reference
Security notes
Troubleshooting
Limitations
Learning notes
Acknowledgements
What the app does
Answers natural-language questions about the Transformer paper.
Cites page numbers for every answer, so you can check the source.
Understands figures, not just text. Diagrams such as the Transformer architecture are described by a vision model and stored in the same index as the text.
Shows the retrieved sources under each answer: text snippets for text matches, and the rendered page image for figure matches.
Keeps a chat history during the session, and offers example questions in the sidebar.
How it works

The app follows the standard RAG pipeline, split into an offline step (run once) and an online step (run on every question).

Offline: building the index

Extract text. PyMuPDF reads the text of each PDF page.
Chunk. LangChain's RecursiveCharacterTextSplitter cuts each page into overlapping pieces of about 800 characters, with 150 characters shared between neighbors. Overlap keeps ideas that cross a boundary searchable.
Describe figures. Pages with diagrams or many vector drawings are rendered as PNG images. Gemini describes each figure in words, and that description becomes a searchable chunk.
Embed. Each chunk is converted into a vector of numbers by gemini-embedding-001. Similar meanings produce nearby vectors.
Store. Vectors and their metadata (page number, chunk type, image path) are saved in a local Chroma database in chroma_db/.

Online: answering a question

The question is embedded using the query task type, which is tuned for searching.
Chroma returns the four most similar chunks (TOP_K = 4).
A prompt template combines the retrieved chunks with the question and instructs the model to answer only from that context.
gemini-2.5-flash writes the answer, and the app displays it with its sources.
Project structure
text
Multimodal RAG/
├── app.py              # Streamlit web interface (chat UI, source cards, sidebar)
├── build_index.py      # Step 1 of indexing: text pages -> chunks -> Chroma
├── describe_images.py  # Step 2 of indexing: figure pages -> descriptions -> Chroma
├── chunker.py          # Splits page text into overlapping chunks
├── config.py           # Loads settings and API keys, retry helper for rate limits
├── embed_store.py      # Embedding model, Chroma vector store, search helpers
├── ingest.py           # PDF text extraction, figure detection, page rendering
├── main.py             # Terminal chat interface (no browser needed)
├── rag.py              # Retrieval and answer generation chain
├── data/
│   ├── attention_is_all_you_need.pdf
│   └── pages/          # Rendered PNGs of figure pages (created by describe_images.py)
├── chroma_db/          # Saved vector index (committed so the deployed app starts fast)
├── .streamlit/
│   └── config.toml     # Theme settings (accent color, font)
├── .env.example        # Placeholder settings (safe to commit)
├── .env                # Your real keys (never committed)
├── .gitignore
├── requirements.txt
└── README.md
Tech stack
Part	Tool	Why it's used
LLM (answers)	Gemini 2.5 Flash	Fast, free tier, handles images
Vision (figures)	Gemini 2.5 Flash	Same model reads figure pages
Embeddings	gemini-embedding-001	Converts text to searchable vectors
Vector store	Chroma	Local, file-based, no server to run
Orchestration	LangChain	Standard building blocks for chunking, retrieval, prompts
PDF processing	PyMuPDF	Extracts text and renders pages to images
Web UI	Streamlit	Turns Python into a web app with minimal code
Config	python-dotenv	Loads secrets from .env locally
Requirements
Python 3.12 or 3.13
Windows, macOS, or Linux
A free Google Gemini API key from https://aistudio.google.com/apikey
A GitHub account (only if you want to deploy)
Local setup

1. Clone the repository

powershell
git clone https://github.com/ZeeshanAli77/Multimodal---RAG.git
cd Multimodal---RAG

2. Create and activate a virtual environment

powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

If PowerShell blocks the script, run Set-ExecutionPolicy -Scope CurrentUser RemoteSigned once and try again. Your prompt should now start with (.venv).

3. Install the packages

powershell
pip install -r requirements.txt

4. Add your API key

powershell
copy .env.example .env

Open .env and replace the placeholder with your key:

text
GEMINI_API_KEY=your_real_key_here
CHAT_MODEL=gemini-2.5-flash
EMBEDDING_MODEL=gemini-embedding-001
VISION_MODEL=gemini-2.5-flash

Keep .env private. It's listed in .gitignore, so Git ignores it.

5. Add the paper

Download https://arxiv.org/abs/1706.03762, rename it to attention_is_all_you_need.pdf, and place it in data/. The repository may already include it, so check first.

Building the index

The repository already includes a prebuilt chroma_db/ folder and data/pages/, so you can skip this section unless you change the chunking settings or the PDF.

To rebuild from scratch:

powershell
Remove-Item -Recurse -Force chroma_db, data\pages -ErrorAction SilentlyContinue
python build_index.py
python describe_images.py

build_index.py produces about 60 to 120 text chunks depending on settings. describe_images.py makes one vision request per figure page.

Rate limits: The free tier allows a limited number of requests per minute and per day. The code waits and retries automatically when it hits a limit. If you see Rate limit hit, waiting..., let it finish. If you reach the daily quota, run the scripts again the next day. Chroma keeps what's already saved, and fixed chunk IDs prevent duplicates.

Running the app

Web interface

powershell
streamlit run app.py

Open http://localhost:8501. Stop the server with Ctrl + C.

Terminal chat

powershell
python main.py

Type exit to quit. The terminal version also prints the page numbers used for each answer.

Example questions
What is multi-head attention?
Why does the Transformer avoid recurrence?
How is positional encoding done?
Describe the Transformer architecture diagram.
What optimizer and learning rate schedule did the authors use?
What BLEU scores did the Transformer achieve on English-to-German translation?
Deploying on Streamlit Community Cloud

The app is deployed at https://multimodal---rag-wsewrcjdtnnckphovqfnyu.streamlit.app/.

To deploy your own copy:

Push the code to GitHub. Confirm .env is not in the repository. .env.example should contain placeholders only.
Sign in. Go to https://share.streamlit.io and sign in with your GitHub account.
Create the app. Click Create app, then Deploy a public app from GitHub.
Set the source.
Repository: ZeeshanAli77/Multimodal---RAG
Branch: main
Main file path: app.py
Add secrets. Open Advanced settings, choose Python 3.12 or 3.13, and paste this into the Secrets box with your real key:
toml
   GEMINI_API_KEY = "your_real_key_here"
   CHAT_MODEL = "gemini-2.5-flash"
   EMBEDDING_MODEL = "gemini-embedding-001"
   VISION_MODEL = "gemini-2.5-flash"
Deploy. Click Deploy. The first build takes 3 to 6 minutes while packages install.
Check the logs if something fails. Use Manage app at the bottom right.

Why the index is committed: The deployed app reads chroma_db/ and data/pages/ directly. This means it doesn't call the embedding or vision APIs at startup, so the app loads fast and doesn't use quota on each visit. Only question answering calls the API.

Changing secrets later: Open the app's Settings → Secrets, edit the values, and reboot the app.

Updating the live app

After changing code:

powershell
git add .
git commit -m "Describe your change"
git push

Streamlit redeploys automatically after each push. If you rebuild the index locally, commit the new chroma_db/ folder too.

Configuration reference

All settings are read in config.py. Each one can be set in .env locally or in Streamlit secrets when deployed.

Setting	Default	Purpose
GEMINI_API_KEY	none (required)	Your Google Gemini API key
CHAT_MODEL	gemini-2.5-flash	Model that writes answers
EMBEDDING_MODEL	gemini-embedding-001	Model that creates vectors
VISION_MODEL	gemini-2.5-flash	Model that describes figures

Fixed values in config.py (edit the file to change them, then rebuild the index):

Constant	Value	Effect
CHUNK_SIZE	800	Characters per text chunk
CHUNK_OVERLAP	150	Characters shared between neighboring chunks
TOP_K	4	Chunks retrieved per question
COLLECTION_NAME	attention_paper	Name of the Chroma collection
Security notes
Keys belong in .env locally and in Streamlit secrets when deployed. Never put them in code or in any committed file.
If a key is exposed, delete it in Google AI Studio, create a new one, and update your local .env and Streamlit secrets.
Gemini's free tier may use submitted content to improve Google's products. This project only processes a public paper. Use a paid plan for private documents.
Anyone who opens the public app uses your free-tier quota. Watch your usage in AI Studio.
Troubleshooting
Symptom	Likely cause	Fix
No module named ...	Virtual environment not active	Run .\.venv\Scripts\Activate.ps1
Put your real GEMINI_API_KEY...	.env missing, has the placeholder, or is named .env.txt	Check the filename and the key value
File not found: data/attention_is_all_you_need.pdf	Running from the wrong folder	Run commands from the project root
Model not found	Model name changed or misspelled	Check names at https://ai.google.dev/gemini-api/docs/models
Rate limit hit, waiting...	Free-tier quota	Normal. Wait, or try again tomorrow
"No API key found" on the live app	Secret missing or misnamed	Fix it under Settings → Secrets, then reboot
Answer says "I don't know"	Retrieval missed the right chunk	Ask a more specific question, or rebuild the index with different chunk settings
Chroma or SQLite error on the live app	chroma_db/ not committed	Check that the folder is in the GitHub repository
Limitations
Figure descriptions are generated by a vision model. They can miss fine detail, especially in dense diagrams and tables.
Answers are only as good as the retrieved chunks. Retrieval mistakes cause most wrong answers.
The free tier limits requests per minute and per day, so heavy use will hit the limit.
Only one document is indexed: the Transformer paper.
Learning notes

This project was built from scratch to learn the pieces of a RAG system. The main concepts covered are:

Chunking: how chunk size and overlap trade off precision against context.
Embeddings: how text becomes vectors, and why query and document task types differ.
Vector search: how a database finds the nearest chunks to a question.
Prompt grounding: instructing the model to answer only from retrieved context and cite its sources.
Multimodal indexing: turning images into text descriptions so they can be retrieved.
Operational concerns: rate limits, retries, secret management, and deployment.
Acknowledgements
Vaswani et al., "Attention Is All You Need" (2017)
LangChain, Google Gemini, Chroma, PyMuPDF, and Streamlit
