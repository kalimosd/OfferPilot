# Skill Pack 审查：优化空间与修正方案

Date: 2026-06-07
Context: 基于 offerpilot-skill 分支全量文档审查（18 个文档 + agent 分支 SYSTEM_PROMPT + 3 适配器 + 测试）

---

## 审查方法

对上一轮初步分析中的 8 个提议，逐条做 4 维度复查：

- **Correctness**：是否准确诊断了问题
- **Completeness**：是否有遗漏的下游影响
- **Risk**：改动是否引入新问题
- **Consistency**：是否匹配现有模式

同时交叉对比 `offerpilot-agent` 分支的 `graph.py` SYSTEM_PROMPT、3 个适配器、测试文件，检查改动面。

---

## 提议 0：消除规则重复

### 初步诊断

> 同一规则出现在多个文档，改一处要同步 3-4 个文件。

### 复查结论：**部分错误，需要重新界定**

逐条核实：

| 声称重复的规则 | WORKFLOW.md | OUTPUTS.md | PROMPTS.md | 判断 |
|---|---|---|---|---|
| section 顺序 | L66-68 作为「生成时必须遵守」 | L51-67 作为「输出期望」 | 无 | **有意重复**：两个关注点不同。WORKFLOW 是「怎么做」，OUTPUTS 是「怎么验证」 |
| 实习/工作/项目必须分开 | L67-68 | L64 | 无 | 同上 |
| PDF style 默认 | L69 | L107-115 | 无 | **可消除**：WORKFLOW.md 只需引用 OUTPUTS.md |
| 不编造事实 | L48-54 多次强调 | L95-96 | L9 | **可消除**：应收敛到 PROMPTS.md |
| 不猜测联系方式 | L54 | L101 | L10 | 同上 |

**修正结论**：不是「提取共享约束到一个新文件」，而是：

1. **WORKFLOW.md 不应内嵌输出格式规则** — Section 4 的关键规则速查（L64-70）改为引用 OUTPUTS.md
2. **PROMPTS.md 作为行为约束的唯一来源** — WORKFLOW.md 和 OUTPUTS.md 中的行为规则改为引用 PROMPTS.md
3. **保留两处出现的规则仅当关注点不同**（如「生成规则」vs「验证规则」）

### 下游影响

- Agent 分支 SYSTEM_PROMPT 不受影响（已经是独立压缩版）
- 3 个适配器不受影响（只引用文档名，不引用具体段落）

---

## 提议 1：精简 WORKFLOW.md

### 初步诊断

> WORKFLOW.md 224 行，既是路由器又是执行手册，Section 4 每个 task 类型占了 5-10 行。

### 复查结论：**方向正确，但范围需要更精确**

**实际分析 Section 4 的结构：**

```
Section 4: Generate the Draft (L56-148，共 93 行)
├── 关键规则速查 (L64-70, 7 行)          ← 保留，但引用 OUTPUTS.md/PROMPTS.md
├── jd-fit diagnosis (L72-79, 8 行)      ← 保留，属于 WORKFLOW 层面的编排指令
├── resume optimization (L81-86, 6 行)   ← 同上
├── targeted resumes (L88-101, 14 行)    ← 保留 datastore 路径描述
├── cover letters (L103-107, 5 行)       ← 保留
├── job discovery (L109-115, 7 行)        ← 保留
├── mock interview (L117-122, 6 行)       ← 已有 MOCK_INTERVIEW.md，可精简为引用
├── product research (L124-129, 6 行)     ← 已有 PRODUCT_RESEARCH.md，可精简为引用
├── structured evaluation (L131-135, 5 行) ← 已有 EVALUATION.md，可精简为引用
├── application tracking (L137-141, 5 行)  ← 已有 TRACKER.md，可精简为引用
└── LinkedIn outreach (L143-147, 5 行)     ← 已有 OUTREACH.md，可精简为引用
```

**修正结论**：

- 已有独立 task 文档的 7 个任务（mock interview、product research、evaluation、tracker、outreach），Section 4 内只需一行 `read <DOC>.md` 引用
- 没有独立 task 文档的 4 个任务（jd-fit、optimization、targeted resume、cover letter、job discovery），保留当前段落的编排指令，但不应在 WORKFLOW.md 里维护完整规则
- 当前 L64-70 的「关键规则速查」是 WORKFLOW 的合法职责 — 它是「生成前必须检查的硬约束」，类似 pre-flight checklist

**实际可删减量**：约 30-40 行（7 个已有文档的任务从详细指令改为单行引用），不是之前估计的「整个 Section 4 删掉」

### 遗漏发现：WORKFLOW.md 缺少 pipeline 任务的生成指令

Task 列表里有 `job discovery and recommendation` 但 Section 4 里有对应段。检查 agent 分支 — pipeline 在 graph.py 里是硬编码的 subgraph，不走 ReAct 循环。Skill 分支没有对应的 pipeline task 执行文档？实际上有 — WORKFLOW.md L109-115 的 "For job discovery and recommendation" 确实存在。没问题。

---

## 提议 2：增加 v2 迭代指南

### 初步诊断

> 用户生成 v1 后 review 要改，缺少迭代指导。

### 复查结论：**诊断正确，但粒度需要细化**

**当前流程假设**：一次生成 → 一次 review → 完成。实际使用是：

```
生成 v1 → 用户 review → "教育背景错了，改一下" → agent 该做什么？
```

现有文档没有明确回答：
- 是否应该**重新生成整个文档**？还是**局部修改**？
- 如果局部修改，**哪些 section 保持不变**？
- 版本号怎么处理？（v1 → v2？还是覆盖 v1？）

**修正方案**：在 WORKFLOW.md Section 5 (Review) 后增加 Section 5b：`Iterating on Feedback`

```markdown
### 5b. 迭代修改

用户 review 后提出修改意见时：

- 优先局部修改 — 只改用户指出的部分，不要重新生成整个文档
- 保持未修改的 section 内容不变（包括措辞和顺序）
- 如果用户说「重新生成」或「推翻重来」，才走完整生成流程
- 修改后版本号递增（v1 → v2），保留旧版本文件
- 文件名保持 `_v2` 后缀（不要覆盖 v1）

迭代完成后重新运行 Section 6（Finalize），包括 PDF 重新导出。
```

### 下游影响

- Agent 分支 SYSTEM_PROMPT 需同步这个行为规则
- 适配器不受影响

---

## 提议 3：增加简历诊断独立文档

### 初步诊断

> 缺少不针对特定 JD 的「纯简历诊断」独立文档。

### 复查结论：**诊断正确**

**当前状态**：

- OUTPUTS.md L69-74 定义了 `Resume Diagnosis Expectations`（4 条规则）
- WORKFLOW.md 没有对应的 task type
- 既不在 Section 1 的 task 列表中，也不在 Section 4 有执行指令

这确实是一个功能缺口。与 jd-fit diagnosis 的区别：

| | Resume Diagnosis | JD-Fit Diagnosis |
|---|---|---|
| 输入 | 仅简历/profile | 简历 + JD |
| 输出 | 简历结构/表达问题 + 优化建议 | 与 JD 的匹配度 + 差距 + 改写建议 |
| 评分 | 不评分 | 5 维度评分 |
| 文档 | 无 | JD_MATCHING.md |

**修正方案**：新增 `RESUME_DIAGNOSIS.md`，定义：
- 诊断维度：完整性、量化程度、结构、语言质量、关键词密度
- 输出格式
- 与 jd-fit 的路由区分（有无 JD 输入）

### 下游影响

- WORKFLOW.md Section 1 新增 task type
- WORKFLOW.md Section 4 新增执行指令
- 3 个适配器 SKILL.md 的 task document 列表新增
- `tests/test_validators.py` 的 `test_adapters_share_task_documents_and_triggers` 需要更新
- Agent 分支 SYSTEM_PROMPT 的 task 列表可能需要同步

---

## 提议 4：缺少错误恢复模式

### 复查结论：**诊断正确，优先级应提升至 P1**

逐一检查每个 task 文档的「如果出了问题怎么办」：

| 失败场景 | 当前处理 | 问题 |
|---|---|---|
| `extract_text.py` 失败 | 无明确指令 | agent 可能卡住或幻觉内容 |
| 搜索结果为空（product research） | 无明确指令 | 明确写了「不可凭空编造」，但没说搜索不到怎么办 |
| profile_store 没有匹配 tag | 无明确指令 | DATASTORE.md 只说「tagless bullets 被降低优先级」，没说一个都匹配不到怎么办 |
| `render_pdf.py` 因为 Chromium 未安装而失败 | 脚本内部有提示 | 但 agent 不知道该怎么告诉用户 |

**修正方案**：每个 task 文档增加 `## Error Recovery` 节，定义最可能的失败场景和降级策略。同时在 WORKFLOW.md Section 2 增加通用错误处理规则。

### 下游影响

- Agent 分支：这些降级策略可以编码到 tool 的返回内容中

---

## 首次分析遗漏的发现

### 重大遗漏 #1：Agent 分支 SYSTEM_PROMPT 与 Skill 分支的规则同步

交叉对比发现：

| Skill 分支规则来源 | Agent SYSTEM_PROMPT 是否同步 | 风险 |
|---|---|---|
| WORKFLOW.md section 顺序 | ✅ 已同步 | 低 |
| WORKFLOW.md 输出目录 | ✅ 已同步 | 低 |
| EVALUATION.md 10 维评分 | ✅ 已同步 | 低 |
| JD_MATCHING.md experience+1 | ❌ **未同步** | **中**：agent 分支的 JD 匹配行为与 skill 分支不一致 |
| OUTPUTS.md 文件命名规则 | ✅ 已同步 | 低 |
| PROMPTS.md 技能列表格式 | ✅ 已同步 | 低 |
| DATASTORE.md variants 选择逻辑 | ❌ **未同步** | **中**：agent 不知道 variants 机制 |
| PRODUCT_RESEARCH.md 6 步流程 | ❌ **未同步** | **中**：agent 只知道用 tool，不知道流程 |

**结论**：当前 SYSTEM_PROMPT 是硬编码的压缩版，与 skill 分支文档没有自动同步机制。当 skill 分支规则变化时，需要手动更新 graph.py。这是一个架构层面的维护风险，建议在 `docs/` 下增加一个 `AGENT_SYNC_CHECKLIST.md`。

### 重大遗漏 #2：Git 仓库中的无关文件

`.gitignore` 已经配置了 `__pycache__/`、`*.pyc`、`.DS_Store`，但这些文件在被 gitignore 之前已经被 track 了：

```
skill-pack/.DS_Store                     ← 已跟踪，需 git rm --cached
skill-pack/scripts/__pycache__/*.pyc     ← 已跟踪，需 git rm --cached
```

建议清理。

### 遗漏 #3：适配器短触发覆盖不全

3 个适配器的 `Short Triggers` 节只包含 8 个触发词，但 task 列表有 11 个任务：

| 缺失的触发词 | 对应任务 |
|---|---|
| `/offerpilot 求职信` | cover letter |
| `/offerpilot 申请追踪` | application tracking |
| `/offerpilot 批量评估` | batch evaluation |

---

## 修正后的优先级排序

| 优先级 | 改动 | 修正后的范围 | 影响面 |
|---|---|---|---|
| **P0** | 精简 WORKFLOW.md Section 4 | 7 个已有文档的任务改为单行引用（-30 行）；关键规则速查保留但引用 OUTPUTS.md/PROMPTS.md | WORKFLOW.md |
| **P0** | 清理 git 跟踪的无关文件 | `git rm --cached` 两个路径 | 仓库清洁度 |
| **P1** | 增加 v2 迭代指南（WORKFLOW.md 5b） | WORKFLOW.md +10 行；agent SYSTEM_PROMPT 同步 | WORKFLOW.md, graph.py |
| **P1** | 每个 task 文档增加 Error Recovery | 7 个 task 文档各 +5-10 行 | 7 个 .md 文件 |
| **P1** | 新增 RESUME_DIAGNOSIS.md | 新建 1 个文档；WORKFLOW.md +5 行；3 适配器 +1 行；测试更新 | 新建文件 + 5 个已有文件 |
| **P2** | PROMPTS.md 作为行为约束唯一来源 | WORKFLOW.md/OUTPUTS.md 中行为规则改为引用 PROMPTS.md | 2-3 个文件 |
| **P2** | 适配器短触发覆补齐 | 3 个适配器各 +3 个触发词 | 3 个适配器 |
| **P2** | 增加 AGENT_SYNC_CHECKLIST.md | 新建 1 个文件，列出 agent SYSTEM_PROMPT 需同步的规则项 | 新建文件 |

---

## 不应做的改动

1. **不要创建新的「共享约束」文件** — 增加 agent 需要读取的文档数量，反而加重上下文负担。应让现有文档之间通过引用关联，而非提取到新文件
2. **不要删除 WORKFLOW.md 的关键规则速查（L64-70）** — 它是合法的 pre-flight checklist，不是重复
3. **不要创建 skill_aliases 扩展指南** — 当前 108 条够用，扩展需求尚未出现。过早优化
4. **不要创建快速参考卡片** — agent 已经通过 Read Order 加载文档，额外参考卡片增加维护负担但边际收益不大
