# Agent Branch Sync Checklist

当 `offerpilot-skill` 分支的 skill-pack 文档发生变更时，检查 `offerpilot-agent` 分支的 `offerpilot/graph.py` SYSTEM_PROMPT 是否需要同步更新。

## 需要检查的规则项

| Skill 分支来源 | Agent SYSTEM_PROMPT 对应段落 | 检查频率 |
|---|---|---|
| WORKFLOW.md Section 4 — section 顺序 | 简历格式规则 — section 顺序 | 每次变更 |
| WORKFLOW.md Section 6 — 输出目录规则 | 输出目录规则 | 每次变更 |
| OUTPUTS.md — 文件命名规则 | 简历格式规则 — 文件命名 | 每次变更 |
| OUTPUTS.md — PDF style 默认 | 简历格式规则 — PDF style | 每次变更 |
| OUTPUTS.md — 教育行格式 | 简历格式规则 — 教育行格式 | 每次变更 |
| OUTPUTS.md — 技能列表格式 | 简历格式规则 — 技能格式 | 每次变更 |
| OUTPUTS.md — 年龄显示 | 简历格式规则 — 联系信息行 | 每次变更 |
| EVALUATION.md — 10 维评分权重 | 结构化评估维度 | 每次变更 |
| JD_MATCHING.md — experience+1 规则 | ❌ 未同步 | 需手动添加 |
| DATASTORE.md — variants 选择逻辑 | ❌ 未同步 | 需手动添加 |
| DATASTORE.md — impact priority | ❌ 未同步 | 需手动添加 |
| PRODUCT_RESEARCH.md — 6 步流程 | 任务类型列表 | 新增任务时检查 |
| RESUME_DIAGNOSIS.md | ❌ 未同步 | 新增文档 |
| WORKFLOW.md Section 5b — 迭代修改 | ❌ 未同步 | 新增规则 |

## 变更类型与同步动作

| 变更类型 | 同步动作 |
|---|---|
| 新增 task 文档 | SYSTEM_PROMPT 任务类型列表 +1（如 RESUME_DIAGNOSIS.md） |
| 修改评分维度/权重 | 更新 SYSTEM_PROMPT 中对应的维度表 |
| 修改格式规则 | 更新 SYSTEM_PROMPT 中对应的格式规则 |
| 修改输出目录 | 更新 SYSTEM_PROMPT 中对应的目录映射 |
| 新增 Error Recovery | 通常不影响 SYSTEM_PROMPT，无需同步 |
| 修改 PROMPTS.md 行为约束 | 检查 SYSTEM_PROMPT「工作规则」段落 |

## 当前未同步项（2026-06-07）

1. **experience+1 规则** — JD_MATCHING.md 定义了 `actual experience + 1 year` 匹配规则，但 agent SYSTEM_PROMPT 未提及
2. **variants 选择逻辑** — DATASTORE.md 定义了 variant 按角色类型选择的规则，agent 不知道
3. **impact priority** — DATASTORE.md 定义了 `quantified > qualitative > context-only` 优先级，agent 不知道
4. **product research 流程** — agent SYSTEM_PROMPT 仅列出任务名，未描述 6 步执行流程
5. **迭代修改规则** — WORKFLOW.md Section 5b 新增，agent 不知道
6. **RESUME_DIAGNOSIS.md** — 新文档，agent task 列表未包含
