from fastapi import FastAPI
from ragkg.schemas import QARequest, QAResponse, Citation, GraphPath
from ragkg.retrieval.pipeline import hybrid_retrieve
from ragkg.generation.rerank import rerank_hits
from ragkg.generation.pipeline import build_context, generate_answer, extract_citations
from ragkg.generation.verify import verify_with_evidence

app = FastAPI(title="rag-kg-qa-system", version="0.3.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/qa", response_model=QAResponse)
def qa(req: QARequest):
    retrieved = hybrid_retrieve(req.question, req.top_k)

    # M3: 重排
    merged_text_hits = retrieved.get("text_hits", []) + retrieved.get("bm25_hits", [])
    reranked_hits = rerank_hits(req.question, merged_text_hits, top_n=req.top_k)
    retrieved["reranked_hits"] = reranked_hits

    # 生成
    context = build_context(retrieved)
    answer, confidence = generate_answer(req.question, context)

    # 证据抽取与一致性校验
    citation_dicts = extract_citations(reranked_hits, top_n=min(3, req.top_k))
    verify_result = verify_with_evidence(req.question, citation_dicts, confidence)

    citations = [
        Citation(doc_id=x["doc_id"], chunk_id=x["chunk_id"], text=x["text"])
        for x in citation_dicts
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
        evidence_coverage=verify_result["coverage"],
        review_reason=verify_result["reason"],
        needs_human_review=verify_result["needs_human_review"],
    )
