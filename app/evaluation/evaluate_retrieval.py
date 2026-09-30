from app.evaluation.test_questions import EVALUATION_QUESTIONS
from app.retrieval.embeddings import create_embeddings

from langchain_chroma import Chroma


CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "resume"


def evaluate_question(vector_store, question_data, k=5):

    question = question_data["question"]
    expected_topics = question_data["expected_topics"]

    documents = vector_store.similarity_search(
        question,
        k=k,
    )

    combined_context = " ".join(
        document.page_content.lower()
        for document in documents
    )

    matched_topics = []
    missing_topics = []

    for topic in expected_topics:

        if topic.lower() in combined_context:
            matched_topics.append(topic)
        else:
            missing_topics.append(topic)

    score = len(matched_topics) / len(expected_topics) * 100

    print("\n" + "=" * 80)
    print(f"QUESTION: {question}")
    print("=" * 80)

    print(f"\nRetrieval k: {k}")

    print("\nMatched topics:")
    for topic in matched_topics:
        print(f"  [OK] {topic}")

    print("\nMissing topics:")
    for topic in missing_topics:
        print(f"  [MISS] {topic}")

    print(f"\nTopic coverage: {score:.1f}%")

    print("\nRetrieved chunks:")

    for index, document in enumerate(documents, start=1):

        print(f"\n--- Rank {index} ---")
        print(f"Page: {document.metadata.get('page')}")
        print(document.page_content[:300])


def main():

    embeddings = create_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )

    for question_data in EVALUATION_QUESTIONS:

        evaluate_question(
            vector_store,
            question_data,
            k=5,
        )


if __name__ == "__main__":
    main()