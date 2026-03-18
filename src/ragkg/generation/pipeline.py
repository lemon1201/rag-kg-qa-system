from typing import Dict, Tuple


def build_context(retrieval_result: Dict) -> str:
    text_parts = [f"[VEC] {x['text']}" for x in retrieval_result.get("text_hits", [])]
    bm25_parts = [f"[BM25] {x['text']}" for x in retrieval_result.get("bm25_hits", [])]
    return "\n".join((text_parts + bm25_parts)[:8])


def generate_answer(question: str, context: str) -> Tuple[str, float]:
    # TODO: 替换为真实 LLM 调用
    if not context.strip():
        return "未检索到足够证据，建议补充问题上下文。", 0.35
    return f"基于检索证据，对问题『{question}』的回答：\n{context[:260]}...", 0.76


def verify_answer(answer: str, confidence: float, threshold: float = 0.65) -> bool:
    return confidence < threshold
