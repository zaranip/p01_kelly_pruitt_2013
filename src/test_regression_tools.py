import pandas as pd
import numpy as np
import statsmodels.api as sm
from pandas.testing import assert_series_equal

# Assuming the provided code is saved in regression_tools.py
import regression_tools as rt

def create_synthetic_data():
    """
    Creates synthetic data for testing. 
    Constructed so that expected relationships (covariances and slopes) are perfectly known.
    """
    dates = pd.date_range("2000-01-01", periods=6, freq="ME")
    
    # Target series (e.g., market returns)
    y_series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], index=dates, name="Mkt")
    
    # Valuation ratios for 3 portfolios (need at least 3 to pass the cross-sectional len >= 3 check)
    # Designed so that v_t perfectly predicts y_{t+1}.
    # e.g., if h=1, y_shifted = [2.0, 3.0, 4.0, 5.0, 6.0, NaN]
    v_df = pd.DataFrame({
        "Port_A": [2.0, 3.0, 4.0, 5.0, 6.0, 7.0],  # 1.0 * y_shifted
        "Port_B": [4.0, 6.0, 8.0, 10.0, 12.0, 14.0], # 2.0 * y_shifted
        "Port_C": [6.0, 9.0, 12.0, 15.0, 18.0, 21.0] # 3.0 * y_shifted
    }, index=dates)
    
    return v_df, y_series

def test_first_stage_regressions():
    """Test Stage 1: Expected slopes and NaN alignment handling."""
    v_df, y_series = create_synthetic_data()
    
    # Calculate Stage 1 with h=1
    phi = rt.first_stage_regressions(v_df, y_series, h=1)
    
    # Expected slope phi_i = Cov(v_i, y_{t+1}) / Var(y_{t+1})
    # Since Port_A = y_{t+1}, slope is 1.0
    # Since Port_B = 2 * y_{t+1}, slope is 2.0
    # Since Port_C = 3 * y_{t+1}, slope is 3.0
    expected_phi = pd.Series({"Port_A": 1.0, "Port_B": 2.0, "Port_C": 3.0})
    
    assert_series_equal(phi, expected_phi, check_names=False)

def test_first_stage_minimum_data_check():
    """Test that portfolios with less than 3 valid paired observations are dropped."""
    v_df, y_series = create_synthetic_data()
    
    # Introduce NaNs in Port_A so that only 2 valid pairs exist after shifting
    v_df.loc[v_df.index[:4], "Port_A"] = np.nan 
    
    phi = rt.first_stage_regressions(v_df, y_series, h=1)
    
    # Port_A should be entirely dropped from the output due to the 'len(pair) < 3' check
    assert "Port_A" not in phi.index
    assert "Port_B" in phi.index
    assert "Port_C" in phi.index

def test_second_stage_regressions():
    """Test Stage 2: Cross-sectional expected slopes and accurate factor extraction."""
    v_df, y_series = create_synthetic_data()
    phi = pd.Series({"Port_A": 1.0, "Port_B": 2.0, "Port_C": 3.0})
    
    F_series = rt.second_stage_regressions(v_df, phi)
    
    # At t=0, v_t = [2.0, 4.0, 6.0]. This is exactly 2.0 * phi.
    # At t=1, v_t = [3.0, 6.0, 9.0]. This is exactly 3.0 * phi.
    # Therefore, F_t should just be [2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    expected_F = pd.Series([2.0, 3.0, 4.0, 5.0, 6.0, 7.0], index=v_df.index).astype(float)
    
    assert_series_equal(F_series, expected_F, check_names=False, check_freq=False)

def test_second_stage_minimum_cross_section_check():
    """Test that time periods with less than 3 valid cross-sectional observations are skipped."""
    v_df, y_series = create_synthetic_data()
    phi = pd.Series({"Port_A": 1.0, "Port_B": 2.0, "Port_C": 3.0})
    
    # Drop enough values in the first row (date 0) so it has < 3 valid portfolios
    v_df.loc[v_df.index[0], "Port_A"] = np.nan
    
    F_series = rt.second_stage_regressions(v_df, phi)
    
    # The first date should be missing from the extracted F_series
    assert v_df.index[0] not in F_series.index
    # The second date should be intact
    assert v_df.index[1] in F_series.index

def test_third_stage_regression():
    """Test Stage 3: Predictive time-series regression mechanics."""
    dates = pd.date_range("2000-01-01", periods=6, freq="ME")
    y_series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], index=dates, name="Mkt")
    
    # Synthetic factor extracted from stage 2
    # F_t perfectly lines up with y_{t+1}
    F_series = pd.Series([2.0, 3.0, 4.0, 5.0, 6.0, 7.0], index=dates, name="F_t")
    
    model = rt.third_stage_regression(F_series, y_series, h=1)
    
    # Because y_{t+1} perfectly equals F_t, the R-squared should be 1.0
    assert np.isclose(model.rsquared, 1.0)
    
    # Check that coefficient for F_t is ~1.0 and intercept is ~0.0
    assert np.isclose(model.params["F_t"], 1.0)
    assert np.isclose(model.params["const"], 0.0)
    
    # Ensure statsmodels output exposes the predicted elements
    assert hasattr(model, "fittedvalues")