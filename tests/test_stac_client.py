"""Tests for STAC client functionality."""

import pytest
from unittest.mock import Mock, patch, PropertyMock
from sar_processing.stac_client import STACClient
from sar_processing.config import STACConfig


def test_stac_client_initialization():
    """Test STAC client initialization."""
    client = STACClient()
    assert client.config is not None
    assert client.config.stac_url == "https://planetarycomputer.microsoft.com/api/stac/v1"


def test_stac_client_custom_config():
    """Test STAC client with custom config."""
    config = STACConfig(limit=10)
    client = STACClient(config=config)
    assert client.config.limit == 10


def test_stac_client_lazy_loading():
    """Test that client is lazy-loaded."""
    stac_client = STACClient()
    assert stac_client._client is None
    # Accessing client property should initialize it
    client = stac_client.client
    assert client is not None
    assert stac_client._client is not None


# ============================================================
# UNIT TESTS WITH MOCKING (No internet required, fast!)
# ============================================================

def test_search_with_mock():
    """Test search method using mock (no internet needed)."""
    client = STACClient()
    
    # Create mock STAC items
    mock_item1 = Mock()
    mock_item1.id = "S1A_IW_GRDH_1SDV_20220101T123456"
    mock_item1.datetime = "2022-01-01T12:34:56Z"
    
    mock_item2 = Mock()
    mock_item2.id = "S1A_IW_GRDH_1SDV_20220105T123456"
    mock_item2.datetime = "2022-01-05T12:34:56Z"
    
    # Create mock search result
    mock_search_result = Mock()
    mock_search_result.items.return_value = [mock_item1, mock_item2]
    
    # Create mock client
    mock_client = Mock()
    mock_client.search.return_value = mock_search_result
    
    # Replace the real client with mock
    client._client = mock_client
    
    # Test the search method
    items = client.search(
        bbox=(13.0, 52.0, 14.0, 53.0),
        datetime="2022-01-01/2022-01-31",
        limit=10
    )
    
    # Assertions
    assert len(items) == 2
    assert items[0].id == "S1A_IW_GRDH_1SDV_20220101T123456"
    assert items[1].id == "S1A_IW_GRDH_1SDV_20220105T123456"
    
    # Verify the mock was called correctly
    mock_client.search.assert_called_once()
    call_kwargs = mock_client.search.call_args.kwargs
    assert call_kwargs["bbox"] == (13.0, 52.0, 14.0, 53.0)
    assert call_kwargs["datetime"] == "2022-01-01/2022-01-31"
    assert call_kwargs["limit"] == 10


def test_sign_items_with_mock():
    """Test sign_items method using mock."""
    client = STACClient()
    
    # Create mock unsigned items
    unsigned_item1 = Mock()
    unsigned_item1.id = "item1"
    unsigned_item2 = Mock()
    unsigned_item2.id = "item2"
    
    # Create mock signed items
    signed_item1 = Mock()
    signed_item1.id = "item1"
    signed_item1.signed = True
    
    signed_item2 = Mock()
    signed_item2.id = "item2"
    signed_item2.signed = True
    
    # Mock the planetary_computer.sign function
    with patch('sar_processing.stac_client.planetary_computer') as mock_pc:
        mock_pc.sign.side_effect = [signed_item1, signed_item2]
        
        # Test signing
        signed_items = client.sign_items([unsigned_item1, unsigned_item2])
        
        # Assertions
        assert len(signed_items) == 2
        assert signed_items[0].signed == True
        assert signed_items[1].signed == True
        assert mock_pc.sign.call_count == 2


def test_search_and_sign_with_mock():
    """Test search_and_sign method using mock."""
    client = STACClient()
    
    # Create mock items
    mock_item = Mock()
    mock_item.id = "test-item"
    
    # Mock both search and sign_items methods
    with patch.object(client, 'search') as mock_search, \
         patch.object(client, 'sign_items') as mock_sign:
        
        mock_search.return_value = [mock_item]
        mock_sign.return_value = [mock_item]
        
        # Test combined method
        result = client.search_and_sign(
            bbox=(13.0, 52.0, 14.0, 53.0),
            datetime="2022-01-01/2022-01-31",
            limit=5
        )
        
        # Verify both methods were called
        mock_search.assert_called_once_with(
            (13.0, 52.0, 14.0, 53.0),
            "2022-01-01/2022-01-31",
            5
        )
        mock_sign.assert_called_once_with([mock_item])
        assert result == [mock_item]


def test_search_with_config_limit():
    """Test that config limit is used when no limit provided."""
    config = STACConfig(limit=15)
    client = STACClient(config=config)
    
    # Mock client
    mock_client = Mock()
    mock_search_result = Mock()
    mock_search_result.items.return_value = []
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    # Search without specifying limit
    client.search(
        bbox=(13.0, 52.0, 14.0, 53.0),
        datetime="2022-01-01/2022-01-31"
    )
    
    # Verify config limit was used
    call_kwargs = mock_client.search.call_args.kwargs
    assert call_kwargs["limit"] == 15


def test_search_limit_override():
    """Test that method limit overrides config limit."""
    config = STACConfig(limit=15)
    client = STACClient(config=config)
    
    # Mock client
    mock_client = Mock()
    mock_search_result = Mock()
    mock_search_result.items.return_value = []
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    # Search with explicit limit
    client.search(
        bbox=(13.0, 52.0, 14.0, 53.0),
        datetime="2022-01-01/2022-01-31",
        limit=20  # Override config limit
    )
    
    # Verify method limit was used, not config limit
    call_kwargs = mock_client.search.call_args.kwargs
    assert call_kwargs["limit"] == 20


def test_search_query_parameters():
    """Test that correct query parameters are sent."""
    client = STACClient()
    
    # Mock client
    mock_client = Mock()
    mock_search_result = Mock()
    mock_search_result.items.return_value = []
    mock_client.search.return_value = mock_search_result
    client._client = mock_client
    
    # Perform search
    client.search(
        bbox=(13.0, 52.0, 14.0, 53.0),
        datetime="2022-01-01/2022-01-31"
    )
    
    # Verify query parameters
    call_kwargs = mock_client.search.call_args.kwargs
    assert call_kwargs["query"]["sat:orbit_state"] == {"eq": "descending"}
    assert call_kwargs["query"]["sar:instrument_mode"] == {"eq": "IW"}
    assert call_kwargs["collections"] == ["sentinel-1-grd"]


# ============================================================
# INTEGRATION TESTS (Require internet, slower)
# ============================================================

@pytest.mark.integration
def test_search_sentinel1(sample_bbox, sample_datetime_range):
    """Test searching for Sentinel-1 data."""
    client = STACClient()
    items = client.search(
        bbox=sample_bbox,
        datetime=sample_datetime_range,
        limit=5,
    )
    assert isinstance(items, list)
    # May or may not find items depending on the area/date
    if len(items) > 0:
        assert hasattr(items[0], 'id')


@pytest.mark.integration
def test_sign_items(sample_bbox, sample_datetime_range):
    """Test signing items."""
    client = STACClient()
    items = client.search(
        bbox=sample_bbox,
        datetime=sample_datetime_range,
        limit=2,
    )
    if len(items) > 0:
        signed_items = client.sign_items(items)
        assert len(signed_items) == len(items)


@pytest.mark.integration
def test_search_and_sign(sample_bbox, sample_datetime_range):
    """Test combined search and sign."""
    client = STACClient()
    items = client.search_and_sign(
        bbox=sample_bbox,
        datetime=sample_datetime_range,
        limit=2,
    )
    assert isinstance(items, list)