"""
Retrieves, cleans, and caches Fama-French portfolio datasets.

Processes raw Ken French data by handling missing value indicators, 
standardizing datetime indices, and calculating monthly Book-to-Market (BM) 
ratios from annual book equity and monthly market equity. Saves the 
resulting clean datasets as Parquet files for faster downstream access.
"""

import pandas as pd
import numpy as np

import pull_ken_french_data as pkf

DATA_DIR = pkf.DATA_DIR

def clean_kelly_pruitt_data(load_from_cache=False):
    """
    Pulls and cleans the Ken French datasets to replicate Kelly & Pruitt (2013) Table 1.
    If load_from_cache is True, it skips cleaning and simply reads the saved Parquet files.
    """
    datasets = [
        "F-F_Research_Data_Factors",
        "6_Portfolios_2x3",
        "25_Portfolios_5x5",
        "100_Portfolios_10x10"
    ]
    
    if load_from_cache:
        cleaned_data = {}
        cleaned_data["Market_Returns"] = pd.read_parquet(DATA_DIR / "Market_Returns.parquet")
        for ds in datasets[1:]:
            cleaned_data[f"{ds}_Returns"] = pd.read_parquet(DATA_DIR / f"{ds}_Returns.parquet")
            cleaned_data[f"{ds}_BM"] = pd.read_parquet(DATA_DIR / f"{ds}_BM.parquet")
        return cleaned_data
        
    # Missing value indicators in Ken French data
    missing_indicators = [-99.99, -999, -999.00, -99.990]
    cleaned_data = {}
        
    # Extract Aggregate Market Return (Mkt = Mkt-RF + RF)
    ff_factors = pkf.load_sheet("F-F_Research_Data_Factors", sheet_name="0", data_dir=DATA_DIR)
    
    # Replace missing values with NaN
    ff_factors.replace(missing_indicators, np.nan, inplace=True)
    
    if 'Date' in ff_factors.columns and not pd.api.types.is_datetime64_any_dtype(ff_factors['Date']):
        ff_factors['Date'] = pd.to_datetime(ff_factors['Date'].astype(str), format='%Y%m', errors='coerce')
        
    # Drop rows with unparseable dates (NaT)
    ff_factors.dropna(subset=['Date'], inplace=True)
    
    # Calculate total market return
    ff_factors['Mkt'] = ff_factors['Mkt-RF'] + ff_factors['RF']
    ff_factors['Log_Mkt'] = np.log(1 + (ff_factors['Mkt'] / 100.0))
    cleaned_data["Market_Returns"] = ff_factors.set_index('Date')[['Mkt', 'Log_Mkt', 'Mkt-RF', 'RF']]
    
    # Construct Monthly Portfolio Book-to-Market Ratios
    for ds in datasets[1:]:
        # Sheet indices based on Ken French's standard layout:
        # 0: Monthly Value-Weighted Returns
        # 6: Monthly Value-Weighted Average of BE/ME
        #    ("Sum[ME(Mth) * BE(FY t-1) / ME(Dec t-1)] / Sum[ME(Mth)]")
        #    This is the portfolio-level book-to-market ratio at each month.
        returns = pkf.load_sheet(ds, sheet_name="0", data_dir=DATA_DIR)
        beme = pkf.load_sheet(ds, sheet_name="6", data_dir=DATA_DIR)
        
        # Replace missing values with NaN
        returns.replace(missing_indicators, np.nan, inplace=True)
        beme.replace(missing_indicators, np.nan, inplace=True)
        
        # Ensure dates are parsed
        for df in [returns, beme]:
            if 'Date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['Date']):
                df['Date'] = pd.to_datetime(df['Date'].astype(str), format='%Y%m', errors='coerce')
            df.dropna(subset=['Date'], inplace=True)
        
        portfolio_cols = [c for c in returns.columns if c not in ['Date', 'Year', 'Month']]
        
        # Log book-to-market ratio: v_{i,t} = log(BM_{i,t})
        # Sheet 6 provides monthly BE/ME ratios directly (positive values only)
        bm_values = beme.set_index('Date')[portfolio_cols].astype(float)
        log_bm = np.log(bm_values.where(bm_values > 0))
        
        cleaned_data[f"{ds}_Returns"] = returns.set_index('Date')[portfolio_cols]
        cleaned_data[f"{ds}_BM"] = log_bm
    return cleaned_data

if __name__ == "__main__":
    data_dict = clean_kelly_pruitt_data(load_from_cache=False)
    
    for key, df in data_dict.items():
        # Ensure column names are strings before saving to Parquet
        df.columns = df.columns.astype(str)
        save_path = DATA_DIR / f"{key}.parquet"
        df.to_parquet(save_path)
        print(f"Saved {save_path}")
        
    print("Data cleaned and cached successfully.")