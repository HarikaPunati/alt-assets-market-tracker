import os
import pandas as pd
from sqlalchemy import create_engine
from dateutil.parser import parse as parse_date

DB_PATH = "tracker.db"
OUT_DIR = "qa/reports"

def pct_required(df, req_cols):
    return round(100 * (df[req_cols].notnull().all(axis=1).mean()), 2)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    eng = create_engine(f"sqlite:///{DB_PATH}", future=True)
    with eng.begin() as c:
        firms = pd.read_sql("SELECT * FROM stg_firm", c)
        funds = pd.read_sql("SELECT * FROM stg_fund", c)
        txs   = pd.read_sql("SELECT * FROM stg_transaction", c)

    comp_firms = pct_required(firms, ["firm_id","name","hq_country"])
    comp_funds = pct_required(funds, ["fund_id","firm_id","fund_name"])
    comp_txs   = pct_required(txs,   ["tx_id","firm_id","date","amount_usd"])

    dup_firms = (
        firms.assign(k=firms["name"].str.lower().str.strip()+"|"+firms["hq_country"].str.lower().str.strip())
             .duplicated("k").sum()
    )
    orphan_funds = (~funds["firm_id"].astype(str).isin(firms["firm_id"].astype(str))).sum()

    def good_date(x):
        try: parse_date(str(x)); return True
        except: return False
    bad_dates = (~txs["date"].apply(good_date)).sum()
    neg_amts  = (txs["amount_usd"] < 0).fillna(False).sum()

    summary = pd.DataFrame([
        {"metric":"firms_completeness_pct","value":comp_firms},
        {"metric":"funds_completeness_pct","value":comp_funds},
        {"metric":"txs_completeness_pct","value":comp_txs},
        {"metric":"duplicate_firms","value":int(dup_firms)},
        {"metric":"orphan_funds","value":int(orphan_funds)},
        {"metric":"txs_bad_dates","value":int(bad_dates)},
        {"metric":"txs_negative_amounts","value":int(neg_amts)},
    ])
    summary.to_csv(os.path.join(OUT_DIR, "quality_summary.csv"), index=False)
    print("Validation complete → qa/reports/quality_summary.csv")

if __name__ == "__main__":
    main()

