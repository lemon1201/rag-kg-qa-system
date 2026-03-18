from typing import List, Dict


def bm25_retrieve(question: str, top_k: int) -> List[Dict]:
    # TODO: 接入真实 BM25
    return [{"doc_id": "doc-001", "chunk_id": "c-01", "text": "BM25召回片段示例", "score": 0.72}][:top_k]


def vector_retrieve(question: str, top_k: int) -> List[Dict]:
    # TODO: 接入真实向量库（FAISS/HNSW）
    return [{"doc_id": "doc-001", "chunk_id": "c-12", "text": "向量召回片段示例", "score": 0.83}][:top_k]


def graph_retrieve(question: str, top_k: int) -> List[Dict]:
    # TODO: 接入真实 Neo4j 子图检索
    return [{"from_node": "成果A", "rel": "包含", "to": "指标B", "score": 0.66}][:top_k]


def hybrid_retrieve(question: str, top_k: int) -> Dict:
    return {
        "text_hits": vector_retrieve(question, top_k),
        "bm25_hits": bm25_retrieve(question, top_k),
        "graph_hits": graph_retrieve(question, top_k),
    }
