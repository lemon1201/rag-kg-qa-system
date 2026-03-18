from __future__ import annotations

from typing import Dict

from ragkg.agent.planner import Plan
from ragkg.agent.tools import run_retrieval


def route_and_retrieve(question: str, plan: Plan) -> Dict:
    return run_retrieval(question=question, top_k=plan.top_k, graph_first=plan.use_graph_first)
