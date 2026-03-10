# Dataframe: `P01:ken_french_25_portfolios` - 25 Portfolios (5x5 Size x BM)

Monthly data for 25 portfolios formed on Size (market cap) and Book-to-Market ratio. Contains value-weighted returns, number of firms, average firm size, and annual BE/ME ratios. Primary dataset for the three-pass regression filter replication.


## DataFrame Glimpse

```
Rows: 1140
Columns: 26
$ SMALL LoBM          <f64> -2.134531507997796
$ ME1 BM2             <f64> -1.2888047398426334
$ ME1 BM3             <f64> -0.7698122654954308
$ ME1 BM4             <f64> -0.3298939212610904
$ SMALL HiBM          <f64> 0.31181355202670896
$ ME2 BM1             <f64> -2.0980129272652714
$ ME2 BM2             <f64> -1.2833768271132042
$ ME2 BM3             <f64> -0.7765287894989963
$ ME2 BM4             <f64> -0.35012501307499977
$ ME2 BM5             <f64> 0.27982629648619733
$ ME3 BM1             <f64> -2.1794828958600623
$ ME3 BM2             <f64> -1.2594855142561947
$ ME3 BM3             <f64> -0.8128320235059251
$ ME3 BM4             <f64> -0.34291293345119983
$ ME3 BM5             <f64> 0.08672800350982415
$ ME4 BM1             <f64> -2.184802057337662
$ ME4 BM2             <f64> -1.3276481656871573
$ ME4 BM3             <f64> -0.7837285587911837
$ ME4 BM4             <f64> -0.35967945295903114
$ ME4 BM5             <f64> 0.0968544413638821
$ BIG LoBM            <f64> -2.501036031717884
$ ME5 BM2             <f64> -1.3719970564190662
$ ME5 BM3             <f64> -0.7431781141655103
$ ME5 BM4             <f64> -0.3979434667093183
$ BIG HiBM            <f64> 0.06503839617922215
$ Date       <datetime[ns]> 2024-12-01 00:00:00


```

## Dataframe Manifest

| Dataframe Name                 | 25 Portfolios (5x5 Size x BM)                                                   |
|--------------------------------|--------------------------------------------------------------------------------------|
| Dataframe ID                   | [ken_french_25_portfolios](../dataframes/P01/ken_french_25_portfolios.md)                                       |
| Data Sources                   | Kenneth French Data Library                                        |
| Data Providers                 | Kenneth French                                      |
| Links to Providers             | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html                             |
| Topic Tags                     | Fama-French, Portfolios, Book-To-Market, Size                                          |
| Type of Data Access            | P,u,b,l,i,c                                  |
| How is data pulled?            | pandas_datareader / direct HTTP download                                                    |
| Data available up to (min)     | 2024-12-01 00:00:00                                                             |
| Data available up to (max)     | 2024-12-01 00:00:00                                                             |
| Dataframe Path                 | /Users/dylanwang/Desktop/UChicago/Classes/FINM_32900/p01_kelly_pruitt_2013/_data/25_Portfolios_5x5_BM.parquet                                                   |


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


