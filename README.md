# Alternative Assets Market Tracker

An end-to-end data engineering and analytics project simulating the kind of institutional-grade intelligence platforms used by firms like Preqin and PitchBook. Built to demonstrate production-style ETL pipeline design, data quality monitoring, and BI-ready output for the alternative assets industry.

---

## What This Project Does

The tracker ingests raw data on private equity firms, funds, investment transactions, and investor outreach activity — cleans and validates it, transforms it into a queryable star schema, and serves the results through an interactive Streamlit dashboard.

It covers the full analytical workflow a data analyst would encounter in a fund intelligence or market research role:

- Tracking AUM, fund vintages, and deal activity across firms
- Monitoring data completeness, duplicate records, and referential integrity
- Enriching transactions with geographic and sector dimensions
- Producing clean, analysis-ready tables for BI consumption

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3 |
| Data manipulation | pandas |
| Database ORM | SQLAlchemy |
| Database | SQLite (`tracker.db`) |
| Date parsing | python-dateutil |
| Dashboard | Streamlit |
| Charts | Plotly |

---

## Pipeline Architecture

The pipeline follows a strict linear flow. Each stage reads from the previous stage's output, ensuring clean separation between raw, validated, and transformed data.

```
data/raw/*.csv
      │
      ▼
┌─────────────┐
│   Ingest    │  scripts/ingest.py
│             │  Loads firms, funds, transactions, outreach
│             │  → SQLite staging tables (stg_*)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validate   │  scripts/validate.py
│             │  Checks completeness, duplicates,
│             │  orphan records, bad dates, negative amounts
│             │  → qa/reports/quality_summary.csv
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Transform  │  scripts/transform.py
│             │  Joins staging tables with reference data
│             │  (countries, sectors) to build star schema
│             │  → dim_* and fact_* tables in tracker.db
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Export    │  scripts/export.py
│             │  Dumps all dim/fact tables to CSV
│             │  → data/processed/*.csv
└──────┬──────┘
       │
       ▼
 Streamlit Dashboard
```

All four steps can be run in sequence with a single command via `run_pipeline.py`, which handles errors at each stage and stops the pipeline with a clear message if any step fails.

---

## Installation

**Prerequisites:** Python 3.8+

```bash
git clone <repo-url>
cd alt-assets-market-tracker
pip install -r requirements.txt
```

---

## Running the Pipeline

**Run the full pipeline (recommended):**

```bash
python run_pipeline.py
```

**Or run each step individually:**

```bash
python scripts/ingest.py
python scripts/validate.py
python scripts/transform.py
python scripts/export.py
```

**Expected output:**

```
2026-04-28 22:13:41  INFO      Pipeline starting — 4 steps
2026-04-28 22:13:41  INFO      Starting step: Ingest (scripts/ingest.py)
2026-04-28 22:13:43  INFO      Completed step: Ingest
2026-04-28 22:13:43  INFO      Starting step: Validate (scripts/validate.py)
2026-04-28 22:13:43  INFO      Completed step: Validate
2026-04-28 22:13:43  INFO      Starting step: Transform (scripts/transform.py)
2026-04-28 22:13:43  INFO      Completed step: Transform
2026-04-28 22:13:43  INFO      Starting step: Export (scripts/export.py)
2026-04-28 22:13:44  INFO      Completed step: Export
2026-04-28 22:13:44  INFO      Pipeline finished successfully.
```

---

## Data Model

The database uses a **star schema** with two fact tables and four dimension tables, designed for efficient slice-and-dice analysis across firms, funds, sectors, and geographies.

```
                    ┌──────────────┐
                    │  dim_sector  │
                    │  sector_id   │
                    │  sector      │
                    │  subsector   │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────┴───────┐ ┌──────┴────────┐ ┌────┴─────────┐
   │   dim_firm   │ │ fact_transact │ │   dim_geo    │
   │   firm_id ◄──┼─┤ tx_id         ├─►  geo_id      │
   │   name       │ │ fund_id       │ │  country     │
   │   hq_country │ │ firm_id       │ │  region      │
   │   strategy   │ │ date          │ └──────────────┘
   │   aum_usd    │ │ sector_id     │
   └──────┬───────┘ │ geo_id        │
          │         │ stage         │
          │         │ amount_usd    │
   ┌──────┴───────┐ │ confidence    │
   │   dim_fund   │ └───────────────┘
   │   fund_id ◄──┤
   │   firm_id    │ ┌───────────────┐
   │   fund_name  │ │ fact_outreach │
   │   fund_type  │ │ outreach_id   │
   │   vintage_yr │ │ firm_id       │
   │   target_usd │ │ contact_role  │
   │   status     │ │ date          │
   └──────────────┘ │ channel       │
                    │ outcome       │
                    │ notes         │
                    └───────────────┘
```

### Tables

| Table | Type | Description |
|---|---|---|
| `dim_firm` | Dimension | Private equity / VC firms with AUM and strategy |
| `dim_fund` | Dimension | Individual funds linked to firms, with vintage and target size |
| `dim_geo` | Dimension | Countries and regions for geographic analysis |
| `dim_sector` | Dimension | Investment sectors and subsectors |
| `fact_transaction` | Fact | Investment transactions with amount, stage, and confidence score |
| `fact_outreach` | Fact | Investor outreach log with channel, outcome, and contact notes |

---

## Data Quality Monitoring

After ingestion, `validate.py` runs seven automated checks and writes results to `qa/reports/quality_summary.csv`:

| Check | Description |
|---|---|
| `firms_completeness_pct` | % of firm records with all required fields populated |
| `funds_completeness_pct` | % of fund records with all required fields populated |
| `txs_completeness_pct` | % of transaction records with all required fields populated |
| `duplicate_firms` | Count of duplicate firms by name + country |
| `orphan_funds` | Count of funds with no matching parent firm |
| `txs_bad_dates` | Count of transactions with unparseable dates |
| `txs_negative_amounts` | Count of transactions with negative deal values |

---

## Output

After running the full pipeline, the following files are produced:

```
data/processed/
├── dim_firm.csv
├── dim_fund.csv
├── dim_geo.csv
├── dim_sector.csv
├── fact_transaction.csv
└── fact_outreach.csv

qa/reports/
└── quality_summary.csv

tracker.db               ← SQLite database with all staging + star schema tables
```

The CSVs are read directly by the Streamlit dashboard for visualisation.

---

## Dashboard

After running the pipeline, launch the interactive dashboard with:

```bash
streamlit run app/dashboard.py
```

Then open **http://localhost:8501** in your browser. The dashboard displays four charts:

- **Top 10 Firms by AUM** — horizontal bar chart ranked by assets under management
- **Deal Count by Sector** — bar chart showing number of transactions per investment sector
- **Transaction Volume Over Time** — monthly line chart of total deal value in USD
- **Outreach Outcomes** — bar chart breaking down investor outreach results by outcome type

---

## Project Structure

```
alt-assets-market-tracker/
├── data/
│   ├── raw/                  # Source CSVs (firms, funds, transactions, outreach)
│   ├── reference/            # Lookup tables (countries, sectors)
│   └── processed/            # Pipeline output CSVs for the dashboard
├── db/
│   └── schema.sql            # Star schema DDL
├── qa/
│   └── reports/              # Data quality reports
├── scripts/
│   ├── ingest.py
│   ├── validate.py
│   ├── transform.py
│   └── export.py
├── app/
│   └── dashboard.py          # Streamlit dashboard
├── run_pipeline.py           # Orchestrator — runs all four steps in sequence
├── requirements.txt
└── tracker.db                # SQLite database (generated)
```
