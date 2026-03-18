from typing import Dict, Tuple


def build_context(retrieval_result: Dict) -> str:
    text_parts = [x["text"] for x in retrieval_result.get("text_hits", [])]
    bm25_parts = [x["text"] for x in retrieval_result.get("bm25_hits", [])]
    return "\n".join((text_parts + bm25_parts)[:8])


def generate_answer(question: str, context: str) -> Tuple[str, float]:
    # TODO: 接入真实 LLM（本地或API）
    if not context.strip():
        return "未检索到足够证据，建议补充问题上下文。", 0.35
    return f"基于检索证据，问题『{question}』的回答如下：\n{context[:120]}...", 0.78


def verify_answer(answer: str, confidence: float, threshold: float = 0.65) -> bool:
    # True 表示需要人工复核
    return confidence < threshold
