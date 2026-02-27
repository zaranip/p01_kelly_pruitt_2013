# Dataframe: `P01:crsp_monthly_stock` - CRSP Monthly Stock Data

Monthly stock-level data from CRSP including prices, returns, shares outstanding, and market capitalization. Contains 4.4M records covering 31,654 unique stocks from 1929-2024.


## DataFrame Glimpse

```
Rows: 4418680
Columns: 25
$ permno                    <i64> 10006
$ permco                    <i64> 22156
$ date             <datetime[ns]> 1929-12-31 00:00:00
$ ret                       <f64> -0.076779
$ retx                      <f64> -0.093023
$ shrout                    <f64> 600000.0
$ prc                       <f64> 78.0
$ vol                       <f64> 22600.0
$ cfacshr                   <f64> 7.26
$ cfacpr                    <f64> 7.26
$ primaryexch               <str> 'N'
$ siccd                     <i64> 3740
$ naics                     <str> '0'
$ issuertype                <str> 'ACOR'
$ securitytype              <str> 'EQTY'
$ securitysubtype           <str> 'COM'
$ sharetype                 <str> 'NS'
$ usincflg                  <str> 'Y'
$ tradingstatusflg          <str> 'A'
$ conditionaltype           <str> 'RW'
$ altprc                    <f64> 78.0
$ adj_shrout                <f64> 4356000.0
$ adj_prc                   <f64> 10.743801652892563
$ market_cap                <f64> 46800000.0
$ jdate            <datetime[ns]> 1929-12-31 00:00:00


```

## Dataframe Manifest

| Dataframe Name                 | CRSP Monthly Stock Data                                                   |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [crsp_monthly_stock](../dataframes/P01/crsp_monthly_stock.md)                                       |
| Data Sources                   | CRSP                                        |
| Data Providers                 | WRDS                                      |
| Links to Providers             | https://wrds-www.wharton.upenn.edu/                             |
| Topic Tags                     | Stock Returns, Market Data, Crsp                                          |
| Type of Data Access            | S,u,b,s,c,r,i,p,t,i,o,n, ,(,W,R,D,S,)                                  |
| How is data pulled?            | WRDS Python API                                                    |
| Data available up to (min)     | N/A (large file)                                                             |
| Data available up to (max)     | N/A (large file)                                                             |
| Dataframe Path                 | /Users/dylanwang/Desktop/UChicago/Classes/FINM 32900/p01_kelly_pruitt_2013/_data/CRSP_monthly_stock.parquet                                                   |
| Download Data as Parquet       | [Parquet](../../download_dataframe/P01/crsp_monthly_stock.parquet)         |
| Download Data as Excel         | [Excel](../../download_dataframe/P01/crsp_monthly_stock.xlsx)              |
| Linked Charts                  |  None  |

## Pipeline Manifest

| Pipeline Name                   | Market Expectations in the Cross-Section of Present Values                       |
|---------------------------------|--------------------------------------------------------|
| Pipeline ID                     | [P01](../index.md)              |
| Lead Pipeline Developer         | Zara and Dylan             |
| Contributors                    | Zara, Dylan           |
| Git Repo URL                    | https://github.com/zaranip/p01_kelly_pruitt_2013                        |
| Pipeline Web Page               | <a href="file:///Users/dylanwang/Desktop/UChicago/Classes/FINM 32900/p01_kelly_pruitt_2013/docs/index.html">Pipeline Web Page      |
| Date of Last Code Update        | 2026-02-05 15:45:21           |
| OS Compatibility                |  |
| Linked Dataframes               |  [P01:crsp_monthly_stock](../dataframes/P01/crsp_monthly_stock.md)<br>  [P01:crsp_market_returns](../dataframes/P01/crsp_market_returns.md)<br>  [P01:compustat](../dataframes/P01/compustat.md)<br>  [P01:ccm_link](../dataframes/P01/ccm_link.md)<br>  |


