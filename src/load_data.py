import pandas as pd
import numpy as np

import pull_ken_french_data as pkf

DATA_DIR = pkf.DATA_DIR

def clean_kelly_pruitt_data():
    """
    Pulls and cleans the Ken French datasets to replicate Kelly & Pruitt (2013) Table 1.
    Includes handling for invalid data markers commonly used by Ken French (-99.99, -999).
    """
    datasets = [
        "F-F_Research_Data_Factors",
        "6_Portfolios_2x3",
        "25_Portfolios_5x5",
        "100_Portfolios_10x10"
    ]
    
    # Missing value indicators in Ken French data
    missing_indicators = [-99.99, -999, -999.00, -99.990]
    
    # 1. Pull the raw datasets into Excel files
    for ds in datasets:
        pkf.pull_ken_french_excel(dataset_name=ds, data_dir=DATA_DIR)
        
    cleaned_data = {}
        
    # 2. Extract Aggregate Market Return (Mkt = Mkt-RF + RF)
    ff_factors = pkf.load_sheet("F-F_Research_Data_Factors", sheet_name="0", data_dir=DATA_DIR)
    
    # Replace missing values with NaN
    ff_factors.replace(missing_indicators, np.nan, inplace=True)
    
    if 'Date' in ff_factors.columns and not pd.api.types.is_datetime64_any_dtype(ff_factors['Date']):
        ff_factors['Date'] = pd.to_datetime(ff_factors['Date'].astype(str), format='%Y%m', errors='coerce')
        
    # Drop rows with unparseable dates (NaT)
    ff_factors.dropna(subset=['Date'], inplace=True)
    
    # Calculate total market return
    ff_factors['Mkt'] = ff_factors['Mkt-RF'] + ff_factors['RF']
    cleaned_data["Market_Returns"] = ff_factors.set_index('Date')[['Mkt', 'Mkt-RF', 'RF']]
    
    # 3. Construct Monthly Portfolio Book-to-Market Ratios
    for ds in datasets[1:]:
        # Sheet indices based on Ken French's standard layout:
        # 0: Monthly Returns
        # 4: Number of Firms (Monthly)
        # 5: Average Firm Size (Monthly)
        # 6: Annual Sum of BE / Sum of ME
        returns = pkf.load_sheet(ds, sheet_name="0", data_dir=DATA_DIR)
        n_firms = pkf.load_sheet(ds, sheet_name="4", data_dir=DATA_DIR)
        avg_size = pkf.load_sheet(ds, sheet_name="5", data_dir=DATA_DIR)
        annual_beme = pkf.load_sheet(ds, sheet_name="6", data_dir=DATA_DIR)
        
        # Replace missing values with NaN across all loaded sheets
        returns.replace(missing_indicators, np.nan, inplace=True)
        n_firms.replace(missing_indicators, np.nan, inplace=True)
        avg_size.replace(missing_indicators, np.nan, inplace=True)
        annual_beme.replace(missing_indicators, np.nan, inplace=True)
        
        # Standardize dates for monthly data
        for df in [returns, n_firms, avg_size]:
            if 'Date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['Date']):
                df['Date'] = pd.to_datetime(df['Date'].astype(str), format='%Y%m', errors='coerce')
            df.dropna(subset=['Date'], inplace=True)
            df['Year'] = df['Date'].dt.year
            df['Month'] = df['Date'].dt.month
            
        # Standardize dates for annual data
        if 'Date' in annual_beme.columns:
            # Clean up trailing decimals if pandas parsed as float
            date_str = annual_beme['Date'].astype(str).str.replace(r'\.0$', '', regex=True)
            annual_beme['Year'] = pd.to_numeric(date_str.str[:4], errors='coerce')
            annual_beme.dropna(subset=['Year'], inplace=True)
            annual_beme['Year'] = annual_beme['Year'].astype(int)
            
        # Calculate Monthly Market Equity (ME = N_Firms * Avg_Size)
        portfolio_cols = [c for c in n_firms.columns if c not in ['Date', 'Year', 'Month']]
        monthly_me = n_firms[['Date', 'Year', 'Month']].copy()
        monthly_me[portfolio_cols] = n_firms[portfolio_cols] * avg_size[portfolio_cols]
        
        # Calculate Annual Book Equity (BE_Y = Annual BEME_Y * ME_Dec_Y)
        dec_me = monthly_me[monthly_me['Month'] == 12].set_index('Year')[portfolio_cols]
        annual_beme_idx = annual_beme.set_index('Year')[portfolio_cols]
        annual_be = (annual_beme_idx * dec_me).reset_index().rename(columns={'Year': 'Formation_Year'})
        
        # Shift BE visibility to June of the following year
        # e.g., if we are in July Year Y, the most recent observable BE is from Dec Year Y-1
        monthly_me['Formation_Year'] = np.where(monthly_me['Month'] >= 7, 
                                                monthly_me['Year'] - 1, 
                                                monthly_me['Year'] - 2)
        
        # Merge lagged BE and calculate Monthly BM (BM_t = BE_Y / ME_t)
        merged_be = pd.merge(monthly_me[['Date', 'Formation_Year']], annual_be, on='Formation_Year', how='left')
        
        bm_ratios = monthly_me[['Date']].copy()
        for c in portfolio_cols:
            # Divide BE by ME. If ME is 0 or NaN, or BE is NaN, pandas will correctly yield NaN or inf.
            # We replace inf with NaN just to be safe.
            bm_ratios[c] = merged_be[c] / monthly_me[c]
            bm_ratios[c].replace([np.inf, -np.inf], np.nan, inplace=True)
            
        cleaned_data[f"{ds}_Returns"] = returns.set_index('Date')[portfolio_cols]
        cleaned_data[f"{ds}_BM"] = bm_ratios.set_index('Date')[portfolio_cols]
        
    return cleaned_data

if __name__ == "__main__":
    data_dict = clean_kelly_pruitt_data()
    print("Data loaded successfully. Available keys:", list(data_dict.keys()))