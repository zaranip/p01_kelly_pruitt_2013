# Dataframe: `P01:compustat` - Compustat Fundamentals

Annual accounting data from Compustat including book equity components (seq, ceq, at, lt, pstk, txditc). Contains 593K records for 46,655 unique firms from 1950-2026.


## DataFrame Glimpse

```
Rows: 595540
Columns: 22
$ gvkey                      <str> '370994'
$ datadate          <datetime[ns]> 2024-12-31 00:00:00
$ at                         <f64> 4772.024
$ lt                         <f64> 4371.585
$ sale                       <f64> 1182.783
$ cogs                       <f64> 631.295
$ xsga                       <f64> 78.52
$ xint                       <f64> null
$ pstkl                      <f64> 0.0
$ txditc                     <f64> null
$ pstkrv                     <f64> 0.0
$ seq                        <f64> 381.906
$ pstk                       <f64> 0.0
$ ceq                        <f64> 381.906
$ ni                         <f64> 127.893
$ sich                       <i64> null
$ dp                         <f64> 26.652
$ ebit                       <f64> 446.316
$ csho                       <f64> 789.269
$ prcc_f                     <f64> null
$ year                       <i32> 2024
$ __index_level_0__          <i64> 95539


```

## Dataframe Manifest

| Dataframe Name                 | Compustat Fundamentals                                                   |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [compustat](../dataframes/P01/compustat.md)                                       |
| Data Sources                   | Compustat                                        |
| Data Providers                 | WRDS                                      |
| Links to Providers             | https://wrds-www.wharton.upenn.edu/                             |
| Topic Tags                     | Accounting Data, Book Equity, Compustat                                          |
| Type of Data Access            | S,u,b,s,c,r,i,p,t,i,o,n, ,(,W,R,D,S,)                                  |
| How is data pulled?            | WRDS Python API                                                    |
| Data available up to (min)     | 2026-01-31 00:00:00                                                             |
| Data available up to (max)     | 2026-02-28 00:00:00                                                             |
| Dataframe Path                 | /Users/dylanwang/Desktop/UChicago/Classes/FINM_32900/p01_kelly_pruitt_2013/_data/Compustat.parquet                                                   |


**Linked Charts:**


- [P01:compustat_coverage](../../charts/P01.compustat_coverage.md)



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


