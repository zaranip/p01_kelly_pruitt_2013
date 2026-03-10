# Dataframe: `P01:ken_french_ff_factors` - Fama-French Research Factors

Monthly Fama-French factors (Mkt-RF, SMB, HML, RF) and aggregate market return. Used to construct the target variable (log market return) for the three-pass regression filter. Covers 1926 to present.


## DataFrame Glimpse

```
Rows: 1140
Columns: 5
$ Mkt              <f64> -2.8
$ Log_Mkt          <f64> -0.028399474521698
$ Mkt-RF           <f64> -3.17
$ RF               <f64> 0.37
$ Date    <datetime[ns]> 2024-12-01 00:00:00


```

## Dataframe Manifest

| Dataframe Name                 | Fama-French Research Factors                                                   |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [ken_french_ff_factors](../dataframes/P01/ken_french_ff_factors.md)                                       |
| Data Sources                   | Kenneth French Data Library                                        |
| Data Providers                 | Kenneth French                                      |
| Links to Providers             | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html                             |
| Topic Tags                     | Fama-French, Market Returns, Factors                                          |
| Type of Data Access            | P,u,b,l,i,c                                  |
| How is data pulled?            | pandas_datareader / direct HTTP download                                                    |
| Data available up to (min)     | 2024-12-01 00:00:00                                                             |
| Data available up to (max)     | 2024-12-01 00:00:00                                                             |
| Dataframe Path                 | /Users/dylanwang/Desktop/UChicago/Classes/FINM_32900/p01_kelly_pruitt_2013/_data/Market_Returns.parquet                                                   |


**Linked Charts:**


- [P01:ff_factors](../../charts/P01.ff_factors.md)



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


