from __future__ import annotations

from typing import Dict, List


def _tokenize(text: str) -> List[str]:
    text = text.strip().lower()
    if not text:
        return []
    words = [x.strip() for x in text.replace("\n", " ").split(" ") if x.strip()]
    chars = [ch for ch in text if ch.strip() and ch not in {"，", "。", "：", "；", "、", ",", ".", ":", ";", "?", "？", "!", "！"}]
    return list(dict.fromkeys(words + chars))


def lexical_overlap_score(question: str, text: str) -> float:
    q = set(_tokenize(question))
    t = set(_tokenize(text))
    if not q or not t:
        return 0.0
    inter = len(q.intersection(t))
    return inter / max(len(q), 1)


def rerank_hits(question: str, hits: List[Dict], top_n: int = 5) -> List[Dict]:
    scored = []
    for h in hits:
        base = float(h.get("score", 0.0))
        overlap = lexical_overlap_score(question, h.get("text", ""))
        final_score = 0.6 * base + 0.4 * overlap
        scored.append({**h, "rerank_score": final_score})

    scored.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored[:top_n]
