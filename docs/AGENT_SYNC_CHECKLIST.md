# Agent Branch Sync Checklist

当 `offerpilot-skill` 分支的 skill-pack 文档发生变更时，检查 `offerpilot-agent` 分支的 `offerpilot/graph.py` SYSTEM_PROMPT 是否需要同步更新。

## 需要检查的规则项

| Skill 分支来源 | Agent SYSTEM_PROMPT 对应段落 | 检查频率 |
|---|---|---|
| WORKFLOW.md Section 2 — Minimal Read Graph | 任务路由与上下文加载策略 | 每次变更 |
| WORKFLOW.md Section 5 — section 顺序 | 简历格式规则 — section 顺序 | 每次变更 |
| WORKFLOW.md Section 7 — 输出目录规则 | 输出目录规则 | 每次变更 |
| OUTPUTS.md — 一页纸篇幅预算 (14-18 bullets) | ❌ 未同步 | 需手动添加 |
| OUTPUTS.md — 文件命名规则 | 简历格式规则 — 文件命名 | 每次变更 |
| OUTPUTS.md — PDF style 默认 | 简历格式规则 — PDF style | 每次变更 |
| OUTPUTS.md — 教育行格式 | 简历格式规则 — 教育行格式 | 每次变更 |
| OUTPUTS.md — 技能列表格式 | 简历格式规则 — 技能格式 | 每次变更 |
| OUTPUTS.md — 年龄显示 | 简历格式规则 — 联系信息行 | 每次变更 |
| PROMPTS.md — Golden Bullet Formula & 黑名单 | ❌ 未同步 | 需手动添加 |
| EVALUATION.md — 10 维评分权重与自适应归一化 | 结构化评估维度 | 每次变更 |
| JD_MATCHING.md — experience+1 规则 | ❌ 未同步 | 需手动添加 |
| DATASTORE.md — variants 选择逻辑 | ❌ 未同步 | 需手动添加 |
| DATASTORE.md — impact priority | ❌ 未同步 | 需手动添加 |
| PROFILE_BUILDER.md — 素材库构建与追问深挖 | ❌ 未同步 | 新增文档 |
| OFFER_EVALUATION.md — 总包拆解与谈薪话术 | ❌ 未同步 | 新增文档 |
| OUTREACH.md — 多渠道外联 (Boss直聘/内推/LinkedIn) | ❌ 未同步 | 规则扩充 |
| MOCK_INTERVIEW.md — Phase 3 面经复盘 & Phase 4 行为面 | ❌ 未同步 | 规则扩充 |
| PRODUCT_RESEARCH.md — 6 步流程 | 任务类型列表 | 新增任务时检查 |
| RESUME_DIAGNOSIS.md | ❌ 未同步 | 新增文档 |
| WORKFLOW.md Section 6b — 迭代修改 | ❌ 未同步 | 新增规则 |

## 变更类型与同步动作

| 变更类型 | 同步动作 |
|---|---|
| 新增 task 文档 | SYSTEM_PROMPT 任务类型列表 +1（如 PROFILE_BUILDER.md、OFFER_EVALUATION.md） |
| 修改评分维度/权重 | 更新 SYSTEM_PROMPT 中对应的维度表 |
| 修改格式规则 | 更新 SYSTEM_PROMPT 中对应的格式规则 |
| 修改输出目录 | 更新 SYSTEM_PROMPT 中对应的目录映射 |
| 新增 Error Recovery | 通常不影响 SYSTEM_PROMPT，无需同步 |
| 修改 PROMPTS.md 行为约束 | 检查 SYSTEM_PROMPT「工作规则」段落 |

## 当前未同步项

1. **experience+1 规则** — `JD_MATCHING.md` 定义了 `actual experience + 1 year` 匹配规则，但 agent `SYSTEM_PROMPT` 未提及
2. **variants 选择逻辑** — `DATASTORE.md` 定义了 variant 按角色类型选择的规则，agent 不知道
3. **impact priority & 单页预算** — `DATASTORE.md` 与 `OUTPUTS.md` 定义了 `quantified > qualitative > context-only` 优先级及 14–18 条 bullets 单页预算
4. **product research 流程** — agent `SYSTEM_PROMPT` 仅列出任务名，未描述 6 步执行流程
5. **迭代修改规则** — `WORKFLOW.md` Section 6b 新增，agent 不知道
6. **新增与扩展任务文档** — `RESUME_DIAGNOSIS.md`、`PROFILE_BUILDER.md`、`OFFER_EVALUATION.md`、`OUTREACH.md`（多渠道打招呼/内推）、`MOCK_INTERVIEW.md`（Phase 3 真实面经复盘与 Phase 4 行为面 STAR 故事卡）
