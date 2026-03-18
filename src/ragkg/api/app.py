from fastapi import FastAPI
from ragkg.schemas import QARequest, QAResponse, Citation, GraphPath
from ragkg.retrieval.pipeline import hybrid_retrieve
from ragkg.generation.pipeline import build_context, generate_answer, verify_answer

app = FastAPI(title="rag-kg-qa-system", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/qa", response_model=QAResponse)
def qa(req: QARequest):
    retrieved = hybrid_retrieve(req.question, req.top_k)
    context = build_context(retrieved)
    answer, confidence = generate_answer(req.question, context)
    needs_review = verify_answer(answer, confidence)

    citations = [
        Citation(doc_id=x["doc_id"], chunk_id=x["chunk_id"], text=x["text"])
        for x in retrieved.get("text_hits", [])
    ]
    graph_paths = [
        GraphPath(from_node=x["from_node"], rel=x["rel"], to=x["to"])
        for x in retrieved.get("graph_hits", [])
    ]

    return QAResponse(
        answer=answer,
        confidence=confidence,
        citations=citations,
        graph_paths=graph_paths,
        needs_human_review=needs_review,
    )
