from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.ingestion.loader import load_document


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=30,
    )

    chunks = splitter.split_documents(documents)
    return chunks


if __name__ == "__main__":
    pdf_path = Path("data/documents/Vignesh_Arumugam_AI_Engineer_CV 4.pdf")

    documents = load_document(pdf_path)
    chunks = split_documents(documents)

    print(f"Total pages: {len(documents)}")
    print(f"Total chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks):
        print(f"\n--- Chunk {index + 1} ---")
        print(f"Source: {chunk.metadata.get('source')}")
        print(f"Page: {chunk.metadata.get('page')}")
        print(chunk.page_content)