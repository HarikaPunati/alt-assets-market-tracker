import sqlite3
import pandas as pd

DB_PATH = "tracker.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    firms = pd.read_sql("SELECT * FROM stg_firm", conn)
    funds = pd.read_sql("SELECT * FROM stg_fund", conn)
    txs   = pd.read_sql("SELECT * FROM stg_transaction", conn)
    outreach = pd.read_sql("SELECT * FROM stg_outreach", conn)

    countries = pd.read_csv("data/reference/countries.csv").reset_index().rename(columns={"index":"geo_id"})
    countries["geo_id"] += 1
    txs = txs.merge(countries[["geo_id","country"]], on="country", how="left")

    sectors = pd.read_csv("data/reference/sectors.csv")
    txs = txs.merge(sectors[["sector_id","sector","subsector"]], on=["sector","subsector"], how="left")

    dim_firm = firms[["firm_id","name","hq_country","strategy","aum_estimate_usd"]]
    dim_fund = funds[["fund_id","firm_id","fund_name","fund_type","vintage_year","target_size_usd","status"]]
    dim_geo = countries[["geo_id","country","region"]]
    dim_sector = sectors[["sector_id","sector","subsector"]]
    fact_tx = txs[["tx_id","fund_id","firm_id","date","sector_id","geo_id","stage","amount_usd","source","confidence_score"]]
    fact_outreach = outreach[["outreach_id","firm_id","contact_role","date","channel","outcome","notes"]]

    cur = conn.cursor()
    cur.executescript(open("db/schema.sql").read())
    dim_firm.to_sql("dim_firm", conn, if_exists="replace", index=False)
    dim_fund.to_sql("dim_fund", conn, if_exists="replace", index=False)
    dim_geo.to_sql("dim_geo", conn, if_exists="replace", index=False)
    dim_sector.to_sql("dim_sector", conn, if_exists="replace", index=False)
    fact_tx.to_sql("fact_transaction", conn, if_exists="replace", index=False)
    fact_outreach.to_sql("fact_outreach", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()
    print("Transform complete → dim_* and fact_* tables ready in tracker.db")

if __name__ == "__main__":
    main()

