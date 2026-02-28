"""
Calculates predictive performance metrics for the three-pass regression filter.

Computes in-sample and out-of-sample predictive R-squared values over 
specified forecasting horizons (e.g., 1-month, 1-year). The out-of-sample 
evaluation utilizes a recursive expanding window methodology to strictly 
prevent look-ahead bias during factor extraction and prediction.
"""

import pandas as pd
import numpy as np
import load_data
import regression_tools as rt
from settings import config
from pathlib import Path

OUTPUT_DIR = Path(config("OUTPUT_DIR"))
START_TRAIN_DATE = config("START_TRAIN_DATE")
START_TEST_DATE = config("START_TEST_DATE")
END_TEST_DATE = config("END_TEST_DATE")

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

def run_out_of_sample(v_df, y_series, h, start_date=START_TEST_DATE):
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