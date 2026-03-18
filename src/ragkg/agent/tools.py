from __future__ import annotations

from typing import Dict, List

from ragkg.retrieval.pipeline import bm25_retrieve, vector_retrieve, graph_retrieve
from ragkg.generation.rerank import rerank_hits
from ragkg.generation.pipeline import extract_citations
from ragkg.generation.verify import verify_with_evidence


def run_retrieval(question: str, top_k: int, graph_first: bool = False) -> Dict:
    vec = vector_retrieve(question, top_k)
    bm25 = bm25_retrieve(question, top_k)
    graph = graph_retrieve(question, top_k)

    merged = (bm25 + vec) if graph_first else (vec + bm25)
    reranked = rerank_hits(question, merged, top_n=top_k)

    return {
        "text_hits": vec,
        "bm25_hits": bm25,
        "graph_hits": graph,
        "reranked_hits": reranked,
    }


def run_verify(question: str, reranked_hits: List[Dict], confidence: float) -> Dict:
    citations = extract_citations(reranked_hits, top_n=3)
    result = verify_with_evidence(question, citations, confidence)
    return {"citations": citations, **result}
