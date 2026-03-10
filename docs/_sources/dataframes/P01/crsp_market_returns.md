# Dataframe: `P01:crsp_market_returns` - CRSP Market Returns

Aggregate market returns from CRSP indices including value-weighted (vwretd) and equal-weighted (ewretd) returns. Contains 1,140 monthly observations from 1930-2024.


## DataFrame Glimpse

```
Rows: 972
Columns: 7
$ date   <datetime[ns]> 2010-12-31 00:00:00
$ vwretd          <f64> 0.067182
$ vwretx          <f64> 0.06485
$ ewretd          <f64> 0.068851
$ ewretx          <f64> 0.065469
$ usdval          <f64> 17339253200.0
$ sprtrn          <f64> 0.0653


```

## Dataframe Manifest

| Dataframe Name                 | CRSP Market Returns                                                   |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [crsp_market_returns](../dataframes/P01/crsp_market_returns.md)                                       |
| Data Sources                   | CRSP                                        |
| Data Providers                 | WRDS                                      |
| Links to Providers             | https://wrds-www.wharton.upenn.edu/                             |
| Topic Tags                     | Market Returns, Crsp, Value-Weighted                                          |
| Type of Data Access            | S,u,b,s,c,r,i,p,t,i,o,n, ,(,W,R,D,S,)                                  |
| How is data pulled?            | WRDS Python API                                                    |
| Data available up to (min)     | 2010-12-31 00:00:00                                                             |
| Data available up to (max)     | 2010-12-31 00:00:00                                                             |
| Dataframe Path                 | /Users/dylanwang/Desktop/UChicago/Classes/FINM_32900/p01_kelly_pruitt_2013/_data/CRSP_market_returns.parquet                                                   |


**Linked Charts:**


- [P01:market_returns](../../charts/P01.market_returns.md)



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


