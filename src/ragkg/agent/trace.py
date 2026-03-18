from __future__ import annotations

from typing import Dict, List


def step(name: str, payload: Dict) -> Dict:
    return {"step": name, "payload": payload}


def summarize_hits(retrieved: Dict) -> Dict:
    return {
        "vector_hits": len(retrieved.get("text_hits", [])),
        "bm25_hits": len(retrieved.get("bm25_hits", [])),
        "graph_hits": len(retrieved.get("graph_hits", [])),
        "reranked_hits": len(retrieved.get("reranked_hits", [])),
    }


def init_trace() -> List[Dict]:
    return []
