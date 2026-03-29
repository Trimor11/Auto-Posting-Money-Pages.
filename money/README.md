# Auto-Posting Money Pages

Auto-Posting Money Pages is a production-ready FastAPI platform that automatically turns keyword ideas into SEO-friendly monetizable content, schedules drafts for publication, and serves them on a responsive frontend with ad/affiliate placeholders, sitemap automation, and an authenticated admin dashboard.

## Highlights

- **Automated pipeline:** keyword intake, AI templated generation, quality gates, scheduling, publishing, internal linking, and sitemap refreshes powered by APScheduler jobs.
- **Content intelligence:** reusable prompt templates per page type, OpenAI-compatible provider abstraction with a safe local fallback, structured JSON responses, schema markup, FAQs, related topics, and freshness timestamps.
- **Quality + safety:** duplicate detection, minimum word thresholds, banned phrase screening, slug/title uniqueness, draft/publish workflow, status tracking for keywords, pages, generation jobs, and publish jobs.
- **Admin operations:** secure login, dashboard metrics, keyword management (manual + CSV import), one-click generation/regeneration, draft preview, bulk publish, settings for ad snippets / affiliate blocks / quotas, and job log visibility.
- **Monetization + SEO ready:** Tailwind-based responsive site, ad placeholders (top/mid/bottom), affiliate block slot, canonical URLs, robots.txt, XML sitemap cache, RSS feed, breadcrumbs, category hubs, search, static policy pages, and analytics snippet injection.
- **Deployment friendly:** Dockerfile, docker-compose, Alembic migrations, .env configuration, seed script with 20+ realistic keywords/pages, and Render/Railway/VPS deployment notes.

## Tech Stack

- **Backend:** FastAPI + Uvicorn, SQLAlchemy ORM, Alembic migrations, SQLite (default) with easy PostgreSQL swap
- **Automation:** APScheduler jobs for generation, publishing, stale-page audits, and link refreshes
- **AI layer:** OpenAI SDK (Responses API) via pluggable provider + local rule-based fallback
- **Frontend:** Jinja templates + Tailwind CDN, responsive components, ad macros
- **Auth/Security:** Session cookies (itsdangerous), bcrypt hashing, rate-limited search, CSRF-safe POST forms

## Project Layout

```
app/
  main.py                # FastAPI entrypoint + scheduler bootstrap + 404 handler
  config.py              # Pydantic settings (env, AI, scheduler, monetization)
  database.py            # SQLAlchemy engine/session helpers
  models/                # ORM models for users, keywords, pages, jobs, settings, links, logs
  services/              # AI provider, content engine, quality checks, keyword manager, publisher, scheduler, linking, analytics
  routers/               # Public site, admin UI, auth, JSON API
  templates/             # Tailwind-powered public + admin Jinja templates
  static/                # CSS/JS assets
  seed_data.py           # Sample categories, keywords, and starter pages
alembic/                 # Migration env + initial schema revision
requirements.txt         # Runtime + tooling dependencies
Dockerfile, docker-compose.yml, Makefile, README.md, .env.example, data/sample_keywords.csv
```

## Quick Start

1. **Clone & install deps**
   ```bash
   git clone <repo> money && cd money
   python -m venv .venv
   .\\.venv\\Scripts\\activate   # Windows
   pip install -r requirements.txt
   ```
2. **Configure environment**
   ```bash
   cp .env.example .env  # use `copy` on Windows
   # Edit SITE_URL, ADMIN_EMAIL/PASSWORD, AI credentials, etc.
   ```
3. **Initialize database**
   ```bash
   alembic upgrade head
   python -m app.seed_data  # loads categories, keywords, and sample pages
   ```
4. **Run locally**
   ```bash
   uvicorn app.main:app --reload
   ```
   - Public site: http://localhost:8000/
   - Admin login: http://localhost:8000/auth/login (default `admin@example.com` / `admin123`)

## Scheduler & Automation

- APScheduler starts with the FastAPI app (see `app/background.py`).
- Jobs run daily:
  - `generate_batch`: creates drafts for queued keywords (respects DB-stored quota + dry-run flag).
  - `publish_batch`: publishes eligible drafts, processes queued publish jobs, rebuilds the sitemap cache.
  - `mark_stale_pages`: flags older published pages for manual refresh.
  - `refresh_links`: rebuilds internal links for top published pages.
- Toggle automation via env vars (`SCHEDULER_ENABLED`, `DRY_RUN_MODE`) and adjust quotas inside **Admin -> Settings** (values stored in DB and picked up by jobs in real time).

## Admin Workflow

1. **Ideas** - manually add keywords or paste CSV (headers in `data/sample_keywords.csv`).
2. **Queue** - mark important keywords as queued or bulk-queue via CSV import.
3. **Generate** - click "Generate" beside a keyword or let the scheduler handle it. Regenerate drafts from the page screen.
4. **Review** - use the preview pane, quality badges, and FAQ view before publishing.
5. **Publish** - publish immediately, bulk publish via dashboard button, or allow the scheduler to release drafts daily.
6. **Settings** - manage ad blocks, affiliate markup, analytics snippet, and automation quotas without redeploying.

## AI Provider Setup

- `AI_PROVIDER`: `openai` (default) uses the Responses API with the configured `AI_MODEL` and `AI_TEMPERATURE`.
- `AI_MOCK_MODE=True` keeps everything offline using the `LocalAIGenerator`-great for demos/tests.
- Add other providers by implementing `AIProvider` in `app/services/ai_provider.py` and updating `load_provider`.

## CSV Import/Export

- Bulk import via **Admin -> Keywords** (textarea). Required column: `phrase`. Optional: `status`, `search_intent`, `priority_score`, `country`, `language`, `source`, `topic_family`.
- Export up to 1000 keywords via `/api/keywords/export` (requires admin auth cookie).

## Monetization & Analytics

- Template macro `partials/ad_slot.html` powers responsive ad placeholders for top/mid/bottom sections.
- Affiliate HTML block and analytics snippet are stored in the DB so you can paste code without redeploying.

## Deployment

### Docker (local or VPS)
```bash
docker compose up --build
```
Expose port 8000 (or remap via compose). For production, point your reverse proxy (NGINX, Caddy) at the container and serve via HTTPS.

### Render
1. Create a new **Web Service**  -> "Deploy from GitHub".
2. Select the repo and keep the Build Command empty so Render auto-detects the Dockerfile.
3. Use the **Dockerfile** build mode (recommended) or `pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port $PORT` for native deployments.
4. Add environment variables from `.env`. Ensure `DATABASE_URL` points to a managed PostgreSQL instance.

### Railway
1. Create a new project  -> "Deploy from Repo".
2. Choose the Dockerfile service (or create a Python service with the same uvicorn command above).
3. Provision a PostgreSQL plugin, grab its connection string, and set `DATABASE_URL` accordingly.
4. Add secrets for AI keys, `SITE_URL`, admin credentials, etc. Deploy - the scheduler launches automatically.

### Bare VPS
- Install Python 3.11, PostgreSQL, and Nginx.
- Clone the repo, configure `.env`, install requirements in a virtualenv.
- Run migrations (`alembic upgrade head`) and seed data.
- Use `uvicorn` behind `systemd` or run `gunicorn -k uvicorn.workers.UvicornWorker app.main:app`.
- Terminate SSL at Nginx; proxy `/` to the ASGI app, serve `/static` directly for best performance.

## Useful Commands

| Task | Command |
| --- | --- |
| Install deps | `make install` |
| Run dev server | `make dev` |
| Seed starter data | `make seed` |
| Run new migration | `make migrate` |
| Upgrade DB | `make upgrade` |
| Docker (build + run) | `make docker` |

## Default Credentials

- Email: `admin@example.com`
- Password: `admin123`
(Override via environment variables before first startup.)

## Next Steps

- Connect a PostgreSQL database for production scale.
- Wire up real AI providers (OpenAI, Azure, etc.) and tune prompt templates per niche.
- Drop in AdSense/affiliate snippets via the settings screen.
- Configure a cron monitor (e.g., Render Cron or external uptime checks) if APScheduler should be supervised.
- Add HTTPS + CDN caching for better Core Web Vitals.

Enjoy building an auto-publishing SEO machine!
