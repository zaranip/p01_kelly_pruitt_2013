import pandas as pd
import numpy as np
from pandas.testing import assert_series_equal

# Assuming the file is named regression.py
import regression as reg

def create_synthetic_data(periods=20):
    """
    Creates synthetic data for testing the regression pipeline.
    Constructed to have a strong predictive relationship so models will yield high R-squareds.
    """
    dates = pd.date_range("1975-01-01", periods=periods, freq="ME")
    
    # Target series
    y_vals = np.linspace(1.0, periods * 1.0, periods)
    y_series = pd.Series(y_vals, index=dates, name="Mkt")
    
    # Valuation ratios perfectly correlated with shifted target
    v_df = pd.DataFrame({
        "Port_A": y_vals * 1.5,
        "Port_B": y_vals * 2.0,
        "Port_C": y_vals * 2.5
    }, index=dates)
    
    return v_df, y_series

def test_calculate_r2_positive():
    """Test that a highly accurate prediction yields a high, positive R-squared."""
    actuals = [10.0, 12.0, 14.0]
    predictions = [9.9, 12.1, 13.9]  # Very close to actuals
    historical_means = [8.0, 9.0, 10.0]  # Far from actuals
    
    r2 = reg.calculate_r2(actuals, predictions, historical_means)
    
    # Model MSE should be tiny, Mean MSE should be large, R2 should be near 100%
    assert r2 > 90.0
    assert r2 <= 100.0

def test_calculate_r2_negative():
    """Test that predictions worse than the historical mean yield a negative R-squared."""
    actuals = [10.0, 12.0, 14.0]
    predictions = [2.0, 20.0, 5.0]  # Terrible predictions
    historical_means = [9.0, 11.0, 13.0]  # Quite close to actuals
    
    r2 = reg.calculate_r2(actuals, predictions, historical_means)
    
    # Model MSE > Mean MSE, therefore R2 must be negative
    assert r2 < 0.0

def test_calculate_r2_zero_variance():
    """Test that a zero-variance benchmark gracefully returns NaN instead of a ZeroDivisionError."""
    actuals = [10.0, 10.0, 10.0]
    predictions = [10.0, 10.0, 10.0]
    historical_means = [10.0, 10.0, 10.0]
    
    r2 = reg.calculate_r2(actuals, predictions, historical_means)
    assert np.isnan(r2)

def test_run_in_sample():
    """Test that the in-sample regression sequence returns a valid R-squared percentage."""
    v_df, y_series = create_synthetic_data(periods=12)
    
    # Run in-sample for h=1
    r2_is = reg.run_in_sample(v_df, y_series, h=1)
    
    # With perfectly synthetic data, IS R2 should be very high and formatted as a percentage
    assert isinstance(r2_is, float)
    assert r2_is > 0.0 
    assert r2_is <= 100.0

def test_run_out_of_sample_expanding_window():
    """Test that the out-of-sample function successfully processes the expanding window."""
    v_df, y_series = create_synthetic_data(periods=60) 
    
    # Set start date halfway through the data to allow for an initial training period
    # Data starts in 1975, so 1978 gives a 3-year initial training window
    start_date = "1978-01-01"
    
    # Run OOS for h=1
    r2_oos = reg.run_out_of_sample(v_df, y_series, h=1, start_date=start_date)
    
    assert isinstance(r2_oos, float)
    assert not np.isnan(r2_oos)

def test_run_out_of_sample_insufficient_data():
    """Test that OOS handles cases where the start date leaves no testing data."""
    v_df, y_series = create_synthetic_data(periods=10)
    
    # Provide a start date that occurs after the dataset ends
    start_date = "1990-01-01"
    
    r2_oos = reg.run_out_of_sample(v_df, y_series, h=1, start_date=start_date)
    
    # Because there are no predictions made, the mse_mean will be 0, resulting in NaN
    assert np.isnan(r2_oos)