# LinkedIn Outreach

Use this workflow for generating LinkedIn outreach messages.

## Overview

根据目标公司/岗位和候选人背景，生成个性化的 LinkedIn 外联消息。

## Inputs

Required:
- 目标公司名称和岗位方向
- profile datastore (`profile_store.yaml`)

Optional:
- 具体 JD 文件（有则更精准）
- 收件人角色（招聘负责人 / 团队 leader / HR）

## Writing Rules

- 控制在 300 字以内（LinkedIn 消息不宜过长）
- 开头提及对方公司/产品的具体了解，不要泛泛而谈
- 用 1-2 个具体项目经历说明自己的相关性
- 保留量化数据（如有）
- 结尾明确表达意图（希望了解岗位 / 希望交流）
- 不要过度谦虚也不要过度自信
- 语言匹配目标公司（国内公司用中文，外企用英文）

## Output

保存到 `outputs/misc/姓名_公司_LinkedIn外联消息.md`
