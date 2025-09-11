import os, sqlite3, pandas as pd

DB = "tracker.db"
OUT = "data/processed"
TABLES = ["dim_firm","dim_fund","dim_geo","dim_sector","fact_transaction","fact_outreach"]

def main():
    os.makedirs(OUT, exist_ok=True)
    conn = sqlite3.connect(DB)
    for t in TABLES:
        df = pd.read_sql(f"SELECT * FROM {t}", conn)
        path = os.path.join(OUT, f"{t}.csv")
        df.to_csv(path, index=False)
        print(f"Exported {t} → {path}")
    conn.close()
    print("Export complete → CSVs in data/processed/ are ready for BI")

if __name__ == "__main__":
    main()

