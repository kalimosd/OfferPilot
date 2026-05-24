# OfferPilot AI Skill Pack

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

OfferPilot 是一套面向求职场景的 AI 工作流 Skill Pack，用来帮助候选人基于真实经历完成简历优化、JD 匹配、定向改写、结构化评估、面试准备、产品研究、申请追踪和外联消息生成。

这个分支是 [offerpilot-skill](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill)。主入口是 `skill-pack/`，适合在 Cursor、Claude Code、Codex 等 AI 编程工具中使用。

如果你想运行 LangGraph Agent、CLI 或 Web UI，请切换到 [offerpilot-agent](https://github.com/kalimosd/OfferPilot/tree/offerpilot-agent) 分支。

[English](./README_en.md)

## 核心原则

- 原始简历和 `profile_store.yaml` 是事实来源。
- 生成内容只能重写、筛选、组织真实经历，不能编造项目、公司、指标、学历或联系方式。
- Markdown 内容应先人工 review，再导出 PDF 或用于投递。
- 所有本地隐私数据默认不提交到 git。

## 能做什么

| 能力 | 说明 |
|---|---|
| 简历诊断 | 判断简历问题、信息缺口、表达弱点 |
| 简历优化 | 精炼措辞、强化 bullet point、提升可读性 |
| 定向改写 | 围绕某个 JD 重排和改写经历 |
| JD 匹配分析 | 识别匹配点、差距、关键词和改写优先级 |
| 结构化评估 | 10 维度打分，输出 A-F 等级和投递建议 |
| 批量评估 | 对多个 JD 做排序，快速筛选值得投递的岗位 |
| 求职信 | 基于真实经历生成针对性 cover letter |
| LinkedIn 外联 | 生成简洁、个性化的 outreach 消息 |
| 模拟面试 | 生成面试题单，支持问答模拟和评估报告 |
| 产品研究 | 针对目标公司/产品做面试前研究 |
| 申请追踪 | 定义 tracker 状态流转和 follow-up 规则 |
| PDF 辅助 | 提供 Markdown 到 PDF 的本地脚本 |

## 快速开始

1. 打开 `skill-pack/README.md`
2. 根据任务阅读对应文档：
   - JD 匹配：`skill-pack/JD_MATCHING.md`
   - 结构化评估：`skill-pack/EVALUATION.md`
   - 简历优化 / 定向改写：`skill-pack/WORKFLOW.md` + `skill-pack/PROMPTS.md`
   - 模拟面试：`skill-pack/MOCK_INTERVIEW.md`
   - 产品研究：`skill-pack/PRODUCT_RESEARCH.md`
   - 申请追踪：`skill-pack/TRACKER.md`
   - 外联消息：`skill-pack/OUTREACH.md`
3. 准备输入文件：
   - 原始简历或 `profile_store.yaml`
   - 目标 JD
   - 可选：目标公司、岗位方向、申请状态记录
4. 按 `skill-pack/OUTPUTS.md` 检查输出格式。
5. 如需本地脚本，查看 `skill-pack/scripts/README.md`。

## Profile Datastore

推荐使用 `profile_store.yaml` 维护完整个人素材库。它不是简历成品，而是事实数据库。

可以从模板开始：

```bash
cp skill-pack/templates/profile_store.yaml profile_store.yaml
```

主要字段：

| 字段 | 说明 |
|---|---|
| `meta` | 姓名、英文名、出生年份、邮箱、电话、更新时间 |
| `experience` | 工作经历，每段经历包含多个 bullet |
| `projects` | 项目经历、开源、比赛、校园项目等 |
| `skills` | 技能、熟练度、使用年限、证据 |
| `education` | 教育背景 |
| `certifications` | 证书 |
| `achievements` | 奖项或荣誉 |

建议把经历写全，不要一开始就压缩。Skill Pack 会根据 JD 选择最相关的部分。

## 输出目录约定

所有输出放在 `outputs/` 下的对应子目录：

| 目录 | 内容 |
|---|---|
| `outputs/resumes/` | 简历优化、定向改写、JD 匹配、结构化评估 |
| `outputs/research/` | 产品研究 |
| `outputs/interview/` | 面试题单、面试评估 |
| `outputs/pipeline/` | 岗位扫描和推荐报告 |
| `outputs/misc/` | 外联消息、项目讲解、其他材料 |

不要直接把正式输出放在 `outputs/` 根目录。

## 本地脚本

这些脚本是辅助工具，不要求运行完整 Agent。

```bash
# 校验输入文件是否存在、格式是否支持
python skill-pack/scripts/validate_inputs.py profile_store.yaml jds/example.md

# 从 PDF / DOCX / TXT / MD 提取文本
python skill-pack/scripts/extract_text.py resume.pdf

# 将 Markdown 渲染成 PDF
python skill-pack/scripts/render_pdf.py outputs/resumes/resume.md outputs/resumes/resume.pdf

# 校验输出文件命名和格式
python skill-pack/scripts/validate_outputs.py outputs/resumes/resume.md

# 校验 profile datastore 和技能别名表
python skill-pack/scripts/validate_profile_store.py profile_store.yaml
python skill-pack/scripts/validate_aliases.py skill-pack/data/skill_aliases.zh-en.json
```

## Skill Pack 结构

```text
skill-pack/
├── README.md              # Skill Pack 入口
├── WORKFLOW.md            # 通用任务流程
├── INPUTS.md              # 输入选择和隐私规则
├── OUTPUTS.md             # 输出格式和质量检查
├── PROMPTS.md             # 生成约束和可复用提示词
├── DATASTORE.md           # profile_store.yaml 数据结构说明
├── JD_MATCHING.md         # JD 匹配分析
├── EVALUATION.md          # 10 维结构化岗位评估
├── MOCK_INTERVIEW.md      # 模拟面试
├── PRODUCT_RESEARCH.md    # 产品研究
├── TRACKER.md             # 申请状态追踪
├── OUTREACH.md            # LinkedIn 外联
├── templates/             # 本地模板
├── data/                  # 技能别名等辅助数据
├── schemas/               # profile_store 和 skill aliases 的 JSON Schema
├── examples/              # 示例
├── scripts/               # 本地辅助脚本
└── adapters/              # Cursor / Claude Code / Codex 适配器
```

## 适配器

`skill-pack/adapters/` 提供不同 AI 编程环境的入口说明：

- `skill-pack/adapters/cursor/SKILL.md`
- `skill-pack/adapters/claude-code/SKILL.md`
- `skill-pack/adapters/codex/SKILL.md`

如果工具支持 repo-local skill，可以优先使用对应 adapter。

## 与 Agent 分支的关系

OfferPilot 有两种形态：

| 分支 | 定位 |
|---|---|
| [offerpilot-skill](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill) | Skill Pack，负责规则、流程、模板、脚本和方法论 |
| [offerpilot-agent](https://github.com/kalimosd/OfferPilot/tree/offerpilot-agent) | Runnable Agent，负责 LangGraph runtime、CLI、Web UI 和自动化执行 |

建议理解为：

```text
skill-pack = 规则层 / 方法论 / 可移植工作流
agent      = skill-pack + runtime + tools + UI
```

因此，Skill Pack 是 OfferPilot 的规则层；Agent 分支是在这套规则层外面加执行器和界面。

本分支可能仍保留少量历史 runtime 文件，但它们不是这个分支的主入口。

## 维护建议

对 Skill Pack 的改动应优先进入 [offerpilot-skill](https://github.com/kalimosd/OfferPilot/tree/offerpilot-skill)：

- workflow 文档
- 输出规范
- prompt 约束
- skill alias 数据
- templates
- scripts
- adapters

Agent runtime、Web UI、API、LangGraph 状态图等改动应进入 [offerpilot-agent](https://github.com/kalimosd/OfferPilot/tree/offerpilot-agent)。

## 写在最后

> **工作很重要。**
> 离开学校以后，它不声不响地占据了你醒着的大部分时间。
>
> 但工作又没那么重要。人不是为了优化 bullet point 而来到这个世界上的。
>
> 你做过真实的事。你解决过真实的问题。你加过班、赶过 deadline、替别人擦过屁股，但没人好好写下来，你自己也没有。
>
> 这个项目改变不了你的人生。但如果它能帮一个人不再低估自己，不再把同一份万能简历投进黑洞，真正拿到一个配得上的面试机会，那就够了。
>
> **去拿 offer 吧。然后合上电脑，好好生活。**

## License

MIT
