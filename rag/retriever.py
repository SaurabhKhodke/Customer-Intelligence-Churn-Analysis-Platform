from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# Paths

BASE_DIR = Path(__file__).resolve().parent

VECTOR_STORE_DIR = BASE_DIR / "vector_store"

COLLECTION_NAME = "customer_churn_knowledge"


# Load embedding model

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Load Chroma vector store

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=str(VECTOR_STORE_DIR),
    embedding_function=embeddings
)


# Retriever


retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 5
    }
)


# Retrieval function


def retrieve_documents(query: str, k: int = 5):
    """
    Retrieve the most relevant knowledge chunks
    for a user query.
    """

    results = vector_store.similarity_search(
        query,
        k=k
    )

    return results


# Test

if __name__ == "__main__":

    print("=" * 60)
    print("CUSTOMER CHURN RAG - RETRIEVAL TEST")
    print("=" * 60)

    query = input("\nEnter your question: ")

    documents = retrieve_documents(query)

    print(f"\nRetrieved documents: {len(documents)}")

    print("\n" + "=" * 60)

    for i, doc in enumerate(documents, start=1):

        print(f"\nRESULT {i}")
        print("-" * 60)

        print("Source:", doc.metadata.get("source"))

        print("\nContent:")
        print(doc.page_content[:1000])

    print("\n" + "=" * 60)