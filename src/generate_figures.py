"""
Generates visualizations and LaTeX tables for the replication report.

Reads intermediate analytical results from CSV files and outputs formatted 
matplotlib/seaborn charts (e.g., data sparsity, factor sensitivities, 
latent factor time-series, and predictive relationships) as well as 
styled LaTeX tabular data for the final PDF handout.
"""

import numpy as np
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
GOLDENROD = "#EAAA00"


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

def format_table_1_latex(csv_path, tex_path):
    """Reads a results CSV and outputs a formatted LaTeX table."""
    df_results = pd.read_csv(csv_path, index_col=0)
    with open(tex_path, "w") as f:
        f.write(df_results.style.format("{:.2f}").to_latex(hrules=True))


def generate_comparison_table():
    """Generates a side-by-side LaTeX table comparing our results to the paper."""
    print("Generating Comparison Table...")
    our = pd.read_csv(OUTPUT_DIR / "table_1_results_original.csv", index_col=0)
    paper = pd.DataFrame({
        "1-Year IS": {"6 Portfolios": 7.72, "25 Portfolios": 13.50, "100 Portfolios": 18.05},
        "1-Year OOS": {"6 Portfolios": 5.81, "25 Portfolios": 3.49, "100 Portfolios": 13.07},
        "1-Month IS": {"6 Portfolios": 0.60, "25 Portfolios": 1.12, "100 Portfolios": 2.38},
        "1-Month OOS": {"6 Portfolios": 0.65, "25 Portfolios": 0.77, "100 Portfolios": 0.93},
    })
    paper.index.name = "Portfolio Set"

    lines = []
    lines.append(r"\begin{tabular}{l rr rr rr rr}")
    lines.append(r"\toprule")
    lines.append(r" & \multicolumn{2}{c}{1-Year IS} & \multicolumn{2}{c}{1-Year OOS} & \multicolumn{2}{c}{1-Month IS} & \multicolumn{2}{c}{1-Month OOS} \\")
    lines.append(r"\cmidrule(lr){2-3} \cmidrule(lr){4-5} \cmidrule(lr){6-7} \cmidrule(lr){8-9}")
    lines.append(r"Portfolio Set & Paper & Ours & Paper & Ours & Paper & Ours & Paper & Ours \\")
    lines.append(r"\midrule")
    for idx in paper.index:
        vals = []
        for col in ["1-Year IS", "1-Year OOS", "1-Month IS", "1-Month OOS"]:
            vals.append(f"{paper.loc[idx, col]:.2f}")
            vals.append(f"{our.loc[idx, col]:.2f}")
        lines.append(f"{idx} & {' & '.join(vals)} \\\\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    with open(OUTPUT_DIR / "table_1_comparison.tex", "w") as f:
        f.write("\n".join(lines))


def generate_comparison_chart():
    """Generates a grouped bar chart comparing our R-squared to the paper's."""
    print("Generating Comparison Bar Chart...")
    our = pd.read_csv(OUTPUT_DIR / "table_1_results_original.csv", index_col=0)
    paper = pd.DataFrame({
        "1-Year IS": {"6 Portfolios": 7.72, "25 Portfolios": 13.50, "100 Portfolios": 18.05},
        "1-Year OOS": {"6 Portfolios": 5.81, "25 Portfolios": 3.49, "100 Portfolios": 13.07},
        "1-Month IS": {"6 Portfolios": 0.60, "25 Portfolios": 1.12, "100 Portfolios": 2.38},
        "1-Month OOS": {"6 Portfolios": 0.65, "25 Portfolios": 0.77, "100 Portfolios": 0.93},
    })

    metrics = ["1-Year IS", "1-Year OOS", "1-Month IS", "1-Month OOS"]
    portfolios = ["6 Portfolios", "25 Portfolios", "100 Portfolios"]

    fig, axes = plt.subplots(1, 4, figsize=(12, 3.5), sharey=False)
    bar_width = 0.3
    x = np.arange(len(portfolios))

    for i, metric in enumerate(metrics):
        ax = axes[i]
        paper_vals = [paper.loc[p, metric] for p in portfolios]
        our_vals = [our.loc[p, metric] for p in portfolios]

        ax.bar(x - bar_width/2, paper_vals, bar_width, label="Paper", color=MAROON, alpha=0.85)
        ax.bar(x + bar_width/2, our_vals, bar_width, label="Ours", color=GOLDENROD, alpha=0.85)

        ax.set_title(metric, fontsize=10, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(["6P", "25P", "100P"], fontsize=8)
        ax.set_ylabel("$R^2$ (\%)", fontsize=8)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(axis='y', alpha=0.3)

        if i == 0:
            ax.legend(fontsize=7, frameon=True)

    fig.suptitle("Table 1 Replication: Paper vs. Our Results", fontsize=11, fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "table_1_comparison.png", bbox_inches="tight", dpi=150)
    plt.close(fig)


def generate_table_1_results():
    """Generates the raw tabular LaTeX for both original and modern results."""
    print("Formatting Table 1 Results (Original Period)...")
    format_table_1_latex(
        OUTPUT_DIR / "table_1_results_original.csv",
        OUTPUT_DIR / "table_1_replication_original.tex"
    )

    print("Formatting Table 1 Results (Modern Period)...")
    format_table_1_latex(
        OUTPUT_DIR / "table_1_results_modern.csv",
        OUTPUT_DIR / "table_1_replication_modern.tex"
    )

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
    generate_comparison_table()
    generate_comparison_chart()

    print("\nDone. Run 'doit compile_replication_report' to build the PDF.")


if __name__ == "__main__":
    main()