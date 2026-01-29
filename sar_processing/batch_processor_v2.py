"""Batch processing for multiple regions and time periods - Day 4 Enhanced Version.

New features:
- Logging for all operations
- Progress tracking with tqdm
- Better error handling
"""

import logging
from typing import List, Dict, Tuple, Optional
import xarray as xr
from dataclasses import dataclass
from tqdm import tqdm
from .stac_client import STACClient
from .data_loader import SARDataLoader
from .change_detection import ChangeDetector
from .statistics import SARStatistics

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ProcessingTask:
    """Definition of a processing task."""
    
    name: str
    bbox: Tuple[float, float, float, float]
    datetime: str
    crs: Optional[str] = None


class BatchProcessor:
    """Process multiple regions and time periods."""
    
    def __init__(
        self,
        stac_client: STACClient,
        data_loader: SARDataLoader,
    ):
        """Initialize batch processor.
        
        Args:
            stac_client: STAC client for searching
            data_loader: Data loader for loading
        """
        self.stac_client = stac_client
        self.data_loader = data_loader
        self.change_detector = ChangeDetector()
        self.statistics = SARStatistics()
    
    def process_tasks(
        self,
        tasks: List[ProcessingTask],
        polarization: str = "vv",
        compute_stats: bool = True,
        compute_change: bool = True,
        show_progress: bool = True,
    ) -> Dict[str, Dict]:
        """Process multiple tasks.
        
        Args:
            tasks: List of processing tasks
            polarization: Polarization to process
            compute_stats: Whether to compute temporal statistics
            compute_change: Whether to compute change detection
            show_progress: Whether to show progress bar
            
        Returns:
            Dictionary mapping task name to results
        """
        results = {}
        
        logger.info(f"Starting batch processing of {len(tasks)} tasks")
        
        # Use tqdm for progress tracking
        task_iterator = tqdm(tasks, desc="Processing tasks", disable=not show_progress)
        
        for task in task_iterator:
            task_iterator.set_description(f"Processing {task.name}")
            logger.info(f"Processing task: {task.name}")
            
            # Search and load data
            items = self.stac_client.search_and_sign(
                bbox=task.bbox,
                datetime=task.datetime,
            )
            
            if len(items) == 0:
                logger.warning(f"No items found for {task.name}")
                results[task.name] = {"error": "No items found"}
                continue
            
            logger.debug(f"Found {len(items)} items for {task.name}")
            
            # Load data
            dataset = self.data_loader.load(
                items=items,
                bbox=task.bbox,
                crs=task.crs,
            )
            
            data = self.data_loader.get_polarization(dataset, polarization)
            
            task_results = {
                "num_items": len(items),
                "shape": data.shape,
                "data": data,
            }
            
            # Compute statistics
            if compute_stats and len(data.time) > 0:
                try:
                    logger.debug(f"Computing statistics for {task.name}")
                    stats = self.statistics.temporal_stats(
                        data,
                        compute=True,
                        show_progress=False,
                    )
                    task_results["stats"] = stats
                    logger.info(f"Computed statistics for {task.name}")
                except Exception as e:
                    logger.error(f"Error computing stats for {task.name}: {e}")
            
            # Compute change detection
            if compute_change and len(data.time) >= 2:
                try:
                    logger.debug(f"Computing change detection for {task.name}")
                    change = self.change_detector.temporal_change(data)
                    if change is not None:
                        task_results["change"] = change.compute()
                        logger.info(f"Computed change detection for {task.name}")
                except Exception as e:
                    logger.error(f"Error computing change for {task.name}: {e}")
            
            results[task.name] = task_results
        
        logger.info(f"Batch processing complete: processed {len(results)} tasks")
        return results
    
    def process_multiple_regions(
        self,
        regions: Dict[str, Tuple[float, float, float, float]],
        datetime: str,
        **kwargs,
    ) -> Dict[str, Dict]:
        """Process multiple regions for the same time period.
        
        Args:
            regions: Dictionary mapping region name to bbox
            datetime: Date range for all regions
            **kwargs: Additional arguments for process_tasks
            
        Returns:
            Dictionary mapping region name to results
        """
        tasks = [
            ProcessingTask(name=name, bbox=bbox, datetime=datetime)
            for name, bbox in regions.items()
        ]
        
        return self.process_tasks(tasks, **kwargs)
    
    def process_multiple_periods(
        self,
        bbox: Tuple[float, float, float, float],
        periods: Dict[str, str],
        **kwargs,
    ) -> Dict[str, Dict]:
        """Process the same region for multiple time periods.
        
        Args:
            bbox: Bounding box for all periods
            periods: Dictionary mapping period name to datetime range
            **kwargs: Additional arguments for process_tasks
            
        Returns:
            Dictionary mapping period name to results
        """
        tasks = [
            ProcessingTask(name=name, bbox=bbox, datetime=dt)
            for name, dt in periods.items()
        ]
        
        return self.process_tasks(tasks, **kwargs)
