# API Contract MVP

Base URL: `/api/v1`

## Conventions

- Successful responses use `{ "data": ... }`.
- Collection responses include `{ "data": [], "meta": { "total": 0 } }`.
- Errors use `{ "error": { "code": "...", "message": "...", "details": [] } }`.
- Authentication and role middleware are reserved for the next iteration; the MVP route handlers currently expose the contract with in-memory data.

## Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Service health check |
| GET | `/companies` | List mining companies |
| GET | `/companies/:id` | Get one company |
| GET | `/indicators?dimension=E` | List ESG indicators |
| POST | `/esg-records` | Create an ESG data record |
| GET | `/esg-records?companyId=&period=` | Filter ESG records |
| GET | `/dashboard/summary?companyId=&period=` | Get dashboard summary |

## `POST /esg-records`

Required fields:

```json
{
  "id": "record-001",
  "companyId": "company-vale",
  "indicatorId": "indicator-e01",
  "period": "2024",
  "numericValue": 1415596.83,
  "textValue": null,
  "unit": "tCO2e",
  "dataStatus": "REPORTED",
  "sourceDocument": "Sustainability Report 2024, p. 80"
}
```

Business rules:

1. `companyId` must reference an existing company.
2. `indicatorId` must reference an existing indicator.
3. `period` must use `YYYY` format.
4. `dataStatus` distinguishes unavailable data from reported data; missing data must not be interpreted as zero.
5. Every reported value should eventually include a traceable source document and page reference.

## Next implementation steps

1. Add PostgreSQL persistence and migrations.
2. Replace the in-memory store with repositories backed by the PostgreSQL schema.
3. Add authentication, role-based authorization, and review workflow.
4. Add source documents and validation endpoints.
5. Add calculation endpoints only after indicator formulas and production data are confirmed.
