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

RAW_DIR = "data/raw"
DB_PATH = "tracker.db"

TABLES = [
    ("firms.csv",        "stg_firm"),
    ("funds.csv",        "stg_fund"),
    ("transactions.csv", "stg_transaction"),
    ("outreach.csv",     "stg_outreach"),
]


def read_csv(name):
    path = os.path.join(RAW_DIR, name)
    if not os.path.exists(path):
        log.error("Missing CSV file: %s", path)
        sys.exit(1)
    return pd.read_csv(path)


def main():
    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
    try:
        with engine.begin() as conn:
            for csv_name, table_name in TABLES:
                df = read_csv(csv_name)
                try:
                    df.to_sql(table_name, conn, if_exists="replace", index=False)
                except SQLAlchemyError as exc:
                    log.error("Database write failed for table '%s': %s", table_name, exc)
                    sys.exit(1)
    except SQLAlchemyError as exc:
        log.error("Failed to connect to database '%s': %s", DB_PATH, exc)
        sys.exit(1)
    log.info("Ingest complete → stg_firm, stg_fund, stg_transaction, stg_outreach")


if __name__ == "__main__":
    main()
