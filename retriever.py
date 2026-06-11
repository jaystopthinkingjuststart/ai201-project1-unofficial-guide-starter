"""
retriever.py — Milestone 4: embed chunks and test retrieval.

Run:  python retriever.py
On first run it downloads all-MiniLM-L6-v2 (~80MB), embeds every chunk from
ingest.build_chunks() into a persistent ChromaDB collection, then runs sample
queries and prints the results with distance scores so you can sanity-check
retrieval before adding generation.

To re-embed after changing chunking: delete ./chroma_db and re-run.
"""

import chromadb
from chromadb.utils import embedding_functions
from ingest import build_chunks

EMBEDDING_MODEL = "all-MiniLM-L6-v2"   # local, no API key (planning.md)
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "unofficial_guide"
TOP_K = 5                               # planning.md: aggregate several opinions

# Embedding function + persistent client are created once at import.
_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=_ef,
    metadata={"hnsw:space": "cosine"},   # cosine distance: lower = more similar
)


def embed_and_store(chunks):
    """Embed chunks and store them in ChromaDB with source + position metadata.

    ChromaDB runs each `documents` string through the embedding function above,
    so we hand over text, not vectors. Metadata travels with each vector for
    later attribution.
    """
    _collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[
            {"source": c["source"], "position": int(c["chunk_id"].rsplit("_", 1)[1])}
            for c in chunks
        ],
        ids=[c["chunk_id"] for c in chunks],
    )
    print(f"Stored {_collection.count()} chunks in the vector store.")


def retrieve(query, n_results=TOP_K):
    """Return the top-k most relevant chunks with text, source, and distance."""
    if _collection.count() == 0:
        return []
    results = _collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    return [
        {"text": docs[i], "source": metas[i]["source"], "distance": dists[i]}
        for i in range(len(docs))
    ]


def ingest_if_empty():
    """Embed chunks only if the store is empty (avoids duplicate-id errors on re-run)."""
    if _collection.count() == 0:
        print("Vector store empty — embedding chunks (first run downloads the model)...")
        embed_and_store(build_chunks())
    else:
        print(f"Vector store already has {_collection.count()} chunks. "
              "Delete ./chroma_db to re-embed after changing chunking.")


if __name__ == "__main__":
    ingest_if_empty()

    test_queries = [
        "Which professors do students say are the best?",
        "Which computer engineering (CPR E) professors should I avoid?",
        "What are some fun, easy classes to take?",
    ]
    for q in test_queries:
        print("\n" + "=" * 70)
        print(f"QUERY: {q}")
        print("=" * 70)
        for r in retrieve(q):
            print(f"\n[{r['source']}] (distance: {r['distance']:.3f})")
            print(r["text"][:300])
