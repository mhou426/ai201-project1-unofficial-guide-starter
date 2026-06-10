from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from ingest import get_chunks

CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "text_chunks"
MODEL_NAME = "all-MiniLM-L6-v2"

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def _get_client():
    return chromadb.PersistentClient(path=str(CHROMA_DIR))

def build_index():
    chunks = get_chunks()
    if not chunks:
        raise ValueError("No chunks found. Add .txt files to documents/.")

    model = _get_model()
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    ids = [f"{c['source']}__{c['chunk_index']}" for c in chunks]
    metadatas = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]

    client = _get_client()
    # fresh rebuild each time so re-running doesn't duplicate
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.create_collection(name=COLLECTION_NAME)
    collection.add(
        documents=texts,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings.tolist(),
    )
    print(f"Stored {len(texts)} embeddings in ChromaDB collection '{COLLECTION_NAME}'.")

def retrieve(query: str, k: int = 4):
    model = _get_model()
    query_embedding = model.encode(query, convert_to_numpy=True)
    client = _get_client()
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    result = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    chunks = []
    for text, meta, distance in zip(documents, metadatas, distances):
        chunks.append({"text": text, "source": meta.get("source", "unknown"), "distance": distance})
    return chunks

if __name__ == "__main__":
    build_index()
