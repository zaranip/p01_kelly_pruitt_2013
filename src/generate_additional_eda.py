"""
Additional EDA charts for Kelly & Pruitt (2013) replication.

Provides comprehensive exploration of all data sources:
1. CRSP stock coverage over time
2. Market capitalization distribution
3. Fama-French factors time series
4. CRSP-Compustat link coverage
5. Book equity components availability
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from settings import config

DATA_DIR = Path(config("DATA_DIR"))
OUTPUT_DIR = Path(config("OUTPUT_DIR"))


def create_crsp_stock_coverage_chart():
    """
    Create chart showing CRSP stock universe coverage over time.
    """
    df = pd.read_parquet(DATA_DIR / "CRSP_monthly_stock.parquet")
    
    # Count unique stocks per month
    df['year_month'] = df['date'].dt.to_period('M')
    coverage = df.groupby('year_month').agg({
        'permno': 'nunique',
        'market_cap': 'sum'
    }).reset_index()
    coverage.columns = ['year_month', 'num_stocks', 'total_market_cap']
    coverage['date'] = coverage['year_month'].dt.to_timestamp()
    
    # Create dual-axis chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=coverage['date'], y=coverage['num_stocks'],
                   name="Number of Stocks", line=dict(color='blue')),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=coverage['date'], y=coverage['total_market_cap'] / 1e12,
                   name="Total Market Cap ($T)", line=dict(color='red')),
        secondary_y=True,
    )
    
    fig.update_layout(
        title="CRSP Stock Universe Coverage Over Time",
        template="plotly_white",
        hovermode="x unified"
    )
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Number of Stocks", secondary_y=False)
    fig.update_yaxes(title_text="Total Market Cap ($Trillion)", secondary_y=True)
    
    output_path = OUTPUT_DIR / "chart_crsp_stock_coverage.html"
    fig.write_html(str(output_path))
    print(f"Saved CRSP stock coverage chart to {output_path}")
    return fig


def create_market_cap_distribution_chart():
    """
    Create chart showing market cap distribution evolution.
    """
    df = pd.read_parquet(DATA_DIR / "CRSP_monthly_stock.parquet")
    
    # Get end-of-year snapshots for selected years
    df['year'] = df['date'].dt.year
    sample_years = [1960, 1980, 2000, 2020]
    
    fig = go.Figure()
    colors = ['blue', 'green', 'orange', 'red']
    
    for year, color in zip(sample_years, colors):
        year_data = df[(df['year'] == year) & (df['market_cap'] > 0)]['market_cap']
        if len(year_data) > 0:
            # Use log scale for market cap
            log_mcap = year_data.apply(lambda x: x / 1e6)  # Convert to millions
            fig.add_trace(go.Histogram(
                x=log_mcap,
                name=str(year),
                opacity=0.6,
                marker_color=color
            ))
    
    fig.update_layout(
        title="Market Capitalization Distribution (Selected Years)",
        xaxis_title="Market Cap ($Millions)",
        yaxis_title="Number of Stocks",
        xaxis_type="log",
        barmode='overlay',
        template="plotly_white",
        legend_title="Year"
    )
    
    output_path = OUTPUT_DIR / "chart_market_cap_distribution.html"
    fig.write_html(str(output_path))
    print(f"Saved market cap distribution chart to {output_path}")
    return fig


def create_ff_factors_chart():
    """
    Create chart showing Fama-French factors over time.
    """
    df = pd.read_parquet(DATA_DIR / "FF_FACTORS.parquet")
    df = df.sort_values('date')
    
    # Calculate cumulative returns
    factors = ['mktrf', 'smb', 'hml']
    factor_names = {'mktrf': 'Market-RF', 'smb': 'SMB', 'hml': 'HML'}
    
    fig = go.Figure()
    colors = {'mktrf': 'blue', 'smb': 'green', 'hml': 'red'}
    
    for factor in factors:
        # Handle potential None values
        df_clean = df.dropna(subset=[factor])
        cum_ret = (1 + df_clean[factor]).cumprod()
        fig.add_trace(go.Scatter(
            x=df_clean['date'],
            y=cum_ret,
            mode='lines',
            name=factor_names[factor],
            line=dict(color=colors[factor])
        ))
    
    fig.update_layout(
        title="Fama-French Factors (Cumulative Returns)",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (Growth of $1)",
        yaxis_type="log",
        template="plotly_white",
        hovermode="x unified"
    )
    
    output_path = OUTPUT_DIR / "chart_ff_factors.html"
    fig.write_html(str(output_path))
    print(f"Saved Fama-French factors chart to {output_path}")
    return fig


def create_ccm_link_coverage_chart():
    """
    Create chart showing CRSP-Compustat link table coverage.
    """
    df = pd.read_parquet(DATA_DIR / "CRSP_Comp_Link_Table.parquet")
    
    # Analyze link types
    link_summary = df.groupby('linktype').size().reset_index(name='count')
    
    fig = px.bar(
        link_summary,
        x='linktype',
        y='count',
        title="CRSP-Compustat Link Table: Link Types",
        labels={'linktype': 'Link Type', 'count': 'Number of Links'},
        template="plotly_white"
    )
    
    output_path = OUTPUT_DIR / "chart_ccm_link_coverage.html"
    fig.write_html(str(output_path))
    print(f"Saved CCM link coverage chart to {output_path}")
    return fig


def create_compustat_variables_availability_chart():
    """
    Create chart showing availability of key book equity components over time.
    """
    df = pd.read_parquet(DATA_DIR / "Compustat.parquet")
    
    # Key variables for book equity calculation
    key_vars = ['seq', 'ceq', 'at', 'lt', 'pstk', 'txditc']
    
    # Calculate availability by year
    availability = []
    for year in df['year'].unique():
        year_data = df[df['year'] == year]
        total = len(year_data)
        if total > 0:
            row = {'year': year, 'total_firms': total}
            for var in key_vars:
                row[f'{var}_pct'] = (year_data[var].notna().sum() / total) * 100
            availability.append(row)
    
    avail_df = pd.DataFrame(availability).sort_values('year')
    
    fig = go.Figure()
    colors = {'seq': 'blue', 'ceq': 'green', 'at': 'red', 'lt': 'purple', 'pstk': 'orange', 'txditc': 'brown'}
    
    for var in key_vars:
        fig.add_trace(go.Scatter(
            x=avail_df['year'],
            y=avail_df[f'{var}_pct'],
            mode='lines',
            name=var.upper(),
            line=dict(color=colors[var])
        ))
    
    fig.update_layout(
        title="Compustat: Availability of Book Equity Components Over Time",
        xaxis_title="Year",
        yaxis_title="% of Firms with Data Available",
        template="plotly_white",
        hovermode="x unified",
        yaxis_range=[0, 105]
    )
    
    output_path = OUTPUT_DIR / "chart_compustat_variables.html"
    fig.write_html(str(output_path))
    print(f"Saved Compustat variables availability chart to {output_path}")
    return fig


def create_data_summary_report():
    """
    Generate a text summary of all data files.
    """
    summary = []
    summary.append("=" * 70)
    summary.append("KELLY & PRUITT (2013) REPLICATION - DATA SUMMARY REPORT")
    summary.append("=" * 70)
    
    # CRSP Monthly Stock
    df = pd.read_parquet(DATA_DIR / "CRSP_monthly_stock.parquet")
    summary.append("\n1. CRSP MONTHLY STOCK DATA")
    summary.append(f"   - Records: {len(df):,}")
    summary.append(f"   - Unique stocks (permno): {df['permno'].nunique():,}")
    summary.append(f"   - Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    summary.append(f"   - Key columns: permno, date, ret, prc, shrout, market_cap")
    
    # CRSP Market Returns
    df = pd.read_parquet(DATA_DIR / "CRSP_market_returns.parquet")
    summary.append("\n2. CRSP MARKET RETURNS")
    summary.append(f"   - Records: {len(df):,}")
    summary.append(f"   - Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    summary.append(f"   - Key columns: vwretd (value-weighted), ewretd (equal-weighted)")
    
    # Compustat
    df = pd.read_parquet(DATA_DIR / "Compustat.parquet")
    summary.append("\n3. COMPUSTAT FUNDAMENTALS")
    summary.append(f"   - Records: {len(df):,}")
    summary.append(f"   - Unique firms (gvkey): {df['gvkey'].nunique():,}")
    summary.append(f"   - Year range: {df['year'].min()} to {df['year'].max()}")
    summary.append(f"   - Key columns: gvkey, datadate, seq, ceq, at, lt, pstk (for book equity)")
    
    # CCM Link
    df = pd.read_parquet(DATA_DIR / "CRSP_Comp_Link_Table.parquet")
    summary.append("\n4. CRSP-COMPUSTAT LINK TABLE")
    summary.append(f"   - Records: {len(df):,}")
    summary.append(f"   - Unique gvkey: {df['gvkey'].nunique():,}")
    summary.append(f"   - Unique permno: {df['permno'].nunique():,}")
    summary.append(f"   - Link types: {df['linktype'].value_counts().to_dict()}")
    
    # FF Factors
    df = pd.read_parquet(DATA_DIR / "FF_FACTORS.parquet")
    summary.append("\n5. FAMA-FRENCH FACTORS")
    summary.append(f"   - Records: {len(df):,}")
    summary.append(f"   - Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    summary.append(f"   - Factors: mktrf, smb, hml, rf")
    
    summary.append("\n" + "=" * 70)
    summary.append("DATA STATUS: ALL REQUIRED DATA FOR KELLY & PRUITT (2013) IS AVAILABLE")
    summary.append("=" * 70)
    
    report_text = "\n".join(summary)
    
    # Save report
    output_path = OUTPUT_DIR / "data_summary_report.txt"
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    print(report_text)
    print(f"\nSaved data summary report to {output_path}")
    
    return report_text


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate all charts
    print("\nGenerating additional EDA charts...")
    print("-" * 50)
    
    create_crsp_stock_coverage_chart()
    create_market_cap_distribution_chart()
    create_ff_factors_chart()
    create_ccm_link_coverage_chart()
    create_compustat_variables_availability_chart()
    
    print("-" * 50)
    print("\nGenerating data summary report...")
    print("-" * 50)
    create_data_summary_report()
    
    print("\n" + "=" * 50)
    print("ALL EDA CHARTS AND REPORTS GENERATED SUCCESSFULLY!")
    print("=" * 50)
