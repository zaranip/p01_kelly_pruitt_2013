import pandas as pd
import numpy as np
import load_data
import regression_tools as rt

def calculate_log_returns(market_data):
    """
    Converts simple market returns to log returns as specified in the paper's 
    present value identity.
    """
    # Using 'Mkt' which is Mkt-RF + RF
    simple_returns = market_data['Mkt'] / 100.0
    log_returns = np.log(1 + simple_returns)
    return log_returns

def calculate_r2(actuals, predictions, historical_means):
    """Calculates the out-of-sample predictive R-squared."""
    actuals = np.array(actuals)
    predictions = np.array(predictions)
    historical_means = np.array(historical_means)
    
    mse_model = np.sum((actuals - predictions)**2)
    mse_mean = np.sum((actuals - historical_means)**2)
    
    if mse_mean == 0:
        return np.nan
    return (1 - (mse_model / mse_mean)) * 100

def run_in_sample(v_df, y_series, h):
    """Calculates the in-sample R-squared using the full dataset."""
    phi = rt.first_stage_regressions(v_df, y_series, h=h)
    F_series = rt.second_stage_regressions(v_df, phi)
    model = rt.third_stage_regression(F_series, y_series, h=h)
    
    # In-sample R-squared converted to percentage
    return model.rsquared * 100

def run_out_of_sample(v_df, y_series, h, start_date='1980-01-01'):
    """
    Calculates the out-of-sample R-squared using a recursive expanding window.
    Forecasts begin at start_date.
    """
    valid_dates = v_df.loc[start_date:].index
    
    predictions = []
    actuals = []
    historical_means = []
    
    for t in valid_dates:
        # 1. Filter data to only include information observable at time t
        v_train = v_df.loc[:t]
        y_train = y_series.loc[:t]
        
        # 2. Run the three-pass regression filter on the training window
        # (Internal shifts inside these functions will correctly drop the last 
        # h observations so we don't look ahead)
        phi = rt.first_stage_regressions(v_train, y_train, h=h)
        
        # If there's not enough data to estimate phi, skip this period
        if phi.empty:
            continue
            
        F_series = rt.second_stage_regressions(v_train, phi)
        model = rt.third_stage_regression(F_series, y_train, h=h)
        
        # 3. Generate out-of-sample forecast for time t+h
        if t in F_series.index and pd.notna(F_series.loc[t]):
            F_t = F_series.loc[t]
            pred = model.params.iloc[0] + model.params.iloc[1] * F_t
            
            # Find the actual target realized at t+h to evaluate the forecast later
            t_idx = y_series.index.get_loc(t)
            target_idx = t_idx + h
            
            if target_idx < len(y_series):
                actual = y_series.iloc[target_idx]
                # Historical mean of target variable up to time t
                hist_mean = y_train.mean()
                
                predictions.append(pred)
                actuals.append(actual)
                historical_means.append(hist_mean)
                
    return calculate_r2(actuals, predictions, historical_means)

def replicate_table_1():
    print("Loading datasets...")
    data = load_data.clean_kelly_pruitt_data(load_from_cache=True)
    
    # Restrict sample to 1930 - 2010
    start_sample = '1930-01-01'
    end_sample = '2010-12-31'
    
    # Setup Targets
    log_returns = calculate_log_returns(data['Market_Returns'].loc[start_sample:end_sample])
    
    y_1m = log_returns
    y_12m = log_returns.rolling(12).sum().dropna()
    
    portfolios = [
        ("6 Portfolios", "6_Portfolios_2x3_BM"),
        ("25 Portfolios", "25_Portfolios_5x5_BM"),
        ("100 Portfolios", "100_Portfolios_10x10_BM")
    ]
    
    results = []

    print("\nReplicating Kelly & Pruitt (2013) Table 1...")
    print("-" * 65)
    print(f"{'Portfolio Set':<18} | {'1-Year IS':<10} | {'1-Year OOS':<10} | {'1-Month IS':<10} | {'1-Month OOS':<10}")
    print("-" * 65)
    
    for label, bm_key in portfolios:
        v_df = data[bm_key].loc[start_sample:end_sample]
        
        # Align indices for 12-month series
        v_df_12m = v_df.loc[v_df.index.intersection(y_12m.index)]
        y_12m_aligned = y_12m.loc[v_df_12m.index]
        
        # Align indices for 1-month series
        v_df_1m = v_df.loc[v_df.index.intersection(y_1m.index)]
        y_1m_aligned = y_1m.loc[v_df_1m.index]
        
        # Run 1-Year Forecasts (h=12)
        is_12m = run_in_sample(v_df_12m, y_12m_aligned, h=12)
        oos_12m = run_out_of_sample(v_df_12m, y_12m_aligned, h=12, start_date='1980-01-01')
        
        # Run 1-Month Forecasts (h=1)
        is_1m = run_in_sample(v_df_1m, y_1m_aligned, h=1)
        oos_1m = run_out_of_sample(v_df_1m, y_1m_aligned, h=1, start_date='1980-01-01')
        
        print(f"{label:<18} | {is_12m:>9.2f}% | {oos_12m:>9.2f}% | {is_1m:>9.2f}% | {oos_1m:>9.2f}%")

if __name__ == "__main__":
    replicate_table_1()