import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL"),
)

response = llm.invoke(
    "Explain RAG in one simple sentence."
)

print(response.content)