# OfferPilot Web UI Design Spec

## Goal

Product-grade Web UI for OfferPilot: Next.js frontend + FastAPI backend, clean professional style (Vercel/Linear aesthetic). Three pages: Chat, Tracker, Outputs.

## Architecture

```
web/
├── api/                        # FastAPI backend
│   ├── main.py                 # App entry, mount routers
│   ├── routes/
│   │   ├── chat.py             # SSE streaming agent chat
│   │   ├── tracker.py          # Tracker CRUD
│   │   └── files.py            # File upload/list/download/preview
│   └── requirements.txt        # fastapi, uvicorn, sse-starlette
├── frontend/                   # Next.js frontend
│   ├── app/
│   │   ├── layout.tsx          # Root layout + nav sidebar
│   │   ├── page.tsx            # Chat page (default)
│   │   ├── tracker/page.tsx    # Tracker page
│   │   └── outputs/page.tsx    # Outputs file browser
│   ├── components/
│   │   ├── chat-message.tsx    # Single message bubble (user/assistant/tool)
│   │   ├── file-upload.tsx     # Drag-and-drop file upload
│   │   ├── tracker-table.tsx   # Tracker data table with inline edit
│   │   └── file-browser.tsx    # File tree with preview/download
│   ├── lib/
│   │   └── api.ts              # API client helpers
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── next.config.ts
└── README.md                   # Setup and run instructions
```

## Pages

### 1. Chat (/)

- Left panel: conversation thread, streaming display of agent replies
- Tool calls shown inline as collapsible blocks: `🔧 read_file(path='...')` with result preview
- Right panel: file upload zone (resume/JD), uploaded files listed with remove button
- Bottom: text input + send button, disabled while agent is responding
- Uploaded files saved to project root (resume → `resume.md`, JD → `jds/` directory)

### 2. Tracker (/tracker)

- Top: follow-up reminders banner (yellow, shows count of overdue items)
- Table columns: Company, Title, Status (color badge), Applied Date, Last Update, Notes, Actions
- Status badges: discovered(gray), applied(blue), interviewing(yellow), offer(green), rejected(red), ghosted(muted)
- Inline status dropdown to update
- Filter bar: status dropdown + company search
- Sort by: date (default), company, status
- Add button opens a simple form modal

### 3. Outputs (/outputs)

- Tab bar: Resumes | Research | Interview | Pipeline | Misc
- File list per tab showing filename, size, date
- Click .md → render markdown preview in side panel
- Click .pdf → download
- Delete button per file

## API Endpoints

### Chat

```
POST /api/chat
Content-Type: application/json
Body: { "message": "string", "history": [...] }
Response: SSE stream
  event: token     data: {"content": "partial text"}
  event: tool_call data: {"name": "read_file", "args": {"path": "..."}}
  event: tool_result data: {"name": "read_file", "result": "..."}
  event: done      data: {}
```

### Tracker

```
GET    /api/tracker?status=applied&company=美团
POST   /api/tracker          Body: {url, company, title, status?, notes?}
PATCH  /api/tracker           Body: {url, status, notes?}
GET    /api/tracker/followups
```

### Files

```
POST   /api/files/upload      multipart/form-data, field: file
GET    /api/files/outputs?dir=resumes
GET    /api/files/outputs/{subdir}/{filename}   (download/preview)
DELETE /api/files/outputs/{subdir}/{filename}
```

## Style

- Tailwind CSS + shadcn/ui components
- Color: black/white/gray primary, blue accent (#2563EB)
- Font: Inter for UI, JetBrains Mono for tool call blocks
- Minimal borders, subtle shadows, generous whitespace
- Dark mode: not in v1, can add later
- Responsive: desktop-first, basic mobile support

## Integration with existing code

- Backend imports `offerpilot.graph.build_graph` directly to run the agent
- Backend imports `offerpilot.tools` functions directly for tracker operations
- No duplication of logic — web layer is a thin wrapper over existing modules
- File paths relative to REPO_ROOT (same as CLI agent)

## Deployment

- Development: `uvicorn web.api.main:app` + `cd web/frontend && npm run dev`
- Production: Next.js static export + FastAPI behind reverse proxy, or Docker compose
- Single `docker-compose.yml` at project root for one-command startup
