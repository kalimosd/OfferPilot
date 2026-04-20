# Product Research Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增 product-research 任务类型，让 agent 能根据 JD 输出产品介绍、竞品分析、面试预测和准备建议。

**Architecture:** 新建独立 skill 文档 `skill-pack/PRODUCT_RESEARCH.md` 定义完整流程，WORKFLOW.md 新增 task type 入口指向该文档。

**Tech Stack:** Markdown 文档（无代码变更）

---

### Task 1: 创建 PRODUCT_RESEARCH.md

**Files:**
- Create: `skill-pack/PRODUCT_RESEARCH.md`

- [ ] **Step 1: 创建 skill 文档**

```markdown
# Product Research

Use this workflow for product research tasks (面试前产品认知准备).

## Overview

根据 JD 对目标公司/产品进行调研，输出产品介绍、竞品分析、面试问题预测和准备建议。帮助候选人在面试前快速建立对目标产品的认知。

## Inputs

Required:
- job description (JD file or inline text)

Optional:
- profile datastore (`profile_store.yaml`) — 有则生成个性化面试预测和关联点分析

## Execution Flow

### Step 1: 解析 JD

从 JD 中提取：
- 公司名称
- 产品名称（如有明确提及）
- 岗位核心职责
- 关键技术方向和业务场景关键词

### Step 2: 联网调研

搜索以下信息：
- 产品官网、功能介绍、产品定位
- 客户群体和商业模式
- 竞品信息和行业格局
- 公司最新技术/AI 布局动态
- 产品相关的技术方案（如 JD 中提到的具体技术）

### Step 3: 生成产品介绍 + 竞品分析

产品介绍需覆盖：
- 产品定位与背景（一段话说清楚这是什么）
- 核心功能模块（表格形式）
- 客户群体
- 商业模式
- 如 JD 涉及特定技术方向，详细展开该方向的能力现状

竞品分析需覆盖：
- 直接竞品对比表（维度：定位、功能、价格、技术路线、优劣势）
- 该产品的差异化优势总结

### Step 4: 生成面试问题预测

分类输出预测问题，每题包含题目和答题要点：

- **产品理解类**：考察对产品的认知深度
- **技术方案类**：考察 JD 中提到的技术方向
- **产品设计类**：考察产品思维
- **结合背景类**（仅当有 profile_store 时）：预测面试官针对候选人经历与该岗位交叉点的追问

无 profile_store 时跳过"结合背景类"。

### Step 5: 生成关联点分析 + 准备清单

**有 profile_store 时：**
- Section 四（关联点）：从 profile 中找出与该岗位直接相关的经历，给出面试中主动展示的切入点建议
- Section 五（准备清单）：个性化的概念学习 + 产品体验 + 材料阅读建议

**无 profile_store 时：**
- 跳过 Section 四
- Section 五仅输出通用准备建议

### Step 6: 保存文件

保存到 `outputs/` 目录：
```
姓名_公司_岗位_产品研究_v1.md
```

无 profile_store 时姓名使用"候选人"占位。

## Output Structure

```markdown
# 产品研究 — {公司} {岗位}

- 候选人: {姓名}
- 目标岗位: {公司} - {岗位}
- 生成时间: {时间}

---

## 一、产品介绍

### 1.1 产品定位
（一段话概述）

### 1.2 核心功能模块
| 模块 | 功能 |
|------|------|
| ... | ... |

### 1.3 客户群体
（列表）

### 1.4 商业模式
（简述）

### 1.5 {JD 关键技术方向} 能力现状
（详细展开）

## 二、竞品分析

### 2.1 直接竞品对比
| 维度 | 竞品A | 本产品 | 竞品B |
|------|-------|--------|-------|
| ... | ... | ... | ... |

### 2.2 差异化优势
（编号列表）

## 三、面试问题预测

### 3.1 产品理解类
1. **问题**
   - 答题要点: ...

### 3.2 技术方案类
...

### 3.3 产品设计类
...

### 3.4 结合背景类（有 profile_store 时）
...

## 四、你的关联点（有 profile_store 时）
- 相关经历 → 岗位需求的映射
- 面试中主动展示的切入点建议

## 五、准备清单
- [ ] 必须了解的概念
- [ ] 建议体验的产品/功能
- [ ] 建议阅读的材料
```

## Quality Rules

- 产品介绍必须基于搜索结果，不可凭空编造产品功能
- 竞品对比维度需与 JD 岗位职责相关（不是泛泛对比）
- 面试问题需具体、可回答，不能过于宽泛
- 准备清单需可执行（给出具体网址、产品名、文档名）
- 不输出 PDF，仅 Markdown

## Task Checklist

- [ ] JD 已解析，关键信息已提取
- [ ] 联网搜索已执行，信息来源可靠
- [ ] 产品介绍覆盖定位、功能、客户、商业模式
- [ ] 竞品对比表维度与岗位相关
- [ ] 面试问题分类清晰，每题有答题要点
- [ ] 有 profile_store 时，关联点分析和个性化内容已生成
- [ ] 无 profile_store 时，Section 四已跳过
- [ ] 文件已保存到 outputs/ 且命名正确
```

- [ ] **Step 2: Commit**

```bash
git add skill-pack/PRODUCT_RESEARCH.md
git commit -m "feat: add product-research skill document"
```

---

### Task 2: 更新 WORKFLOW.md

**Files:**
- Modify: `skill-pack/WORKFLOW.md`

- [ ] **Step 1: 在 Section 1 (Classify the Task) 中新增 task type**

在现有列表末尾添加：
```markdown
- product research
```

- [ ] **Step 2: 在 Section 2 (Collect Inputs) 的 "Additional inputs when needed" 中添加**

```markdown
- job description for product research
```

- [ ] **Step 3: 在 Section 4 (Generate the Draft) 中，mock interview 段落之后添加**

```markdown
For product research:

- read `PRODUCT_RESEARCH.md` before generating any content
- follow the six-step execution flow: JD parsing, research, product intro, interview prediction, profile analysis, save
- JD is required; profile datastore is optional but enhances output
```

- [ ] **Step 4: 在 Section 5 (Review the Draft) 的 Check 列表中添加**

```markdown
- for product research, whether product information is sourced from search results (not fabricated)
- for product research, whether interview questions are specific and answerable
```

- [ ] **Step 5: 在 Task Checklist 末尾添加**

```markdown
- [ ] for product research, output saved as Markdown only (no PDF)
- [ ] for product research, profile_store sections included/skipped correctly based on availability
```

- [ ] **Step 6: Commit**

```bash
git add skill-pack/WORKFLOW.md
git commit -m "feat: add product-research task type to workflow"
```
