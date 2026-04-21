import os
import hashlib
import chromadb
import streamlit as st
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "data/chroma"
EMBED_MODEL = "paraphrase-multilingual-mpnet-base-v2"
SHARED_USER = "__shared__"

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
    if k is None:
        k = int(os.getenv("SEARCH_K", 5))
    embedding = _model.encode([query]).tolist()

    raw: list[dict] = []
    for col_user in [username, SHARED_USER]:
        collection = _get_collection(col_user)
        count = collection.count()
        if count == 0:
            continue
        n = min(k, count)
        result = collection.query(query_embeddings=embedding, n_results=n)
        for text, meta, dist in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        ):
            raw.append({
                "text": text,
                "source": meta["source"],
                "page": meta["page"],
                "score": round(1 / (1 + dist), 4),
                "shared": col_user == SHARED_USER,
            })

    # スコア降順にソートして重複テキストを除去し上位 k 件を返す
    seen: set[str] = set()
    hits: list[dict] = []
    for r in sorted(raw, key=lambda x: x["score"], reverse=True):
        if r["text"] not in seen:
            seen.add(r["text"])
            hits.append(r)
        if len(hits) >= k:
            break
    return hits


def has_any_sources(username: str) -> bool:
    """個人または共有コレクションにドキュメントが存在するか確認する。"""
    for col_user in [username, SHARED_USER]:
        if _get_collection(col_user).count() > 0:
            return True
    return False


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
