# rag-kg-qa-system

可追溯问答系统（RAG + Knowledge Graph）重构版（Project 1）。

## 目标
- 输入问题后输出：**答案 + 证据片段 + 图谱路径 + 元数据**
- 支持多路召回：BM25 + 向量检索 + 图谱检索
- 支持重排、证据一致性检查与“不确定”兜底

## 当前里程碑
- [x] M1：项目骨架 + 可运行 API demo
- [x] M2：可运行检索闭环（BM25 + TF-IDF向量 + 图谱检索）
- [x] M3：重排与证据一致性校验（规则版，可运行）
- [ ] M4：Neo4j / 向量库生产化接入 + LLM真实生成

## 目录结构
```
src/ragkg/
  ingest/       # 文档解析、切分、抽取
  retrieval/    # BM25/向量/图谱召回
  generation/   # 上下文拼接、生成、校验
  graph/        # Neo4j 适配层
  api/          # FastAPI
configs/        # 配置文件
scripts/        # 启动与本地脚本
tests/          # 单测
```

## 快速开始
> 建议 Python 3.11 / 3.12（当前部分依赖对 3.14 支持不完整）

```bash
python -m venv .venv
. .venv/Scripts/activate   # Windows
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File scripts/prepare_sample_data.ps1
python src/ragkg/ingest/build_index.py
python -m uvicorn ragkg.api.app:app --reload --app-dir src
```

接口：
- `GET /health`
- `POST /qa`

## 示例请求
```json
{
  "question": "某成果评价里的关键测试指标有哪些？",
  "top_k": 5
}
```

## 返回结构
```json
{
  "answer": "...",
  "confidence": 0.78,
  "citations": [{"doc_id":"doc-001","chunk_id":"c-12","text":"..."}],
  "graph_paths": [{"from_node":"成果A","rel":"包含","to":"指标B"}],
  "evidence_coverage": 0.67,
  "review_reason": "ok",
  "needs_human_review": false
}
```

## 备注
本仓库先追求结构正确与可演进。每个模块会按“可运行最小版本 -> 指标提升版本”逐步补齐。
