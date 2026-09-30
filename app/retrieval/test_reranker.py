from app.retrieval.embeddings import create_embeddings
from app.retrieval.reranker import LLMReranker

from langchain_chroma import Chroma


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "resume"


def main():

    question = "What experience does Vignesh have with RAG?"

    embeddings = create_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )

    print("Retrieving candidates...")

    documents = vector_store.similarity_search(
        question,
        k=5,
    )

    print("\n=== CHROMA RESULTS ===")

    for index, document in enumerate(documents):

        print(f"\n--- Rank {index + 1} ---")
        print(document.page_content)

    print("\nRunning reranker...")

    reranker = LLMReranker()

    reranked_documents = reranker.rerank(
        question,
        documents,
        top_n=3,
    )

    print("\n=== RERANKED RESULTS ===")

    for index, document in enumerate(reranked_documents):

        print(f"\n--- Rank {index + 1} ---")
        print(document.page_content)


if __name__ == "__main__":
    main()