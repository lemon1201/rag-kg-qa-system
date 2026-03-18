# rag-kg-qa-system

可追溯问答系统（RAG + Knowledge Graph）重构版（Project 1）。

## 目标
- 输入问题后输出：**答案 + 证据片段 + 图谱路径 + 元数据**
- 支持多路召回：BM25 + 向量检索 + 图谱检索
- 支持重排、证据一致性检查与“不确定”兜底

## 当前里程碑（M1）
- [x] 项目骨架
- [x] 配置与数据结构定义
- [x] 可运行 API demo（stub）
- [ ] 文档解析与抽取流水线
- [ ] FAISS/BM25/Neo4j 接入
- [ ] 重排与验证模块

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
```bash
python -m venv .venv
. .venv/Scripts/activate   # Windows
pip install -r requirements.txt
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
  "graph_paths": [{"from":"成果A","rel":"包含","to":"指标B"}],
  "needs_human_review": false
}
```

## 备注
本仓库先追求结构正确与可演进。每个模块会按“可运行最小版本 -> 指标提升版本”逐步补齐。
