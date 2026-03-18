from pydantic import BaseModel, Field
from typing import List


class Citation(BaseModel):
    doc_id: str
    chunk_id: str
    text: str


class GraphPath(BaseModel):
    from_node: str
    rel: str
    to: str


class QARequest(BaseModel):
    question: str
    top_k: int = 5


class QAResponse(BaseModel):
    answer: str
    confidence: float
    citations: List[Citation]
    graph_paths: List[GraphPath]
    needs_human_review: bool
