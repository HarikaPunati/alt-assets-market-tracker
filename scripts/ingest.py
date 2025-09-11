import os
import pandas as pd
from sqlalchemy import create_engine

RAW_DIR = "data/raw"
DB_PATH = "tracker.db"

def read_csv(name): return pd.read_csv(os.path.join(RAW_DIR, name))

def main():
    engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
    with engine.begin() as conn:
        read_csv("firms.csv").to_sql("stg_firm", conn, if_exists="replace", index=False)
        read_csv("funds.csv").to_sql("stg_fund", conn, if_exists="replace", index=False)
        read_csv("transactions.csv").to_sql("stg_transaction", conn, if_exists="replace", index=False)
        read_csv("outreach.csv").to_sql("stg_outreach", conn, if_exists="replace", index=False)
    print("Ingest complete → stg_firm, stg_fund, stg_transaction, stg_outreach")

if __name__ == "__main__":
    main()

