## Backend:
- Set up supabase auth with Google auth to access YouTube data
- Add GCP client scopes
- Remove IAM permissions dependency for service account (`credentials/`, `credentials/client_secret.json`, `credentials/service_account.json`)

## Database:
- Set up supabase project and database schema
- Create queries and mutations for core functionality in:
  - `db/supabase/mutations/index.ts`
  - `db/supabase/queries/index.ts`

## Project Setup:
- Decide between pnpm workspaces vs turbo repo for monorepo setup
- Configure exports and TypeScript configs for chosen solution