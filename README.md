<div align="center">

# OfferPilot AI

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)](https://playwright.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)

[![Claude Code](https://img.shields.io/badge/Claude_Code-000?style=flat&logo=anthropic&logoColor=white)](https://claude.ai)
[![Cursor](https://img.shields.io/badge/Cursor-000?style=flat&logo=cursor&logoColor=white)](https://cursor.com)
[![Codex](https://img.shields.io/badge/Codex-412991?style=flat&logo=openai&logoColor=white)](https://openai.com)
[![Kiro](https://img.shields.io/badge/Kiro-FF9900?style=flat&logo=amazon&logoColor=white)](https://kiro.dev)

**AI 求职助手，把弱申请变成面试敲门砖。**

简历写得像岗位描述的复制粘贴？<br>
求职信换个名字就能给任何人用？<br>
最硬核的项目经历被埋在第二页？<br>
活是你干的，但纸上看不出来？

别再低估自己了。让 AI 把你真实的经历打磨得更锋利。

[功能](#功能) · [快速开始](#快速开始) · [效果示例](#效果示例) · [进阶用法](#进阶用法) · [路线图](#路线图) · [参与贡献](#参与贡献)

[English](./README_en.md)

丢进简历和 JD，拿回一份更强的简历、一份定向改写、一份 JD 匹配度分析、或一封求职信 — 基于你的真实经历，不编不造。

</div>

---

## 为什么做这个项目

很多留学生和职场新人明明做了很好的工作，但简历写得太泛、求职信千篇一律、最相关的经历反而被埋没。

OfferPilot 只关注结果：更清晰的定位、更强的材料、更高的面试概率。

## 功能

| 功能 | 说明 |
|------|------|
| **简历优化** | 精炼措辞、去除水分、强化 bullet point — 不编造事实 |
| **定向简历改写** | 围绕目标 JD 重写和重排内容 |
| **JD 匹配度分析** | 识别匹配信号、差距和改写优先级 |
| **求职信生成** | 基于真实经历生成简洁、有针对性的求职信 |
| **Profile 素材库** | 从结构化 YAML 素材库中选取最相关的经历 |
| **职位发现** | 自动扫描招聘网站和搜索引擎，发现匹配岗位 |
| **模拟面试** | 基于 JD 和个人经历生成技术面试题单，对话模拟并输出评估报告 |
| **产品研究** | 根据 JD 调研目标产品，输出产品介绍、竞品分析、面试预测和准备清单 |
| **PDF 导出** | 将 Markdown 草稿渲染为带样式的 PDF，支持嵌入照片 |

## 快速开始（Skills 优先）

1. 准备 `resume.md`（或 `resume.pdf`）
2. 准备 `job.md`（目标岗位的 JD）
3. 打开 `skill-pack/README.md` 并按 read order 执行
4. 在 agent 里使用短触发语，例如：
   - `按照 offerpilot 优化简历`
   - `用 offerpilot 做 JD 匹配`
   - `/offerpilot 根据我简历推荐10个岗位`
   - `用 offerpilot 模拟面试这个岗位`
   - `用 offerpilot 研究一下这个产品`
5. 审阅生成的 Markdown 输出，满意后导出


## 效果示例

**优化前**

```text
- 负责 Android 开发，和不同团队合作。
- 帮忙修 bug，提升 app 性能。
```

**优化后**

```text
- 使用 Perfetto 和 Systrace 诊断渲染、内存和 ANR 问题，推动跨平台团队修复，
  提升 Android 系统稳定性和性能。
- 负责最近任务功能的交付，协调工程干系人按期上线，加速跨团队问题闭环。
```

生成的内容可以直接使用，几乎不需要额外编辑。

## 技术栈

- Python · LLM 驱动的改写与分析
- 模块化 skill-pack 架构
- YAML 格式的 profile 素材库
- 基于 Playwright 的 PDF 导出和招聘网站扫描

## 项目结构

```text
.
├── README.md               # 中文（主页）
├── README_en.md            # English
├── profile_store.yaml      # 个人素材库（不入 git）
├── portals_cn.yml
├── skill-pack/
│   ├── README.md           # skill pack 入口
│   ├── WORKFLOW.md         # 任务流程和检查点
│   ├── PRODUCT_RESEARCH.md # 产品研究流程
│   ├── DATASTORE.md        # 素材库规范
│   ├── JD_MATCHING.md      # 中国市场 JD 匹配
│   ├── INPUTS.md / OUTPUTS.md / PROMPTS.md
│   ├── adapters/           # Claude Code、Codex、Cursor 适配器
│   ├── examples/           # 示例输出
│   ├── data/               # 技能别名映射
│   └── scripts/            # 提取、渲染、扫描、校验
├── jds/                    # （不入 git）扫描保存的 JD
├── data/                   # （不入 git）扫描历史
└── tests/
```

## 可选辅助命令（CLI）

`skill-pack` 是主入口，CLI 只是可选执行器：

```bash
# 查看全部命令
offerpilot

# 提取源文件文本
offerpilot extract "resume.pdf" --output "resume.txt"

# 导出 PDF
offerpilot pdf "resume.md" "resume.pdf" --style classic

# 扫描岗位
offerpilot scan --cn-only

# 最小流程：校验输入 + 导出简历 PDF
offerpilot run "resume.md" "outputs/resume.pdf" --style ats

# 端到端岗位流水线：扫描 + 排序 + TopN 推荐
offerpilot pipeline --days 7 --top-n 10 --cn-focus
```

直接脚本调用（同样是可选项）：

从 PDF 或 DOCX 提取文本：

```bash
python3 skill-pack/scripts/extract_text.py "resume.pdf" --output "resume.txt"
```

将审阅后的草稿导出为 PDF：

```bash
python3 skill-pack/scripts/render_pdf.py "resume.md" "resume.pdf" --document-type resume --style classic
```

导出时嵌入照片：

```bash
python3 skill-pack/scripts/render_pdf.py "resume.md" "resume.pdf" --style standard_cn --photo "photo.jpg"
```

扫描招聘网站寻找匹配岗位：

```bash
# 全量扫描（国内 API + Greenhouse + 搜索引擎）
python3 skill-pack/scripts/scan_portals.py

# 仅国内公司 API（美团、快手、滴滴）
python3 skill-pack/scripts/scan_portals.py --cn-only

# 仅 Greenhouse API（海外公司）
python3 skill-pack/scripts/scan_portals.py --greenhouse-only

# 仅搜索引擎（DuckDuckGo，覆盖 20+ 公司）
python3 skill-pack/scripts/scan_portals.py --search-only

# 预览模式，不写入文件
python3 skill-pack/scripts/scan_portals.py --dry-run
```

匹配到的岗位会保存到 `jds/`，包含完整 JD 内容和投递链接。扫描历史记录在 `data/scan-history.tsv` 中用于去重。

## 路线图

- 基于 RAG 的职位搜索和简历知识系统
- 模拟面试与反馈
- 更好的素材库检索和排序
- Agent 驱动的自动投递工作流
- 简历版本管理和定向自动化

## 参与贡献

欢迎反馈、提 issue 和 PR。

如果你想改进工作流、测试输出质量、或者提产品方向建议 — 开个 issue 或发起讨论。

## 写在最后

工作很重要。离开学校以后，它不声不响地占据了你醒着的大部分时间，这没什么好争的。

但工作又没那么重要。人不是为了优化 bullet point 而来到这个世界上的。

你做过真实的事。你解决过真实的问题。你加过班、赶过 deadline、替别人擦过屁股，但没人好好写下来 — 你自己也没有。

这个项目改变不了你的人生。但如果它能帮一个人不再低估自己，不再把同一份万能简历投进黑洞，真正拿到一个配得上的面试机会 —

那就够了。

去拿 offer 吧。然后合上电脑，好好生活。
