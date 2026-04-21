import os
import hashlib
import chromadb
import streamlit as st
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "data/chroma"
EMBED_MODEL = "paraphrase-multilingual-mpnet-base-v2"

_client = chromadb.PersistentClient(path=CHROMA_PATH)
_model = SentenceTransformer(EMBED_MODEL)


def _get_collection(username: str):
    name = f"documents_{username}" if username else "documents"
    return _client.get_or_create_collection(name)


def add_documents(chunks: list[dict], username: str) -> None:
    collection = _get_collection(username)
    texts = [c["text"] for c in chunks]
    embeddings = _model.encode(texts).tolist()
    ids = [_make_id(c) for c in chunks]
    metadatas = [{"source": c["source"], "page": str(c["page"])} for c in chunks]
    collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    list_sources.clear()
    list_sources_with_count.clear()


def search(query: str, username: str, k: int = None) -> list[dict]:
    collection = _get_collection(username)
    if k is None:
        k = int(os.getenv("SEARCH_K", 5))
    count = collection.count()
    if count == 0:
        return []
    k = min(k, count)
    embedding = _model.encode([query]).tolist()
    result = collection.query(query_embeddings=embedding, n_results=k)
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


@st.cache_data(ttl=30, show_spinner=False)
def list_sources(username: str) -> list[str]:
    collection = _get_collection(username)
    data = collection.get(include=["metadatas"])
    sources = {m["source"] for m in data["metadatas"]}
    return sorted(sources)


@st.cache_data(ttl=30, show_spinner=False)
def list_sources_with_count(username: str) -> list[dict]:
    collection = _get_collection(username)
    data = collection.get(include=["metadatas"])
    counts: dict[str, int] = {}
    for m in data["metadatas"]:
        counts[m["source"]] = counts.get(m["source"], 0) + 1
    return [{"source": s, "chunks": counts[s]} for s in sorted(counts)]


def delete_source(source: str, username: str) -> None:
    collection = _get_collection(username)
    data = collection.get(where={"source": source})
    if data["ids"]:
        collection.delete(ids=data["ids"])
    list_sources.clear()
    list_sources_with_count.clear()


def _make_id(chunk: dict) -> str:
    raw = f"{chunk['source']}_{chunk['page']}_{chunk['text'][:50]}"
    return hashlib.md5(raw.encode()).hexdigest()
