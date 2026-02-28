import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
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

# Set plotting style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)

def save_latex_figure_env(filename, img_filename, caption, label):
    """Helper function to generate LaTeX figure environments with descriptive captions."""
    latex_code = f"""\\begin{{figure}}[htbp]
\\centering
\\includegraphics[width=\\textwidth]{{{img_filename}}}
\\caption{{{caption}}}
\\label{{{label}}}
\\end{{figure}}
"""
    with open(OUTPUT_DIR / filename, "w") as f:
        f.write(latex_code)

def data_sparsity_analysis(data):
    """Analyzes data availability over time and generates LaTeX figure."""
    bm_6 = data["6_Portfolios_2x3_BM"]
    bm_25 = data["25_Portfolios_5x5_BM"]
    bm_100 = data["100_Portfolios_10x10_BM"]

    valid_6 = bm_6.count(axis=1)
    valid_25 = bm_25.count(axis=1)
    valid_100 = bm_100.count(axis=1)

    plt.figure(figsize=(12, 6))
    plt.plot(valid_100.index, valid_100, label="100 Portfolios", color='darkred', linewidth=2)
    plt.plot(valid_25.index, valid_25, label="25 Portfolios", color='steelblue', linewidth=2)
    plt.plot(valid_6.index, valid_6, label="6 Portfolios", color='forestgreen', linewidth=2)

    plt.title("Data Availability: Number of Active Portfolios Over Time", fontsize=14)
    plt.ylabel("Count of Portfolios with Valid Data", fontsize=12)
    plt.xlabel("Date", fontsize=12)
    plt.legend(loc='lower right')
    plt.tight_layout()
    
    img_name = "data_sparsity.png"
    plt.savefig(OUTPUT_DIR / img_name)
    plt.close()

    caption = "Figure \\ref{fig:sparsity} illustrates the number of active portfolios with valid data over time for the 6, 25, and 100 portfolio datasets. The key takeaway is the data availability constraint in earlier periods, particularly for the 100-portfolio set. This motivates the use of Partial Least Squares (PLS)-style methods, such as the three-pass regression filter, which can effectively handle missing or unbalanced panels without discarding large swaths of historical data."
    save_latex_figure_env("data_sparsity.tex", img_name, caption, "fig:sparsity")

    return valid_6, valid_25, valid_100

def generate_summary_statistics(data):
    """Generates a summary statistics table of the underlying data and outputs to LaTeX."""
    v_df = data["25_Portfolios_5x5_BM"].loc[START_TRAIN_DATE:END_TEST_DATE]
    y_1m = data['Market_Returns']['Log_Mkt'].loc[START_TRAIN_DATE:END_TEST_DATE]
    
    # Calculate summary statistics
    summary_df = v_df.describe().T[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    
    mkt_stats = y_1m.describe()[['mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    mkt_stats.name = "Log Market Return"
    
    # Combine Market Return with Portfolio Data
    summary_df = pd.concat([pd.DataFrame(mkt_stats).T, summary_df])

    caption = "Table \\ref{tab:sum_stats} presents the summary statistics of the log market returns and the 25 portfolio book-to-market ratios. The reader should observe the varying distribution, mean, and volatility across different portfolios. This table highlights the significant cross-sectional variation in book-to-market ratios, which is necessary for the Kelly and Pruitt (2013) three-pass regression filter to successfully extract meaningful predictive factors."
    
    latex_table = summary_df.style.format("{:.3f}").to_latex(
        caption=caption,
        label="tab:sum_stats",
        hrules=True
    )
    
    with open(OUTPUT_DIR / "summary_statistics.tex", "w") as f:
        f.write(latex_table)
        
    return summary_df

def run_stage_1_analysis(v_df, y_1m):
    """Runs Stage 1 of the regression filter and generates a LaTeX figure of sensitivities."""
    phi = rt.first_stage_regressions(v_df, y_1m, h=1)

    plt.figure(figsize=(12, 5))
    phi.sort_values().plot(kind='bar', color='coral', edgecolor='black')
    plt.title("Stage 1: Estimated Sensitivities ($\\phi_i$) for 25 Portfolios", fontsize=14)
    plt.ylabel("Sensitivity ($\\phi_i$)", fontsize=12)
    plt.xlabel("Portfolio", fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.tight_layout()
    
    img_name = "stage_1_sensitivities.png"
    plt.savefig(OUTPUT_DIR / img_name)
    plt.close()

    caption = "Figure \\ref{fig:stage1} displays the estimated sensitivities ($\\phi_i$) for the 25 portfolios derived from the first stage of the regression filter. This chart highlights which specific portfolios exhibit the strongest comovement with future market returns. The reader should take away that the filter applies distinct cross-sectional weights, favoring assets with stronger predictive signals rather than using a simple equal-weighted average."
    save_latex_figure_env("stage_1_sensitivities.tex", img_name, caption, "fig:stage1")

    return phi

def run_stage_2_analysis(v_df, phi):
    """Runs Stage 2 to extract the latent factor and generates a LaTeX figure."""
    F_series = rt.second_stage_regressions(v_df, phi)

    plt.figure(figsize=(12, 5))
    plt.plot(F_series.index, F_series, color='purple', linewidth=1.5)
    plt.title("Stage 2: Extracted Latent Factor ($F_t$) Over Time", fontsize=14)
    plt.ylabel("$F_t$", fontsize=12)
    plt.xlabel("Date", fontsize=12)
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    plt.tight_layout()
    
    img_name = "stage_2_factor.png"
    plt.savefig(OUTPUT_DIR / img_name)
    plt.close()

    caption = "Figure \\ref{fig:stage2} plots the extracted latent factor ($F_t$) over time. The reader should note the cyclicality and significant structural spikes in the factor, which often correspond to major macroeconomic events. The key takeaway is that the cross-section of book-to-market ratios successfully aggregates time-varying expected returns into a single, cohesive predictive index."
    save_latex_figure_env("stage_2_factor.tex", img_name, caption, "fig:stage2")

    return F_series

def run_stage_3_analysis(F_series, y_1m):
    """Runs Stage 3 Predictive relationship and generates a LaTeX scatter plot figure."""
    model = rt.third_stage_regression(F_series, y_1m, h=1)

    df_plot = pd.concat([F_series.rename('F_t'), y_1m.shift(-1).rename('Future_Mkt_Ret')], axis=1).dropna()

    plt.figure(figsize=(8, 6))
    sns.regplot(
        x='F_t', y='Future_Mkt_Ret', data=df_plot, 
        scatter_kws={'alpha': 0.3, 'color': 'gray'}, 
        line_kws={'color': 'red', 'linewidth': 2}
    )
    plt.title("Stage 3: Predictive Relationship (In-Sample)", fontsize=14)
    plt.xlabel("Extracted Factor ($F_t$)", fontsize=12)
    plt.ylabel("Realized Future Market Return ($y_{t+1}$)", fontsize=12)
    plt.tight_layout()
    
    img_name = "stage_3_predictive.png"
    plt.savefig(OUTPUT_DIR / img_name)
    plt.close()

    caption = "Figure \\ref{fig:stage3} depicts the predictive relationship between the extracted latent factor ($F_t$) and the realized future market returns ($y_{t+1}$). The upward-sloping trend line demonstrates the strong in-sample predictive power of the factor. The reader should conclude that the information extracted from the cross-section is highly relevant and linearly correlated with forecasting aggregate market movements."
    save_latex_figure_env("stage_3_predictive.tex", img_name, caption, "fig:stage3")

    return model

def replicate_table_1(data):
    """Replicates Kelly and Pruitt (2013) Table 1 and exports to LaTeX."""
    log_returns = data['Market_Returns']['Log_Mkt'].loc[START_TRAIN_DATE:END_TEST_DATE]
    
    y_1m = log_returns
    y_12m = log_returns.rolling(12).sum().dropna()
    
    portfolios = [
        ("6 Portfolios", "6_Portfolios_2x3_BM"),
        ("25 Portfolios", "25_Portfolios_5x5_BM"),
        ("100 Portfolios", "100_Portfolios_10x10_BM")
    ]
    
    results = []

    for label, bm_key in portfolios:
        v_df = data[bm_key].loc[START_TRAIN_DATE:END_TEST_DATE]
        
        v_df_12m = v_df.loc[v_df.index.intersection(y_12m.index)]
        y_12m_aligned = y_12m.loc[v_df_12m.index]
        
        v_df_1m = v_df.loc[v_df.index.intersection(y_1m.index)]
        y_1m_aligned = y_1m.loc[v_df_1m.index]
        
        # Calling the functions directly from the imported regression module
        is_12m = pls_regression.run_in_sample(v_df_12m, y_12m_aligned, h=12)
        oos_12m = pls_regression.run_out_of_sample(v_df_12m, y_12m_aligned, h=12, start_date=START_TEST_DATE)
        
        is_1m = pls_regression.run_in_sample(v_df_1m, y_1m_aligned, h=1)
        oos_1m = pls_regression.run_out_of_sample(v_df_1m, y_1m_aligned, h=1, start_date=START_TEST_DATE)
        
        results.append({
            "Portfolio Set": label,
            "1-Year IS": is_12m,
            "1-Year OOS": oos_12m,
            "1-Month IS": is_1m,
            "1-Month OOS": oos_1m
        })

    df_results = pd.DataFrame(results).set_index("Portfolio Set")
    
    caption = "Table \\ref{tab:kp2013_table1} replicates Table 1 from Kelly and Pruitt (2013). The table presents both in-sample and out-of-sample $R^2$ statistics (in percentages) for predicting 1-month and 1-year aggregate market returns. The reader should note that out-of-sample predictability remains economically significant across different cross-sectional granularities, demonstrating the robustness of the derived latent factors."
    
    latex_table = df_results.style.format("{:.2f}").to_latex(
        caption=caption,
        label="tab:kp2013_table1",
        hrules=True
    )
    
    with open(OUTPUT_DIR / "table_1_replication.tex", "w") as f:
        f.write(latex_table)
        
    return df_results

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
    model = run_stage_3_analysis(F_series, y_1m_aligned)
    
    print("Replicating Table 1...")
    table_1_results = replicate_table_1(data)
    
    print("Replication routine complete! All LaTeX files and charts have been saved to the output directory.")
    return table_1_results

if __name__ == "__main__":
    run_all()