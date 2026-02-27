import pandas as pd
import numpy as np
from pandas import Timestamp
from pandas.testing import assert_frame_equal

# Assuming the provided code is saved in load_data.py
import load_data 
from settings import config

DATA_DIR = config("DATA_DIR")

def test_clean_kelly_pruitt_data_keys():
    """Test that all expected datasets are properly loaded and returned as keys."""
    data_dict = load_data.clean_kelly_pruitt_data()
    
    expected_keys = [
        "Market_Returns",
        "6_Portfolios_2x3_Returns",
        "6_Portfolios_2x3_BM",
        "25_Portfolios_5x5_Returns",
        "25_Portfolios_5x5_BM",
        "100_Portfolios_10x10_Returns",
        "100_Portfolios_10x10_BM"
    ]
    
    for key in expected_keys:
        assert key in data_dict, f"Missing expected dataset key: {key}"
        assert isinstance(data_dict[key], pd.DataFrame), f"Data for {key} is not a DataFrame"


def test_market_returns_calculation():
    """Test that Market_Returns calculates Mkt correctly and maintains the correct shape."""
    data_dict = load_data.clean_kelly_pruitt_data()
    mkt_returns = data_dict["Market_Returns"]

    # Check for presence of required columns
    assert "Mkt" in mkt_returns.columns
    assert "Mkt-RF" in mkt_returns.columns
    assert "RF" in mkt_returns.columns
    
    # Check that Mkt is exactly the sum of Mkt-RF and RF
    assert np.allclose(mkt_returns["Mkt"], mkt_returns["Mkt-RF"] + mkt_returns["RF"])

    # Verify index is a DatetimeIndex
    assert pd.api.types.is_datetime64_any_dtype(mkt_returns.index)


def test_portfolio_shapes_and_alignment():
    """Test that the portfolio datasets have the correct number of columns and align correctly."""
    data_dict = load_data.clean_kelly_pruitt_data()
    
    # 6 Portfolios Check
    ret_6 = data_dict["6_Portfolios_2x3_Returns"]
    bm_6 = data_dict["6_Portfolios_2x3_BM"]
    assert ret_6.shape[1] == 6
    assert bm_6.shape[1] == 6
    assert (ret_6.columns == bm_6.columns).all()
    
    # 25 Portfolios Check
    ret_25 = data_dict["25_Portfolios_5x5_Returns"]
    bm_25 = data_dict["25_Portfolios_5x5_BM"]
    assert ret_25.shape[1] == 25
    assert bm_25.shape[1] == 25
    assert (ret_25.columns == bm_25.columns).all()
    
    # 100 Portfolios Check
    ret_100 = data_dict["100_Portfolios_10x10_Returns"]
    bm_100 = data_dict["100_Portfolios_10x10_BM"]
    assert ret_100.shape[1] == 100
    assert bm_100.shape[1] == 100
    assert (ret_100.columns == bm_100.columns).all()


def test_bm_ratio_validity():
    """Test that the calculated Book-to-Market ratios are reasonable and strictly positive."""
    data_dict = load_data.clean_kelly_pruitt_data()
    bm_25 = data_dict["25_Portfolios_5x5_BM"]
    
    # Drop NaNs to test valid ranges (there may be NaNs at the beginning of the series due to lagging)
    valid_bm = bm_25.dropna()
    
    # BM ratios should generally be positive in normal bounds.
    assert (valid_bm > 0).all().all(), "Found negative or zero Book-to-Market ratios"
    
    # Verify index is a proper pandas DatetimeIndex for merging later
    assert pd.api.types.is_datetime64_any_dtype(bm_25.index)


def test_data_date_range():
    """Test that all datasets cover the 1932 to 2010 date range necessary to replicate Table 1."""
    data_dict = load_data.clean_kelly_pruitt_data()
    
    # Table 1 in Kelly and Pruitt evaluates the 1932-2010 sample period
    required_start = pd.Timestamp("1932-01-01")
    required_end = pd.Timestamp("2010-12-31")
    
    for key, df in data_dict.items():
        # Drop rows where all values might be NA to find the true bounds of the data
        valid_df = df.dropna(how='all')
        
        min_date = valid_df.index.min()
        max_date = valid_df.index.max()
        
        assert min_date <= required_start, f"Dataset '{key}' starts too late: {min_date.date()} (Needs to be <= 1930-01-01)"
        assert max_date >= required_end, f"Dataset '{key}' ends too early: {max_date.date()} (Needs to be >= 2010-12-31)"

