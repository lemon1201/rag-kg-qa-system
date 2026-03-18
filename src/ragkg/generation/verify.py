from __future__ import annotations

from typing import Dict, List


def _tokenize(text: str) -> List[str]:
    text = text.strip().lower()
    if not text:
        return []
    words = [x.strip() for x in text.replace("\n", " ").split(" ") if x.strip()]
    chars = [ch for ch in text if ch.strip() and ch not in {"，", "。", "：", "；", "、", ",", ".", ":", ";", "?", "？", "!", "！"}]
    # 混合词级与字级，兼容中英文
    return list(dict.fromkeys(words + chars))


def evidence_coverage(question: str, citations: List[Dict]) -> float:
    q_tokens = set(_tokenize(question))
    if not q_tokens or not citations:
        return 0.0

    evidence_text = " ".join([c.get("text", "") for c in citations])
    e_tokens = set(_tokenize(evidence_text))
    if not e_tokens:
        return 0.0

    covered = len(q_tokens.intersection(e_tokens))
    return covered / max(len(q_tokens), 1)


def verify_with_evidence(question: str, citations: List[Dict], confidence: float) -> Dict:
    coverage = evidence_coverage(question, citations)

    # 门槛策略：覆盖率过低或者模型置信度过低，都标记为人工复核
    needs_human_review = (coverage < 0.35) or (confidence < 0.65)

    return {
        "coverage": round(coverage, 4),
        "needs_human_review": needs_human_review,
        "reason": "low_evidence_coverage" if coverage < 0.35 else ("low_confidence" if confidence < 0.65 else "ok"),
    }
