{
  "name": "echo",
  "version": "1.0.0",
  "scripts": {
    "start": "node index.js",
    "test": "jest",
    "db:migrate": "pnpm dlx supabase db push",
    "db:codegen": "sqlacodegen $DATABASE_URL --generator asyncpg --outfile apps/core/app/db/models.py",
    "db:refresh": "pnpm run db:migrate && pnpm run db:codegen"
  },
  "dependencies": {
    "express": "^4.17.1"
  }
}
