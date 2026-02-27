# Market Expectations in the Cross-Section of Present Values

Last updated: {sub-ref}`today` 


## Table of Contents

```{toctree}
:maxdepth: 1
:caption: Notebooks 📖

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
| Pipeline Web Page               | <a href="file:///Users/dylanwang/Desktop/UChicago/Classes/FINM 32900/p01_kelly_pruitt_2013/docs/index.html">Pipeline Web Page      |
| Date of Last Code Update        | 2026-02-05 15:45:21           |
| OS Compatibility                |  |
| Linked Dataframes               |  [P01:crsp_monthly_stock](./dataframes/P01/crsp_monthly_stock.md)<br>  [P01:crsp_market_returns](./dataframes/P01/crsp_market_returns.md)<br>  [P01:compustat](./dataframes/P01/compustat.md)<br>  [P01:ccm_link](./dataframes/P01/ccm_link.md)<br>  |




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
├── src/
│   ├── settings.py              # Project configuration
│   ├── pull_CRSP_stock.py       # Pull CRSP stock data
│   ├── pull_CRSP_Compustat.py   # Pull Compustat data
│   └── generate_exploratory_charts.py
├── _data/                       # Downloaded data (gitignored)
├── _output/                     # Generated outputs
├── docs/                        # Chartbook site
├── dodo.py                      # PyDoit task runner
├── chartbook.toml               # Chartbook configuration
├── consultation.md              # Consultation meeting agenda
└── README.md
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

- **Zara**: Data pipeline, CRSP data, chartbook setup
- **Dylan**: Compustat data, book equity calculation, PLS implementation

## References

- [Paper on SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1686814)
- [Author's code and data](https://sethpruitt.net/2013/10/31/market-expectations-in-the-cross-section-of-present-values/)
- [WRDS Documentation](https://wrds-www.wharton.upenn.edu/)
