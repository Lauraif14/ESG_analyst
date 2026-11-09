# ESG Mining Intelligence System

Backend MVP for managing and analyzing Environmental, Social, and Governance data for mining companies.

## Development

```bash
npm install
npm run dev
```

The API runs on `http://localhost:3000`.

Build and type-check:

```bash
npm run build
npm run typecheck
```

The current MVP uses in-memory data. See [docs/api-contract.md](docs/api-contract.md) for the API contract and next implementation steps.

## PostgreSQL setup

Copy `.env.example` to `.env`, set `DATABASE_URL`, and run the migration with:

```bash
npm run db:migrate
```

The server currently starts in in-memory mode when `DATABASE_URL` is not set. The PostgreSQL schema is prepared in `db/001_initial_schema.sql`; route-level repository migration is the next step.
