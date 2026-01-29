"""Tests for batch processing functionality."""

import pytest
from sar_processing.batch_processor import BatchProcessor, ProcessingTask
from sar_processing.stac_client import STACClient
from sar_processing.data_loader import SARDataLoader


def test_processing_task_creation():
    """Test creating a processing task."""
    task = ProcessingTask(
        name="test_region",
        bbox=(13.0, 52.0, 14.0, 53.0),
        datetime="2022-01-01/2022-01-31",
    )
    
    assert task.name == "test_region"
    assert task.bbox == (13.0, 52.0, 14.0, 53.0)
    assert task.datetime == "2022-01-01/2022-01-31"
    assert task.crs is None


def test_batch_processor_initialization():
    """Test batch processor initialization."""
    stac_client = STACClient()
    data_loader = SARDataLoader()
    
    processor = BatchProcessor(stac_client=stac_client, data_loader=data_loader)
    
    assert processor.stac_client is not None
    assert processor.data_loader is not None
    assert processor.change_detector is not None
    assert processor.statistics is not None


@pytest.mark.integration
def test_process_multiple_regions():
    """Test processing multiple regions."""
    stac_client = STACClient()
    data_loader = SARDataLoader()
    processor = BatchProcessor(stac_client=stac_client, data_loader=data_loader)
    
    regions = {
        "berlin": (13.0, 52.0, 14.0, 53.0),
        "munich": (11.3, 48.0, 11.8, 48.3),
    }
    
    # Use small limit for testing
    stac_client.config.limit = 2
    
    results = processor.process_multiple_regions(
        regions=regions,
        datetime="2022-01-01/2022-01-15",
        compute_stats=False,
        compute_change=False,
    )
    
    assert isinstance(results, dict)
    # Results may be empty if no data found


@pytest.mark.integration
def test_process_multiple_periods():
    """Test processing multiple time periods."""
    stac_client = STACClient()
    data_loader = SARDataLoader()
    processor = BatchProcessor(stac_client=stac_client, data_loader=data_loader)
    
    periods = {
        "january": "2022-01-01/2022-01-31",
        "february": "2022-02-01/2022-02-28",
    }
    
    stac_client.config.limit = 2
    
    results = processor.process_multiple_periods(
        bbox=(13.0, 52.0, 14.0, 53.0),
        periods=periods,
        compute_stats=False,
        compute_change=False,
    )
    
    assert isinstance(results, dict)