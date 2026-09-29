from langchain_chroma import Chroma

from app.retrieval.embeddings import create_embeddings


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "resume"


def create_vector_store():
    embeddings = create_embeddings()

    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )


if __name__ == "__main__":
    vector_store = create_vector_store()

    question = "What experience does Vignesh have with RAG?"

    results = vector_store.similarity_search_with_score(
        question,
        k=5,
    )

    print(f"Retrieved documents: {len(results)}")

    for index, (document, score) in enumerate(results):
        print(f"\n--- Result {index + 1} ---")
        print(f"Score: {score}")
        print(f"Page: {document.metadata.get('page')}")
        print(document.page_content)