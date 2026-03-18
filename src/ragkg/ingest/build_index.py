from __future__ import annotations

import json
import math
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict


DATA_DIR = Path("data")
RAW_FILE = DATA_DIR / "raw" / "docs.jsonl"
INDEX_DIR = DATA_DIR / "processed"
INDEX_FILE = INDEX_DIR / "retrieval_index.pkl"


@dataclass
class Chunk:
    doc_id: str
    chunk_id: str
    text: str


class SimpleBM25:
    def __init__(self, tokenized_docs: List[List[str]], k1: float = 1.5, b: float = 0.75):
        self.tokenized_docs = tokenized_docs
        self.k1 = k1
        self.b = b
        self.N = len(tokenized_docs)
        self.avgdl = sum(len(d) for d in tokenized_docs) / max(self.N, 1)

        self.doc_freq: Dict[str, int] = {}
        self.term_freqs: List[Dict[str, int]] = []
        for doc in tokenized_docs:
            tf: Dict[str, int] = {}
            for t in doc:
                tf[t] = tf.get(t, 0) + 1
            self.term_freqs.append(tf)
            for t in set(doc):
                self.doc_freq[t] = self.doc_freq.get(t, 0) + 1

        self.idf: Dict[str, float] = {}
        for t, df in self.doc_freq.items():
            self.idf[t] = math.log(1 + (self.N - df + 0.5) / (df + 0.5))

    @staticmethod
    def tokenize(text: str) -> List[str]:
        return [x.strip().lower() for x in text.replace("\n", " ").split(" ") if x.strip()]

    def score(self, query: str, idx: int) -> float:
        q_tokens = self.tokenize(query)
        doc = self.tokenized_docs[idx]
        tf = self.term_freqs[idx]
        dl = len(doc)
        s = 0.0
        for t in q_tokens:
            if t not in tf:
                continue
            idf = self.idf.get(t, 0.0)
            freq = tf[t]
            denom = freq + self.k1 * (1 - self.b + self.b * dl / max(self.avgdl, 1e-6))
            s += idf * (freq * (self.k1 + 1) / max(denom, 1e-6))
        return s


def _norm(vec: Dict[str, float]) -> float:
    return math.sqrt(sum(v * v for v in vec.values()))


def _tfidf_vector(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
    tf: Dict[str, int] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    total = max(len(tokens), 1)
    out: Dict[str, float] = {}
    for t, c in tf.items():
        out[t] = (c / total) * idf.get(t, 0.0)
    return out


def load_chunks() -> List[Chunk]:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"Missing raw file: {RAW_FILE}")

    chunks: List[Chunk] = []
    with RAW_FILE.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            obj = json.loads(line)
            doc_id = obj.get("doc_id", f"doc-{i:03d}")
            text = obj["text"].strip()
            chunks.append(Chunk(doc_id=doc_id, chunk_id=f"{doc_id}-c1", text=text))
    return chunks


def build_index() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    chunks = load_chunks()
    corpus_tokens = [SimpleBM25.tokenize(c.text) for c in chunks]

    bm25 = SimpleBM25(corpus_tokens)

    idf = bm25.idf
    doc_vectors = [_tfidf_vector(tokens, idf) for tokens in corpus_tokens]
    doc_norms = [_norm(v) for v in doc_vectors]

    payload = {
        "chunks": [c.__dict__ for c in chunks],
        "bm25": {
            "tokenized_docs": corpus_tokens,
            "k1": bm25.k1,
            "b": bm25.b,
        },
        "idf": idf,
        "doc_vectors": doc_vectors,
        "doc_norms": doc_norms,
    }

    with INDEX_FILE.open("wb") as f:
        pickle.dump(payload, f)

    print(f"Index built: {INDEX_FILE} | chunks={len(chunks)}")


if __name__ == "__main__":
    build_index()
