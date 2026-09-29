from langchain_chroma import Chroma

from app.ingestion.chunker import split_documents
from app.ingestion.loader import load_document
from app.retrieval.embeddings import create_embeddings


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "resume"


def create_vector_store():
    documents = load_document()
    chunks = split_documents(documents)

    embeddings = create_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )

    vector_store.add_documents(chunks)

    return vector_store


if __name__ == "__main__":
    vector_store = create_vector_store()

    print("Vector store created successfully.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Location: {CHROMA_PATH}")