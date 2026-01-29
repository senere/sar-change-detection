"""Tests for data loading functionality."""

import pytest
import xarray as xr
import numpy as np
from sar_processing.data_loader import SARDataLoader
from sar_processing.config import ProcessingConfig


def test_data_loader_initialization():
    """Test data loader initialization."""
    loader = SARDataLoader()
    assert loader.config is not None
    assert loader.config.bands == ["vh", "vv"]


def test_data_loader_custom_config():
    """Test data loader with custom config."""
    config = ProcessingConfig(resolution=10)
    loader = SARDataLoader(config=config)
    assert loader.config.resolution == 10


def test_get_polarization(sample_dataset):
    """Test extracting polarization from dataset."""
    loader = SARDataLoader()
    vv_data = loader.get_polarization(sample_dataset, polarization="vv")
    
    assert isinstance(vv_data, xr.DataArray)
    assert "time" in vv_data.dims
    assert vv_data.name == "vv"


def test_get_polarization_sorting(sample_dataset):
    """Test that polarization data is sorted by time."""
    loader = SARDataLoader()
    vv_data = loader.get_polarization(sample_dataset, polarization="vv", sort_by_time=True)
    
    # Check time is monotonically increasing
    times = vv_data.time.values
    assert all(times[i] <= times[i+1] for i in range(len(times)-1))


def test_config_to_chunks_dict():
    """Test conversion of chunk size to dictionary."""
    config = ProcessingConfig(chunk_size=(256, 256))
    chunks_dict = config.to_chunks_dict()
    
    assert chunks_dict == {"x": 256, "y": 256}


def test_get_polarization_to_db(sample_dataset):
    """Test extracting polarization and converting to dB."""
    loader = SARDataLoader()
    vv_db = loader.get_polarization(sample_dataset, polarization="vv", to_db=True)
    # Should be dB scale
    assert isinstance(vv_db, xr.DataArray)
    # Check that values are not equal to original (should be log-transformed)
    assert not np.allclose(vv_db.values, sample_dataset["vv"].values)


def test_get_polarization_speckle_filter(sample_dataset):
    """Test extracting polarization with speckle filtering."""
    loader = SARDataLoader()
    vv_filtered = loader.get_polarization(sample_dataset, polarization="vv", speckle_filter=True, filter_size=3)
    assert isinstance(vv_filtered, xr.DataArray)
    # Should have same shape as input
    assert vv_filtered.shape == sample_dataset["vv"].shape