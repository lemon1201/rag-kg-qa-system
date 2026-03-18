# M4-Agent 升级计划（基于 rag-kg-qa-system）

> 目标：将当前“RAG+图谱问答流水线”升级为“可规划、可调用工具、可自检、可重试、可记忆”的 Agent 系统。

## 0. 当前基线（已完成）
- M1：项目骨架 + API
- M2：BM25 + 向量 + 图谱检索闭环
- M3：重排 + 证据一致性校验（规则版）

---

## 1. M4 总体目标
实现一个 **Plan → Act → Check → Final** 的 Agent 主流程，满足：
1. 能按问题类型选择工具路径
2. 证据不足时自动重试
3. 有短期记忆（会话态）
4. 返回可解释执行轨迹（trace）

---

## 2. 模块增量清单（必须新增）

### 2.1 Orchestrator（编排器）
**新增文件**
- `src/ragkg/agent/orchestrator.py`

**职责**
- 统一执行 Plan → Act → Check → Final
- 管理状态：步骤、尝试次数、失败原因

---

### 2.2 Planner（任务规划）
**新增文件**
- `src/ragkg/agent/planner.py`

**职责**
- 依据问题类型选择执行策略：
  - 定义/说明类：向量+BM25优先
  - 关系推理类：图谱优先
  - 证据不足：触发 query rewrite + 扩大 top_k

---

### 2.3 Tool Registry（工具注册）
**新增文件**
- `src/ragkg/agent/tools.py`

**职责**
- 标准化工具调用接口（统一 I/O schema）
- 封装现有模块：
  - bm25_retrieve
  - vector_retrieve
  - graph_retrieve
  - rerank_hits
  - verify_with_evidence

---

### 2.4 Router（工具路由）
**新增文件**
- `src/ragkg/agent/router.py`

**职责**
- 根据 Planner 策略决定调用顺序
- 先做规则路由，后续可升级模型路由

---

### 2.5 Critic / Verifier（自检器）
**增量文件**
- `src/ragkg/generation/verify.py`（增强）

**增强点**
- 覆盖率（已有）
- 引用一致性（结论-证据关键字一致性）
- 冲突检测（多证据相互矛盾时标记）

---

### 2.6 Retry / Reflection（重试与反思）
**新增文件**
- `src/ragkg/agent/retry.py`

**规则建议**
- `confidence < 0.65`：top_k +2
- `coverage < 0.35`：query rewrite 后重检索
- 最多重试 2~3 次，超出返回人工复核

---

### 2.7 Memory（记忆）
**新增文件**
- `src/ragkg/agent/memory.py`

**最小实现**
- short-term memory：当前会话最近 N 轮
- long-term memory（可选）：高质量Q&A缓存

---

### 2.8 Observability（可观测）
**新增文件**
- `src/ragkg/agent/trace.py`

**输出内容**
- 每一步调用工具
- 每一步输入/输出摘要
- 分数变化（rerank、coverage、confidence）
- 最终决策原因（ok / low_confidence / low_evidence_coverage）

---

## 3. API 升级方案

### 3.1 新增 Agent API
- `POST /agent/qa`

### 3.2 响应字段新增
- `trace`: 执行轨迹数组
- `attempts`: 尝试次数
- `policy`: 命中策略名（例如 graph_first）

---

## 4. 评测与验收

### 4.1 评测集
**新增目录**
- `eval/qa_set.jsonl`（30~100条）

### 4.2 指标
- answer_accept_rate
- citation_precision
- evidence_coverage_avg
- retry_rate
- human_review_rate

### 4.3 验收标准（M4 Done）
- 能稳定跑通 Agent 主流程
- 低证据问题能自动重试
- API 返回 trace 且可解释
- 相比 M3，coverage 与可用性有可见提升

---

## 5. 实施顺序（建议）
1. 新建 `agent/` 包：orchestrator、planner、tools、router
2. 接入 retry 与 trace
3. API 增加 `/agent/qa`
4. 增强 verify（一致性/冲突）
5. 增加 eval 脚本与样例集

---

## 6. 工作量预估
- P0（主流程跑通）：0.5~1 天
- P1（重试+trace+API）：1 天
- P2（评测+文档+优化）：1 天

总计约：2~3 天可形成可演示版本。

---

## 7. 当前决策记录
- 当前采用规则驱动 Agent（先保证稳定与可解释）
- 真实 LLM Planner / Router 放入后续 M5
- 生产化 Neo4j 与向量库接入继续在 M4 后半段推进
