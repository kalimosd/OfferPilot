<div align="center">

# OfferPilot AI

**AI 求职助手，把弱申请变成面试敲门砖。**

简历写得像岗位描述的复制粘贴？<br>
求职信换个名字就能给任何人用？<br>
最硬核的项目经历被埋在第二页？<br>
活是你干的，但纸上看不出来？

别再低估自己了。让 AI 把你真实的经历打磨得更锋利。

丢进简历和 JD，<br>
拿回一份更强的简历、一份定向改写、一份 JD 匹配度分析、或一封求职信 —<br>
基于你的真实经历，不编不造。

[功能](#功能) · [快速开始](#快速开始) · [效果示例](#效果示例) · [进阶用法](#进阶用法) · [路线图](#路线图) · [参与贡献](#参与贡献)

[English](./README.md)

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
| **PDF 导出** | 将 Markdown 草稿渲染为带样式的 PDF，支持嵌入照片 |

## 快速开始

1. 准备 `resume.md`（或 `resume.pdf`）
2. 准备 `job.md`（目标岗位的 JD）
3. 打开 `skill-pack/README.md`
4. 通过 Cursor、Claude Code 或 Codex 类 agent 运行工作流
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
├── README.md               # English
├── README_zh.md            # 中文
├── profile_store.yaml      # 个人素材库（不入 git）
├── portals_cn.yml
├── skill-pack/
│   ├── README.md           # skill pack 入口
│   ├── WORKFLOW.md         # 任务流程和检查点
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

## 进阶用法

可选命令入口（`skill-pack` 仍是主入口）：

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
```

直接脚本调用：

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
