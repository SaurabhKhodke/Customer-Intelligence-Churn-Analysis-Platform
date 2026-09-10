from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"


COLLECTION_NAME = "customer_churn_knowledge"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def load_documents():
    """
    Load all Markdown documents from rag/data/.
    """

    print("\nLoading Markdown documents...")

    loader = DirectoryLoader(
        str(DATA_DIR),
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={
            "encoding": "utf-8"
        },
        show_progress=True
    )

    documents = loader.load()

    print(f"\nDocuments loaded: {len(documents)}")

    for document in documents:
        print(
            f"  - {Path(document.metadata['source']).name}"
        )

    return documents



def split_documents(documents):
    """
    Split documents into smaller overlapping chunks.
    """

    print("\nSplitting documents into chunks...")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n## ",
            "\n### ",
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = text_splitter.split_documents(
        documents
    )

    print(
        f"Total chunks created: {len(chunks)}"
    )

    return chunks


def create_embeddings():
    """
    Load the Sentence Transformer embedding model.
    """

    print("\nLoading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        }
    )

    print("Embedding model loaded.")

    return embeddings


# ============================================================
# CREATE VECTOR STORE
# ============================================================

def create_vector_store(chunks, embeddings):
    """
    Create a persistent Chroma vector store.
    """

    print("\nCreating Chroma vector store...")

    # Remove old vector store contents if needed.
    # We recreate the collection so ingestion is reproducible.
    if VECTOR_STORE_DIR.exists():
        import shutil

        shutil.rmtree(
            VECTOR_STORE_DIR
        )

        print(
            "Existing vector store removed."
        )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(
            VECTOR_STORE_DIR
        )
    )

    print(
        "\nVector store created successfully."
    )

    print(
        f"Location: {VECTOR_STORE_DIR}"
    )

    print(
        f"Collection: {COLLECTION_NAME}"
    )

    return vector_store


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("CUSTOMER CHURN RAG - DOCUMENT INGESTION")
    print("=" * 60)

    # 1. Load Markdown documents
    documents = load_documents()

    if not documents:
        print(
            "\nNo Markdown documents found."
        )
        return

    # 2. Split into chunks
    chunks = split_documents(
        documents
    )

    # 3. Create embedding model
    embeddings = create_embeddings()

    # 4. Create Chroma vector database
    create_vector_store(
        chunks,
        embeddings
    )

    print("\n" + "=" * 60)
    print("INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()