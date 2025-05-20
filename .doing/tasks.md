Below is an **action-by-action checklist** you can paste straight into an issue tracker.
Every task is atomic, starts unchecked `[ ]`, and contains all the context a teammate needs to execute or verify it.

````
# ─────────────────────────────
# 🗃  A. Remove Alembic traces
# ─────────────────────────────
[X] Delete directory **apps/core/alembic/** and commit.
[X] Delete file **alembic.ini** at repo root.
[X] In **pyproject.toml** remove the entire `[tool.poetry.dependencies] alembic = "*"` (or similar) stanza.
[ ] Run `uv pip uninstall alembic` (or `pip uninstall`) and update the lockfile with `uv pip compile`.

# ─────────────────────────────
# 📦  B. Create migration folder
# ─────────────────────────────
[X] Make directory **packages/db/migrations/** (add to git).
[ ] Add `.keep` plus a README that states:
    “Raw PostgreSQL files - executed top-down.
     Naming: `YYYYMMDDHHMMSS_<description>.sql` (UTC).”
[ ] Copy the existing SQL migration found at *supabase/migrations/* (turn1file14) into this new folder, rename using the timestamp format.

# ─────────────────────────────
# ⚙️  C. Root scripts for DB workflow
# ─────────────────────────────
[ ] Add to **package.json** (repo root):

```jsonc
"scripts": {
  "db:migrate": "pnpm dlx supabase db push",          // or `psql -f packages/db/migrations/*.sql`
  "db:codegen": "sqlacodegen $DATABASE_URL --generator asyncpg --outfile apps/core/app/db/models.py",
  "db:refresh": "pnpm run db:migrate && pnpm run db:codegen"
}
````

\[ ] Commit and verify `pnpm run db:refresh` completes on a fresh clone.

# ─────────────────────────────

# 🧬  D. Regenerate models → schemas

# ─────────────────────────────

\[ ] Install codegen tools once:
`uv pip install sqlacodegen pydantic-sqlalchemy` (and lock).
\[ ] Run `pnpm run db:codegen` and inspect **apps/core/app/db/models.py** for correctness.
\[ ] Replace manual Pydantic models in **apps/core/app/db/schemas.py** with:

```python
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from .models import YourOrmModel  # repeat per model

YourOrmModelSchema = sqlalchemy_to_pydantic(YourOrmModel, exclude=["created_at", "updated_at"])
```

# ─────────────────────────────

# 🛠  E. Harmonise bin scripts

# ─────────────────────────────

\[ ] Edit **apps/core/bin/dev.sh** ⇒

```bash
#!/usr/bin/env bash
uv pip sync                      # ensure deps
uvicorn apps.core.main:app --reload --port 8000
```

\[ ] Prepend every script in **apps/core/bin/** with `#!/usr/bin/env bash` and `set -euo pipefail`.
\[ ] At repo root, add shortcuts to **package.json**:

```jsonc
"scripts": {
  "dev": "bash apps/core/bin/dev.sh",
  "lint": "bash apps/core/bin/lint.sh",
  "format": "bash apps/core/bin/format.sh",
  "typecheck": "bash apps/core/bin/typecheck.sh",
  "test": "bash apps/core/bin/test.sh"
}
```

# ─────────────────────────────

# 🌳  F. Delete duplicate old models

# ─────────────────────────────

\[ ] Grep repo for `class .*Base(` outside **apps/core/app/db/models.py** and remove legacy ORM classes.
\[ ] Update all imports (`from apps.core.models` → `from apps.core.app.db.models`) via IDE-wide replace.

# ─────────────────────────────

# 🔐  G. Standardise env handling

# ─────────────────────────────

\[ ] Ensure **apps/core/app/db/engine.py** reads `DATABASE_URL` from `python-dotenv`:

```python
from dotenv import load_dotenv; load_dotenv()
```

\[ ] Add sample **.env.example** with `DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db`.

# ─────────────────────────────

# 🚦  H. CI tweaks (optional but recommended)

# ─────────────────────────────

\[ ] Update GitHub Actions workflow to run:

```bash
pnpm install --frozen-lockfile
pnpm run db:codegen              # verifies models up-to-date
pnpm run lint && pnpm run test
```

# ─────────────────────────────

# 📚  I. Developer docs refresh

# ─────────────────────────────

\[ ] Replace Alembic instructions in **README.md** with:

```
## Local DB workflow
pnpm run db:migrate   # apply SQL
pnpm run db:codegen   # regenerate ORM
pnpm run dev          # boot FastAPI
```

\[ ] Add a “Writing migrations” section linking to `packages/db/migrations/README.md`.

# ─────────────────────────────

# ✅  Done-when

# ─────────────────────────────

• `pnpm run dev` works from repo root.
• A teammate can pull, run `pnpm run db:refresh`, and start coding without CD-ing or touching Alembic.

```
```
