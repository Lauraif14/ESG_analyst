# ESG Mining Intelligence System

Backend MVP menggunakan Python, FastAPI, dan PostgreSQL untuk mengelola data ESG perusahaan pertambangan.

## Development

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
set DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5432/esg_mining
uvicorn app.main:app --reload --port 3000
```

API berjalan di `http://localhost:3000`. Dokumentasi interaktif tersedia di `/docs`.

Seed data awal:

```bash
python scripts/seed.py
```

Schema PostgreSQL ada di [db/001_initial_schema.sql](db/001_initial_schema.sql), sedangkan kontrak endpoint ada di [docs/api-contract.md](docs/api-contract.md).
