# Outputs

## Output Directory Structure

All outputs are saved under `outputs/` with the following subdirectories:

| Subdirectory | Content |
|---|---|
| `outputs/resumes/` | 简历诊断、简历优化、定向改写、JD 匹配度分析、结构化评估、批量评估、Offer 评估与谈薪方案 |
| `outputs/research/` | 产品研究 |
| `outputs/interview/` | 面试题单、面试评估、真实面经复盘、行为面故事卡与反问清单 |
| `outputs/pipeline/` | 扫描推荐、pipeline 报告 |
| `outputs/misc/` | Boss直聘打招呼、内推私信、LinkedIn 外联消息、求职信、其他材料 |

Rules:

- 所有输出必须保存到对应子目录，不允许直接保存到 `outputs/` 根目录
- 子目录会自动创建（agent 的 write_file 工具会 mkdir -p）
- 分类依据是任务类型，不是文件格式

## Output Categories

OfferPilot supports these output types:

- resume diagnosis
- optimized resume
- job-targeted resume
- jd-fit diagnosis
- cover letter
- structured evaluation report
- batch evaluation ranking
- offer evaluation and negotiation report
- mock interview question sheet
- mock interview evaluation report
- post-interview debrief report
- product research report
- multi-channel outreach message (Boss直聘 / 内推 / LinkedIn / Email)
- pipeline recommendation report

## Age Display

- Display age on the contact information line, after email: `电话（微信同） | 邮箱 | XX 岁`
- Calculate age from the `birth_year` field in the profile datastore: `current_year - birth_year`
- Format: `XX 岁` for Chinese outputs, `Age XX` for English outputs
- If `birth_year` is not provided, omit the age line

## Resume Page Budget & Length Control (一页纸篇幅预算)

在国内社招/校招与外企初筛中，**A4 单页简历**拥有最高的阅读完成率。切忌生成 1.2～1.3 页（第二页仅余几行尾巴）的尴尬篇幅。

### 单页容量硬指标
- **总字数预算**：中文简历控制在 **800 ～ 1100 字**；英文简历控制在 **350 ～ 500 词**。
- **全篇 Bullet 总数**：控制在 **14 ～ 18 条**以内。
- **各模块条数分配**：
  - 核心/最近一份工作经历：4 ～ 6 条 bullets
  - 次要工作或实习经历：每段 2 ～ 3 条 bullets（最多保留 2–3 段强相关实习）
  - 强相关项目经历（精选 2–3 个）：每个项目 2 ～ 4 条 bullets
  - 技能清单：精选 8 ～ 12 项与目标岗位匹配的核心技能（避免罗列低相关工具）

### 超标裁剪优先级（Pruning Priority）
当候选人 `profile_store.yaml` 素材超出单页容量时，按以下顺序裁剪：
1. **首先剔除 `context-only` 条目**：删除纯职责介绍、无明确技术动作或成果的铺垫句。
2. **折叠低相关实习/次要项目**：与目标 JD 方向跨度较大的早期实习或课程项目，压缩至 1–2 条核心 bullet 或直接省略。
3. **严格遵守 `quantified` > `qualitative`**：优先保留有真实指标支撑或深度架构决策的条目。
4. **PDF 页数校验**：调用 `render_pdf.py` 后会自动检测 PDF 页数；若超过 1 页，优先精简低权重 bullet，或改用 `--style compact` 重新渲染。

## Education Line Format

- 学历 emphasis 行使用 `|` 分隔学校、专业和学位，格式为：`**学校名 | 专业 | 学位**`
- 示例：`**墨尔本大学 | 数据科学 | 硕士**`
- 英文示例：`**University of Melbourne | Data Science | Master**`

## Default Section Ordering

Use this order for resume outputs unless the user requests otherwise:

1. 教育背景
2. 工作经历
3. 与目标岗位强相关的项目经历（如投 AI 岗则优先展示 AI 项目）
4. 实习经历
5. 其他项目经历（科研、学术等）
6. 技能

Rules:

- 实习经历和项目经历必须分开，不能合并为同一个 section
- 当存在多类项目时，与目标岗位相关性更高的项目 section 排在实习之前，其余排在实习之后
- 如果没有明确的目标岗位，所有项目经历统一放在实习经历之后
- 不要生成"工作亮点"等额外总结性 section，除非用户明确要求

## Resume Diagnosis Expectations

See `RESUME_DIAGNOSIS.md` for the full diagnosis workflow. Key output expectations:

- identifies strengths that are already supported by the source
- identifies gaps relative to either general job-readiness or a target job
- calls out risks without inventing problems
- suggests the highest-value rewrite priorities before generation

## JD-Fit Diagnosis Expectations

- explains how well the resume matches the target JD
- separates matched, partial, and missing signals
- prioritizes practical rewrite actions over abstract commentary
- uses a score only as supporting context, not as the sole conclusion
- avoids `ATS score` framing for China-first outputs unless explicitly requested

## Language Options

- `same`: keep the source language unless the source is mixed and the user asked for cleanup
- `zh`: produce professional Simplified Chinese
- `en`: produce polished English for job applications

## Resume Output Expectations

- clear sectioning
- concise bullet points within the 1-page budget
- stronger action-oriented phrasing
- no fabricated facts
- no inflated metrics
- compact, interview-ready tone
- do not add standalone target-intention lines such as `求职方向` / `求职意向` unless the user explicitly requests them
- preserves real source contact details in the final deliverable unless the user explicitly requested anonymization
- does not leave placeholder fields such as `<name>`, `<phone number>`, or `<email>` in application-ready outputs
- does not add guessed or fabricated contact details that are missing from the source

## PDF Style Options

The `render_pdf.py` script supports multiple styles via `--style`:

- `standard_cn` — default for Chinese resume outputs; centered name/contact line, section dividers, and right-aligned dates
- `classic` — default for English outputs; clean left-aligned layout with right-aligned dates
- `ats` — optimized for ATS parsing, slightly smaller text
- `compact` — tighter margins and spacing for dense content

**默认选择规则：**

- 中文简历 → `standard_cn`
- 英文简历 → `classic`
- 除非用户明确指定其他 style

## PDF Formatting Rules

- Project links (e.g. GitHub URLs) should be placed on a separate line below the project title in small text, not inline with the title
- Dates in headings are rendered right-aligned; all date columns start at the same horizontal position
- Section headings and their content are kept together across page breaks when possible

## Recommended File Naming

Use scheme `B` by default for locally saved resume deliverables:

- if only a target role is known: `姓名_岗位_v1`
- if both company and role are known: `姓名_公司_岗位_v1`
- keep the version suffix even for the first saved draft
- use `_` as the separator
- avoid spaces in filenames
- keep Markdown and PDF filenames aligned except for the file extension

Examples:

- `outputs/resumes/候选人A_安卓开发工程师_v1.md`
- `outputs/resumes/候选人A_小米_安卓开发工程师_v1.md`
- `outputs/resumes/候选人A_小米_安卓开发工程师_v2.pdf`

If the user explicitly requests anonymized sample files, replace `姓名` with an obvious example name rather than a real person.

## Targeted Resume Expectations

- emphasizes experience relevant to the target role
- incorporates job-description language naturally
- reorders emphasis without changing the underlying facts

## Cover Letter Expectations

- reflects the job description
- stays grounded in the candidate's real background
- avoids generic filler
- keeps the tone professional and direct

## Mock Interview Question Sheet Expectations

- 8-12 questions by default unless the user specifies otherwise
- ~60% strong-point deep-dive, ~40% weakness probing
- each question includes: tag, difficulty, topic, examination points, reference answer key points
- reference answers are concise key points, not full essays
- naming: `outputs/interview/姓名_公司_岗位_面试题单_v1.md`

## Mock Interview Evaluation Report Expectations

- per-question scoring (1-5 stars) with highlights, gaps, and improvement suggestions
- overall summary in 2-3 sentences
- review checklist with priority levels (高/中/低) and concrete learning recommendations
- naming: `outputs/interview/姓名_公司_岗位_面试评估_v1.md`

## Post-Interview Debrief Expectations

- deconstructs real interview questions into underlying examination points, answer strengths/flaws, and high-scoring reference answers grounded in the candidate's profile
- naming: `outputs/interview/姓名_公司_岗位_面经复盘_v1.md`

## Structured Evaluation Expectations

- single evaluation naming: `outputs/resumes/姓名_公司_岗位_评估_v1.md`
- batch ranking naming: `outputs/resumes/姓名_批量评估汇总排名.md`
- each scored dimension includes a concrete reason grounded in the JD and profile
- total score and grade are supporting context, not a replacement for the application recommendation

## Offer Evaluation Expectations

- breaks down total compensation into deterministic cash, variable bonus, equity value, and benefits
- includes 10-dimension scorecard when comparing offers and tailored negotiation scripts
- naming: `outputs/resumes/姓名_公司_Offer评估_v1.md`

## Outreach Expectations

- save to `outputs/misc/姓名_公司_打招呼.md` or `outputs/misc/姓名_公司_LinkedIn外联消息.md`
- match word count and tone to the target channel (Boss直聘 80–120 字, 内推私信 150–200 字, LinkedIn < 300 词)
- mention only experiences supported by the resume or profile datastore

## English Name Check

When the source resume is Chinese and the output is English:

- verify the English name order
- default to `Given Name + Family Name`
- keep the user-provided spelling if one exists

Example:

- `中文名` -> `<Given Name> <Family Name>`

## Final Review Checklist

- [ ] name is correct
- [ ] phone number is correct when present in the source
- [ ] email address is correct when present in the source
- [ ] missing contact details were left absent unless the user explicitly provided them later
- [ ] dates are correct
- [ ] titles and employer names are correct
- [ ] content matches the intended task and stays within the 1-page budget for resumes
- [ ] language matches the request
- [ ] fit conclusions are supported by resume and JD evidence
- [ ] rewrite suggestions are concrete and truthful
- [ ] no placeholder contact fields remain unless anonymization was explicitly requested
- [ ] saved filenames follow the default naming rule unless the user asked for a different scheme
- [ ] nothing confidential is accidentally included in publishable artifacts
