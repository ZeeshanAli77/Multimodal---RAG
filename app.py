import streamlit as st
from config import GEMINI_API_KEY
from rag import answer

st.set_page_config(
    page_title="Attention Paper Explorer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
.hero {
    padding: 1.8rem 2rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #db2777 100%);
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 12px 32px rgba(79, 70, 229, 0.28);
}
.hero h1 { margin: 0; font-size: 2.1rem; color: white; letter-spacing: -0.5px; }
.hero p { margin: 0.5rem 0 0.9rem 0; opacity: 0.92; font-size: 1.02rem; }
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    margin-right: 0.45rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.22);
    font-size: 0.8rem;
    font-weight: 500;
}
.source-card {
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-left: 4px solid #7c3aed;
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.7rem;
    background: rgba(128, 128, 128, 0.06);
}
.source-card.figure { border-left-color: #db2777; }
.source-header { font-weight: 600; font-size: 0.95rem; }
.source-type {
    font-size: 0.72rem;
    padding: 0.12rem 0.5rem;
    border-radius: 6px;
    margin-left: 0.4rem;
    background: rgba(124, 58, 237, 0.15);
    color: #7c3aed;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}
.source-card.figure .source-type {
    background: rgba(219, 39, 119, 0.15);
    color: #db2777;
}
.source-snippet { font-size: 0.88rem; opacity: 0.85; margin-top: 0.45rem; line-height: 1.5; }
.empty-state {
    text-align: center;
    padding: 2.5rem 1rem;
    opacity: 0.75;
    border: 1px dashed rgba(128, 128, 128, 0.35);
    border-radius: 16px;
}
#MainMenu, footer { visibility: hidden; }
</style>
"""

EXAMPLE_QUESTIONS = [
    "What is multi-head attention?",
    "Why does the Transformer avoid recurrence?",
    "How is positional encoding done?",
    "Describe the Transformer architecture diagram.",
]

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
        <h1>📄 Attention Paper Explorer</h1>
        <p>Ask questions about <em>"Attention Is All You Need"</em>.
        Answers come from the paper's text and figures, with page citations.</p>
        <span class="badge">Gemini 2.5 Flash</span>
        <span class="badge">LangChain</span>
        <span class="badge">Chroma</span>
        <span class="badge">Multimodal RAG</span>
    </div>
    """,
    unsafe_allow_html=True,
)


def render_sources(sources):
    for s in sources:
        is_figure = s["type"] == "image"
        css_class = "source-card figure" if is_figure else "source-card"
        label = "Figure" if is_figure else "Text"
        snippet = s["text"][:280].replace("<", "&lt;") + "..."

        st.markdown(
            f"""
            <div class="{css_class}">
                <span class="source-header">Page {s['page']}</span>
                <span class="source-type">{label}</span>
                <div class="source-snippet">{snippet}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if s.get("image_path"):
            st.image(s["image_path"], caption=f"Page {s['page']} (rendered)")


if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None

with st.sidebar:
    st.markdown("## 🧭 Explore")
    st.caption("Try one of these to get started:")
    for q in EXAMPLE_QUESTIONS:
        if st.button(q, use_container_width=True):
            st.session_state.pending = q

    st.divider()
    st.markdown("**How it works**")
    st.caption(
        "1. Your question is embedded as numbers.\n"
        "2. The closest text and figure chunks are retrieved.\n"
        "3. Gemini writes an answer using only those chunks."
    )

    st.divider()
    if st.button("🧹 Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if not GEMINI_API_KEY or GEMINI_API_KEY.startswith("your_"):
    st.error("No API key found. Add GEMINI_API_KEY to your .env file (or Streamlit secrets) and restart.")
    st.stop()

typed = st.chat_input("Ask about attention, multi-head, positional encoding...")
question = typed or st.session_state.pending
st.session_state.pending = None

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    try:
        with st.spinner("Searching the paper..."):
            reply, docs = answer(question)
        sources = [
            {
                "page": d.metadata["page"],
                "type": d.metadata["type"],
                "text": d.page_content,
                "image_path": d.metadata.get("image_path", ""),
            }
            for d in docs
        ]
        st.session_state.messages.append(
            {"role": "assistant", "content": reply, "sources": sources}
        )
    except Exception as e:
        st.session_state.messages.append(
            {"role": "assistant", "content": f"Something went wrong: `{e}`", "sources": []}
        )

if not st.session_state.messages:
    st.markdown(
        '<div class="empty-state">💬 Ask your first question below, or pick an example from the sidebar.</div>',
        unsafe_allow_html=True,
    )

for m in st.session_state.messages:
    avatar = "🧑‍💻" if m["role"] == "user" else "🤖"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m["content"])
        if m.get("sources"):
            with st.expander(f"Sources ({len(m['sources'])})", expanded=False):
                render_sources(m["sources"])