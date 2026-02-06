"""Day 4 Advanced Testing - Comprehensive tests with parametrize, logging, and generators.

This module demonstrates:
1. Testing with different data sizes using parametrize
2. Testing logging functionality with caplog
3. Testing generator patterns
4. Error handling and edge cases
5. Progress tracking tests
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from sar_processing.stac_client import STACClient
from sar_processing.batch_processor import BatchProcessor, ProcessingTask
from sar_processing.config import STACConfig


# ============================================================
# PARAMETRIZED TESTS - Test with different data sizes
# ============================================================

@pytest.mark.parametrize("size,expected_count", [
    ("small", 2),      # Small dataset
    ("medium", 10),    # Medium dataset
    ("large", 50),     # Large dataset
])
def test_search_different_sizes(size, expected_count):
    """Test searching with different dataset sizes using parametrize.
    
    This demonstrates how to test the same functionality with different inputs
    efficiently using pytest.mark.parametrize.
    """
    client = STACClient()
    
    # Create mock items based on size
    mock_items = []
    for i in range(expected_count):
        mock_item = Mock()
        mock_item.id = f"S1A_IW_GRDH_{size}_{i:03d}"
        mock_item.datetime = f"2022-01-{i+1:02d}T12:34:56Z"
        mock_items.append(mock_item)
    
    # Mock search result
    mock_search_result = Mock()
    mock_search_result.items.return_value = mock_items
    
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    # Perform search
    items = client.search(
        bbox=(13.0, 52.0, 14.0, 53.0),
        datetime="2022-01-01/2022-01-31",
        limit=expected_count
    )
    
    # Assertions
    assert len(items) == expected_count
    assert all(size in item.id for item in items)


@pytest.mark.parametrize("bbox,is_valid", [
    ((13.0, 52.0, 14.0, 53.0), True),     # Valid bbox
    ((-180, -90, 180, 90), True),         # World bbox
    ((0, 0, 1, 1), True),                 # Minimal bbox
    ((10.5, 45.2, 10.6, 45.3), True),     # Small area
])
def test_search_different_bboxes(bbox, is_valid):
    """Test search with different bounding boxes."""
    client = STACClient()
    
    mock_search_result = Mock()
    mock_search_result.items.return_value = []
    
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    if is_valid:
        # Should complete without error
        items = client.search(bbox=bbox, datetime="2022-01-01/2022-01-31")
        assert isinstance(items, list)
    else:
        # Should raise error for invalid bbox
        with pytest.raises(Exception):
            client.search(bbox=bbox, datetime="2022-01-01/2022-01-31")


@pytest.mark.parametrize("limit,config_limit,expected", [
    (10, 20, 10),    # Method limit overrides config
    (None, 25, 25),  # Config limit used when method limit is None
    (5, 100, 5),     # Small method limit
    (None, 1, 1),    # Minimal config limit
])
def test_limit_priority(limit, config_limit, expected):
    """Test that method limit correctly overrides config limit."""
    config = STACConfig(limit=config_limit)
    client = STACClient(config=config)
    
    mock_search_result = Mock()
    mock_search_result.items.return_value = []
    
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    client.search(
        bbox=(13.0, 52.0, 14.0, 53.0),
        datetime="2022-01-01/2022-01-31",
        limit=limit
    )
    
    call_kwargs = mock_client.search.call_args.kwargs
    assert call_kwargs["limit"] == expected


# ============================================================
# LOGGING TESTS - Test logging with caplog fixture
# ============================================================

def test_client_initialization_logging(caplog):
    """Test that client initialization logs correctly.
    
    The caplog fixture captures all log messages during the test.
    """
    with caplog.at_level(logging.DEBUG):
        config = STACConfig(stac_url="https://test.example.com/stac")
        client = STACClient(config=config)
        
    # Check that debug message was logged
    assert "Initialized STACClient" in caplog.text
    assert "https://test.example.com/stac" in caplog.text
    assert caplog.records[0].levelname == "DEBUG"


def test_search_logging_info(caplog):
    """Test that search method logs at INFO level."""
    client = STACClient()
    
    mock_search_result = Mock()
    mock_search_result.items.return_value = []
    
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    with caplog.at_level(logging.INFO):
        client.search(
            bbox=(13.0, 52.0, 14.0, 53.0),
            datetime="2022-01-01/2022-01-31",
            limit=10
        )
    
    # Check INFO level logs
    assert "Searching STAC catalog" in caplog.text
    assert "Found 0 items" in caplog.text
    assert any(record.levelname == "INFO" for record in caplog.records)


def test_search_warning_on_no_results(caplog):
    """Test that WARNING is logged when no items are found."""
    client = STACClient()
    
    mock_search_result = Mock()
    mock_search_result.items.return_value = []
    
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    with caplog.at_level(logging.WARNING):
        client.search(
            bbox=(13.0, 52.0, 14.0, 53.0),
            datetime="2022-01-01/2022-01-31"
        )
    
    # Check that warning was logged
    assert "No items found" in caplog.text
    warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warning_records) > 0


def test_sign_items_debug_logging(caplog):
    """Test that sign_items logs at DEBUG level."""
    client = STACClient()
    
    mock_items = [Mock(id="item1"), Mock(id="item2")]
    
    with caplog.at_level(logging.DEBUG):
        with patch('sar_processing.stac_client.planetary_computer') as mock_pc:
            mock_pc.sign.side_effect = mock_items
            client.sign_items(mock_items)
    
    # Check debug logs
    assert "Signing 2 items" in caplog.text
    assert "All items signed successfully" in caplog.text


def test_logging_levels_hierarchy(caplog):
    """Test that logging respects level hierarchy."""
    client = STACClient()
    
    mock_search_result = Mock()
    mock_search_result.items.return_value = [Mock()]
    
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    # Test with INFO level - should not capture DEBUG
    with caplog.at_level(logging.INFO):
        client.search(
            bbox=(13.0, 52.0, 14.0, 53.0),
            datetime="2022-01-01/2022-01-31"
        )
    
    # INFO and WARNING should be captured, but not DEBUG
    assert any(record.levelname == "INFO" for record in caplog.records)
    # DEBUG messages should not appear
    debug_records = [r for r in caplog.records if r.levelname == "DEBUG"]
    assert len(debug_records) == 0  # DEBUG not captured at INFO level


# ============================================================
# GENERATOR PATTERN TESTS
# ============================================================

def test_generator_yields_items():
    """Test that search_generator yields items one at a time."""
    client = STACClient()
    
    # Create mock items
    mock_items = [Mock(id=f"item{i}") for i in range(5)]
    
    # Mock the search to return an iterable
    mock_search_result = Mock()
    mock_search_result.items.return_value = iter(mock_items)
    
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    # Use generator
    generator = client.search_generator(
        bbox=(13.0, 52.0, 14.0, 53.0),
        datetime="2022-01-01/2022-01-31"
    )
    
    # Verify it's a generator
    assert hasattr(generator, '__iter__')
    assert hasattr(generator, '__next__')
    
    # Consume generator and collect items
    collected_items = list(generator)
    
    assert len(collected_items) == 5
    assert all(item.id.startswith('item') for item in collected_items)


def test_generator_memory_efficiency():
    """Test that generator doesn't load all items at once.
    
    This test demonstrates that generators process items one at a time,
    which is crucial for large datasets.
    """
    client = STACClient()
    
    # Create a large number of mock items
    num_items = 1000
    
    # Track how many items are created
    items_created = []
    
    def item_factory():
        """Factory that tracks item creation."""
        for i in range(num_items):
            mock_item = Mock(id=f"large_item_{i}")
            items_created.append(i)
            yield mock_item
    
    mock_search_result = Mock()
    mock_search_result.items.return_value = item_factory()
    
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    # Use generator to process first 10 items only
    generator = client.search_generator(
        bbox=(13.0, 52.0, 14.0, 53.0),
        datetime="2022-01-01/2022-01-31"
    )
    
    first_10 = []
    for i, item in enumerate(generator):
        first_10.append(item)
        if i >= 9:  # Stop after 10 items
            break
    
    # Only 10 items should have been created, not all 1000
    assert len(first_10) == 10
    # Generator is lazy - only items we consumed were created
    assert len(items_created) == 10


def test_generator_with_logging(caplog):
    """Test that generator logs correctly."""
    client = STACClient()
    
    mock_items = [Mock(id=f"item{i}") for i in range(3)]
    
    mock_search_result = Mock()
    mock_search_result.items.return_value = iter(mock_items)
    
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    with caplog.at_level(logging.INFO):
        generator = client.search_generator(
            bbox=(13.0, 52.0, 14.0, 53.0),
            datetime="2022-01-01/2022-01-31"
        )
        list(generator)  # Consume the generator
    
    # Check logging
    assert "Starting generator search" in caplog.text
    assert "Generator search complete" in caplog.text
    assert "yielded 3 items" in caplog.text


def test_search_and_sign_generator():
    """Test combined search and sign generator."""
    client = STACClient()
    
    mock_items = [Mock(id=f"item{i}") for i in range(3)]
    signed_items = [Mock(id=f"item{i}", signed=True) for i in range(3)]
    
    mock_search_result = Mock()
    mock_search_result.items.return_value = iter(mock_items)
    
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    with patch('sar_processing.stac_client.planetary_computer') as mock_pc:
        mock_pc.sign.side_effect = signed_items
        
        generator = client.search_and_sign_generator(
            bbox=(13.0, 52.0, 14.0, 53.0),
            datetime="2022-01-01/2022-01-31"
        )
        
        result = list(generator)
        
        assert len(result) == 3
        assert all(item.signed for item in result)


# ============================================================
# PROGRESS TRACKING TESTS
# ============================================================

def test_batch_processor_with_progress(caplog):
    """Test that batch processor shows progress and logs."""
    mock_stac_client = Mock()
    mock_data_loader = Mock()
    
    processor = BatchProcessor(
        stac_client=mock_stac_client,
        data_loader=mock_data_loader
    )
    
    # Mock the dependencies
    mock_stac_client.search_and_sign.return_value = [Mock()]
    mock_data_loader.load.return_value = Mock()
    mock_data_loader.get_polarization.return_value = Mock(time=[], shape=(10, 10))
    
    tasks = [
        ProcessingTask("task1", (13.0, 52.0, 14.0, 53.0), "2022-01-01/2022-01-31"),
        ProcessingTask("task2", (14.0, 53.0, 15.0, 54.0), "2022-02-01/2022-02-28"),
    ]
    
    with caplog.at_level(logging.INFO):
        results = processor.process_tasks(tasks, show_progress=False)
    
    # Check results
    assert len(results) == 2
    assert "task1" in results
    assert "task2" in results
    
    # Check logging
    assert "Starting batch processing of 2 tasks" in caplog.text
    assert "Batch processing complete" in caplog.text


def test_batch_processor_no_items_warning(caplog):
    """Test that warning is logged when no items found."""
    mock_stac_client = Mock()
    mock_data_loader = Mock()
    
    processor = BatchProcessor(
        stac_client=mock_stac_client,
        data_loader=mock_data_loader
    )
    
    # Mock no items found
    mock_stac_client.search_and_sign.return_value = []
    
    tasks = [
        ProcessingTask("empty_task", (13.0, 52.0, 14.0, 53.0), "2022-01-01/2022-01-31"),
    ]
    
    with caplog.at_level(logging.WARNING):
        results = processor.process_tasks(tasks, show_progress=False)
    
    # Check warning was logged
    assert "No items found" in caplog.text
    assert results["empty_task"]["error"] == "No items found"


@patch('sar_processing.batch_processor.tqdm')
def test_progress_bar_disabled(mock_tqdm):
    """Test that progress bar can be disabled."""
    mock_stac_client = Mock()
    mock_data_loader = Mock()
    
    processor = BatchProcessor(
        stac_client=mock_stac_client,
        data_loader=mock_data_loader
    )
    
    mock_stac_client.search_and_sign.return_value = []
    
    # Mock tqdm to return a simple iterable with set_description method
    class FakeTqdm(list):
        def set_description(self, desc):
            pass

    mock_tqdm.return_value = FakeTqdm([
        ProcessingTask("task1", (13.0, 52.0, 14.0, 53.0), "2022-01-01/2022-01-31")
    ])
    
    processor.process_tasks(
        [ProcessingTask("task1", (13.0, 52.0, 14.0, 53.0), "2022-01-01/2022-01-31")],
        show_progress=False
    )
    
    # Verify tqdm was called with disable=True
    call_kwargs = mock_tqdm.call_args.kwargs
    assert call_kwargs.get('disable') == True


# ============================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================

@pytest.mark.parametrize("error_scenario,error_message", [
    ("network_error", "Network connection failed"),
    ("timeout", "Request timeout"),
    ("invalid_credentials", "Authentication failed"),
])
def test_error_handling(error_scenario, error_message):
    """Test error handling for different scenarios."""
    client = STACClient()
    
    mock_client = Mock()
    mock_client.search.side_effect = Exception(error_message)
    client._client = mock_client
    
    with pytest.raises(Exception) as exc_info:
        client.search(
            bbox=(13.0, 52.0, 14.0, 53.0),
            datetime="2022-01-01/2022-01-31"
        )
    
    assert error_message in str(exc_info.value)


def test_empty_items_list():
    """Test handling of empty items list."""
    client = STACClient()
    
    # Test signing empty list
    result = client.sign_items([])
    assert result == []


def test_single_item():
    """Test handling of single item."""
    client = STACClient()
    
    mock_item = Mock(id="single_item")
    
    with patch('sar_processing.stac_client.planetary_computer') as mock_pc:
        mock_pc.sign.return_value = mock_item
        result = client.sign_items([mock_item])
        
        assert len(result) == 1
        assert result[0].id == "single_item"


# ============================================================
# INTEGRATION WITH MULTIPLE FEATURES
# ============================================================

def test_comprehensive_workflow_with_all_features(caplog):
    """Test a comprehensive workflow using logging, generators, and parametrize concepts.
    
    This test demonstrates how all Day 4 concepts work together.
    """
    client = STACClient()
    
    # Create mock items
    num_items = 10
    mock_items = [Mock(id=f"workflow_item_{i}") for i in range(num_items)]
    
    mock_search_result = Mock()
    mock_search_result.items.return_value = iter(mock_items)
    
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    with caplog.at_level(logging.INFO):
        # Use generator pattern
        generator = client.search_generator(
            bbox=(13.0, 52.0, 14.0, 53.0),
            datetime="2022-01-01/2022-01-31",
            limit=num_items
        )
        
        # Process items one at a time (memory efficient)
        processed_count = 0
        for item in generator:
            processed_count += 1
            # Simulate processing
            assert item.id.startswith("workflow_item_")
    
    # Verify all items were processed
    assert processed_count == num_items
    
    # Verify logging captured the workflow
    assert "Starting generator search" in caplog.text
    assert f"yielded {num_items} items" in caplog.text
