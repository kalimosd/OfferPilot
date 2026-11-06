# Prompts

Use these prompt rules regardless of the AI platform.

## Shared Constraints

- preserve the candidate's real experience and intent
- preserve real contact details from the source resume in the final deliverable unless the user explicitly requests anonymization
- do not invent fake jobs, fake metrics, or fake credentials
- do not guess, infer, or fabricate missing names, phone numbers, or email addresses
- improve clarity, structure, and credibility
- keep outputs concise and usable for applications
- avoid commentary such as `Improved Version`
- do not replace real names, phone numbers, or email addresses with placeholders like `<name>` or `<email>` in local output files unless the user explicitly asks for redaction

## Golden Bullet Formula (Bullet 黄金公式)

Structure every rewritten resume bullet around:

`[强动词 + 业务场景/技术方案 + 解决的具体问题/核心动作 + 量化结果或明确工程收益]`

## Few-Shot Bullet Rewriting Examples (Before vs. After)

Use these concrete examples as the benchmark for high-density, truthful bullet rewriting:

### Example 1: Performance & Reliability (Android / Systems)
- ❌ **Before (Weak / Vague)**: "参与桌面稳定性治理与卡顿排查，负责修复部分 ANR 和内存泄漏问题。"
- ✅ **After (High Signal)**: "拆解桌面端渲染链路卡顿问题，使用 Perfetto/Systrace 定位跨进程阻塞与 Hprof Context 内存泄漏，协同 SurfaceFlinger、BSP 团队推动跨模块修复闭环。"

### Example 2: AI Agent & Workflow Automation (AI Engineering)
- ❌ **Before (Weak / Vague)**: "利用 AI 大模型搭建了自动化分析 Bug 的工具，赋能团队极大地提高了排查效率。"
- ✅ **After (High Signal)**: "设计并落地基于 Jira + Playwright MCP 的 Bug 智能分析工作流，对接飞书机器人实现一键触发日志拉取、分类与 trace 解析回传，将平均单子排查耗时从 25 分钟缩短至 4–5 分钟。"

### Example 3: Data Analysis & Business Growth (Data Science)
- ❌ **Before (Weak / Vague)**: "负责搭建 BI 看板，并使用 Python 做用户数据分析，促进了销售额增长。"
- ✅ **After (High Signal)**: "协同业务与数仓梳理埋点并搭建 BI 看板，基于 LightGBM 构建用户成交率分类模型辅助销售策略迭代，推动企微月销售额从 680 万增长至 1060 万（较业务初期增长 76%）。"

### Example 4: Module Ownership & Cross-Team Delivery (Project Management)
- ❌ **Before (Weak / Vague)**: "负责最近任务模块开发，积极与产品、设计、测试团队沟通，保证按时上线。"
- ✅ **After (High Signal)**: "担任最近任务模块 Owner，主导平板多任务办公化场景的需求拆解、接口边界划分与风险管控，协同产品、设计与多窗口团队推进问题闭环，确保版本按期交付。"

## Anti-Patterns Blacklist (空洞表达黑名单)

Strictly avoid the following resume anti-patterns:
- **无主干成果的被动铺垫**：避免单纯以“负责……”、“参与……”、“协助……”罗列日常职责而不交代技术动作与结果。
- **无基准的空泛形容词**：禁止使用“极大地提高了效率”、“显著优化了性能”、“获得领导一致好评”等无事实支撑的浮夸修饰。
- **纯工具名词堆砌**：避免“使用 Python/SQL/Docker 完成开发”，应写明该工具解决了什么具体技术问题。
- **互联网空洞黑话**：禁用“赋能”、“抓手”、“打通闭环”、“拉齐颗粒度”、“组合拳”、“沉淀方法论”等抽象套话，使用平实、准确的工程师语言。

## Resume Optimization Prompt Shape

Use a prompt that asks the model to:

- rewrite the resume for job applications
- improve bullet quality using the Golden Bullet Formula
- preserve facts
- remove filler and blacklisted buzzwords
- keep the output clean, sectioned, and within the 1-page budget (`OUTPUTS.md`)

## Targeted Resume Prompt Shape

Use a prompt that asks the model to:

- if a profile datastore is provided:
  - parse the JD to extract core requirements
  - match requirements against tagged bullets in the datastore
  - prefer bullets with higher impact level (`quantified` > `qualitative` > `context-only`) when relevance is equal
  - select the best variant for each bullet based on the target role type
  - assemble selected bullets into a coherent 1-page resume (14–18 bullets total)
  - do not include unmatched bullets just to fill space
- if no datastore is provided:
  - tailor the resume toward the provided job description
  - surface matching skills and responsibilities
  - emphasize the most relevant experience first
  - stay truthful to the source

## JD-Fit Diagnosis Prompt Shape

Use a prompt that asks the model to:

- extract the JD's core requirements first
- identify direct evidence from the resume for each requirement
- label each requirement as matched, partially matched, or missing
- explain the fit in practical hiring language instead of abstract theory
- prioritize the top rewrite actions that would most improve alignment
- avoid using the term `ATS score` for China-first outputs unless the user explicitly requests it

For China-first outputs, prefer a structure like:

- `岗位匹配结论`
- `综合匹配度`
- `核心要求命中情况`
- `经历相关性分析`
- `学历 / 背景匹配`
- `信息密度与表达问题`
- `Top 3 修改建议`
- `可直接替换的简历表达`

## Cover Letter Prompt Shape

Use a prompt that asks the model to:

- connect the resume to the job description
- explain relevant fit using real experiences
- keep the letter concise
- avoid generic enthusiasm without evidence

## Name Handling Prompt Rules

For English outputs:

- preserve the candidate name accurately
- if the source name is Chinese, use pinyin unless the user gave a preferred spelling
- format the English name as `Given Name + Family Name`
- do not create a western nickname

## Contact Detail Handling Rules

- keep source phone numbers and email addresses in the final resume when they are present and the document is intended for actual job applications
- if privacy is a concern, avoid repeating sensitive contact details in chat summaries, but keep them in the generated local deliverable
- only use placeholders or redaction when the user explicitly requests anonymization
- if the source does not provide a phone number or email address, leave it absent rather than guessing or inventing one

## Suggested Validation Questions

After generation, ask:

- does every bullet map back to a real source fact or a datastore entry?
- if a datastore was used, were the selected bullets relevant to the JD?
- were low-relevance bullets correctly excluded instead of forced in?
- does the total bullet count stay within the 1-page budget (14–18 bullets)?
- is the name correct?
- are phone number and email preserved when present in the source?
- were missing contact details left absent instead of being guessed or fabricated?
- did the output keep the requested language?
- did the model overstate impact beyond the source?
- does each match or gap cite evidence from the JD or the resume?
- are the rewrite suggestions concrete enough to use immediately?
