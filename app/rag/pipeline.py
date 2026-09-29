import os
import time

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

from app.retrieval.embeddings import create_embeddings


load_dotenv()


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "resume"


class RAGPipeline:

    def __init__(self):
        print("Initializing RAG pipeline...")

        self.embeddings = create_embeddings()

        self.vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=CHROMA_PATH,
        )

        model = os.getenv("GEMINI_MODEL")

        if not model:
            raise ValueError("GEMINI_MODEL is not set")

        self.llm = ChatGoogleGenerativeAI(
            model=model,
        )

        print("RAG pipeline initialized.")

    def build_context(self, documents):
        context_parts = []

        for index, document in enumerate(documents):
            source = document.metadata.get("source", "Unknown")
            page = document.metadata.get("page", "Unknown")

            context_parts.append(
                f"[Source {index + 1}]\n"
                f"File: {source}\n"
                f"Page: {page}\n"
                f"Content:\n{document.page_content}"
            )

        return "\n\n".join(context_parts)

    def ask(self, question):
        total_start = time.perf_counter()

        # -------------------------
        # Retrieval
        # -------------------------

        retrieval_start = time.perf_counter()

        documents = self.vector_store.max_marginal_relevance_search(
            question,
            k=3,
            fetch_k=8,
            lambda_mult=0.5,
        )

        retrieval_time = time.perf_counter() - retrieval_start

        # -------------------------
        # Build context
        # -------------------------

        context_start = time.perf_counter()

        context = self.build_context(documents)

        context_time = time.perf_counter() - context_start

        # -------------------------
        # LLM generation
        # -------------------------

        llm_start = time.perf_counter()

        prompt = f"""
You are a document-based question answering assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not use outside knowledge.
- Do not invent information.
- If the answer cannot be found in the context, say:
  "I couldn't find that information in the provided document."
- Keep the answer concise.
- Mention the relevant source page when useful.

Context:
{context}

User question:
{question}
"""

        response = self.llm.invoke(prompt)

        # -------------------------
        # LLM metadata
        # -------------------------

        print("\n=== RESPONSE TYPE ===")
        print(type(response))
        print("\n=== RESPONSE ATTRIBUTES ===")
        print(response.__dict__)

        llm_time = time.perf_counter() - llm_start

        # -------------------------
        # Normalize response
        # -------------------------

        content = response.content

        if isinstance(content, list):
            content = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
                and item.get("type") == "text"
            )

        # -------------------------
        # Total timing
        # -------------------------

        total_time = time.perf_counter() - total_start

        print(
            f"[RAG] "
            f"retrieval={retrieval_time:.3f}s "
            f"context={context_time:.3f}s "
            f"llm={llm_time:.3f}s "
            f"total={total_time:.3f}s"
        )

        return content, documents


if __name__ == "__main__":

    rag = RAGPipeline()

    question = "What experience does Vignesh have with RAG?"

    answer, documents = rag.ask(question)

    print("\n=== ANSWER ===")
    print(answer)

    print("\n=== SOURCES ===")

    for index, document in enumerate(documents):
        print(
            f"{index + 1}. "
            f"Page {document.metadata.get('page')}"
        )