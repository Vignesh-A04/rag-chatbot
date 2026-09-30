from app.retrieval.embeddings import create_embeddings
from langchain_chroma import Chroma


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "resume"


def evaluate_query(question, k=5):

    embeddings = create_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )

    results = vector_store.similarity_search_with_score(
        question,
        k=k,
    )

    print(f"\nQUESTION: {question}")
    print("=" * 80)

    for index, (document, score) in enumerate(results):

        print(f"\n--- Rank {index + 1} ---")
        print(f"Distance: {score:.4f}")
        print(f"Page: {document.metadata.get('page')}")
        print(f"Source: {document.metadata.get('source')}")

        print("\nContent:")
        print(document.page_content)


if __name__ == "__main__":

    questions = [
        "What experience does Vignesh have with RAG?",
        "What technologies does Vignesh use for Generative AI?",
        "What backend technologies does Vignesh know?",
        "What cloud and deployment technologies does Vignesh use?",
    ]

    for question in questions:
        evaluate_query(question)