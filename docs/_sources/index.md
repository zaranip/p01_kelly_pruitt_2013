# Market Expectations in the Cross-Section of Present Values

Last updated: {sub-ref}`today` 


## Table of Contents

```{toctree}
:maxdepth: 1
:caption: Notebooks 📖
notebooks/P01/summary_statistics
```



```{toctree}
:maxdepth: 1
:caption: Pipeline Charts 📈
charts.md
```

```{postlist}
:format: "{title}"
```


```{toctree}
:maxdepth: 1
:caption: Pipeline Dataframes 📊
dataframes/P01/ccm_link.md
dataframes/P01/compustat.md
dataframes/P01/crsp_market_returns.md
dataframes/P01/crsp_monthly_stock.md
dataframes/P01/ken_french_25_portfolios.md
dataframes/P01/ken_french_ff_factors.md
```


```{toctree}
:maxdepth: 1
:caption: Appendix 💡
myst_markdown_demos.md
apidocs/index
```


## Pipeline Specs
| Pipeline Name                   | Market Expectations in the Cross-Section of Present Values                       |
|---------------------------------|--------------------------------------------------------|
| Pipeline ID                     | [P01](./index.md)              |
| Lead Pipeline Developer         | Zara and Dylan             |
| Contributors                    | Zara, Dylan           |
| Git Repo URL                    | https://github.com/zaranip/p01_kelly_pruitt_2013                        |
| Pipeline Web Page               | <a href="file://C:/Users/Zara/Documents/GitHub/FINM-Winter/full-stack-quant/p01_kelly_pruitt_2013/docs/index.html">Pipeline Web Page      |
| Date of Last Code Update        | 2026-03-05 23:55:41           |
| OS Compatibility                |  |
| Linked Dataframes               |  [P01:crsp_monthly_stock](./dataframes/P01/crsp_monthly_stock.md)<br>  [P01:crsp_market_returns](./dataframes/P01/crsp_market_returns.md)<br>  [P01:compustat](./dataframes/P01/compustat.md)<br>  [P01:ccm_link](./dataframes/P01/ccm_link.md)<br>  [P01:ken_french_ff_factors](./dataframes/P01/ken_french_ff_factors.md)<br>  [P01:ken_french_25_portfolios](./dataframes/P01/ken_french_25_portfolios.md)<br>  |




Replication of **Table 1** from:

> Kelly, B. and Pruitt, S. (2013), "Market Expectations in the Cross-Section of Present Values." *The Journal of Finance*, 68: 1721-1756. https://doi.org/10.1111/jofi.12060

## Overview

This paper demonstrates that returns and cash flow growth for the aggregate US stock market are highly predictable using a single factor extracted from the cross-section of book-to-market ratios. The key methodology is partial least squares (PLS) / three-pass regression filter (3PRF).

## Data Sources

| Source | Description | Access |
|--------|-------------|--------|
| CRSP | Monthly stock returns, prices, market cap | WRDS |
| Compustat | Annual accounting data (book equity) | WRDS |
| CRSP-Compustat Link | Crosswalk between CRSP and Compustat | WRDS |

## Project Structure

```
p01_kelly_pruitt_2013/
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ settings.py              # Project configuration
â”‚   â”œâ”€â”€ pull_CRSP_stock.py       # Pull CRSP stock data
â”‚   â”œâ”€â”€ pull_CRSP_Compustat.py   # Pull Compustat data
â”‚   â””â”€â”€ generate_exploratory_charts.py
â”œâ”€â”€ _data/                       # Downloaded data (gitignored)
â”œâ”€â”€ _output/                     # Generated outputs
â”œâ”€â”€ docs/                        # Chartbook site
â”œâ”€â”€ dodo.py                      # PyDoit task runner
â”œâ”€â”€ chartbook.toml               # Chartbook configuration
â”œâ”€â”€ consultation.md              # Consultation meeting agenda
â””â”€â”€ README.md
```

## Setup

1. **Create environment**:
   ```bash
   conda create -n kelly_pruitt python=3.11
   conda activate kelly_pruitt
   pip install -r requirements.txt
   ```

2. **Configure WRDS credentials**:
   ```bash
   cp .env.example .env
   # Edit .env with your WRDS username
   ```

3. **Run the pipeline**:
   ```bash
   doit
   ```

## Tasks

| Task | Description |
|------|-------------|
| `doit pull_CRSP_stock` | Pull CRSP monthly stock data and market returns |
| `doit pull_CRSP_Compustat` | Pull Compustat fundamentals and CCM link table |
| `doit exploratory_charts` | Generate exploratory charts |
| `doit build_chartbook_site` | Build the chartbook documentation site |

## Team

- **Zara**: Data pipeline, CRSP data, chartbook setup, LaTeX report
- **Dylan**: Book equity calculation, PLS implementation, statistics report

## References

- [Paper on SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1686814)
- [Author's code and data](https://sethpruitt.net/2013/10/31/market-expectations-in-the-cross-section-of-present-values/)
- [WRDS Documentation](https://wrds-www.wharton.upenn.edu/)
