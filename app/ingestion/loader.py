from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader


PDF_PATH = Path(
    "data/documents/Vignesh_Arumugam_AI_Engineer_CV 4.pdf"
)


def load_document():
    loader = PyPDFLoader(str(PDF_PATH))
    documents = loader.load()

    return documents


if __name__ == "__main__":
    documents = load_document()

    print(f"Total pages loaded: {len(documents)}")

    for document in documents:
        print("\n--- Page ---")
        print(document.page_content[:500])