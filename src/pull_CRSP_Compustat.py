"""
This module pulls and saves Compustat fundamentals data and the CRSP-Compustat
Merged (CCM) link table for replicating Kelly & Pruitt (2013) Table 1.

The paper "Market Expectations in the Cross-Section of Present Values" uses
book-to-market ratios from individual stocks to predict aggregate market returns
and dividend growth using partial least squares (PLS).

Data pulled:
- Compustat fundamentals (comp.funda) - for book equity calculation
- CCM link table (crsp.ccmxpf_linktable) - maps Compustat GVKEY to CRSP PERMNO
- Fama-French factors from WRDS (ff.factors_monthly)

For information about Compustat variables, see:
https://wrds-www.wharton.upenn.edu/documents/1583/Compustat_Data_Guide.pdf

For information about the CCM link table, see:
https://wrds-www.wharton.upenn.edu/pages/wrds-research/database-linking-matrix/linking-crsp-with-compustat/

"""

from pathlib import Path

import pandas as pd
import wrds
from pandas.tseries.offsets import MonthEnd

from settings import config

# Note: MonthEnd is still needed for pull_Fama_French_factors()

OUTPUT_DIR = Path(config("OUTPUT_DIR"))
DATA_DIR = Path(config("DATA_DIR"))
WRDS_USERNAME = config("WRDS_USERNAME") or None  # Empty string becomes None


description_compustat = {
    "gvkey": "Global Company Key",
    "datadate": "Data Date",
    "at": "Assets - Total",
    "lt": "Liabilities - Total",
    "sale": "Sales/Revenue",
    "cogs": "Cost of Goods Sold",
    "xsga": "Selling, General and Administrative Expense",
    "xint": "Interest Expense, Net",
    "pstkl": "Preferred Stock - Liquidating Value",
    "txditc": "Deferred Taxes and Investment Tax Credit",
    "pstkrv": "Preferred Stock - Redemption Value",
    "seq": "Stockholders' Equity - Parent",
    "pstk": "Preferred/Preference Stock (Capital) - Total",
    "ceq": "Common/Ordinary Equity - Total",
    "csho": "Common Shares Outstanding",
    "prcc_f": "Price Close - Annual - Fiscal",
    "ni": "Net Income",
    "sich": "Standard Industry Classification - Historical",
    "dp": "Depreciation and Amortization",
    "ebit": "Earnings Before Interest and Taxes",
    "indfmt": "Industry Format",
    "datafmt": "Data Format",
    "popsrc": "Population Source",
    "consol": "Consolidation",
}


def pull_compustat(wrds_username=WRDS_USERNAME):
    """
    Pull Compustat fundamentals data for book equity calculation.
    
    For Kelly & Pruitt (2013), we need book-to-market ratios at the firm level.
    Book equity = Stockholders' Equity + Deferred Taxes - Preferred Stock
    
    See description_compustat for a description of the variables.
    """
    sql_query = """
        SELECT 
            gvkey, datadate, at, lt, sale, cogs, xsga, xint, pstkl, txditc,
            pstkrv, seq, pstk, ceq, ni, sich, dp, ebit, csho, prcc_f
        FROM 
            comp.funda
        WHERE 
            indfmt='INDL' AND -- industrial companies
            datafmt='STD' AND -- only standardized records
            popsrc='D' AND -- only from primary sources
            consol='C' AND -- consolidated financial statements
            datadate >= '01/01/1930'
        """
    # with wrds.Connection(wrds_username=wrds_username) as db:
    #     comp = db.raw_sql(sql_query, date_cols=["datadate"])
    db = wrds.Connection(wrds_username=wrds_username)
    comp = db.raw_sql(sql_query, date_cols=["datadate"])
    db.close()

    comp["year"] = comp["datadate"].dt.year
    return comp


description_crsp_comp_link = {
    "gvkey": "Global Company Key - A unique identifier for companies in the Compustat database.",
    "permno": "Permanent Number - A unique stock identifier assigned by CRSP to each security.",
    "linktype": "Link Type - Indicates the type of linkage between CRSP and Compustat records. 'L' types refer to links considered official by CRSP.",
    "linkprim": "Primary Link Indicator - Specifies whether the link is a primary ('P') or secondary ('C') connection between the databases. Primary links are direct matches between CRSP and Compustat entities, while secondary links may represent subsidiary relationships or other less direct connections.",
    "linkdt": "Link Date Start - The starting date for which the linkage between CRSP and Compustat data is considered valid.",
    "linkenddt": "Link Date End - The ending date for which the linkage is considered valid. A blank or high value (e.g., '2099-12-31') indicates that the link is still valid as of the last update.",
}


def pull_CRSP_Comp_Link_Table(wrds_username=WRDS_USERNAME):
    """Pull the CRSP-Compustat Merged link table from WRDS.

    Filters to primary link types (linktype starting with 'L') and
    primary/connecting link indicators (linkprim 'C' or 'P').
    """
    sql_query = """
        SELECT 
            gvkey, lpermno AS permno, linktype, linkprim, linkdt, linkenddt
        FROM 
            crsp.ccmxpf_linktable
        WHERE 
            substr(linktype,1,1)='L' AND 
            (linkprim ='C' OR linkprim='P')
        """
    db = wrds.Connection(wrds_username=wrds_username)
    ccm = db.raw_sql(sql_query, date_cols=["linkdt", "linkenddt"])
    db.close()
    return ccm


def pull_Fama_French_factors(wrds_username=WRDS_USERNAME):
    """Pull monthly Fama-French factors (MktRF, SMB, HML, RF) from the WRDS ff library."""
    conn = wrds.Connection(wrds_username=wrds_username)
    ff = conn.get_table(library="ff", table="factors_monthly")
    conn.close()
    ff[["smb", "hml"]] = ff[["smb", "hml"]].astype(float)

    ff["date"] = pd.to_datetime(ff["date"])
    ff["date"] = ff["date"] + MonthEnd(0)

    return ff


def load_compustat(data_dir=DATA_DIR):
    """Load cached Compustat fundamentals from a local Parquet file."""
    path = Path(data_dir) / "Compustat.parquet"
    comp = pd.read_parquet(path)
    return comp


def load_CRSP_Comp_Link_Table(data_dir=DATA_DIR):
    """Load cached CRSP-Compustat link table from a local Parquet file."""
    path = Path(data_dir) / "CRSP_Comp_Link_Table.parquet"
    ccm = pd.read_parquet(path)
    return ccm


def load_Fama_French_factors(data_dir=DATA_DIR):
    """Load cached Fama-French monthly factors from a local Parquet file."""
    path = Path(data_dir) / "FF_FACTORS.parquet"
    ff = pd.read_parquet(path)
    return ff


def _demo():
    comp = load_compustat(data_dir=DATA_DIR)
    ccm = load_CRSP_Comp_Link_Table(data_dir=DATA_DIR)
    ff = load_Fama_French_factors(data_dir=DATA_DIR)


if __name__ == "__main__":
    comp = pull_compustat(wrds_username=WRDS_USERNAME)
    comp.to_parquet(DATA_DIR / "Compustat.parquet")

    ccm = pull_CRSP_Comp_Link_Table(wrds_username=WRDS_USERNAME)
    ccm.to_parquet(DATA_DIR / "CRSP_Comp_Link_Table.parquet")

    ff = pull_Fama_French_factors(wrds_username=WRDS_USERNAME)
    ff.to_parquet(DATA_DIR / "FF_FACTORS.parquet")
