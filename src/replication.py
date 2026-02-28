"""
Coordinates end-to-end Kelly & Pruitt (2013) replication pipeline.

Handles data loading, descriptive statistics generation, execution of the 
three-stage regression filter, and PLS model evaluations across both the 
original paper's timeframe and modern data. Exports all intermediate 
analytical results to CSV files for downstream reporting.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Custom
import load_data
import regression_tools as rt
import pls_regression
from settings import config

# Settings and configurations
OUTPUT_DIR = Path(config("OUTPUT_DIR"))
START_TRAIN_DATE = config("START_TRAIN_DATE")
START_TEST_DATE = config("START_TEST_DATE")
END_TEST_DATE = config("END_TEST_DATE")
CURRENT_DATE = config("CURRENT_DATE")

def data_sparsity_analysis(data):
    """Analyzes data availability over time and exports to CSV."""
    bm_6 = data["6_Portfolios_2x3_BM"]
    bm_25 = data["25_Portfolios_5x5_BM"]
    bm_100 = data["100_Portfolios_10x10_BM"]

    valid_6 = bm_6.count(axis=1).rename("6_Portfolios")
    valid_25 = bm_25.count(axis=1).rename("25_Portfolios")
    valid_100 = bm_100.count(axis=1).rename("100_Portfolios")
    
    df_sparsity = pd.concat([valid_6, valid_25, valid_100], axis=1)
    df_sparsity.to_csv(OUTPUT_DIR / "data_sparsity.csv")

    return df_sparsity

def generate_summary_statistics(data):
    """Generates a summary statistics table and exports to CSV."""
    v_df = data["25_Portfolios_5x5_BM"].loc[START_TRAIN_DATE:END_TEST_DATE]
    y_1m = data['Market_Returns']['Log_Mkt'].loc[START_TRAIN_DATE:END_TEST_DATE]
    
    # Calculate summary statistics
    summary_df = v_df.describe().T[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    
    mkt_stats = y_1m.describe()[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    mkt_stats.name = "Log Market Return"
    
    # Combine Market Return with Portfolio Data
    summary_df = pd.concat([pd.DataFrame(mkt_stats).T, summary_df])
    summary_df.to_csv(OUTPUT_DIR / "summary_statistics.csv")
        
    return summary_df

def run_stage_1_analysis(v_df, y_1m):
    """Runs Stage 1 of the regression filter and exports sensitivities."""
    phi = rt.first_stage_regressions(v_df, y_1m, h=1)
    phi.name = "phi"
    phi.to_csv(OUTPUT_DIR / "stage_1_phi.csv", index_label="Portfolio")

    return phi

def run_stage_2_analysis(v_df, phi):
    """Runs Stage 2 to extract the latent factor and exports to CSV."""
    F_series = rt.second_stage_regressions(v_df, phi)
    F_series.name = "F_t"
    F_series.to_csv(OUTPUT_DIR / "stage_2_factor.csv", index_label="Date")

    return F_series

def run_stage_3_analysis(F_series, y_1m):
    """Runs Stage 3 Predictive relationship and exports the aligned data."""
    model = rt.third_stage_regression(F_series, y_1m, h=1)
    df_plot = pd.concat([F_series.rename('F_t'), y_1m.shift(-1).rename('Future_Mkt_Ret')], axis=1).dropna()
    df_plot.to_csv(OUTPUT_DIR / "stage_3_predictive.csv", index_label="Date")

    return model, df_plot

def run_pls_evaluations(data, train_start, test_start, test_end):
    """Runs the PLS evaluations for a specific timeframe."""
    log_returns = data['Market_Returns']['Log_Mkt'].loc[train_start:test_end]
    
    y_1m = log_returns
    y_12m = log_returns.rolling(12).sum().dropna()
    
    portfolios = [
        ("6 Portfolios", "6_Portfolios_2x3_BM"),
        ("25 Portfolios", "25_Portfolios_5x5_BM"),
        ("100 Portfolios", "100_Portfolios_10x10_BM")
    ]
    
    results = []

    for label, bm_key in portfolios:
        v_df = data[bm_key].loc[train_start:test_end]
        
        v_df_12m = v_df.loc[v_df.index.intersection(y_12m.index)]
        y_12m_aligned = y_12m.loc[v_df_12m.index]
        
        v_df_1m = v_df.loc[v_df.index.intersection(y_1m.index)]
        y_1m_aligned = y_1m.loc[v_df_1m.index]
        
        is_12m = pls_regression.run_in_sample(v_df_12m, y_12m_aligned, h=12)
        oos_12m = pls_regression.run_out_of_sample(v_df_12m, y_12m_aligned, h=12, start_date=test_start)
        
        is_1m = pls_regression.run_in_sample(v_df_1m, y_1m_aligned, h=1)
        oos_1m = pls_regression.run_out_of_sample(v_df_1m, y_1m_aligned, h=1, start_date=test_start)
        
        results.append({
            "Portfolio Set": label,
            "1-Year IS": is_12m,
            "1-Year OOS": oos_12m,
            "1-Month IS": is_1m,
            "1-Month OOS": oos_1m
        })

    return pd.DataFrame(results).set_index("Portfolio Set")


def replicate_table_1(data):
    """Replicates Kelly and Pruitt Table 1 for both original and modern timeframes."""
    
    # Original Period (Test: 1980 - 2010)
    df_original = run_pls_evaluations(data, START_TRAIN_DATE, START_TEST_DATE, END_TEST_DATE)
    df_original.to_csv(OUTPUT_DIR / "table_1_results_original.csv")
    
    # Modern Period (Test: 2011 - 2024)
    modern_test_start = END_TEST_DATE + pd.Timedelta(days=1)
    df_modern = run_pls_evaluations(data, START_TRAIN_DATE, modern_test_start, CURRENT_DATE)
    df_modern.to_csv(OUTPUT_DIR / "table_1_results_modern.csv")

    return df_original, df_modern

def run_all():
    """Main function that maps out and calls all individual pipeline components in sequence."""
    print("Ensuring output directory exists...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Loading cleaned datasets...")
    data = load_data.clean_kelly_pruitt_data(load_from_cache=True)
    
    print("Running data sparsity analysis...")
    data_sparsity_analysis(data)
    
    print("Generating summary statistics table...")
    generate_summary_statistics(data)
    
    # Align primary data target for stage analysis
    bm_25 = data["25_Portfolios_5x5_BM"]
    y_1m = data['Market_Returns']['Log_Mkt']
    common_idx = bm_25.index.intersection(y_1m.index)
    v_df_aligned = bm_25.loc[common_idx]
    y_1m_aligned = y_1m.loc[common_idx]
    
    print("Running Stage 1 Regression Analysis...")
    phi = run_stage_1_analysis(v_df_aligned, y_1m_aligned)
    
    print("Running Stage 2 Regression Analysis...")
    F_series = run_stage_2_analysis(v_df_aligned, phi)
    
    print("Running Stage 3 Regression Analysis...")
    run_stage_3_analysis(F_series, y_1m_aligned)
    
    print("Replicating Table 1...")
    replicate_table_1(data)
    
    print("Replication math complete! Intermediate CSVs saved to output directory.")

if __name__ == "__main__":
    run_all()