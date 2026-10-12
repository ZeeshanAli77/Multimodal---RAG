from config import check_key
from rag import answer


def main():
    check_key()
    print("Ask a question about the paper. Type 'exit' to quit.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() == "exit":
            break
        if not question:
            continue
        reply, docs = answer(question)
        print(f"\nAssistant: {reply}")
        print("Sources (pages):", sorted({d.metadata["page"] for d in docs}))


if __name__ == "__main__":
    main()