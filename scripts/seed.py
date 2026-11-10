import psycopg

from app.config import settings


COMPANIES = [
    ("company-vale", "PT Vale Indonesia Tbk", "INCO", "Nickel", "Indonesia"),
    ("company-antam", "PT Aneka Tambang Tbk", "ANTM", "Nickel and Gold", "Indonesia"),
    ("company-ptba", "PT Bukit Asam Tbk", "PTBA", "Coal", "Indonesia"),
]

INDICATORS = [
    ("indicator-e01", "E01", "Scope 1 GHG emissions", "E", "tCO2e"),
    ("indicator-e02", "E02", "Energy consumption", "E", "GJ"),
    ("indicator-e03", "E03", "Water withdrawal", "E", "ML"),
]


with psycopg.connect(settings.database_url) as connection:
    with connection.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO companies (company_id, company_name, ticker, commodity, country)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (company_id) DO NOTHING
            """,
            COMPANIES,
        )
        cursor.executemany(
            """
            INSERT INTO esg_indicators
                (indicator_id, indicator_code, indicator_name, dimension, unit)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (indicator_id) DO NOTHING
            """,
            INDICATORS,
        )
    connection.commit()

print("Seed data inserted.")
