from collections.abc import Generator
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from psycopg import Connection

from app.database import get_connection

app = FastAPI(
    title="ESG Mining Intelligence System",
    version="0.2.0",
    description="MVP API for structured ESG data from mining companies.",
)


def connection() -> Generator[Connection, None, None]:
    yield from get_connection()


class EsgRecordCreate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    company_id: str = Field(alias="companyId")
    indicator_id: str = Field(alias="indicatorId")
    period: str = Field(pattern=r"^\d{4}$")
    numeric_value: float | None = Field(default=None, alias="numericValue")
    text_value: str | None = Field(default=None, alias="textValue")
    unit: str | None = None
    data_status: str = Field(alias="dataStatus")
    source_document: str | None = Field(default=None, alias="sourceDocument")
    source_page: str | None = Field(default=None, alias="sourcePage")


@app.get("/api/v1/health")
def health(db: Connection = Depends(connection)) -> dict[str, Any]:
    with db.cursor() as cursor:
        cursor.execute("SELECT 1 AS connection_test, current_database() AS database_name")
        result = cursor.fetchone()
    return {"status": "ok", "database": result}


@app.get("/api/v1/companies")
def list_companies(db: Connection = Depends(connection)) -> dict[str, Any]:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT company_id AS id, company_name AS name, ticker, commodity, country
            FROM companies
            ORDER BY company_name
            """
        )
        data = cursor.fetchall()
    return {"data": data, "meta": {"total": len(data)}}


@app.get("/api/v1/companies/{company_id}")
def get_company(company_id: str, db: Connection = Depends(connection)) -> dict[str, Any]:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT company_id AS id, company_name AS name, ticker, commodity, country
            FROM companies WHERE company_id = %s
            """,
            (company_id,),
        )
        company = cursor.fetchone()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"data": company}


@app.get("/api/v1/indicators")
def list_indicators(
    dimension: str | None = Query(default=None, pattern="^[ESG]$"),
    db: Connection = Depends(connection),
) -> dict[str, Any]:
    query = """
        SELECT indicator_id AS id, indicator_code AS code, indicator_name AS name,
               dimension, unit
        FROM esg_indicators
    """
    parameters: tuple[str, ...] = ()
    if dimension:
        query += " WHERE dimension = %s"
        parameters = (dimension,)
    query += " ORDER BY indicator_code"
    with db.cursor() as cursor:
        cursor.execute(query, parameters)
        data = cursor.fetchall()
    return {"data": data, "meta": {"total": len(data)}}


@app.post("/api/v1/esg-records", status_code=status.HTTP_201_CREATED)
def create_esg_record(payload: EsgRecordCreate, db: Connection = Depends(connection)) -> dict[str, Any]:
    if payload.data_status not in {"REPORTED", "NOT_DISCLOSED", "NOT_APPLICABLE", "PENDING_REVIEW"}:
        raise HTTPException(status_code=400, detail="Invalid dataStatus")

    year = int(payload.period)
    period_id = f"period-{payload.period}"
    source_document_id = f"source-{payload.id}" if payload.source_document else None

    with db.cursor() as cursor:
        cursor.execute("SELECT 1 FROM companies WHERE company_id = %s", (payload.company_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=400, detail="companyId does not exist")
        cursor.execute("SELECT 1 FROM esg_indicators WHERE indicator_id = %s", (payload.indicator_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=400, detail="indicatorId does not exist")
        cursor.execute(
            """
            INSERT INTO reporting_periods (period_id, period_year, period_label)
            VALUES (%s, %s, %s)
            ON CONFLICT (period_id) DO NOTHING
            """,
            (period_id, year, payload.period),
        )
        if source_document_id:
            cursor.execute(
                """
                INSERT INTO source_documents
                    (source_document_id, company_id, document_name, reporting_year)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (source_document_id) DO NOTHING
                """,
                (source_document_id, payload.company_id, payload.source_document, year),
            )
        cursor.execute(
            """
            INSERT INTO esg_records
                (record_id, company_id, indicator_id, period_id, numeric_value,
                 text_value, unit, data_status, source_document_id, source_page)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING record_id AS id, company_id, indicator_id, period_id,
                      numeric_value, text_value, unit, data_status,
                      source_document_id, source_page
            """,
            (
                payload.id,
                payload.company_id,
                payload.indicator_id,
                period_id,
                payload.numeric_value,
                payload.text_value,
                payload.unit,
                payload.data_status,
                source_document_id,
                payload.source_page,
            ),
        )
        record = cursor.fetchone()
    return {"data": record}


@app.get("/api/v1/esg-records")
def list_esg_records(
    company_id: str | None = Query(default=None, alias="companyId"),
    period: str | None = None,
    db: Connection = Depends(connection),
) -> dict[str, Any]:
    query = """
        SELECT record_id AS id, company_id AS "companyId", indicator_id AS "indicatorId",
               rp.period_label AS period, numeric_value AS "numericValue",
               text_value AS "textValue", er.unit, data_status AS "dataStatus",
               source_document_id AS "sourceDocumentId", source_page AS "sourcePage"
        FROM esg_records er
        JOIN reporting_periods rp ON rp.period_id = er.period_id
        WHERE (%s IS NULL OR er.company_id = %s)
          AND (%s IS NULL OR rp.period_label = %s)
        ORDER BY er.created_at DESC
    """
    with db.cursor() as cursor:
        cursor.execute(query, (company_id, company_id, period, period))
        data = cursor.fetchall()
    return {"data": data, "meta": {"total": len(data)}}


@app.get("/api/v1/dashboard/summary")
def dashboard_summary(
    company_id: str | None = Query(default=None, alias="companyId"),
    period: str | None = None,
    db: Connection = Depends(connection),
) -> dict[str, Any]:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT
              (SELECT COUNT(*) FROM companies) AS companies,
              COUNT(er.record_id) AS records,
              COUNT(er.record_id) FILTER (WHERE er.data_status = 'REPORTED') AS reported_records
            FROM esg_records er
            LEFT JOIN reporting_periods rp ON rp.period_id = er.period_id
            WHERE (%s IS NULL OR er.company_id = %s)
              AND (%s IS NULL OR rp.period_label = %s)
            """,
            (company_id, company_id, period, period),
        )
        summary = cursor.fetchone()
    return {"data": summary}
