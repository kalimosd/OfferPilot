# Agent Branch Sync Checklist

当 `offerpilot-skill` 分支的 skill-pack 文档发生变更时，检查 `offerpilot-agent` 分支的 `offerpilot/graph.py` SYSTEM_PROMPT 与 `offerpilot/tools.py` 是否需要同步更新。

## 规则同步状态表

| Skill 分支来源 | Agent SYSTEM_PROMPT / Tools 对应段落 | 状态 |
|---|---|---|
| WORKFLOW.md Section 2 — Minimal Read Graph | 任务路由与上下文加载策略 | ✅ 已同步 |
| WORKFLOW.md Section 5 — section 顺序 | 简历格式规则 — section 顺序 | ✅ 已同步 |
| WORKFLOW.md Section 7 — 输出目录规则 | 输出目录规则 | ✅ 已同步 |
| OUTPUTS.md — 一页纸篇幅预算 (14-18 bullets) | 工作规则 — 一页纸篇幅预算 + `tools.render_pdf` 页数告警 | ✅ 已同步 |
| OUTPUTS.md — 文件命名规则 | 简历格式规则 — 文件命名 | ✅ 已同步 |
| OUTPUTS.md — PDF style 默认 | 简历格式规则 — PDF style | ✅ 已同步 |
| OUTPUTS.md — 教育行格式 | 简历格式规则 — 教育行格式 | ✅ 已同步 |
| OUTPUTS.md — 技能列表格式 | 简历格式规则 — 技能格式 | ✅ 已同步 |
| OUTPUTS.md — 年龄显示 | 简历格式规则 — 联系信息行 | ✅ 已同步 |
| PROMPTS.md — Golden Bullet Formula & 黑名单 | 工作规则 — Bullet 写作规范 | ✅ 已同步 |
| EVALUATION.md — 10 维评分权重与自适应归一化 | 结构化评估维度 | ✅ 已同步 |
| JD_MATCHING.md — experience+1 规则 | 工作规则 — JD 工作年限匹配 | ✅ 已同步 |
| DATASTORE.md — variants 选择逻辑 | 工作规则 — variants 选择 | ✅ 已同步 |
| DATASTORE.md — impact priority | 工作规则 — impact 优先级 | ✅ 已同步 |
| PROFILE_BUILDER.md — 素材库构建与追问深挖 | 任务类型 #16 `profile-build` | ✅ 已同步 |
| OFFER_EVALUATION.md — 总包拆解与谈薪话术 | 任务类型 #17 `offer-eval` | ✅ 已同步 |
| OUTREACH.md — 多渠道外联 (Boss直聘/内推/LinkedIn) | 任务类型 #10 `outreach` | ✅ 已同步 |
| MOCK_INTERVIEW.md — Phase 3 面经复盘 & Phase 4 行为面 | 任务类型 #13 `mock-interview` | ✅ 已同步 |
| PRODUCT_RESEARCH.md — 6 步流程 | 任务类型 #14 `product-research` | ✅ 已同步 |
| RESUME_DIAGNOSIS.md | 任务类型 #15 `resume-diagnosis` | ✅ 已同步 |
| WORKFLOW.md Section 6b — 迭代修改 | 工作规则 — 局部修改与版本号递增 | ✅ 已同步 |
| TRACKER.md — `offer_evaluating` / `accepted` / `declined` | `tools.py` `VALID_STATUSES` & `check_followups` | ✅ 已同步 |

## 变更类型与同步动作

| 变更类型 | 同步动作 |
|---|---|
| 新增 task 文档 | `SYSTEM_PROMPT` 任务类型列表 +1（如 `PROFILE_BUILDER.md`、`OFFER_EVALUATION.md`） |
| 修改评分维度/权重 | 更新 `SYSTEM_PROMPT` 中对应的维度表 |
| 修改格式规则 | 更新 `SYSTEM_PROMPT` 中对应的格式规则 |
| 修改输出目录 | 更新 `SYSTEM_PROMPT` 中对应的目录映射 |
| 新增 Error Recovery | 通常不影响 `SYSTEM_PROMPT`，除非涉及权重归一化等计分规则 |
| 修改 PROMPTS.md 行为约束 | 检查 `SYSTEM_PROMPT`「工作规则」段落 |

## 当前未同步项

暂无未同步项（`offerpilot-skill` 与 `offerpilot-agent` 已完全对齐）。
