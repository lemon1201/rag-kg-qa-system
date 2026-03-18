from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ragkg.agent.planner import make_plan
from ragkg.agent.router import route_and_retrieve
from ragkg.agent.tools import run_verify
from ragkg.agent.retry import make_retry_decision
from ragkg.agent.trace import init_trace, step, summarize_hits
from ragkg.generation.pipeline import build_context, generate_answer


@dataclass
class AgentResult:
    answer: str
    confidence: float
    citations: List[Dict]
    graph_paths: List[Dict]
    evidence_coverage: float
    review_reason: str
    needs_human_review: bool
    attempts: int
    policy: str
    trace: List[Dict]


def run_agent_qa(question: str, top_k: int = 5, max_attempts: int = 3) -> AgentResult:
    trace = init_trace()
    attempt = 1
    current_question = question
    current_top_k = top_k

    final = {
        "answer": "",
        "confidence": 0.0,
        "citations": [],
        "graph_paths": [],
        "evidence_coverage": 0.0,
        "review_reason": "unknown",
        "needs_human_review": True,
        "policy": "text_first",
    }

    while True:
        plan = make_plan(current_question, current_top_k)
        trace.append(step("plan", {"attempt": attempt, "policy": plan.policy, "top_k": plan.top_k}))

        retrieved = route_and_retrieve(current_question, plan)
        trace.append(step("retrieve", summarize_hits(retrieved)))

        context = build_context(retrieved)
        answer, confidence = generate_answer(current_question, context)
        trace.append(step("generate", {"confidence": confidence, "context_len": len(context)}))

        verify = run_verify(current_question, retrieved.get("reranked_hits", []), confidence)
        trace.append(step("verify", {"coverage": verify["coverage"], "reason": verify["reason"]}))

        final.update(
            {
                "answer": answer,
                "confidence": confidence,
                "citations": verify["citations"],
                "graph_paths": retrieved.get("graph_hits", []),
                "evidence_coverage": verify["coverage"],
                "review_reason": verify["reason"],
                "needs_human_review": verify["needs_human_review"],
                "policy": plan.policy,
            }
        )

        decision = make_retry_decision(
            question=current_question,
            top_k=current_top_k,
            coverage=verify["coverage"],
            confidence=confidence,
            attempt=attempt,
            max_attempts=max_attempts,
        )
        trace.append(step("retry_decision", {"retry": decision.should_retry, "reason": decision.reason, "next_top_k": decision.next_top_k}))

        if not decision.should_retry:
            break

        current_question = decision.rewritten_question
        current_top_k = decision.next_top_k
        attempt += 1

    return AgentResult(
        answer=final["answer"],
        confidence=final["confidence"],
        citations=final["citations"],
        graph_paths=final["graph_paths"],
        evidence_coverage=final["evidence_coverage"],
        review_reason=final["review_reason"],
        needs_human_review=final["needs_human_review"],
        attempts=attempt,
        policy=final["policy"],
        trace=trace,
    )
