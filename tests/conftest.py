"""Pytest fixtures for SAR processing tests."""

import pytest
import numpy as np
import xarray as xr
from datetime import datetime, timedelta
import dask.array as da


@pytest.fixture
def sample_bbox():
    """Sample bounding box for Berlin area."""
    return (13.0, 52.0, 14.0, 53.0)


@pytest.fixture
def sample_datetime_range():
    """Sample datetime range."""
    return "2022-01-01/2022-01-31"



@pytest.fixture
def sample_sar_data():
    """Create sample SAR data for testing."""
    # Create synthetic SAR data
    np.random.seed(42)
    times = [datetime(2022, 1, 1) + timedelta(days=i*10) for i in range(3)]
    x = np.arange(100)
    y = np.arange(100)
    # Use Dask array for lazy evaluation
    data_values = da.from_array(np.random.gamma(2, 0.5, (3, 100, 100)), chunks=(1, 100, 100))
    data = xr.DataArray(
        data_values,
        coords={"time": times, "y": y, "x": x},
        dims=["time", "y", "x"],
        name="vv",
    )
    return data

@pytest.fixture
def sample_dataset(sample_sar_data):
    """Create sample xarray Dataset."""
    vv_data = sample_sar_data
    vh_data = vv_data * 0.5  # VH typically lower than VV
    vh_data.name = "vh"
    
    dataset = xr.Dataset({"vv": vv_data, "vh": vh_data})
    return dataset


@pytest.fixture
def sample_image_pair(sample_sar_data):
    """Create a pair of images for change detection."""
    before = sample_sar_data.isel(time=0)
    after = sample_sar_data.isel(time=-1)
    return before, after