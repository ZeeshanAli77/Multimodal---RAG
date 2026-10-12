from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from config import CHAT_MODEL, GEMINI_API_KEY, TOP_K, check_key, call_with_retry
from embed_store import get_vectorstore

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You answer questions about the 'Attention Is All You Need' paper. "
     "Use ONLY the context provided. Cite the page numbers you used, like [page 3]. "
     "If the context does not contain the answer, say you don't know."),
    ("human", "Context:\n{context}\n\nQuestion: {question}"),
])


def format_context(docs):
    return "\n\n".join(
        f"[page {d.metadata['page']}] ({d.metadata['type']}) {d.page_content}"
        for d in docs
    )


def answer(question):
    check_key()

    # Step 1: retrieve the most relevant chunks
    retriever = get_vectorstore().as_retriever(search_kwargs={"k": TOP_K})
    docs = retriever.invoke(question)

    # Step 2: prompt -> model -> plain text
    llm = ChatGoogleGenerativeAI(model=f"models/{CHAT_MODEL}", google_api_key=GEMINI_API_KEY)
    chain = PROMPT | llm | StrOutputParser()

    text = call_with_retry(lambda: chain.invoke({
        "context": format_context(docs),
        "question": question,
    }))
    return text, docs