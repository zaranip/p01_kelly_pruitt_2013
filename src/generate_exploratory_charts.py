"""
Generate exploratory charts for Kelly & Pruitt (2013) replication.

These charts verify that the data was successfully pulled from WRDS.
They show:
1. Market returns time series (from CRSP)
2. Compustat coverage over time (number of firms)
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from settings import config

DATA_DIR = Path(config("DATA_DIR"))
OUTPUT_DIR = Path(config("OUTPUT_DIR"))


def create_market_returns_chart():
    """
    Create an exploratory chart showing aggregate market returns.
    
    This verifies that CRSP market data was successfully pulled.
    """
    # Load market returns data
    df = pd.read_parquet(DATA_DIR / "CRSP_market_returns.parquet")
    
    # Calculate cumulative return
    df = df.sort_values("date")
    df["cum_vwretd"] = (1 + df["vwretd"]).cumprod()
    
    # Create chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["cum_vwretd"],
        mode="lines",
        name="Value-Weighted Return (with dividends)",
        line=dict(color="blue")
    ))
    
    fig.update_layout(
        title="CRSP Value-Weighted Market Returns (Cumulative)",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (Growth of $1)",
        yaxis_type="log",
        template="plotly_white",
        hovermode="x unified"
    )
    
    # Save as HTML
    output_path = OUTPUT_DIR / "chart_market_returns.html"
    fig.write_html(str(output_path))
    print(f"Saved market returns chart to {output_path}")
    
    return fig


def create_compustat_coverage_chart():
    """
    Create an exploratory chart showing Compustat coverage over time.
    
    This verifies that Compustat data was successfully pulled.
    """
    # Load Compustat data
    df = pd.read_parquet(DATA_DIR / "Compustat.parquet")
    
    # Count firms per year
    firms_per_year = df.groupby("year")["gvkey"].nunique().reset_index()
    firms_per_year.columns = ["year", "num_firms"]
    
    # Create chart
    fig = px.bar(
        firms_per_year,
        x="year",
        y="num_firms",
        title="Compustat Coverage: Number of Firms by Year",
        labels={"year": "Year", "num_firms": "Number of Firms"},
        template="plotly_white"
    )
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Firms",
        hovermode="x unified"
    )
    
    # Save as HTML
    output_path = OUTPUT_DIR / "chart_compustat_coverage.html"
    fig.write_html(str(output_path))
    print(f"Saved Compustat coverage chart to {output_path}")
    
    return fig


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate charts
    create_market_returns_chart()
    create_compustat_coverage_chart()
    
    print("Exploratory charts generated successfully!")
