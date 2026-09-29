import os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()


def create_embeddings():
    model = os.getenv("GEMINI_EMBEDDING_MODEL")

    if not model:
        raise ValueError("GEMINI_EMBEDDING_MODEL is not set")

    embeddings = GoogleGenerativeAIEmbeddings(
        model=model,
        task_type="retrieval_document",
    )

    return embeddings


if __name__ == "__main__":
    embeddings = create_embeddings()

    text = """
    Vignesh has experience building Retrieval-Augmented Generation
    systems using LangChain, embeddings, and vector databases.
    """

    vector = embeddings.embed_query(text)

    print(f"Embedding dimensions: {len(vector)}")
    print(f"First 10 values: {vector[:10]}")