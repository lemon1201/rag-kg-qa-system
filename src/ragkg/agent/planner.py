from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Plan:
    policy: str
    top_k: int
    use_graph_first: bool


def make_plan(question: str, top_k: int) -> Plan:
    q = question.lower()
    graph_keywords = ["关系", "路径", "关联", "依赖", "from", "to", "graph"]
    use_graph_first = any(k in q for k in graph_keywords)
    policy = "graph_first" if use_graph_first else "text_first"
    return Plan(policy=policy, top_k=top_k, use_graph_first=use_graph_first)
