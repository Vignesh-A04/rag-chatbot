EVALUATION_QUESTIONS = [
    {
        "question": "What experience does Vignesh have with RAG?",
        "expected_topics": [
            "Retrieval-Augmented Generation",
            "LangChain",
            "embeddings",
            "vector databases",
        ],
    },
    {
        "question": "What technologies does Vignesh use for Generative AI?",
        "expected_topics": [
            "LLMs",
            "LangChain",
            "OpenAI",
            "Google Gemini",
            "Groq",
            "Ollama",
        ],
    },
    {
        "question": "What backend technologies does Vignesh know?",
        "expected_topics": [
            "FastAPI",
            "REST API",
            "Node.js",
            "Spring Boot",
            "Hibernate",
        ],
    },
    {
        "question": "What cloud and deployment technologies does Vignesh use?",
        "expected_topics": [
            "Docker",
            "AWS",
            "Amazon EKS",
            "Kubernetes",
            "CI/CD",
        ],
    },
]

if __name__ == "__main__":
    print(f"Total evaluation questions: {len(EVALUATION_QUESTIONS)}")

    for index, item in enumerate(EVALUATION_QUESTIONS, start=1):
        print(f"\n{index}. {item['question']}")
        print(f"Expected topics: {item['expected_topics']}")