from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.rag.pipeline import RAGPipeline


app = FastAPI(
    title="RAG Chatbot API",
    description="Document-based RAG chatbot using Gemini and Chroma",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize once when the application starts
rag = RAGPipeline()


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask about the document",
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


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer, documents = rag.ask(request.question)

        unique_sources = []
        seen = set()

        for document in documents:
            page = document.metadata.get("page")
            source = document.metadata.get("source", "Unknown")

            # Only return the filename instead of the full Windows path
            source_name = Path(source).name

            source_key = (page, source_name)

            if source_key not in seen:
                seen.add(source_key)

                unique_sources.append(
                    Source(
                        page=page,
                        source=source_name,
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