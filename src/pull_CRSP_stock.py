"""
Functions to pull CRSP stock data for Kelly & Pruitt (2013) replication.

This module pulls monthly CRSP stock data needed to:
1. Calculate market equity for individual stocks (for book-to-market ratios)
2. Compute aggregate market returns and dividend growth

The paper uses book-to-market ratios from individual stocks to predict 
aggregate market returns and dividend growth using partial least squares (PLS).

This module uses the CRSP CIZ format (Flat File Format 2.0), which replaced
the legacy SIZ format as of January 2025.

Key resources:
 - Data for indices: https://wrds-www.wharton.upenn.edu/data-dictionary/crsp_a_indexes/
 - Tidy Finance guide: https://www.tidy-finance.org/python/wrds-crsp-and-compustat.html
 - CRSP 2.0 Update: https://www.tidy-finance.org/blog/crsp-v2-update/
 - Transition FAQ: https://wrds-www.wharton.upenn.edu/pages/support/manuals-and-overviews/crsp/stocks-and-indices/crsp-stock-and-indexes-version-2/crsp-ciz-faq/

Key changes from SIZ to CIZ format:
 - Monthly stock table: crspm.msf -> crspm.msf_v2
 - Security info: crspm.msenames -> crspm.stksecurityinfohist
 - Delisting returns are now built into mthret (no separate table needed)
 - Column names: date->mthcaldt, ret->mthret, retx->mthretx, prc->mthprc
 - Share code filters (shrcd) replaced with securitytype, securitysubtype, sharetype

"""

from datetime import datetime
from pathlib import Path

import pandas as pd
import wrds
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import MonthEnd

from settings import config

DATA_DIR = Path(config("DATA_DIR"))
START_TRAIN_DATE = config("START_TRAIN_DATE")
END_TEST_DATE = config("END_TEST_DATE")
WRDS_USERNAME = config("WRDS_USERNAME") or None  # Empty string becomes None


def pull_CRSP_monthly_file(
    start_date=START_TRAIN_DATE, end_date=END_TEST_DATE, wrds_username=WRDS_USERNAME
):
    """
    Pulls monthly CRSP stock data from a specified start date to end date.

    Uses the new CRSP CIZ format (msf_v2 and stksecurityinfohist tables).
    Delisting returns are now built into mthret, so no separate handling needed.

    To avoid memory issues with large date ranges, this function batches
    the query by decade and concatenates results.

    Notes
    -----

    From Bali, Engle, Murray -- Empirical asset pricing-the cross section of stock returns (2016):
    "There are two main proxies for the market portfolio that are commonly used
    in empirical asset pricing research. The first is the value-weighted portfolio of all
    U.S.-based common stocks in the CRSP database... We follow common convention by referring
    to this portfolio and its excess returns as MKT. The second portfolio commonly used as
    a proxy for the market portfolio is the CRSP value-weighted portfolio, which contains
    all securities in the CRSP database, not just common stocks, but excluding American
    Depository Receipts (ADRs). Following CRSP, we denote this portfolio VWRETD."

    **CIZ Format Security Filtering:**

    The old SIZ format used share codes (shrcd):
    * 10, 11: Common stock
    * 20, 21: Preferred stock
    * 40, 41: Warrants
    * 70, 71: Units
    * 73: Foreign stocks

    The new CIZ format uses these fields instead:
    * securitytype: 'EQTY' for equity
    * securitysubtype: 'COM' (common), 'PFD' (preferred), etc.
    * sharetype: 'NS' (no special), 'AD' (ADR), etc.
    * usincflg: 'Y' for US incorporated
    * issuertype: 'ACOR', 'CORP' for corporations

    This function uses a broad filter to approximate the original shrcd filter
    for VWRETD replication purposes.

    **Note on Returns:**
    The new mthret uses compound daily returns with dividends reinvested on
    ex-dates, which may differ slightly from the old ret (month-to-month
    holding period return with dividends reinvested at month-end).

    """
    # Convert start_date to datetime if it's a string
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Not a perfect solution, but since value requires t-1 period market cap,
    # we need to pull one extra month of data. This is hidden from the user.
    start_date = start_date - relativedelta(months=1)
    
    # Build list of 5-year ranges to batch the query and avoid memory issues
    # (Decades were still too large for some periods)
    year_ranges = []
    current_start = start_date
    while current_start < end_date:
        # End of current 5-year period (or end_date if sooner)
        period_end_year = (current_start.year // 5 + 1) * 5
        current_end = min(
            datetime(period_end_year, 1, 1) - relativedelta(days=1),
            end_date
        )
        year_ranges.append((current_start, current_end))
        current_start = current_end + relativedelta(days=1)
    
    db = wrds.Connection(wrds_username=wrds_username)
    
    dfs = []
    for batch_start, batch_end in year_ranges:
        batch_start_str = batch_start.strftime("%Y-%m-%d")
        batch_end_str = batch_end.strftime("%Y-%m-%d")
        print(f"Pulling CRSP data for {batch_start_str} to {batch_end_str}...")
        
        # CIZ format query using msf_v2 and stksecurityinfohist
        # Delisting returns are now built into mthret - no separate join needed
        query = f"""
        SELECT
            msf.permno,
            msf.permco,
            msf.mthcaldt,
            msf.mthret,
            msf.mthretx,
            msf.shrout,
            msf.mthprc,
            msf.mthvol,
            msf.mthcumfacshr,
            msf.mthcumfacpr,
            ssih.primaryexch,
            ssih.siccd,
            ssih.naics,
            ssih.issuertype,
            ssih.securitytype,
            ssih.securitysubtype,
            ssih.sharetype,
            ssih.usincflg,
            ssih.tradingstatusflg,
            ssih.conditionaltype
        FROM crspm.msf_v2 AS msf
        INNER JOIN crspm.stksecurityinfohist AS ssih
            ON msf.permno = ssih.permno
            AND ssih.secinfostartdt <= msf.mthcaldt
            AND msf.mthcaldt <= ssih.secinfoenddt
        WHERE
            msf.mthcaldt BETWEEN '{batch_start_str}' AND '{batch_end_str}'
            AND ssih.securitytype = 'EQTY'
        """
        # Note: Using securitytype = 'EQTY' as broad filter to include various equity types.
        # For stricter common-stock-only filtering, add:
        #   AND ssih.securitysubtype = 'COM'
        #   AND ssih.sharetype = 'NS'
        #   AND ssih.usincflg = 'Y'
        #   AND ssih.issuertype IN ('ACOR', 'CORP')
        
        df_batch = db.raw_sql(query, date_cols=["mthcaldt"], chunksize=100000)
        dfs.append(df_batch)
    
    db.close()
    
    # Concatenate all batches
    df = pd.concat(dfs, ignore_index=True)
    del dfs  # Free memory
    
    df = df.loc[:, ~df.columns.duplicated()]

    # shrout is in thousands in CRSP, convert to actual shares
    df["shrout"] = df["shrout"] * 1000

    # Rename columns for backward compatibility with downstream code
    # (calc_CRSP_indices.py, calc_SP500_index.py expect these names)
    df = df.rename(
        columns={
            "mthcaldt": "date",
            "mthret": "ret",
            "mthretx": "retx",
            "mthprc": "prc",
            "mthvol": "vol",
            "mthcumfacshr": "cfacshr",
            "mthcumfacpr": "cfacpr",
        }
    )

    # Create altprc for compatibility (absolute value of price)
    df["altprc"] = df["prc"].abs()

    # Calculate adjusted shares and prices for market cap calculation
    # (same logic as the old SIZ format)
    df["adj_shrout"] = df["shrout"] * df["cfacshr"]
    df["adj_prc"] = df["prc"].abs() / df["cfacpr"]
    df["market_cap"] = df["adj_prc"] * df["adj_shrout"]

    # Add jdate (month-end aligned date) for portfolio formation
    df["jdate"] = df["date"] + MonthEnd(0)

    return df


def pull_CRSP_index_files(
    start_date=START_TRAIN_DATE, end_date=END_TEST_DATE, wrds_username=WRDS_USERNAME
):
    """
    Pulls the CRSP index files from crsp_a_indexes.msix:
    (Monthly) NYSE/AMEX/NASDAQ Capitalization Deciles, Annual Rebalanced (msix)

    Note: The index tables (crsp_a_indexes) were not significantly changed
    in the CIZ transition. The column names and structure remain the same.
    """
    query = f"""
        SELECT *
        FROM crsp_a_indexes.msix
        WHERE caldt BETWEEN '{start_date}' AND '{end_date}'
    """
    db = wrds.Connection(wrds_username=wrds_username)
    df = db.raw_sql(query, date_cols=["caldt"])
    db.close()
    return df


def pull_CRSP_market_returns(
    start_date=START_TRAIN_DATE, end_date=END_TEST_DATE, wrds_username=WRDS_USERNAME
):
    """
    Pull aggregate market returns from CRSP for dividend growth calculation.
    
    For Kelly & Pruitt (2013), we need aggregate market returns (with and without
    dividends) to compute dividend growth. The difference between vwretd and vwretx
    gives the dividend yield component.
    
    Returns columns:
    - vwretd: Value-weighted return including dividends
    - vwretx: Value-weighted return excluding dividends  
    - ewretd: Equal-weighted return including dividends
    - ewretx: Equal-weighted return excluding dividends
    - usdval: Total market value in USD
    - sprtrn: S&P 500 return
    
    Note: The crsp.msi table uses 'date' as the date column (not 'caldt').
    """
    query = f"""
        SELECT date, vwretd, vwretx, ewretd, ewretx, usdval, sprtrn
        FROM crsp.msi
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
    """
    db = wrds.Connection(wrds_username=wrds_username)
    df = db.raw_sql(query, date_cols=["date"])
    db.close()
    
    df["date"] = df["date"] + MonthEnd(0)
    
    return df


def load_CRSP_market_returns(data_dir=DATA_DIR):
    path = Path(data_dir) / "CRSP_market_returns.parquet"
    df = pd.read_parquet(path)
    return df


def load_CRSP_monthly_file(data_dir=DATA_DIR):
    path = Path(data_dir) / "CRSP_monthly_stock.parquet"
    df = pd.read_parquet(path)
    return df


def load_CRSP_index_files(data_dir=DATA_DIR):
    path = Path(data_dir) / "CRSP_MSIX.parquet"
    df = pd.read_parquet(path)
    return df


def _demo():
    df_msf = load_CRSP_monthly_file(data_dir=DATA_DIR)
    df_msix = load_CRSP_index_files(data_dir=DATA_DIR)


if __name__ == "__main__":
    df_msf = pull_CRSP_monthly_file(start_date=START_TRAIN_DATE, end_date=END_TEST_DATE)
    path = Path(DATA_DIR) / "CRSP_monthly_stock.parquet"
    df_msf.to_parquet(path)

    df_msix = pull_CRSP_index_files(start_date=START_TRAIN_DATE, end_date=END_TEST_DATE)
    path = Path(DATA_DIR) / "CRSP_MSIX.parquet"
    df_msix.to_parquet(path)

    df_mkt = pull_CRSP_market_returns(start_date=START_TRAIN_DATE, end_date=END_TEST_DATE)
    path = Path(DATA_DIR) / "CRSP_market_returns.parquet"
    df_mkt.to_parquet(path)
