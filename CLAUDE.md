# CLAUDE.md - Project Context for Claude Code

## What is this project?

FastAPI backend for "Parabolic Lab", a Mexican college educational platform for projectile motion experiments. It provides REST APIs for managing institutions, users (students, teachers, admins), classrooms, learning scenarios, and interactive activities.

## Quick Reference

- **Package manager**: `uv` (dependencies in `pyproject.toml`, lockfile in `uv.lock`)
- **Install deps**: `uv sync`
- **Add a dependency**: `uv add <package>` (or `uv add --dev <package>` for dev-only)
- **Run server**: `uv run uvicorn app.main:app --reload`
- **Run migrations**: `uv run alembic upgrade head`
- **Generate migration**: `uv run alembic revision --autogenerate -m "description"`
- **Lint**: `uv run ruff check app/` (auto-fix with `--fix`)
- **Format**: `uv run ruff format app/`
- **API docs**: `http://localhost:8000/docs`
- **Health check**: `GET /` returns `{"status": "ok"}`
- **API prefix**: `/api/v1`

## Tooling

- **uv** - Package manager (replaces pip + venv). Virtual env at `.venv/`
- **ruff** - Linter + formatter (replaces black + isort + flake8). Config in `pyproject.toml`
- **Format on save** configured in `.vscode/settings.json` (requires Ruff VS Code extension)

## Architecture

### Stack

- FastAPI (async), SQLAlchemy 2.0 (async + asyncpg), Alembic, Pydantic v2
- Neon PostgreSQL (project: `autumn-thunder-43526624`, branches: `main`, `development`)
- Stack Auth for authentication (email + password, JWT with ES256)

### Project Layout

```
app/
├── main.py           # App factory, CORS, 13 routers under /api/v1
├── config.py         # pydantic-settings loading from .env
├── database.py       # AsyncEngine, async_sessionmaker, Base
├── dependencies.py   # get_db(), get_current_user() (JWT via x-stack-access-token header)
├── auth/stack_auth.py  # Stack Auth API client + JWT verification
├── models/           # 12 SQLAlchemy models (1 per table, Spanish column names)
├── schemas/          # Pydantic schemas (1 per entity + auth schemas)
└── routes/           # 13 route files (1 per resource, SRP)
```

### Authentication Flow (critical to understand)

1. **Stack Auth** handles passwords/JWTs externally
2. After creating a user in Stack Auth, we **manually insert** their JSON into `neon_auth.users_sync(raw_json)`
3. The `id` column in `users_sync` is a **generated column**: `raw_json->>'id'`
4. FK constraint: `usuario.authid -> neon_auth.users_sync.id ON DELETE CASCADE`
5. This manual sync replaced the broken legacy Neon Auth auto-sync (which is deprecated)

The helper function `_sync_user_to_neon_auth()` in `app/routes/auth.py` handles this.

### neon_auth.users_sync Table

- **Only writable column**: `raw_json` (JSONB) - expects Stack Auth user object format
- **Generated columns**: `id` (from `raw_json->>'id'`), `email` (from `raw_json->>'primary_email'`), `name` (from `raw_json->>'display_name'`), `created_at` (from `raw_json->>'signed_up_at_millis'`)
- Cannot INSERT directly into generated columns - must provide `raw_json` only

### User Role Hierarchy

```
Institucion (1) -> (N) Usuario -> (0..1) Alumno | Docente | Admin
```

- `usuario.tipousuario` CHECK: `alumno | docente | admin`
- Each role has a separate table with a unique FK to `usuario.idusuario`
- Institution registration creates both the institution and its admin atomically

## Conventions

- **All attribute names are in Spanish**, matching the database schema exactly
- Column names are all lowercase: `idusuario`, `authid`, `apellidopaterno`, `tipousuario`, etc.
- All PKs are UUIDs with `gen_random_uuid()` server default
- Route files follow SRP: one file per resource in `app/routes/`
- Schema files mirror model files in `app/schemas/`
- Protected endpoints use `Depends(get_current_user)` which validates the `x-stack-access-token` header

## Important Gotchas

1. **Stack Auth DELETE requires JSON body**: Use `client.request("DELETE", url, content="{}")`, not `client.delete(url)` - see `app/auth/stack_auth.py:delete_stack_user`
2. **Alembic excludes `fk_usuario_auth`**: The `include_object` filter in `alembic/env.py` skips this FK constraint since it references `neon_auth.users_sync` (managed by Neon, not our models)
3. **Don't model `neon_auth.users_sync` in SQLAlchemy**: It's in a separate schema managed by Neon Auth. Interact with it via raw SQL (`text()`)
4. **JSONB fields**: `escenario.configuracionescenario` and `interaccionescenario.datosinteraccion` have GIN indexes
5. **Composite PKs**: `alumnoensalon` (idalumno + idsalon) and `escenarioenactividad` (idescenario + idactividad)

## Database

- **Neon project**: `autumn-thunder-43526624` (tiro-parabolico)
- **Branches**: `main` (primary), `development` (for dev work)
- **Development branch ID**: `br-flat-tree-adhlm4cd`
- **12 domain tables** + `alembic_version` + `neon_auth.users_sync`
- Connection uses SSL (`?ssl=require`)

## Stack Auth

- **Project ID**: `60e4b969-ff4d-4917-b67e-3ea9d6e03655`
- **Base URL**: `https://api.stack-auth.com/api/v1`
- **JWKS**: `{BASE_URL}/projects/{PROJECT_ID}/.well-known/jwks.json`
- **JWT algorithm**: ES256, audience = project ID
- Server-side calls require headers: `x-stack-access-type: server`, `x-stack-project-id`, `x-stack-secret-server-key`
