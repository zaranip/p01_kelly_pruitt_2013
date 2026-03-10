# Dataframe: `P01:ccm_link` - CRSP-Compustat Link Table

Crosswalk table linking CRSP PERMNO to Compustat GVKEY. Contains 39K links covering 34,550 unique gvkeys and 35,066 unique permnos.


## DataFrame Glimpse

```
Rows: 40884
Columns: 6
$ gvkey              <str> '369350'
$ permno             <f64> 27874.0
$ linktype           <str> 'LC'
$ linkprim           <str> 'P'
$ linkdt    <datetime[ns]> 2025-12-08 00:00:00
$ linkenddt <datetime[ns]> null


```

## Dataframe Manifest

| Dataframe Name                 | CRSP-Compustat Link Table                                                   |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [ccm_link](../dataframes/P01/ccm_link.md)                                       |
| Data Sources                   | CRSP, Compustat                                        |
| Data Providers                 | WRDS                                      |
| Links to Providers             | https://wrds-www.wharton.upenn.edu/                             |
| Topic Tags                     | Linking Table, Crsp, Compustat                                          |
| Type of Data Access            | S,u,b,s,c,r,i,p,t,i,o,n, ,(,W,R,D,S,)                                  |
| How is data pulled?            | WRDS Python API                                                    |
| Data available up to (min)     | N/A                                                             |
| Data available up to (max)     | N/A                                                             |
| Dataframe Path                 | /Users/dylanwang/Desktop/UChicago/Classes/FINM_32900/p01_kelly_pruitt_2013/_data/CRSP_Comp_Link_Table.parquet                                                   |


**Linked Charts:**

- None


## Pipeline Manifest

| Pipeline Name                   | Market Expectations in the Cross-Section of Present Values                       |
|---------------------------------|--------------------------------------------------------|
| Pipeline ID                     | [P01](../index.md)              |
| Lead Pipeline Developer         | Zara and Dylan             |
| Contributors                    | Zara, Dylan           |
| Git Repo URL                    | https://github.com/zaranip/p01_kelly_pruitt_2013                        |
| Pipeline Web Page               | <a href="file:///Users/dylanwang/Desktop/UChicago/Classes/FINM_32900/p01_kelly_pruitt_2013/docs/index.html">Pipeline Web Page      |
| Date of Last Code Update        | 2026-03-09 21:57:40           |
| OS Compatibility                |  |
| Linked Dataframes               |  [P01:crsp_monthly_stock](../dataframes/P01/crsp_monthly_stock.md)<br>  [P01:crsp_market_returns](../dataframes/P01/crsp_market_returns.md)<br>  [P01:compustat](../dataframes/P01/compustat.md)<br>  [P01:ccm_link](../dataframes/P01/ccm_link.md)<br>  [P01:ken_french_ff_factors](../dataframes/P01/ken_french_ff_factors.md)<br>  [P01:ken_french_25_portfolios](../dataframes/P01/ken_french_25_portfolios.md)<br>  |


