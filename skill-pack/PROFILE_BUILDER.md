# Profile Builder

Use this workflow for building or updating a candidate's `profile_store.yaml` datastore.

## Purpose

The profile datastore is the single source of truth for all candidate materials. Many users start with an existing unstructured resume (`.pdf`, `.docx`, or `.md`) or want to enrich their datastore with newly completed projects and post-interview debriefs.

This workflow covers:
1. **Cold-start extraction**: Converting an existing resume into a structured, validated `profile_store.yaml`
2. **Elaboration & deep-dive**: Proactively asking targeted questions to transform weak, vague bullets into high-impact, quantified bullets
3. **Continuous ingestion**: Adding new projects or interview learnings back into the datastore

## Inputs

Required (at least one):
- original resume source (`.md`, `.txt`, `.pdf`, or `.docx`) for cold-start extraction
- existing `profile_store.yaml` + new project notes or interview debrief for incremental update

---

## 1. Cold-Start Extraction Flow

### Step 1: Read and Parse Original Resume
- If the source is `.pdf` or `.docx`, run `python3 skill-pack/scripts/extract_text.py "path/to/file"` first.
- Parse candidate identity (`meta`), work experience (`experience`), project history (`projects`), skills (`skills`), education (`education`), and certifications/awards (`certifications`, `achievements`).
- Preserve real contact details (`name`, `email`, `phone`, `birth_year`) present in the source; never invent missing fields.

### Step 2: Canonical Tagging & Impact Labeling
- For every bullet extracted:
  - Normalize technical and domain terms using `skill-pack/data/skill_aliases.zh-en.json` (lowercase, spaces instead of hyphens).
  - Assign 2–5 canonical tags (e.g. `[android, performance, perfetto]`).
  - Classify `impact`:
    - `quantified`: Contains measurable percentages, latency/memory reductions, scale, or business metrics.
    - `qualitative`: Demonstrates clear technical difficulty, architectural decisions, or stakeholder outcomes without hard numbers.
    - `context-only`: Pure responsibility or tool usage description without explicit outcome.

### Step 3: Write and Validate `profile_store.yaml`
- Follow the structure and schema in `skill-pack/DATASTORE.md` and `skill-pack/schemas/profile_store.schema.json`.
- Run `python3 skill-pack/scripts/validate_profile_store.py profile_store.yaml` to guarantee schema and canonical tag compliance.

---

## 2. Elaboration Prompting (Deep-Dive on Weak Bullets)

When extracting from an existing resume, many bullets are brief or purely `context-only` (e.g. "负责线上稳定性治理" or "参与大模型应用开发").

Identify the **top 3–5 high-potential but under-described bullets** and ask the candidate 1–2 targeted questions per item before finalizing:

### Question Patterns by Domain

- **Performance & Reliability (性能与稳定性)**:
  - *Weak*: "参与桌面稳定性治理与卡顿排查"
  - *Follow-up*: "排查卡顿和 ANR 时主要使用了哪些工具（如 Perfetto/Systrace/Hprof）？定位出的核心瓶颈是 Binder 调用阻塞、主线程耗时还是内存泄漏？修复后线上崩溃/ANR 率或帧率有无对比数据？"
- **AI Agent & LLM Engineering (AI 应用与自动化工作流)**:
  - *Weak*: "搭建 AI agent 分析 Bug"
  - *Follow-up*: "工作流串联了哪些组件（如 Jira + Playwright + 飞书机器人）？自动分类或日志分析覆盖了哪些场景？单次排查耗时从过去的多少分钟缩短到了多少分钟？"
- **Data & Business Growth (数据分析与业务增长)**:
  - *Weak*: "完成 BI 看板搭建并进行数据分析"
  - *Follow-up*: "分析支撑了哪项具体业务策略（如销售转化或留存分层）？策略落地后核心指标（GMV、留存率、使用时长）提升了多少？"
- **Architecture & System Design (系统设计与模块重构)**:
  - *Weak*: "参与 Dock 栏状态机开发"
  - *Follow-up*: "当时的状态机设计解决了什么痛点（如多任务场景下的状态冲突或扩展性不足）？重构后对后续新需求的交付效率有何改善？"

### Updating the Datastore
- Once the candidate answers, upgrade the bullet into a `quantified` or strong `qualitative` entry using ONLY the candidate's confirmed facts.
- If the same achievement can be framed from multiple angles (e.g. technical depth vs cross-team leadership), store a primary `text` and add `variants: { technical: "...", leadership: "..." }`.

---

## 3. Post-Interview / Post-Project Ingestion

When a candidate finishes an interview debrief or completes a new project milestone:
1. Extract newly articulated technical details, edge-case solutions, and verified metrics.
2. Check whether a matching entry already exists in `experience` or `projects`:
   - If yes: append or refine the bullet points and update `meta.updated`.
   - If no: create a new entry with `category`, `context`, `bullets`, and `tags`.
3. Re-run `python3 skill-pack/scripts/validate_profile_store.py profile_store.yaml` to verify all tags and fields pass validation.

---

## Error Recovery

- **原始简历无法提取文本**：提示用户检查文件是否加密或为纯图片扫描件，建议提供 `.md` 或 `.txt` 文本。
- **用户暂时记不清具体量化数字**：保留为 `qualitative` 级别，描述清楚技术手段与解决的具体问题，切勿编造或估算虚假百分比。
- **新标签不在 `skill_aliases.zh-en.json` 中**：优先映射至最接近的 canonical key；若确属全新高频领域词，可同步更新 `skill-pack/data/skill_aliases.zh-en.json` 并运行 `validate_aliases.py`。

## Task Checklist

- [ ] source resume or new experience notes parsed accurately
- [ ] no fabricated metrics, companies, or credentials introduced
- [ ] every bullet has lowercase canonical tags aligned with `skill_aliases.zh-en.json`
- [ ] `impact` field (`quantified` / `qualitative` / `context-only`) assigned accurately
- [ ] targeted follow-up questions asked for high-value `context-only` bullets
- [ ] `validate_profile_store.py` executed and passed with zero errors
