CREATE TABLE IF NOT EXISTS dim_firm (
  firm_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  hq_country TEXT,
  strategy TEXT,
  aum_estimate_usd REAL
);

CREATE TABLE IF NOT EXISTS dim_fund (
  fund_id TEXT PRIMARY KEY,
  firm_id TEXT NOT NULL REFERENCES dim_firm(firm_id),
  fund_name TEXT NOT NULL,
  fund_type TEXT,
  vintage_year INTEGER,
  target_size_usd REAL,
  status TEXT
);

CREATE TABLE IF NOT EXISTS dim_geo (
  geo_id INTEGER PRIMARY KEY,
  country TEXT,
  region TEXT
);

CREATE TABLE IF NOT EXISTS dim_sector (
  sector_id INTEGER PRIMARY KEY,
  sector TEXT,
  subsector TEXT
);

CREATE TABLE IF NOT EXISTS fact_transaction (
  tx_id TEXT PRIMARY KEY,
  fund_id TEXT REFERENCES dim_fund(fund_id),
  firm_id TEXT NOT NULL REFERENCES dim_firm(firm_id),
  date TEXT NOT NULL,
  sector_id INTEGER REFERENCES dim_sector(sector_id),
  geo_id INTEGER REFERENCES dim_geo(geo_id),
  stage TEXT,
  amount_usd REAL CHECK (amount_usd >= 0),
  source TEXT,
  confidence_score REAL
);

CREATE TABLE IF NOT EXISTS fact_outreach (
  outreach_id TEXT PRIMARY KEY,
  firm_id TEXT NOT NULL REFERENCES dim_firm(firm_id),
  contact_role TEXT,
  date TEXT,
  channel TEXT,
  outcome TEXT,
  notes TEXT
);

