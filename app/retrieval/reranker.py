import os
import json

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


class LLMReranker:

    def __init__(self):

        model = os.getenv("GEMINI_MODEL")

        if not model:
            raise ValueError("GEMINI_MODEL is not set")

        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
        )

    def rerank(self, question, documents, top_n=3):

        candidates = []

        for index, document in enumerate(documents):

            candidates.append(
                {
                    "index": index,
                    "content": document.page_content,
                }
            )

        prompt = f"""
You are a document retrieval reranker.

Your task is to rank the provided document chunks
according to how relevant they are for answering the user's question.

User question:
{question}

Document chunks:
{json.dumps(candidates, indent=2)}

Return ONLY a JSON array containing the indexes of the
most relevant chunks, ordered from most relevant to least relevant.

Return exactly {top_n} indexes.

Example:
[2, 0, 4]
"""

        response = self.llm.invoke(prompt)

        content = response.content

        if isinstance(content, list):
            content = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
                and item.get("type") == "text"
            )

        ranked_indexes = json.loads(content)

        reranked_documents = [
            documents[index]
            for index in ranked_indexes
        ]

        return reranked_documents