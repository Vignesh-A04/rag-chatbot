# RAG Chatbot

A full-stack Retrieval-Augmented Generation (RAG) chatbot built with Python, LangChain, Google Gemini, Chroma, FastAPI, and Next.js.

The application allows users to upload multiple PDF documents, retrieve relevant information from them, and generate grounded answers using Gemini.

## Features

- Multi-PDF document upload
- PDF text extraction using PyPDFLoader
- Recursive text chunking
- Gemini embeddings
- Chroma vector database
- Semantic similarity search
- Gemini-powered RAG responses
- Source and page attribution
- Document listing
- Individual document deletion
- Clear all documents
- Greeting handling
- Out-of-document fallback handling
- FastAPI REST API
- Next.js chat interface
- Document management interface

---

## Architecture

### Document Ingestion

```text
PDF
 ↓
FastAPI Upload
 ↓
PyPDFLoader
 ↓
Document Pages
 ↓
RecursiveCharacterTextSplitter
 ↓
Text Chunks
 ↓
Gemini Embeddings
 ↓
Chroma Vector Database



Question Answering
User Question
 ↓
Gemini Embedding
 ↓
Chroma Similarity Search
 ↓
Top 3 Relevant Chunks
 ↓
Context Construction
 ↓
Gemini LLM
 ↓
Answer + Sources

Technology Stack
Area	Technology	Purpose
Backend	Python	Application development
Backend	FastAPI	REST API
Backend	Uvicorn	ASGI server
Backend	Pydantic	Request/response validation
AI	LangChain	LLM and document processing
AI	Google Gemini	Answer generation
Embeddings	Gemini Embedding	Text embeddings
Vector DB	Chroma	Vector storage and similarity search
Document Processing	PyPDFLoader	PDF loading
Document Processing	RecursiveCharacterTextSplitter	Text chunking
Frontend	Next.js	Web application
Frontend	React	UI
Frontend	TypeScript	Frontend language
Frontend	Tailwind CSS	Styling
Version Control	Git / GitHub	Source control


Project Structure
rag-chatbot/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── chunker.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── embeddings.py
│   │
│   └── rag/
│       ├── __init__.py
│       └── pipeline.py
│
├── data/
│   ├── documents/
│   └── uploads/
│
├── frontend/
│
├── chroma_db/
├── .env
├── .gitignore
├── requirements.txt
└── README.md

Setup
Prerequisites
Install:
- Python 3.x
- Node.js
- npm
- Git
- Google Gemini API key
1. Clone the Repository
git clone https://github.com/vignesh-a-nt07/rag-chatbot.git
cd rag-chatbot

2. Backend Setup
Create Virtual Environment
python -m venv venv

Activate Virtual Environment
.\venv\Scripts\Activate.ps1

You should see:
(venv)

Install Dependencies
Use:
python -m pip install -r requirements.txt

3. Configure Environment Variables
Create a .env file in the project root:
GOOGLE_API_KEY=your_google_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-001

Replace your_google_api_key with your actual Gemini API key.
Never commit .env to GitHub.
Running the Application
4. Start the FastAPI Backend
From the project root:
python -m uvicorn app.main:app --reload

Backend:
http://127.0.0.1:8000

Swagger API documentation:
http://127.0.0.1:8000/docs

5. Start the Next.js Frontend
Open a second PowerShell terminal.
cd frontend
npm install
npm run dev

Frontend:
http://localhost:3000

API Endpoints
Health Check
GET /health

Example:
Invoke-RestMethod http://127.0.0.1:8000/health

Response:
{
  "status": "ok"
}

Upload Document
POST /upload

Accepts PDF files.
Example response:
{
  "document_id": "document-uuid",
  "filename": "example.pdf",
  "pages": 2,
  "chunks": 34
}

List Documents
GET /documents

Returns all currently uploaded documents.
Delete Document
DELETE /documents/{document_id}

Deletes one document and its associated chunks.
Delete All Documents
DELETE /documents

Removes all uploaded documents and their vector data.
Chat
POST /chat

Example request:
{
  "question": "What experience does Vignesh have with RAG?"
}

Example response:
{
  "answer": "The generated answer based on the uploaded documents.",
  "sources": [
    {
      "page": 1,
      "source": "example.pdf",
      "document_id": "document-uuid"
    }
  ]
}

RAG Configuration
Current configuration:
LLM:
gemini-3.5-flash-lite

Embedding Model:
gemini-embedding-001

Vector Database:
Chroma

Retrieval:
Similarity Search

Top K:
3

Chunk Size:
300

Chunk Overlap:
30

Multi-Document Architecture
Each uploaded PDF receives a unique document_id.
Document chunks contain metadata including:
document_id
source
page

This allows the application to:
- Upload multiple PDFs
- Store documents in the same Chroma collection
- Identify chunks belonging to each document
- Delete individual documents
- Clear all documents
- Return document and page sources with answers
Document Lifecycle
Upload PDF
    ↓
Generate document_id
    ↓
Save PDF
    ↓
Load PDF
    ↓
Split into chunks
    ↓
Generate embeddings
    ↓
Store in Chroma
    ↓
User asks question
    ↓
Similarity search
    ↓
Retrieve top 3 chunks
    ↓
Build context
    ↓
Gemini generates answer
    ↓
Return answer + sources

Frontend
The frontend contains two main sections:
Chat
- Ask questions about uploaded documents
- Display conversation history
- Display retrieved sources
- Handle loading states
- Handle backend errors
Documents
- Upload PDF files
- View uploaded documents
- Delete individual documents
- Clear all documents
Runtime Data
The following directories contain runtime data and should not be committed:
chroma_db/
data/uploads/

The .env file is also ignored by Git.
Testing
Backend Import Test
python -c "from app.main import app; print('Backend imports successfully')"

Expected:
Initializing RAG pipeline...
RAG pipeline initialized.
Backend imports successfully

Health Test
With the backend running:
Invoke-RestMethod http://127.0.0.1:8000/health

Expected:
{
  "status": "ok"
}

Example Questions
After uploading a document, try questions based on the uploaded pdf.

The chatbot should answer using information retrieved from the uploaded documents.
Project Flow
                    ┌─────────────────┐
                    │   Next.js UI    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     FastAPI     │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
      ┌───────────────┐             ┌───────────────┐
      │ PDF Ingestion │             │ RAG Pipeline  │
      └───────┬───────┘             └───────┬───────┘
              │                             │
              ▼                             ▼
      ┌───────────────┐             ┌───────────────┐
      │ Text Chunking │             │    Chroma     │
      └───────┬───────┘             │ Vector Store  │
              │                     └───────┬───────┘
              ▼                             │
      ┌───────────────┐                     │
      │    Gemini     │                     │
      │   Embeddings  │                     │
      └───────────────┘                     │
                                            ▼
                                    ┌───────────────┐
                                    │  Gemini LLM   │
                                    └───────────────┘

Interview Explanation
I built a full-stack RAG chatbot using Python, LangChain, Google Gemini, Chroma, FastAPI, and Next.js.
The system allows users to upload multiple PDF documents. Each document is loaded using PyPDFLoader and split into smaller chunks using RecursiveCharacterTextSplitter. Gemini embeddings convert the chunks into vectors, which are stored in Chroma.
When a user asks a question, the question is embedded and a similarity search retrieves the top relevant chunks from Chroma. These chunks are provided as context to Gemini, which generates a grounded response.
Each document receives a unique document ID, allowing individual documents to be listed, deleted, or cleared. The API also returns source and page information for retrieved content.
FastAPI exposes the backend REST APIs, while Next.js provides the web-based chat and document management interface.

Current Status
The following functionality is implemented:
- [x] PDF upload
- [x] Multiple document support
- [x] PDF text extraction
- [x] Document chunking
- [x] Gemini embeddings
- [x] Chroma vector database
- [x] Similarity search
- [x] Top-K retrieval
- [x] Context construction
- [x] Gemini LLM generation
- [x] Grounded responses
- [x] Source attribution
- [x] Greeting handling
- [x] Out-of-document fallback
- [x] FastAPI backend
- [x] Pydantic validation
- [x] CORS
- [x] Next.js frontend
- [x] Chat interface
- [x] Document management
- [x] Document deletion
- [x] Clear all documents
- [x] Git/GitHub repository
