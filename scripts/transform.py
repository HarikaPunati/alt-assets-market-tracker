import logging
import os
import sys

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

DB_PATH = "tracker.db"


def read_table(conn, table_name):
    try:
        return pd.read_sql(f"SELECT * FROM {table_name}", conn)
    except Exception as exc:
        log.error("Failed to read staging table '%s': %s", table_name, exc)
        sys.exit(1)


def read_reference_csv(path):
    if not os.path.exists(path):
        log.error("Missing reference CSV: %s", path)
        sys.exit(1)
    try:
        return pd.read_csv(path)
    except Exception as exc:
        log.error("Failed to read reference CSV '%s': %s", path, exc)
        sys.exit(1)


def main():
    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
    try:
        with engine.begin() as conn:
            firms    = read_table(conn, "stg_firm")
            funds    = read_table(conn, "stg_fund")
            txs      = read_table(conn, "stg_transaction")
            outreach = read_table(conn, "stg_outreach")

            countries = read_reference_csv("data/reference/countries.csv").reset_index().rename(columns={"index":"geo_id"})
            countries["geo_id"] += 1
            txs = txs.merge(countries[["geo_id","country"]], on="country", how="left")

            sectors = read_reference_csv("data/reference/sectors.csv")
            txs = txs.merge(sectors[["sector_id","sector","subsector"]], on=["sector","subsector"], how="left")

            dim_firm = firms[["firm_id","name","hq_country","strategy","aum_estimate_usd"]]
            dim_fund = funds[["fund_id","firm_id","fund_name","fund_type","vintage_year","target_size_usd","status"]]
            dim_geo = countries[["geo_id","country","region"]]
            dim_sector = sectors[["sector_id","sector","subsector"]]
            fact_tx = txs[["tx_id","fund_id","firm_id","date","sector_id","geo_id","stage","amount_usd","source","confidence_score"]]
            fact_outreach = outreach[["outreach_id","firm_id","contact_role","date","channel","outcome","notes"]]

            schema_path = "db/schema.sql"
            if not os.path.exists(schema_path):
                log.error("Missing schema file: %s", schema_path)
                sys.exit(1)

            try:
                conn.connection.executescript(open(schema_path).read())
                dim_firm.to_sql("dim_firm", conn, if_exists="replace", index=False)
                dim_fund.to_sql("dim_fund", conn, if_exists="replace", index=False)
                dim_geo.to_sql("dim_geo", conn, if_exists="replace", index=False)
                dim_sector.to_sql("dim_sector", conn, if_exists="replace", index=False)
                fact_tx.to_sql("fact_transaction", conn, if_exists="replace", index=False)
                fact_outreach.to_sql("fact_outreach", conn, if_exists="replace", index=False)
            except SQLAlchemyError as exc:
                log.error("Database write failed during transform: %s", exc)
                sys.exit(1)
    except SQLAlchemyError as exc:
        log.error("Failed to connect to database '%s': %s", DB_PATH, exc)
        sys.exit(1)

    log.info("Transform complete → dim_* and fact_* tables ready in tracker.db")


if __name__ == "__main__":
    main()
