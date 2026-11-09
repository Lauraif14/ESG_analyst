CREATE TABLE companies (
  company_id TEXT PRIMARY KEY,
  company_name TEXT NOT NULL,
  ticker TEXT NOT NULL UNIQUE,
  commodity TEXT NOT NULL,
  country TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE esg_indicators (
  indicator_id TEXT PRIMARY KEY,
  indicator_code TEXT NOT NULL UNIQUE,
  indicator_name TEXT NOT NULL,
  dimension CHAR(1) NOT NULL CHECK (dimension IN ('E', 'S', 'G')),
  unit TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE reporting_periods (
  period_id TEXT PRIMARY KEY,
  period_year INTEGER NOT NULL CHECK (period_year BETWEEN 1900 AND 2200),
  period_label TEXT NOT NULL UNIQUE
);

CREATE TABLE source_documents (
  source_document_id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL REFERENCES companies(company_id),
  document_name TEXT NOT NULL,
  document_url TEXT,
  reporting_year INTEGER NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE esg_records (
  record_id TEXT PRIMARY KEY,
  company_id TEXT NOT NULL REFERENCES companies(company_id),
  indicator_id TEXT NOT NULL REFERENCES esg_indicators(indicator_id),
  period_id TEXT NOT NULL REFERENCES reporting_periods(period_id),
  numeric_value NUMERIC,
  text_value TEXT,
  unit TEXT,
  data_status TEXT NOT NULL CHECK (data_status IN ('REPORTED', 'NOT_DISCLOSED', 'NOT_APPLICABLE', 'PENDING_REVIEW')),
  source_document_id TEXT REFERENCES source_documents(source_document_id),
  source_page TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CHECK (numeric_value IS NOT NULL OR text_value IS NOT NULL OR data_status <> 'REPORTED')
);

CREATE INDEX esg_records_company_period_idx ON esg_records(company_id, period_id);
CREATE INDEX esg_records_indicator_idx ON esg_records(indicator_id);
