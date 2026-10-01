"use client";

import { FormEvent, useEffect, useState } from "react";

type Source = {
  page: number | null;
  source: string;
  document_id: string | null;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

type ChatResponse = {
  answer: string;
  sources: Source[];
};

type Document = {
  document_id: string;
  filename: string;
  pages: number;
  chunks: number;
};

type View = "chat" | "documents";

const API_URL = "https://rag-chatbot-p2ds.onrender.com";

export default function Home() {
  const [view, setView] = useState<View>("chat");

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [clearing, setClearing] = useState(false);

  const [error, setError] = useState("");

  // -----------------------------------------
  // Load documents
  // -----------------------------------------

  async function loadDocuments() {
    try {
      const response = await fetch(`${API_URL}/documents`);

      if (!response.ok) {
        throw new Error("Failed to load documents");
      }

      const data: Document[] = await response.json();

      setDocuments(data);
    } catch (error) {
      console.error(error);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  // -----------------------------------------
  // Upload PDF
  // -----------------------------------------

  async function handleUpload(
    event: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.");
      event.target.value = "";
      return;
    }

    setError("");
    setUploading(true);

    const formData = new FormData();

    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      await loadDocuments();

      // Start a fresh conversation because
      // the document collection changed.
      setMessages([]);

      // Return to chatbot after upload.
      setView("chat");
    } catch (error) {
      console.error(error);

      setError(
        error instanceof Error
          ? error.message
          : "Failed to upload PDF."
      );
    } finally {
      setUploading(false);

      // Allow the same file to be selected again.
      event.target.value = "";
    }
  }

  // -----------------------------------------
  // Delete one document
  // -----------------------------------------

  async function handleDelete(documentId: string) {
    setError("");

    try {
      const response = await fetch(
        `${API_URL}/documents/${documentId}`,
        {
          method: "DELETE",
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Delete failed");
      }

      await loadDocuments();

      // Clear current conversation because
      // the document collection changed.
      setMessages([]);
    } catch (error) {
      console.error(error);

      setError(
        error instanceof Error
          ? error.message
          : "Failed to delete document."
      );
    }
  }

  // -----------------------------------------
  // Clear all documents
  // -----------------------------------------

  async function handleClearAll() {
    if (documents.length === 0) {
      return;
    }

    const confirmed = window.confirm(
      "Are you sure you want to delete all uploaded documents?"
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setClearing(true);

    try {
      const response = await fetch(`${API_URL}/documents`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Clear failed");
      }

      setDocuments([]);
      setMessages([]);
    } catch (error) {
      console.error(error);

      setError(
        error instanceof Error
          ? error.message
          : "Failed to clear documents."
      );
    } finally {
      setClearing(false);
    }
  }

  // -----------------------------------------
  // Chat
  // -----------------------------------------

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setError("");

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: trimmedQuestion,
      },
    ]);

    setQuestion("");
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
        }),
      });

      const data: ChatResponse = await response.json();

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (error) {
      console.error(error);

      setError(
        "Unable to connect to the RAG backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  // -----------------------------------------
  // Chat View
  // -----------------------------------------

  function renderChat() {
    return (
      <div className="flex min-h-0 flex-1 flex-col">
        {/* -------------------------------- */}
        {/* Chat messages */}
        {/* -------------------------------- */}

        <div className="min-h-0 flex-1 overflow-y-auto rounded-xl bg-white p-5 shadow-sm">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <h2 className="text-xl font-semibold text-gray-800">
                  Start a conversation
                </h2>

                <p className="mt-2 text-gray-500">
                  Ask a question about your uploaded documents.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={
                    message.role === "user"
                      ? "flex justify-end"
                      : "flex justify-start"
                  }
                >
                  <div
                    className={
                      message.role === "user"
                        ? "max-w-[80%] rounded-2xl rounded-br-md bg-black px-5 py-3 text-white"
                        : "max-w-[85%] rounded-2xl rounded-bl-md bg-gray-100 px-5 py-4 text-gray-900"
                    }
                  >
                    {/* Message role */}

                    <div className="mb-1 text-xs font-semibold uppercase tracking-wide opacity-60">
                      {message.role === "user" ? "You" : "AI"}
                    </div>

                    {/* Message content */}

                    <div className="whitespace-pre-wrap leading-7">
                      {message.content}
                    </div>

                    {/* Sources */}

                    {message.role === "assistant" &&
                      message.sources &&
                      message.sources.length > 0 && (
                        <div className="mt-5 border-t border-gray-300 pt-4">
                          <p className="mb-2 text-sm font-semibold text-gray-700">
                            Sources
                          </p>

                          <div className="space-y-2">
                            {message.sources.map(
                              (source, sourceIndex) => (
                                <div
                                  key={`${source.document_id}-${source.page}-${sourceIndex}`}
                                  className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-600"
                                >
                                  <span className="font-medium">
                                    📄 Page{" "}
                                    {source.page !== null
                                      ? source.page + 1
                                      : "?"}
                                  </span>

                                  <span className="mx-2">
                                    •
                                  </span>

                                  <span>
                                    {source.source}
                                  </span>
                                </div>
                              )
                            )}
                          </div>
                        </div>
                      )}
                  </div>
                </div>
              ))}

              {/* Loading */}

              {loading && (
                <div className="flex justify-start">
                  <div className="rounded-2xl rounded-bl-md bg-gray-100 px-5 py-4 text-gray-600">
                    <div className="flex items-center gap-2">
                      <span>AI is thinking</span>

                      <span className="animate-pulse">
                        ...
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* -------------------------------- */}
        {/* Chat input */}
        {/* -------------------------------- */}

        <form
          onSubmit={handleSubmit}
          className="mt-3 flex flex-shrink-0 gap-3 rounded-xl bg-white p-3 shadow-sm"
        >
          <input
            type="text"
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            placeholder="Ask a question..."
            disabled={loading}
            className="flex-1 rounded-lg border border-gray-300 px-4 py-3 text-gray-900 placeholder-gray-400 outline-none focus:border-gray-500 disabled:bg-gray-100"
          />

          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="rounded-lg bg-black px-6 py-3 font-medium text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "..." : "Send"}
          </button>
        </form>
      </div>
    );
  }

  // -----------------------------------------
  // Documents View
  // -----------------------------------------

  function renderDocuments() {
    return (
      <div className="flex min-h-0 flex-1 flex-col rounded-xl bg-white p-6 shadow-sm">
        {/* Header */}

        <div className="flex flex-col gap-4 border-b border-gray-200 pb-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              Documents
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              Upload and manage documents used by the chatbot.
            </p>
          </div>

          <div className="flex gap-2">
            {/* Upload */}

            <label
              className={`cursor-pointer rounded-lg px-4 py-2 text-sm font-medium text-white transition ${
                uploading
                  ? "cursor-not-allowed bg-gray-400"
                  : "bg-black hover:bg-gray-800"
              }`}
            >
              {uploading ? "Uploading..." : "Upload PDF"}

              <input
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleUpload}
                disabled={uploading}
                className="hidden"
              />
            </label>

            {/* Clear All */}

            {documents.length > 0 && (
              <button
                type="button"
                onClick={handleClearAll}
                disabled={clearing}
                className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {clearing ? "Clearing..." : "Clear All"}
              </button>
            )}
          </div>
        </div>

        {/* Document list */}

        <div className="min-h-0 flex-1 overflow-y-auto">
          {documents.length === 0 ? (
            <div className="flex h-full min-h-[300px] items-center justify-center">
              <div className="text-center">
                <div className="text-4xl">📄</div>

                <h3 className="mt-4 font-semibold text-gray-800">
                  No documents uploaded
                </h3>

                <p className="mt-2 text-sm text-gray-500">
                  Upload a PDF to start asking questions.
                </p>
              </div>
            </div>
          ) : (
            <div className="space-y-3 pt-5">
              {documents.map((document) => (
                <div
                  key={document.document_id}
                  className="flex flex-col gap-3 rounded-lg border border-gray-200 bg-gray-50 p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="min-w-0">
                    <p className="truncate font-medium text-gray-800">
                      📄 {document.filename}
                    </p>

                    <p className="mt-1 text-xs text-gray-500">
                      {document.pages}{" "}
                      {document.pages === 1
                        ? "page"
                        : "pages"}{" "}
                      • {document.chunks} chunks
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      handleDelete(
                        document.document_id
                      )
                    }
                    className="self-start rounded-md px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-100 sm:self-auto"
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // -----------------------------------------
  // Main Layout
  // -----------------------------------------

  return (
    <main className="h-screen overflow-hidden bg-gray-100">
      <div className="mx-auto flex h-full max-w-5xl flex-col px-4 py-3">
        {/* -------------------------------- */}
        {/* Navigation */}
        {/* -------------------------------- */}

        <header className="mb-3 flex flex-shrink-0 items-center justify-between rounded-xl bg-white px-5 py-3 shadow-sm">
          {/* Logo / title */}

          <button
            type="button"
            onClick={() => setView("chat")}
            className="text-left"
          >
            <h1 className="text-xl font-bold text-gray-900">
              RAG Chatbot
            </h1>

            <p className="text-xs text-gray-500">
              Document-based AI assistant
            </p>
          </button>

          {/* Navigation */}

          <nav className="flex items-center gap-1">
            <button
              type="button"
              onClick={() => setView("chat")}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                view === "chat"
                  ? "bg-gray-100 text-gray-900"
                  : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              Chat
            </button>

            <button
              type="button"
              onClick={() => setView("documents")}
              className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                view === "documents"
                  ? "bg-gray-100 text-gray-900"
                  : "text-gray-500 hover:bg-gray-50 hover:text-gray-900"
              }`}
            >
              Documents
            </button>
          </nav>
        </header>

        {/* -------------------------------- */}
        {/* Error */}
        {/* -------------------------------- */}

        {error && (
          <div className="mb-3 flex-shrink-0 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* -------------------------------- */}
        {/* Main content */}
        {/* -------------------------------- */}

        {view === "chat"
          ? renderChat()
          : renderDocuments()}
      </div>
    </main>
  );
}