from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


def load_document(pdf_path: str | Path):
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()

    return documents


if __name__ == "__main__":
    pdf_path = Path("data/documents/Vignesh_Arumugam_AI_Engineer_CV 4.pdf")

    documents = load_document(pdf_path)

    print(f"Total pages loaded: {len(documents)}")

    for document in documents:
        print("\n--- Page ---")
        print(document.page_content[:500])