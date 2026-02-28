"""
Generate Kelly & Pruitt Replication Figures
===========================================
Generates all figures and tables for the replication report handout.
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from settings import config

OUTPUT_DIR = Path(config("OUTPUT_DIR"))
END_TEST_DATE = config("END_TEST_DATE")

# UChicago color palette
MAROON = "#800000"
TERRACOTTA = "#DE7C00"
DARK_GREY = "#737373"
GREEN = "#319866"
RED = "#CC0000"


def generate_report_date():
    """Writes the analysis date to a text file."""
    with open(OUTPUT_DIR / "report_date.txt", "w") as f:
        # Check if it has a strftime method (like datetime or Timestamp) to format it nicely
        if hasattr(END_TEST_DATE, "strftime"):
            f.write(END_TEST_DATE.strftime('%B %Y'))
        else:
            # Fallback to a standard string cast if it's already a string or other type
            f.write(str(END_TEST_DATE))
    print("  Saved report_date.txt")


def generate_data_sparsity_chart():
    """Generates the data availability constraints chart."""
    print("Generating Data Sparsity Chart...")
    df_sparsity = pd.read_csv(OUTPUT_DIR / "data_sparsity.csv", index_col=0, parse_dates=True)
    
    fig, ax = plt.subplots(figsize=(6, 3.5))
    if "100_Portfolios" in df_sparsity.columns:
        ax.plot(df_sparsity.index, df_sparsity["100_Portfolios"], label="100 Portfolios", color=MAROON, linewidth=1.5)
    ax.plot(df_sparsity.index, df_sparsity["25_Portfolios"], label="25 Portfolios", color=DARK_GREY, linewidth=1.5)
    ax.plot(df_sparsity.index, df_sparsity["6_Portfolios"], label="6 Portfolios", color=GREEN, linewidth=1.5)
    
    ax.set_ylabel("Valid Portfolios", fontsize=9)
    ax.legend(loc='lower right', frameon=True, fontsize=8)
    for spine in ax.spines.values(): 
        spine.set_visible(False)
        
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "data_sparsity.png", bbox_inches="tight")
    plt.close(fig)


def generate_summary_statistics_table():
    """Generates the raw tabular LaTeX for summary statistics."""
    print("Generating Summary Statistics Table...")
    summary_df = pd.read_csv(OUTPUT_DIR / "summary_statistics.csv", index_col=0)
    summary_df.columns = [str(c).replace('%', '\\%') for c in summary_df.columns]
    
    with open(OUTPUT_DIR / "summary_statistics.tex", "w") as f:
        f.write(summary_df.style.format("{:.3f}").to_latex(hrules=True))


def generate_stage_1_chart():
    """Generates the estimated sensitivities bar chart."""
    print("Generating Stage 1 Chart...")
    phi = pd.read_csv(OUTPUT_DIR / "stage_1_phi.csv", index_col=0)
    
    fig, ax = plt.subplots(figsize=(6, 3))
    phi.sort_values(by="phi")["phi"].plot(kind='bar', color=TERRACOTTA, ax=ax)
    ax.set_ylabel("$\\phi_i$", fontsize=9)
    ax.set_xlabel("")
    plt.xticks(rotation=45, ha='right', fontsize=6)
    for spine in ax.spines.values(): 
        spine.set_visible(False)
        
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "stage_1_sensitivities.png", bbox_inches="tight")
    plt.close(fig)


def generate_stage_2_chart():
    """Generates the extracted latent factor time-series chart."""
    print("Generating Stage 2 Chart...")
    F_series = pd.read_csv(OUTPUT_DIR / "stage_2_factor.csv", index_col=0, parse_dates=True)
    
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(F_series.index, F_series["F_t"], color=MAROON, linewidth=1)
    ax.axhline(0, color=DARK_GREY, linestyle='--', linewidth=0.8)
    ax.set_ylabel("$F_t$", fontsize=9)
    for spine in ax.spines.values(): 
        spine.set_visible(False)
        
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "stage_2_factor.png", bbox_inches="tight")
    plt.close(fig)


def generate_stage_3_chart():
    """Generates the in-sample predictive relationship scatter plot."""
    print("Generating Stage 3 Predictive Chart...")
    df_plot = pd.read_csv(OUTPUT_DIR / "stage_3_predictive.csv", index_col=0)
    
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.regplot(
        x='F_t', y='Future_Mkt_Ret', data=df_plot, ax=ax, 
        scatter_kws={'alpha': 0.3, 'color': DARK_GREY}, 
        line_kws={'color': RED, 'linewidth': 1.5}
    )
    ax.set_xlabel("$F_t$", fontsize=9)
    ax.set_ylabel("$y_{t+1}$", fontsize=9)
    for spine in ax.spines.values(): 
        spine.set_visible(False)
        
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "stage_3_predictive.png", bbox_inches="tight")
    plt.close(fig)


def generate_table_1_results():
    """Generates the raw tabular LaTeX for Table 1 replication results."""
    print("Formatting Table 1 Results...")
    df_results = pd.read_csv(OUTPUT_DIR / "table_1_results.csv", index_col=0)
    with open(OUTPUT_DIR / "table_1_replication.tex", "w") as f:
        f.write(df_results.style.format("{:.2f}").to_latex(hrules=True))


def main():
    print("Loading intermediate analytical results...")
    sns.set_theme(style="whitegrid", font_scale=1.0)
    
    generate_report_date()
    generate_data_sparsity_chart()
    generate_summary_statistics_table()
    generate_stage_1_chart()
    generate_stage_2_chart()
    generate_stage_3_chart()
    generate_table_1_results()

    print("\nDone. Run 'doit compile_replication_report' to build the PDF.")


if __name__ == "__main__":
    main()