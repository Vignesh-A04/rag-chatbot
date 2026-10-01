# RAG Chatbot

A full-stack Retrieval-Augmented Generation (RAG) chatbot that answers questions from a provided PDF document.

The project demonstrates an end-to-end RAG pipeline using:

- Python
- LangChain
- Google Gemini
- Gemini Embeddings
- Chroma
- FastAPI
- Next.js
- React
- TypeScript
- Tailwind CSS

The application loads a PDF, splits it into smaller chunks, converts those chunks into embeddings, stores them in Chroma, retrieves the most relevant chunks for a user question, and uses Gemini to generate a grounded answer.

---

# 1. Project Overview

Traditional LLM applications can generate answers using the model's general knowledge, but they do not automatically know the contents of a private document.

This project solves that problem using Retrieval-Augmented Generation.

Instead of asking the LLM to answer directly:

```text
User Question
      ↓
     LLM
      ↓
   Answer
































 
   
RAG Chatbot

Full-stack Retrieval-Augmented Generation chatbot using Python, LangChain, Google Gemini, Chroma, FastAPI, and Next.js.

1. Project Overview

This project reads a PDF document, processes and chunks its content, creates embeddings, stores the embeddings in Chroma, retrieves relevant chunks for a user's question, and uses Google Gemini to generate a grounded answer. The Next.js frontend provides a web-based chat interface and displays document sources.

PDF
 |
 v
PyPDFLoader
 |
 v
RecursiveCharacterTextSplitter
 |
 v
Gemini Embeddings
 |
 v
Chroma Vector Database
 |
 v
User Question
 |
 v
Query Embedding
 |
 v
Chroma Similarity Search
 |
 v
Top 3 Relevant Chunks
 |
 v
Gemini LLM
 |
 v
FastAPI
 |
 v
Next.js Frontend

2. Technology Stack

Area

Technology

Purpose

Backend

Python

Main backend language

Backend

FastAPI

REST API

Backend

Uvicorn

ASGI server

Backend

Pydantic

Request/response validation

AI

LangChain

AI/LLM integrations and orchestration

AI

Google Gemini

LLM generation

AI

gemini-embedding-001

Text embeddings

Vector DB

Chroma

Vector storage and similarity search

Document

PyPDFLoader

PDF loading

Document

RecursiveCharacterTextSplitter

Document chunking

Frontend

Next.js

Frontend framework

Frontend

React

UI

Frontend

TypeScript

Frontend language

Frontend

Tailwind CSS

Styling

Development

Git / GitHub

Version control and repository

3. Prerequisites

Install the following before running the project:

Python 3.x

Node.js and npm

Git

A Google Gemini API key

4. Clone the Repository

git clone https://github.com/vignesh-a-nt07/rag-chatbot.git
cd rag-chatbot

5. Backend Setup

Step 1 - Create the Python Virtual Environment

python -m venv venv

Step 2 - Activate the Virtual Environment

.\venv\Scripts\Activate.ps1

The terminal should show (venv) after activation.

Step 3 - Install Backend Dependencies

pip install -r requirements.txt

6. Configure Environment Variables

Create a .env file in the project root:

GOOGLE_API_KEY=your_google_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-001

Replace your_google_api_key with the actual Gemini API key. Never commit the API key to GitHub.

7. Source Document

The current source document is:

data/documents/Vignesh_Arumugam_AI_Engineer_CV 4.pdf

8. Create the Chroma Vector Database

The vector database must be created before the application can answer questions. Run this once after the initial setup:

python -m app.retrieval.vector_store

This performs PDF loading, chunking, embedding generation, and Chroma storage.

chroma_db/

9. Rebuild Chroma When Needed

If the source document, chunk size, chunk overlap, or embedding model changes, rebuild the local Chroma database:

Remove-Item chroma_db -Recurse -Force
python -m app.retrieval.vector_store

10. Current Chunking Configuration

chunk_size = 300
chunk_overlap = 30

This configuration was tested against the current resume document and produced focused retrieval results for the project's test questions.

11. Start the FastAPI Backend

python -m uvicorn app.main:app --reload

Backend URL:

http://127.0.0.1:8000

12. Test Backend Health

Invoke-RestMethod http://127.0.0.1:8000/health

Expected response:

{
  "status": "ok"
}

13. FastAPI Swagger UI

Open:

http://127.0.0.1:8000/docs

The Swagger UI exposes:

GET /health

POST /chat

14. Test the Chat API

$body = @{
    question = "What experience does Vignesh have with RAG?"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

The API returns an answer and source metadata.

15. Frontend Setup

Open a second PowerShell terminal and move into the frontend directory:

cd frontend
npm install

16. Start Next.js

npm run dev

Frontend URL:

http://localhost:3000

17. Run the Complete Application

Two terminals are required.

Terminal 1 - Backend

cd D:\vicky\practice\Repo\rag-chatbot
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload

Terminal 2 - Frontend

cd D:\vicky\practice\Repo\rag-chatbot\frontend
npm run dev

Then open:

http://localhost:3000

18. Test Questions

What experience does Vignesh have with RAG?

What technologies does Vignesh use for Generative AI?

What backend technologies does Vignesh know?

What cloud and deployment technologies does Vignesh use?

19. Greeting Test

hi

Simple greetings are handled directly without running the complete RAG process.

20. Out-of-Document Test

how are you?

Expected fallback: "I couldn't find that information in the provided document."

21. Frontend to Backend Flow

Next.js
   |
   | POST /chat
   v
FastAPI
   |
   v
RAGPipeline
   |
   +----> Gemini Embeddings
   |
   +----> Chroma Search
   |
   +----> Gemini LLM
   |
   v
Answer + Sources
   |
   v
Next.js

22. Project Structure

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
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── retriever.py
│   │
│   └── rag/
│       ├── __init__.py
│       └── pipeline.py
│
├── data/
│   └── documents/
│       └── Vignesh_Arumugam_AI_Engineer_CV 4.pdf
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── public/
│   ├── package.json
│   └── ...
│
├── chroma_db/
├── .env
├── .gitignore
├── requirements.txt
└── README.md

23. Module Responsibilities

File

Responsibility

app/ingestion/loader.py

Loads the PDF using PyPDFLoader.

app/ingestion/chunker.py

Splits documents into chunks.

app/retrieval/embeddings.py

Creates the Gemini embedding integration.

app/retrieval/vector_store.py

Creates and populates the Chroma vector database.

app/retrieval/retriever.py

Provides the retrieval abstraction.

app/rag/pipeline.py

Coordinates retrieval, context construction, prompting, and Gemini generation.

app/main.py

Exposes the RAG pipeline through FastAPI.

frontend/app/page.tsx

Provides the chat interface and calls the backend API.

24. Important Component Responsibilities

Component

Role

Python

Runs the application code.

LangChain

Provides integrations and orchestration.

Gemini Embeddings

Converts text into vectors.

Chroma

Stores vectors and performs vector similarity search.

Gemini LLM

Generates the final answer.

FastAPI

Exposes the backend REST API.

Next.js

Provides the web interface.

25. Current Retrieval Configuration

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

26. Retrieval Evaluation

The project includes evaluation questions covering RAG, Generative AI, backend technologies, and cloud/deployment technologies.

The current test set achieved 100% topic coverage. This result applies only to the current questions and source document and is not a general RAG benchmark.

27. Latency Measurement

The RAG pipeline measures retrieval time, context construction time, LLM generation time, and total response time.

[RAG]
retrieval=0.762s
context=0.001s
llm=1.442s
total=2.204s

28. Troubleshooting

Backend cannot connect

Make sure FastAPI is running:

python -m uvicorn app.main:app --reload

Then check:

http://127.0.0.1:8000/health

Frontend says Unable to connect to backend

Make sure both applications are running:

Backend: http://127.0.0.1:8000

Frontend: http://localhost:3000

Also check the browser developer console for errors.

Gemini API error

Check the .env values and restart the backend after changing them.

Chroma problems

Remove-Item chroma_db -Recurse -Force
python -m app.retrieval.vector_store

Node/npm not recognized

node --version
npm --version

If Node.js is installed but PowerShell cannot find it, restart PowerShell so the updated PATH is loaded.

29. .gitignore

# Python
venv/
__pycache__/
*.py[cod]
*.pyo

# Environment variables
.env
.env.*

# Chroma
chroma_db/

# Next.js
frontend/node_modules/
frontend/.next/
frontend/out/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

30. Git Workflow

git status
git add .
git commit -m "complete RAG chatbot V1"
git push origin main

31. Current Project Status

PDF document loading

Document chunking

Gemini embeddings

Chroma vector database

Similarity search

Top-K retrieval

Context construction

Gemini LLM generation

Grounded responses

Greeting handling

Out-of-document handling

FastAPI backend

Pydantic validation

CORS

Next.js frontend

React chat UI

TypeScript

Tailwind CSS

Chat history

Loading state

Error handling

Source display

Retrieval evaluation

Latency measurement

Git/GitHub

32. Current Limitations

Single configured PDF document

Local Chroma database

No authentication

No persistent conversation storage

No document upload UI

No streaming responses

No multi-user architecture

No production vector database

No cloud deployment

Similarity search only

33. Future Improvements

Multi-document support
        |
        v
Document upload
        |
        v
Metadata filtering
        |
        v
Hybrid search
        |
        v
Reranking
        |
        v
Streaming responses
        |
        v
Authentication
        |
        v
Persistent conversations
        |
        v
Production vector database
        |
        v
Cloud deployment
        |
        v
Monitoring and observability

34. Quick Start

For an already cloned repository:

# Terminal 1 - Backend
cd rag-chatbot
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd rag-chatbot\frontend
npm run dev

Open:

http://localhost:3000

35. First-Time Setup - Complete Command List

git clone https://github.com/vignesh-a-nt07/rag-chatbot.git
cd rag-chatbot

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Create .env with your Gemini API key

python -m app.retrieval.vector_store

# Terminal 1
python -m uvicorn app.main:app --reload

# Terminal 2
cd frontend
npm install
npm run dev

36. Interview Explanation

I built a full-stack RAG chatbot using Python, LangChain, Google Gemini, Chroma, FastAPI, and Next.js. The system loads a PDF using PyPDFLoader, splits it into chunks using RecursiveCharacterTextSplitter, generates embeddings using Gemini's embedding model, and stores those embeddings in Chroma. When a user asks a question, the question is converted into an embedding and Chroma performs similarity search to retrieve the top relevant chunks. Those chunks are passed as context to Gemini, which generates a grounded answer. FastAPI exposes the RAG pipeline through REST APIs, while the Next.js frontend provides the chat interface and displays the retrieved document sources.

37. Repository

GitHub repository:

https://github.com/vignesh-a-nt07/rag-chatbot