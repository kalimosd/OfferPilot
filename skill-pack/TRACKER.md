# Application Tracker

Use this workflow for managing job application status.

## Data File

- Location: `data/tracker.tsv`
- Format: TSV with header row

| Field | Description |
|-------|-------------|
| url | 岗位链接 |
| company | 公司名 |
| title | 岗位名 |
| status | 状态 |
| applied_date | 投递日期 |
| last_update | 最后更新日期 |
| notes | 备注 |

## Status Flow

```
discovered → applied → interviewing → offer_evaluating → accepted
                                                       → declined
                                    → rejected
                                    → ghosted
```

Note: `offer` is also accepted as a shorthand alias for `offer_evaluating`. When a candidate receives an offer, suggest running `OFFER_EVALUATION.md` (`/offerpilot 谈薪决策`) for total compensation breakdown and negotiation scripts.

## Follow-up Rules

- `applied` 超过 7 天无更新 → 提醒跟进（可结合 `OUTREACH.md` 发送礼貌跟进或打招呼消息）
- `interviewing` 超过 5 天无更新 → 提醒跟进 HR 询问面试结果
- `offer_evaluating`（或 `offer`）超过 3 天无更新 → 提醒确认谈薪进展与 Offer 签署截止日期
- 其他状态不提醒

## Usage

当用户要求追踪申请状态时：

1. 读取 `data/tracker.tsv`（如不存在则创建）
2. 按用户指令添加、更新或查询记录
3. 检查 follow-up 时，计算每条记录的 `last_update` 距今天数，按规则提醒

## Error Recovery

- **tracker.tsv 不存在**（首次使用）：自动创建带 header 的空文件，正常执行添加操作
- **TSV 行解析失败**（字段数不匹配、日期格式错误）：跳过该行，在处理结果最后标注「跳过了 N 条格式异常记录」，不阻塞其余记录的读取和更新
- **URL 匹配不到记录**（update 操作）：明确提示「未找到 URL 对应的记录」，列出当前 tracker 中已有的 URL 供用户选择

## Output

Tracker 操作结果直接在对话中返回，不保存到 outputs 目录。
