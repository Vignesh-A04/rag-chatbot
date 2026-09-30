"use client";

import { FormEvent, useState } from "react";

type Source = {
  page: number;
  source: string;
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

export default function Home() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) {
      return;
    }

    setError("");

    // Add user's message immediately
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
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
        }),
      });

      if (!response.ok) {
        throw new Error("Backend request failed");
      }

      const data: ChatResponse = await response.json();

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

  return (
    <main className="min-h-screen bg-gray-100">
      <div className="mx-auto flex min-h-screen max-w-4xl flex-col px-4 py-8">
        {/* Header */}
        <header className="mb-6 text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            RAG Chatbot
          </h1>

          <p className="mt-2 text-gray-600">
            Ask questions about the provided document.
          </p>
        </header>

        {/* Chat area */}
        <div className="flex-1 rounded-xl bg-white p-5 shadow-sm">
          {messages.length === 0 ? (
            <div className="flex h-full min-h-[400px] items-center justify-center">
              <div className="text-center">
                <h2 className="text-xl font-semibold text-gray-800">
                  Start a conversation
                </h2>

                <p className="mt-2 text-gray-500">
                  Ask something about the document.
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
                    <div className="mb-1 text-xs font-semibold uppercase tracking-wide opacity-60">
                      {message.role === "user" ? "You" : "AI"}
                    </div>

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
                            {message.sources.map((source, sourceIndex) => (
                              <div
                                key={`${source.source}-${source.page}-${sourceIndex}`}
                                className="rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-600"
                              >
                                <span className="font-medium">
                                  📄 Page {source.page + 1}
                                </span>

                                <span className="mx-2">•</span>

                                <span>
                                  {source.source.replace(
                                    "Vignesh_Arumugam_AI_Engineer_CV 4.pdf",
                                    "Resume"
                                  )}
                                </span>
                              </div>
                            ))}
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

                      <span className="animate-pulse">...</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {/* Input */}
        <form
          onSubmit={handleSubmit}
          className="mt-4 flex gap-3 rounded-xl bg-white p-3 shadow-sm"
        >
          <input
            type="text"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
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
    </main>
  );
}