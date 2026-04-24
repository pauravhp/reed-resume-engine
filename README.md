# R.E.E.D — Resume Engine

A job assistant that turns a pasted job description into a tailored, recruiter-ready resume, answers application questions from your real profile, and tracks every application on a dashboard.

**Live:** [reed-resume-engine.vercel.app](https://reed-resume-engine.vercel.app)

---

## What it does

1. **Tailored resume generation** — paste a job description, get back a LaTeX resume that picks the most relevant bullets from your saved work history, picks your two most relevant projects, reorders your skills to front-load JD-matched tech, and writes a 2–3 sentence summary. Also returns a 0–100 match score with written reasoning.
2. **Tailored application answers** — paste a JD + an application question (e.g. "Why are you a good fit?"), get back a 3–5 sentence personalised answer grounded in your bio, experiences, and projects — with explicit guardrails against fabricating credentials.
3. **Application dashboard** — every generated resume creates an application row with auto-extracted company + role (if the JD names them), inline-editable status (`not_applied`, `applied`, `response_received`, `interview`, `rejected`, `offer`) and notes.
4. **Profile banks** — structured storage of bio, phone, LinkedIn, GitHub, experiences, projects, skills, education, leadership. Designed as the data source a future browser autofill extension would read.

---

## Architecture

```
Browser ──► Vercel (React SPA)
            │
            └─► HTTPS ──► Caddy (VPS) ──► FastAPI (Docker) ──► Neon (serverless Postgres)
                                           │
                                           └─► Groq API (llama-3.3-70b)
```

- **Frontend**: React 19 + Vite + TanStack Router + TanStack Query, shadcn/ui on Tailwind v4, auto-generated TS client from the backend OpenAPI schema. Hosted on Vercel.
- **Backend**: FastAPI (Python 3.10) + SQLModel + Alembic, running under uvicorn in Docker Compose on a Hetzner CPX11. Caddy handles TLS via Let's Encrypt.
- **Database**: Neon (serverless Postgres), `psycopg3` driver, `PGSSLMODE=require`.
- **LLM**: Groq (`llama-3.3-70b-versatile`). Users bring their own API key; the key is **Fernet-encrypted per-user at rest** (Fernet key derived from the server `SECRET_KEY` via SHA-256). Keys are decrypted only for the duration of a generation request and never logged.
- **Auth**: JWT via the FastAPI template's built-in login flow.

### Three parallel Groq calls per resume generation

1. **Call A — Summary**: writes the opening 2–3 sentences from bio context + JD, with explicit no-hallucination guardrails (won't invent degrees, schools, or seniority).
2. **Call B — Experiences**: selects which existing bullets from each work experience to keep for this JD (never rewrites bullets — zero fabrication risk), computes the match score + reasoning, decides whether to include coursework, and extracts company + role_title from the JD if literally present.
3. **Call C — Projects & Skills**: picks the 2 most relevant projects and reorders each skill category to front-load JD-matched tech.

All three run concurrently via `asyncio.gather` — full generation typically completes in 6–12 seconds.

---

## Local development

```bash
# From repo root
cp .env.example .env
# Fill in Neon credentials, a generated SECRET_KEY, FIRST_SUPERUSER creds, etc.
# Add PGSSLMODE=require (not in the template's .env.example)

docker compose up --build
```

Then:

- Frontend dev server: http://localhost:5173
- Backend API docs (Swagger): http://localhost:8000/docs
- Adminer: http://localhost:8080
- Mailcatcher: http://localhost:1080

### Regenerating the frontend API client after backend changes

```bash
docker compose up -d backend
cd frontend && npm run generate-client
```

### Alembic migrations

Always run inside the backend container:

```bash
docker compose exec backend alembic revision --autogenerate -m "describe_change"
docker compose exec backend alembic upgrade head
```

Migration files live at `backend/app/alembic/versions/` (**not** `backend/alembic/versions/`).

---

## Production deployment

### Backend (Hetzner VPS)

Production compose file: `docker-compose.prod.yml`. Two services only:

- `prestart`: runs `alembic upgrade head` + seeds superuser. Exits 0.
- `backend`: uvicorn on `127.0.0.1:8000`. Caddy on the host proxies `https://5-78-200-61.nip.io` → `localhost:8000` with auto-TLS via Let's Encrypt.

```bash
# On VPS
cd ~/reed-resume-engine
git pull origin main
docker compose -f docker-compose.prod.yml up --build -d
```

### Frontend (Vercel)

```bash
cd frontend
vercel --prod
```

`VITE_API_URL` is set in Vercel's Production env var (baked into the bundle at build time).

### Deployment notes

- `.env` on the VPS is never committed — generate a fresh `SECRET_KEY` in production; reusing the dev key would let dev Fernet tokens decrypt prod API keys.
- SPA rewrite rule lives in `frontend/vercel.json` — required so deep-link refreshes don't 404.
- The `application` table's `company` and `role_title` columns are populated by Call B's JD extraction (null if the JD doesn't name them explicitly). Dashboard allows inline-edit as a fallback.

---

## Repository layout

```
reed-resume-engine/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # one file per route group
│   │   ├── alembic/versions/  # migrations
│   │   ├── core/              # config, security, db engine
│   │   ├── models.py          # all SQLModel tables + schemas
│   │   └── templates/         # LaTeX Jinja2 template
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── routes/            # TanStack Router file-based routes
│   │   ├── features/          # feature-scoped components
│   │   ├── hooks/             # react-query hooks
│   │   ├── components/        # shared UI
│   │   └── client/            # auto-generated OpenAPI client — never hand-edit
│   └── vercel.json
├── docker-compose.yml         # dev
├── docker-compose.prod.yml    # prod
└── .env.example
```

---

## Credits

Built on top of the [full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) by Sebastián Ramírez, retheming and rebuilding around the resume-engine domain.
