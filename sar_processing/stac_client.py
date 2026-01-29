"""STAC catalog client for searching satellite data."""

import logging
from typing import List, Optional, Tuple, Generator
from pystac_client import Client
from pystac import Item
import planetary_computer
from .config import STACConfig

# Configure logging
logger = logging.getLogger(__name__)


class STACClient:
    """Client for interacting with STAC catalogs."""
    
    def __init__(self, config: Optional[STACConfig] = None):
        """Initialize STAC client.
        
        Args:
            config: STAC configuration object
        """
        self.config = config or STACConfig()
        self._client: Optional[Client] = None
        logger.debug(f"Initialized STACClient with URL: {self.config.stac_url}")
    
    @property
    def client(self) -> Client:
        """Lazy-load STAC client."""
        if self._client is None:
            logger.info(f"Opening STAC catalog: {self.config.stac_url}")
            self._client = Client.open(self.config.stac_url)
            logger.debug("STAC client successfully initialized")
        return self._client
    
    def search(
        self,
        bbox: Tuple[float, float, float, float],
        datetime: str,
        limit: Optional[int] = None,
    ) -> List[Item]:
        """Search for Sentinel-1 items.
        
        Args:
            bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
            datetime: Date range as "YYYY-MM-DD/YYYY-MM-DD"
            limit: Maximum number of items to return
            
        Returns:
            List of STAC items
        """
        search_limit = limit or self.config.limit
        logger.info(f"Searching STAC catalog: bbox={bbox}, datetime={datetime}, limit={search_limit}")
        
        search = self.client.search(
            collections=[self.config.collection],
            bbox=bbox,
            datetime=datetime,
            query={
                "sat:orbit_state": {"eq": self.config.orbit_state},
                "sar:instrument_mode": {"eq": self.config.instrument_mode},
            },
            limit=search_limit,
        )
        
        items = list(search.items())
        logger.info(f"Found {len(items)} items")
        
        if len(items) == 0:
            logger.warning(f"No items found for bbox={bbox}, datetime={datetime}")
        
        return items
    
    def sign_items(self, items: List[Item]) -> List[Item]:
        """Sign items for Microsoft Planetary Computer access.
        
        Args:
            items: List of STAC items
            
        Returns:
            List of signed items
        """
        logger.debug(f"Signing {len(items)} items")
        signed = [planetary_computer.sign(item) for item in items]
        logger.debug("All items signed successfully")
        return signed
    
    def search_and_sign(
        self,
        bbox: Tuple[float, float, float, float],
        datetime: str,
        limit: Optional[int] = None,
    ) -> List[Item]:
        """Search and sign items in one call.
        
        Args:
            bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
            datetime: Date range as "YYYY-MM-DD/YYYY-MM-DD"
            limit: Maximum number of items to return
            
        Returns:
            List of signed STAC items
        """
        items = self.search(bbox, datetime, limit)
        return self.sign_items(items)
    
    # ============================================================
    # GENERATOR PATTERN - For handling large datasets efficiently
    # ============================================================
    
    def search_generator(
        self,
        bbox: Tuple[float, float, float, float],
        datetime: str,
        limit: Optional[int] = None,
    ) -> Generator[Item, None, None]:
        """Search for items using generator pattern (memory efficient).
        
        This is useful for large datasets as it yields items one at a time
        instead of loading all items into memory at once.
        
        Args:
            bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
            datetime: Date range as "YYYY-MM-DD/YYYY-MM-DD"
            limit: Maximum number of items to return
            
        Yields:
            STAC items one at a time
            
        Example:
            >>> client = STACClient()
            >>> for item in client.search_generator(bbox, datetime):
            ...     process_item(item)  # Process without loading all into memory
        """
        search_limit = limit or self.config.limit
        
        logger.info(f"Starting generator search: bbox={bbox}, datetime={datetime}, limit={search_limit}")
        
        search = self.client.search(
            collections=[self.config.collection],
            bbox=bbox,
            datetime=datetime,
            query={
                "sat:orbit_state": {"eq": self.config.orbit_state},
                "sar:instrument_mode": {"eq": self.config.instrument_mode},
            },
            limit=search_limit,
        )
        
        count = 0
        for item in search.items():
            count += 1
            logger.debug(f"Yielding item {count}: {item.id}")
            yield item
        
        logger.info(f"Generator search complete: yielded {count} items")
    
    def search_and_sign_generator(
        self,
        bbox: Tuple[float, float, float, float],
        datetime: str,
        limit: Optional[int] = None,
    ) -> Generator[Item, None, None]:
        """Search and sign items using generator pattern.
        
        Memory-efficient version that yields signed items one at a time.
        
        Args:
            bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
            datetime: Date range as "YYYY-MM-DD/YYYY-MM-DD"
            limit: Maximum number of items to return
            
        Yields:
            Signed STAC items one at a time
        """
        for item in self.search_generator(bbox, datetime, limit):
            logger.debug(f"Signing item: {item.id}")
            yield planetary_computer.sign(item)