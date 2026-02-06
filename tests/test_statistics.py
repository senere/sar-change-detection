"""Tests for statistical computations."""

import pytest
import numpy as np
import xarray as xr
from sar_processing.statistics import SARStatistics



def test_temporal_stats(sample_sar_data):
    """Test temporal statistics computation."""
    stats = SARStatistics.temporal_stats(sample_sar_data, compute=True, show_progress=False)
    
    assert "mean" in stats
    assert "std" in stats
    assert isinstance(stats["mean"], xr.DataArray)
    assert isinstance(stats["std"], xr.DataArray)
    assert "time" not in stats["mean"].dims


def test_temporal_stats_lazy(sample_sar_data):
    """Test lazy temporal statistics."""
    stats = SARStatistics.temporal_stats(sample_sar_data, compute=False)
    
    # Should still be lazy (dask array)
    assert hasattr(stats["mean"].data, "compute")


def test_temporal_stats_no_time():
    """Test temporal stats with no time dimension."""
    data = xr.DataArray(np.ones((10, 10)), dims=["y", "x"])
    
    with pytest.raises(ValueError):
        SARStatistics.temporal_stats(data)


def test_spatial_stats(sample_image_pair):
    """Test spatial statistics."""
    before, _ = sample_image_pair
    
    stats = SARStatistics.spatial_stats(before, compute=True)
    
    assert "min" in stats
    assert "max" in stats
    assert "mean" in stats
    assert "std" in stats
    assert all(isinstance(v, float) for v in stats.values())
    assert stats["min"] <= stats["mean"] <= stats["max"]


def test_percentiles(sample_image_pair):
    """Test percentile computation."""
    before, _ = sample_image_pair
    
    percentiles = SARStatistics.percentiles(before, percentiles=[25, 50, 75], compute=True)
    
    assert "p25" in percentiles
    assert "p50" in percentiles
    assert "p75" in percentiles
    assert percentiles["p25"] <= percentiles["p50"] <= percentiles["p75"]