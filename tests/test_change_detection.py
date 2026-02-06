"""Tests for change detection functionality."""

import pytest
import numpy as np
import xarray as xr
from sar_processing.change_detection import ChangeDetector


def test_log_ratio_basic(sample_image_pair):
    """Test basic log-ratio computation."""
    before, after = sample_image_pair
    
    change = ChangeDetector.log_ratio(before, after)
    
    assert isinstance(change, xr.DataArray)
    assert change.shape == before.shape
    assert not np.any(np.isnan(change))


def test_log_ratio_increase():
    """Test log-ratio detects increase."""
    before = xr.DataArray(np.ones((10, 10)))
    after = xr.DataArray(np.ones((10, 10)) * 2)
    
    change = ChangeDetector.log_ratio(before, after)
    
    # Doubling should give ~3 dB increase
    assert np.allclose(change, 3.0103, atol=0.01)


def test_log_ratio_decrease():
    """Test log-ratio detects decrease."""
    before = xr.DataArray(np.ones((10, 10)) * 2)
    after = xr.DataArray(np.ones((10, 10)))
    
    change = ChangeDetector.log_ratio(before, after)
    
    # Halving should give ~-3 dB decrease
    assert np.allclose(change, -3.0103, atol=0.01)


def test_log_ratio_db_input():
    """Test log-ratio with dB input (should subtract)."""
    before_db = xr.DataArray(np.ones((10, 10)) * 5)
    after_db = xr.DataArray(np.ones((10, 10)) * 8)
    change = ChangeDetector.log_ratio(before_db, after_db, input_is_db=True)
    assert np.allclose(change, 3.0, atol=0.01)

    # Negative change
    before_db = xr.DataArray(np.ones((10, 10)) * 8)
    after_db = xr.DataArray(np.ones((10, 10)) * 5)
    change = ChangeDetector.log_ratio(before_db, after_db, input_is_db=True)
    assert np.allclose(change, -3.0, atol=0.01)


def test_temporal_change(sample_sar_data):
    """Test temporal change detection."""
    change = ChangeDetector.temporal_change(sample_sar_data)
    
    assert change is not None
    assert isinstance(change, xr.DataArray)
    assert "time" not in change.dims  # Should be reduced


def test_temporal_change_insufficient_data():
    """Test temporal change with insufficient data."""
    data = xr.DataArray(np.ones((1, 10, 10)), dims=["time", "y", "x"])
    
    change = ChangeDetector.temporal_change(data)
    
    assert change is None


def test_to_db():
    """Test conversion to dB."""
    data = xr.DataArray(np.array([1, 10, 100, 1000]))
    
    db_data = ChangeDetector.to_db(data)
    
    expected = np.array([0, 10, 20, 30])
    assert np.allclose(db_data, expected, atol=0.01)


def test_get_time_range(sample_sar_data):
    """Test getting time range from data."""
    min_time, max_time = ChangeDetector.get_time_range(sample_sar_data)
    
    assert min_time is not None
    assert max_time is not None
    assert min_time <= max_time


def test_get_time_range_no_time():
    """Test getting time range from data without time dim."""
    data = xr.DataArray(np.ones((10, 10)), dims=["y", "x"])
    
    result = ChangeDetector.get_time_range(data)
    
    assert result is None