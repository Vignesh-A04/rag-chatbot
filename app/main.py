from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from app.rag.pipeline import RAGPipeline


app = FastAPI(
    title="RAG Chatbot API",
    description="Multi-document RAG chatbot using Gemini and Chroma",
    version="2.0.0",
)


# -----------------------------------------
# CORS
# -----------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://rag-chatbot-1-h8de.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------
# Paths
# -----------------------------------------

UPLOAD_DIR = Path("data/uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# -----------------------------------------
# RAG pipeline
# -----------------------------------------

rag = RAGPipeline()


# -----------------------------------------
# Request / Response models
# -----------------------------------------

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask about the uploaded documents",
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Question cannot be empty")

        return value


class Source(BaseModel):
    page: int | None
    source: str
    document_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    pages: int
    chunks: int


# -----------------------------------------
# Health
# -----------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


# -----------------------------------------
# Upload PDF
# -----------------------------------------

@app.post(
    "/upload",
    response_model=DocumentResponse,
)
def upload_document(
    file: UploadFile = File(...)
):

    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    # Only allow PDF files
    if Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # Create temporary filename
    temp_filename = f"{uuid.uuid4()}.pdf"

    temp_path = UPLOAD_DIR / temp_filename

    try:

        # Save uploaded file
        with temp_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer,
            )

        # Index the PDF
        result = rag.ingest_document(
            pdf_path=temp_path,
            filename=Path(file.filename).name,
        )

        # Rename temporary file to document ID
        final_path = (
            UPLOAD_DIR
            / f"{result['document_id']}.pdf"
        )

        temp_path.rename(final_path)

        return DocumentResponse(
            **result
        )

    except Exception as exc:

        # Remove temporary file if something failed
        if temp_path.exists():
            temp_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(exc)}",
        )

    finally:

        file.file.close()


# -----------------------------------------
# List documents
# -----------------------------------------

@app.get(
    "/documents",
    response_model=list[DocumentResponse],
)
def get_documents():

    documents = rag.get_document_info()

    return documents


# -----------------------------------------
# Delete one document
# -----------------------------------------

@app.delete(
    "/documents/{document_id}"
)
def delete_document(
    document_id: str
):

    deleted = rag.delete_document(
        document_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # Remove uploaded PDF
    pdf_path = (
        UPLOAD_DIR
        / f"{document_id}.pdf"
    )

    if pdf_path.exists():
        pdf_path.unlink()

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
    }


# -----------------------------------------
# Clear all documents
# -----------------------------------------

@app.delete("/documents")
def clear_documents():

    rag.clear_documents()

    # Remove all uploaded PDFs
    for pdf_file in UPLOAD_DIR.glob("*.pdf"):
        pdf_file.unlink()

    return {
        "message": "All documents cleared successfully."
    }


# -----------------------------------------
# Chat
# -----------------------------------------

@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    try:

        answer, documents = rag.ask(
            request.question
        )

        unique_sources = []
        seen = set()

        for document in documents:

            page = document.metadata.get(
                "page"
            )

            source = document.metadata.get(
                "source",
                "Unknown",
            )

            document_id = document.metadata.get(
                "document_id"
            )

            source_key = (
                document_id,
                page,
                source,
            )

            if source_key not in seen:

                seen.add(source_key)

                unique_sources.append(
                    Source(
                        page=page,
                        source=Path(source).name,
                        document_id=document_id,
                    )
                )

        return ChatResponse(
            answer=answer,
            sources=unique_sources,
        )

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing the question.",
        )