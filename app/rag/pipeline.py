import os
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

from app.ingestion.chunker import split_documents
from app.ingestion.loader import load_document
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

        self.llm = ChatGoogleGenerativeAI(model=model)

        print("RAG pipeline initialized.")

    def ingest_document(self, pdf_path: str | Path, filename: str):
        """
        Add a new PDF to the existing vector store.
        Multiple PDFs are supported.
        """

        print(f"Loading document: {filename}")

        # Load PDF
        documents = load_document(pdf_path)

        if not documents:
            raise ValueError(
                "The uploaded PDF contains no readable pages."
            )

        # Create a unique ID for this document
        document_id = str(uuid.uuid4())

        # Add document metadata to every page
        for document in documents:
            document.metadata["source"] = filename
            document.metadata["document_id"] = document_id

        # Split pages into chunks
        chunks = split_documents(documents)

        if not chunks:
            raise ValueError(
                "The uploaded PDF produced no text chunks."
            )

        # Make sure every chunk contains document metadata
        for chunk in chunks:
            chunk.metadata["source"] = filename
            chunk.metadata["document_id"] = document_id

        print(f"Pages loaded: {len(documents)}")
        print(f"Chunks created: {len(chunks)}")
        print(f"Document ID: {document_id}")

        # Create unique IDs for every chunk
        ids = [
            f"{document_id}_chunk_{index}"
            for index in range(len(chunks))
        ]

        # Add chunks to Chroma
        self.vector_store.add_documents(
            documents=chunks,
            ids=ids,
        )

        print(
            f"Document '{filename}' indexed successfully."
        )

        return {
            "document_id": document_id,
            "filename": filename,
            "pages": len(documents),
            "chunks": len(chunks),
        }

    def delete_document(self, document_id: str):
        """
        Delete one document and all of its chunks.
        """

        result = self.vector_store.get(
            where={"document_id": document_id}
        )

        ids = result.get("ids", [])

        if not ids:
            return False

        self.vector_store.delete(ids=ids)

        print(
            f"Deleted document {document_id} "
            f"with {len(ids)} chunks."
        )

        return True

    def clear_documents(self):
        """
        Delete all indexed documents.
        """

        result = self.vector_store.get()

        ids = result.get("ids", [])

        if ids:
            self.vector_store.delete(ids=ids)

        print(
            f"Cleared {len(ids)} chunks from Chroma."
        )

    def has_documents(self):
        """
        Check whether Chroma contains any documents.
        """

        result = self.vector_store.get()

        return len(result.get("ids", [])) > 0

    def get_document_info(self):
        """
        Return information about all indexed documents.
        """

        result = self.vector_store.get()

        metadatas = result.get("metadatas", [])

        documents = {}

        for metadata in metadatas:

            if not metadata:
                continue

            document_id = metadata.get("document_id")

            if not document_id:
                continue

            if document_id not in documents:
                documents[document_id] = {
                    "document_id": document_id,
                    "filename": metadata.get(
                        "source",
                        "Unknown",
                    ),
                    "pages": set(),
                    "chunks": 0,
                }

            page = metadata.get("page")

            if page is not None:
                documents[document_id]["pages"].add(page)

            documents[document_id]["chunks"] += 1

        result = []

        for document in documents.values():
            result.append(
                {
                    "document_id": document["document_id"],
                    "filename": document["filename"],
                    "pages": len(document["pages"]),
                    "chunks": document["chunks"],
                }
            )

        return result

    def build_context(self, documents):
        """
        Build the context sent to the LLM.
        """

        context_parts = []

        for index, document in enumerate(documents):

            source = document.metadata.get(
                "source",
                "Unknown",
            )

            page = document.metadata.get(
                "page",
                "Unknown",
            )

            context_parts.append(
                f"[Source {index + 1}]\n"
                f"File: {source}\n"
                f"Page: {page}\n"
                f"Content:\n"
                f"{document.page_content}"
            )

        return "\n\n".join(context_parts)

    @staticmethod
    def is_greeting(question):
        """
        Detect simple greetings without calling
        the vector database or LLM.
        """

        greetings = {
            "hi",
            "hello",
            "hey",
            "hi there",
            "hello there",
            "hey there",
        }

        return question.strip().lower() in greetings

    def ask(self, question):
        """
        Retrieve relevant chunks and generate
        an answer using Gemini.
        """

        # Handle greetings directly
        if self.is_greeting(question):
            return (
                "Hello! Ask me anything about the "
                "provided documents.",
                [],
            )

        # Don't call Gemini when no documents exist
        if not self.has_documents():
            return (
                "No documents have been uploaded. "
                "Please upload a PDF first.",
                [],
            )

        total_start = time.perf_counter()

        # -----------------------------
        # Retrieval
        # -----------------------------

        retrieval_start = time.perf_counter()

        documents = self.vector_store.similarity_search(
            question,
            k=3,
        )

        retrieval_time = (
            time.perf_counter() - retrieval_start
        )

        # -----------------------------
        # Context construction
        # -----------------------------

        context_start = time.perf_counter()

        context = self.build_context(documents)

        context_time = (
            time.perf_counter() - context_start
        )

        # -----------------------------
        # LLM generation
        # -----------------------------

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
- Do NOT write source labels such as [Source 1],
  [Source 2], or [Source 3].
- Do NOT mention source numbers in the answer.
- If multiple documents contain relevant information,
  combine the information when appropriate.

Context:
{context}

User question:
{question}
"""

        response = self.llm.invoke(prompt)

        llm_time = time.perf_counter() - llm_start

        # -----------------------------
        # Normalize Gemini response
        # -----------------------------

        content = response.content

        if isinstance(content, list):
            content = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
                and item.get("type") == "text"
            )

        # -----------------------------
        # No-answer handling
        # -----------------------------

        if (
            "I couldn't find that information "
            "in the provided document."
            in content
        ):
            return content, []

        # -----------------------------
        # Timing
        # -----------------------------

        total_time = (
            time.perf_counter() - total_start
        )

        print(
            f"[RAG] "
            f"retrieval={retrieval_time:.3f}s "
            f"context={context_time:.3f}s "
            f"llm={llm_time:.3f}s "
            f"total={total_time:.3f}s"
        )

        return content, documents