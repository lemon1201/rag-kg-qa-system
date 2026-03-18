from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetryDecision:
    should_retry: bool
    next_top_k: int
    rewritten_question: str
    reason: str


def rewrite_question(question: str) -> str:
    # 规则版重写：扩展检索提示词
    return f"{question} 关键指标 证据 引用"


def make_retry_decision(question: str, top_k: int, coverage: float, confidence: float, attempt: int, max_attempts: int) -> RetryDecision:
    if attempt >= max_attempts:
        return RetryDecision(False, top_k, question, "max_attempts_reached")

    if coverage < 0.35:
        return RetryDecision(True, min(top_k + 2, 12), rewrite_question(question), "low_evidence_coverage")

    if confidence < 0.65:
        return RetryDecision(True, min(top_k + 1, 12), question, "low_confidence")

    return RetryDecision(False, top_k, question, "ok")
