# Dataframe: `P01:compustat` - Compustat Fundamentals

Annual accounting data from Compustat including book equity components (seq, ceq, at, lt, pstk, txditc). Contains 593K records for 46,655 unique firms from 1950-2026.


## DataFrame Glimpse

```
Rows: 593738
Columns: 22
$ gvkey                      <str> '369350'
$ datadate          <datetime[ns]> 2024-12-31 00:00:00
$ at                         <f64> 5715.961
$ lt                         <f64> 2816.05
$ sale                       <f64> 8227.629
$ cogs                       <f64> 5033.69
$ xsga                       <f64> 1886.339
$ xint                       <f64> 13.459
$ pstkl                      <f64> 0.0
$ txditc                     <f64> 308.523
$ pstkrv                     <f64> 0.0
$ seq                        <f64> 2876.098
$ pstk                       <f64> 0.0
$ ceq                        <f64> 2876.098
$ ni                         <f64> 599.446
$ sich                       <f64> 2024.0
$ dp                         <f64> 321.982
$ ebit                       <f64> 985.618
$ csho                       <f64> None
$ prcc_f                     <f64> None
$ year                       <i32> 2024
$ __index_level_0__          <i64> 93737


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
| Data available up to (min)     | 2025-12-31 00:00:00                                                             |
| Data available up to (max)     | 2026-01-31 00:00:00                                                             |
| Dataframe Path                 | C:\Users\Zara\Documents\GitHub\FINM Winter Quarter\full-stack-quant\p01_kelly_pruitt_2013\_data\Compustat.parquet                                                   |
| Download Data as Parquet       | [Parquet](../../download_dataframe/P01/compustat.parquet)         |
| Download Data as Excel         | [Excel](../../download_dataframe/P01/compustat.xlsx)              |
| Linked Charts                  |   [P01:compustat_coverage](../../charts/P01.compustat_coverage.md)<br>   |

## Pipeline Manifest

| Pipeline Name                   | Market Expectations in the Cross-Section of Present Values                       |
|---------------------------------|--------------------------------------------------------|
| Pipeline ID                     | [P01](../index.md)              |
| Lead Pipeline Developer         | Zara and Dylan             |
| Contributors                    | Zara, Dylan           |
| Git Repo URL                    | https://github.com/zaranip/p01_kelly_pruitt_2013                        |
| Pipeline Web Page               | <a href="file://C:/Users/Zara/Documents/GitHub/FINM Winter Quarter/full-stack-quant/p01_kelly_pruitt_2013/docs/index.html">Pipeline Web Page      |
| Date of Last Code Update        | 2026-02-04 20:03:29           |
| OS Compatibility                |  |
| Linked Dataframes               |  [P01:crsp_monthly_stock](../dataframes/P01/crsp_monthly_stock.md)<br>  [P01:crsp_market_returns](../dataframes/P01/crsp_market_returns.md)<br>  [P01:compustat](../dataframes/P01/compustat.md)<br>  [P01:ccm_link](../dataframes/P01/ccm_link.md)<br>  |


