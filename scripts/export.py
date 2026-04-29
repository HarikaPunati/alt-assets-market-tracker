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

DB = "tracker.db"
OUT = "data/processed"
TABLES = ["dim_firm","dim_fund","dim_geo","dim_sector","fact_transaction","fact_outreach"]


def main():
    os.makedirs(OUT, exist_ok=True)
    engine = create_engine(f"sqlite:///{DB}", future=True)
    try:
        with engine.begin() as conn:
            for t in TABLES:
                try:
                    df = pd.read_sql(f"SELECT * FROM {t}", conn)
                except SQLAlchemyError as exc:
                    log.error("Failed to read table '%s': %s", t, exc)
                    sys.exit(1)
                path = os.path.join(OUT, f"{t}.csv")
                try:
                    df.to_csv(path, index=False)
                except Exception as exc:
                    log.error("Failed to write CSV '%s': %s", path, exc)
                    sys.exit(1)
                log.info("Exported %s → %s", t, path)
    except SQLAlchemyError as exc:
        log.error("Failed to connect to database '%s': %s", DB, exc)
        sys.exit(1)

    log.info("Export complete → CSVs in data/processed/ are ready for BI")


if __name__ == "__main__":
    main()
