# Offer Evaluation & Negotiation

Use this workflow for total compensation calculation, multi-offer scorecard comparison, and salary negotiation scripts (谈薪博弈与 Offer 决策).

## Overview

拿到意向书或正式 Offer 后的评估与谈薪是求职闭环的最后一公里。本工作流帮助候选人拆解总包真实价值、跨城市核算实际购买力、进行多 Offer 量化对比，并生成有理有据的谈薪沟通话术。

## Inputs

Required:
- 目标 Offer 信息（公司、岗位、职级、Base 月薪、发薪月数、绩效/年终奖说明、签字费、期权/RSU、五险一金比例、工作城市）

Optional:
- 候选人当前薪资或心理底线
- Competing Offer（其他已拿到或正在谈的 Offer 详情）
- profile datastore (`profile_store.yaml`)

---

## 1. 全包总额拆解与购买力核算

避免被笼统的“总包口径”误导，将薪酬拆解为四个确定性层级进行核算：

```text
1. 年度确定性现金 = Base 月薪 × 固定发薪月数 + 合同写明的保底年终奖 + 首年签字费 (Sign-on Bonus)
2. 年度浮动现金   = 目标年终奖 / 绩效奖金 × 历史常见达成系数 (稳健估算通常取 0.8~1.0)
3. 年度长期激励   = (期权/RSU 授予总额 ÷ 归属年限) × 流动性折现系数
                    - 已上市大厂 RSU：折现系数取 0.85~1.0
                    - 独角兽/Pre-IPO 期权：折现系数取 0.2~0.5
                    - 早期初创公司期权：折现系数取 0~0.2（单独列示，不计入刚性现金流）
4. 法定与补充福利 = 月度双边公积金（尤其是公司缴纳部分）× 12 + 房补/餐补/现金福利年额

综合年包 (Total Compensation) = 年度确定性现金 + 年度浮动现金 + 年度长期激励 + 法定与补充福利
```

### 跨城市与时薪校准
- **有效时薪估算**：结合团队常见作息（如 `10-7-5` vs `10-9-5` / 大小周），计算单位工作小时的现金回报。
- **城市生活成本校准**：若对比一线城市（北京/上海/深圳）与新一线城市（南京/杭州/苏州/成都），扣除租房与通勤差额后再对比“可支配净结余”。

---

## 2. 10 维多 Offer 综合决策矩阵

当候选人对比 2 个及以上 Offer（或对比新 Offer 与现职）时，按以下 10 个维度进行 1–5 分量化评估：

| # | 维度 | 权重 | 评估要点 |
|---|------|------|---------|
| 1 | 确定性现金回报 | 20% | Base、固定月数与保底奖金构成的刚性现金水平 |
| 2 | 业务核心度与天花板 | 15% | 所属部门是公司核心造血业务/战略级投入方向，还是边缘支持部门 |
| 3 | 技术栈与成长空间 | 15% | 能否接触高并发/复杂系统架构/前沿 AI 工程实践，对下一跳简历的背书价值 |
| 4 | 直属 Leader 与团队 | 10% | 面试中感受到的 Leader 技术视野、管理风格及团队工程文化 |
| 5 | 平台品牌与履历背书 | 10% | 公司在行业内的知名度与人才市场认可度 |
| 6 | 作息强度与可持续性 | 10% | 日常上下班节奏、On-call 频率、是否有隐形加班文化 |
| 7 | 城市与通勤成本 | 5% | 目标城市定居意愿、单程通勤时间、远程/混合办公政策 |
| 8 | 长期激励兑现度 | 5% | RSU/期权的变现确定性、归属节奏（如是否均匀归属）与回购机制 |
| 9 | 业务财务健康度 | 5% | 公司现金流、商业化变现能力与组织稳定性 |
| 10 | 个人兴趣与兴奋感 | 5% | 候选人对所做产品与技术方向的内在驱动力 |

---

## 3. 谈薪博弈话术（Negotiation Scripts）

根据候选人的筹码与诉求，输出定制化、得体的沟通话术（支持微信/邮件与电话沟通提纲）：

### 场景 A：手握 Competing Offer 争取提包（Argue Base / 总包）
- **核心策略**：先表达对该团队业务与面试官的强烈认可（明确“只要薪资对齐，优先签贵司”），再客观摆出 Competing Offer 的确定性现金差距，给 HR 明确的内部审批理由。
- **要点**：明确指出目标数字（如期望 Base 提升至 XXk，或总包对齐至 XXw），避免模糊试探。

### 场景 B：Base 触及职级上限，争取结构性替代补偿
- 当 HR 反馈“该职级 Base 薪资带已封顶”时，引导争取以下替代项：
  1. **首年签字费（Sign-on Bonus）**：一次性弥补首年现金差额或老东家年终奖/未归属期权损失。
  2. **首年绩效保底（Guaranteed Bonus）**：争取在 Offer 中注明首年年终奖不低于 X 个月。
  3. **股票/期权增发或提前窗口**：争取额外 RSU 授予定额，或约定满 6 个月参与首次调薪/晋升评审。

### 场景 C：礼貌申请 Offer 延期（争取其他流程开奖时间）
- 当被催促在 2–3 天内签署，但核心心仪岗位仍在终面或审批中：
  - 表达对 Offer 的重视，以“需与家人共同敲定跨城/换工作安排”为由，礼貌协商延长至具体日期（通常 3–5 个工作日）。

### 场景 D：得体婉拒 Offer（留存长期行业人脉）
- 感谢 HR 与业务团队在面试流程中的专业认可，坦诚说明因个人现阶段技术方向选择而忍痛婉拒，保持良好印象。

---

## Output Structure & Naming

保存到 `outputs/resumes/` 目录：
- 单个 Offer 评估与谈薪方案：`outputs/resumes/姓名_公司_Offer评估_v1.md`
- 多 Offer 对比决策：`outputs/resumes/姓名_多Offer对比评估_v1.md`

同时提示用户在 `data/tracker.tsv` 中将对应岗位状态更新为 `offer_evaluating`、`accepted` 或 `declined`。

## Error Recovery

- **Offer 细节不完整**（如只知道月薪，不清楚年终奖月数或公积金比例）：先按行业/该公司常见标准（如 12% 公积金、标准发薪月数）给出带明确标注的基准测算，并列出需要候选人向 HR 追问核实的清单（如“公积金基数是否全额”、“年终奖是否写进合同”、“试用期薪资是否打折”）。
- **无 Competing Offer 且涨幅受限**：不要建议强硬施压；改为基于候选人过往稀缺项目经验（结合 `profile_store.yaml` 中与岗位强相关的亮点）与市场同级别公允水平，温和争取签字费或定级微调。

## Task Checklist

- [ ] compensation broken down into deterministic cash, variable bonus, equity, and benefits
- [ ] missing offer terms explicitly flagged with questions to ask HR
- [ ] multi-offer comparison weighted objectively when multiple offers exist
- [ ] negotiation scripts tailored to the candidate's actual leverage and tone
- [ ] saved to `outputs/resumes/` with `_Offer评估_v1.md` naming
