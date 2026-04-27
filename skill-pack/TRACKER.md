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
discovered → applied → interviewing → offer
                                    → rejected
                                    → ghosted
```

## Follow-up Rules

- `applied` 超过 7 天无更新 → 提醒跟进
- `interviewing` 超过 5 天无更新 → 提醒跟进
- 其他状态不提醒

## Usage

当用户要求追踪申请状态时：

1. 读取 `data/tracker.tsv`（如不存在则创建）
2. 按用户指令添加、更新或查询记录
3. 检查 follow-up 时，计算每条记录的 `last_update` 距今天数，按规则提醒

## Output

Tracker 操作结果直接在对话中返回，不保存到 outputs 目录。
