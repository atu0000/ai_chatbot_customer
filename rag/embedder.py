import os
import hashlib
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "documents"
EMBED_MODEL = "paraphrase-multilingual-mpnet-base-v2"

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_collection = _client.get_or_create_collection(COLLECTION_NAME)
_model = SentenceTransformer(EMBED_MODEL)


def add_documents(chunks: list[dict]) -> None:
    texts = [c["text"] for c in chunks]
    embeddings = _model.encode(texts).tolist()
    ids = [_make_id(c) for c in chunks]
    metadatas = [{"source": c["source"], "page": str(c["page"])} for c in chunks]
    _collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)


def search(query: str, k: int = None) -> list[dict]:
    if k is None:
        k = int(os.getenv("SEARCH_K", 5))
    count = _collection.count()
    if count == 0:
        return []
    k = min(k, count)
    embedding = _model.encode([query]).tolist()
    result = _collection.query(query_embeddings=embedding, n_results=k)
    hits = []
    for text, meta, dist in zip(
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        hits.append({
            "text": text,
            "source": meta["source"],
            "page": meta["page"],
            "score": round(1 / (1 + dist), 4),
        })
    return hits


def list_sources() -> list[str]:
    data = _collection.get(include=["metadatas"])
    sources = {m["source"] for m in data["metadatas"]}
    return sorted(sources)


def list_sources_with_count() -> list[dict]:
    data = _collection.get(include=["metadatas"])
    counts: dict[str, int] = {}
    for m in data["metadatas"]:
        counts[m["source"]] = counts.get(m["source"], 0) + 1
    return [{"source": s, "chunks": counts[s]} for s in sorted(counts)]


def delete_source(source: str) -> None:
    data = _collection.get(where={"source": source})
    if data["ids"]:
        _collection.delete(ids=data["ids"])


def _make_id(chunk: dict) -> str:
    raw = f"{chunk['source']}_{chunk['page']}_{chunk['text'][:50]}"
    return hashlib.md5(raw.encode()).hexdigest()
