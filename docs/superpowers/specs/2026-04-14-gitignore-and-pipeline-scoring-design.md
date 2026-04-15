# Design: .gitignore 保护 + Pipeline 评分增强

Date: 2026-04-14

## 背景

OfferPilot 项目有两个待优化点：
1. `profile_store.yaml` 包含真实个人信息但未被 `.gitignore` 保护
2. `run_pipeline.py` 的岗位评分逻辑过于简单，只看来源类型、标题关键词和国内偏好，缺少与用户技能的匹配

## 改动 1：.gitignore 保护

在 `.gitignore` 末尾添加 `profile_store.yaml`。

## 改动 2：Pipeline 评分增强

### 方案选择

采用叠加式评分（方案 A）：在现有评分基础上叠加新维度，每个维度有独立分数上限。向后兼容，可解释性强。

### 改动文件

`skill-pack/scripts/run_pipeline.py`

### 新增函数

- `load_profile_tags(path) -> set[str]`：从 profile_store.yaml 提取所有 bullet tags + skills 名称
- `expand_profile_tags(tags, aliases) -> set[str]`：用 skill_aliases.zh-en.json 做双语别名扩展
- `load_aliases(path) -> dict`：加载别名映射
- `load_jd_content(title, company) -> str`：根据公司+标题从 jds/ 目录读取已保存的 JD 全文

### score_row 新增维度

| 维度 | 分值 | 逻辑 |
|------|------|------|
| 技能匹配 | 最高 4.0 | profile tags（扩展后）与「标题 + JD 全文」做子串匹配，每命中 +0.5 |
| 城市偏好 | 0.5 | JD 内容中出现 location_filter 中的目标城市 |
| JD 内容质量 | 0.5 | 有 JD 全文的岗位加分 |

现有维度（来源可靠性 1.0-3.0、标题关键词最高 2.0、资深级别 1.5、国内偏好 1.0）保持不变。

### 数据结构变更

Candidate dataclass 新增 `skill_hits: int = 0` 字段。

### CLI 变更

新增 `--profile` 参数，默认值 `profile_store.yaml`。

### 报告变更

- 表格新增 Skills 列（技能命中数）
- 头部新增 profile 加载状态行

### 不改动

- 现有评分逻辑全部保留
- scan_portals.py 不改
- 其他脚本不改
