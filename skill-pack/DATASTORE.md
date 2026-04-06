# Profile Datastore

## Purpose

The profile datastore is a structured personal material library. Instead of only rewriting the few bullets already on a resume, the agent can select and assemble the most relevant bullets from a larger pool based on the target JD.

## File Format

- Use YAML for human readability and easy manual editing
- Default location: project root or any path the user specifies
- Default filename: `profile_store.yaml`
- Template: `skill-pack/templates/profile_store.yaml`

## Structure Overview

```yaml
meta:           # candidate identity and contact info
experience:     # work history with tagged bullets
projects:       # standalone projects, grouped by category
skills:         # skill inventory with proficiency and evidence
education:      # degrees and schools
certifications: # professional certifications
achievements:   # awards, recognitions, notable outcomes
```

## Field Reference

### meta

| Field      | Required | Description                              |
|------------|----------|------------------------------------------|
| name       | yes      | candidate display name                   |
| name_en    | no       | English name in `Given Name Family Name` |
| email      | no       | contact email                            |
| phone      | no       | contact phone                            |
| updated    | no       | last update date                         |

### experience[]

| Field   | Required | Description                                    |
|---------|----------|------------------------------------------------|
| company | yes      | company name                                   |
| role    | yes      | job title                                      |
| start   | yes      | start date in `YYYY-MM`                        |
| end     | yes      | end date in `YYYY-MM` or `present`             |
| bullets | yes      | list of bullet entries (see below)              |

### experience[].bullets[]

| Field    | Required | Description                                              |
|----------|----------|----------------------------------------------------------|
| text     | yes      | the bullet content                                       |
| tags     | yes      | list of skill/domain tags for JD matching                |
| impact   | no       | `quantified` / `qualitative` / `context-only`            |
| variants | no       | map of alternative phrasings keyed by perspective        |

Bullets can be grouped with YAML comments (e.g. `# --- 基础体验 ---`) for readability. The agent ignores comments; ordering within a group is preserved during selection.

### projects[]

| Field    | Required | Description                                              |
|----------|----------|----------------------------------------------------------|
| name     | yes      | project name                                             |
| context  | no       | one-line background                                      |
| link     | no       | URL (e.g. GitHub repo)                                   |
| category | no       | grouping label for resume section layout                 |
| bullets  | yes      | list of bullet entries, same format as experience        |

### category

Use `category` to group projects under a shared resume section. Projects with the same `category` value are rendered together.

Example:

```yaml
projects:
  - name: "OfferPilot"
    category: "ai-engineering"
    bullets: [...]

  - name: "Jira-Power"
    category: "ai-engineering"
    bullets: [...]

  - name: "AOD 预测模型"
    bullets: [...]
```

When generating a resume, the agent groups `ai-engineering` projects under a single heading (e.g. "AI 工程化实践") and renders uncategorized projects under a default heading (e.g. "项目经历").

### link

Use `link` to attach a URL to a project. The agent includes it in the resume output next to the project name.

```yaml
  - name: "OfferPilot"
    link: "https://github.com/user/offerpilot-ai"
```

### ref (cross-reference)

Use `ref` on a bullet to indicate it is a brief mention of something described in detail elsewhere (typically a project). The value should match a project's `name`.

```yaml
experience:
  - company: "某公司"
    bullets:
      - text: "搭建基于 AI agent 的 bug 自动分析工作流，实现日志自动下载、分类与结果回传"
        tags: [ai, agent, automation]
        impact: qualitative
        ref: "Jira-Power — Bug 智能分析工作流"

projects:
  - name: "Jira-Power — Bug 智能分析工作流"
    category: "ai-engineering"
    bullets:
      - text: "配置 Jira + Playwright MCP，根据 bug 标题自动分类..."
        ...
```

Agent rules for `ref`:

- In work experience: use a concise bullet that summarizes the work naturally; do not add parenthetical cross-references like "详见 XXX" or "see project XXX"
- In the project section: use the full bullets from the referenced project to expand on details
- The reader should be able to connect the two by content, not by explicit annotation
- Never duplicate the same level of detail in both places
- If the target JD only needs a brief mention, the project section entry can be omitted
- If the target JD values the project highly, include both the brief mention and the detailed project section

### variants

Variants let you pre-write different angles of the same achievement:

```yaml
variants:
  management: "built onboarding program, cut ramp-up time by 50%"
  technical: "wrote starter kit and internal docs, reduced first-commit time"
```

The agent picks the variant that best fits the target JD. If no variant matches better than the original `text`, use `text`.

### skills[]

| Field    | Required | Description                                    |
|----------|----------|------------------------------------------------|
| name     | yes      | skill name                                     |
| level    | no       | `familiar` / `proficient` / `expert`           |
| years    | no       | years of experience                            |
| evidence | no       | list of concrete uses tied to bullets/projects  |

### impact priority

When multiple bullets match a JD requirement equally well, prefer:

1. `quantified` — has numbers, percentages, scale
2. `qualitative` — clear outcome without hard numbers
3. `context-only` — describes responsibility without outcome

## Tagging Rules

- Use lowercase tags
- Prefer tags that align with keys in `data/skill_aliases.zh-en.json`
- A bullet can have multiple tags
- Tags enable the JD matching step; bullets without tags are deprioritized during selection

## How the Agent Uses the Datastore

1. Parse the JD to extract requirements and keywords
2. Normalize keywords using `data/skill_aliases.zh-en.json`
3. Match normalized keywords against bullet tags
4. Rank matched bullets by relevance and impact level
5. If a bullet has a matching variant for the target role type, use the variant
6. Assemble top bullets into resume sections
7. Polish phrasing per `PROMPTS.md` rules

## Quick Start

### 1. Create your datastore

```bash
cp skill-pack/templates/profile_store.yaml profile_store.yaml
```

See `skill-pack/examples/profile_store_example.yaml` for a filled-in reference.

### 2. Fill in your materials

- Write as many bullets as you can for each work experience and project
- Every bullet must have `tags` — this is how the agent matches against JDs
- Mark `impact` when possible (`quantified` > `qualitative` > `context-only`)
- Add `variants` when the same achievement can be told from different angles (e.g. management vs technical)
- Link skills to concrete evidence so the agent can back up claims

You do not need to be concise here. The datastore is your full material pool, not a finished resume. The more you put in, the more the agent can select from.

### 3. Keep it out of git

```bash
echo "profile_store.yaml" >> .git/info/exclude
```

### 4. Generate a targeted resume

Tell the agent:

> 请根据 profile_store.yaml 和这个 JD，生成一份定向简历

The agent will:

1. Parse the JD to extract requirements and keywords
2. Match keywords against your bullet tags
3. Pick the most relevant bullets, ranked by impact
4. Choose the best variant for each bullet when available
5. Assemble and polish into a targeted resume

Different JDs produce different bullet selections from the same datastore.

### 5. Maintain over time

- After finishing a project or getting a result, add a bullet to the datastore
- Focus on `text` + `tags`; formatting can be rough
- The more you accumulate, the better the agent can tailor future resumes

## When the Datastore Is Not Provided

If the user does not provide a profile datastore, the workflow falls back to the existing behavior: rewrite and optimize the source resume directly. No datastore is required.

## Privacy

- The profile datastore contains personal career details; treat it as private by default
- Do not commit it to version control unless the user explicitly asks
- The template and example files use anonymous placeholder data
