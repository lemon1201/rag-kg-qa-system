from __future__ import annotations

import math
import pickle
from pathlib import Path
from typing import List, Dict

from ragkg.graph.store import search_graph
from ragkg.ingest.build_index import SimpleBM25

INDEX_FILE = Path("data") / "processed" / "retrieval_index.pkl"


def _load_index() -> Dict:
    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            f"Index not found: {INDEX_FILE}. Run `python src/ragkg/ingest/build_index.py` first."
        )
    with INDEX_FILE.open("rb") as f:
        return pickle.load(f)


def _tfidf_vector(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
    tf: Dict[str, int] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    total = max(len(tokens), 1)
    return {t: (c / total) * idf.get(t, 0.0) for t, c in tf.items()}


def _norm(vec: Dict[str, float]) -> float:
    return math.sqrt(sum(v * v for v in vec.values()))


def _cosine(a: Dict[str, float], b: Dict[str, float], b_norm: float) -> float:
    if b_norm <= 0:
        return 0.0
    a_norm = _norm(a)
    if a_norm <= 0:
        return 0.0
    dot = 0.0
    for k, v in a.items():
        dot += v * b.get(k, 0.0)
    return dot / (a_norm * b_norm)


def bm25_retrieve(question: str, top_k: int) -> List[Dict]:
    idx = _load_index()
    bm25 = idx["bm25"]
    chunks = idx["chunks"]

    scored = []
    for i, c in enumerate(chunks):
        s = bm25.score(question, i)
        if s > 0:
            scored.append({**c, "score": float(s), "source": "bm25"})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def vector_retrieve(question: str, top_k: int) -> List[Dict]:
    idx = _load_index()
    idf = idx["idf"]
    doc_vectors = idx["doc_vectors"]
    doc_norms = idx["doc_norms"]
    chunks = idx["chunks"]

    q_tokens = SimpleBM25.tokenize(question)
    q_vec = _tfidf_vector(q_tokens, idf)

    scored = []
    for i, dvec in enumerate(doc_vectors):
        s = _cosine(q_vec, dvec, doc_norms[i])
        scored.append({**chunks[i], "score": float(s), "source": "vector"})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def graph_retrieve(question: str, top_k: int) -> List[Dict]:
    return search_graph(question, top_k)


def hybrid_retrieve(question: str, top_k: int) -> Dict:
    return {
        "text_hits": vector_retrieve(question, top_k),
        "bm25_hits": bm25_retrieve(question, top_k),
        "graph_hits": graph_retrieve(question, top_k),
    }
