from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict

GRAPH_FILE = Path("data") / "raw" / "graph_edges.json"


def load_edges() -> List[Dict]:
    if not GRAPH_FILE.exists():
        return []
    return json.loads(GRAPH_FILE.read_text(encoding="utf-8"))


def search_graph(question: str, top_k: int = 5) -> List[Dict]:
    edges = load_edges()
    if not edges:
        return []

    q = question.lower()
    scored = []
    for e in edges:
        text = f"{e.get('from','')} {e.get('rel','')} {e.get('to','')}"
        score = sum(1 for tok in q.split() if tok in text.lower())
        if score > 0:
            scored.append({**e, "score": float(score)})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
