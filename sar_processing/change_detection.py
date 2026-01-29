"""Change detection algorithms for SAR data."""

import numpy as np
import xarray as xr
from typing import Optional, Tuple


class ChangeDetector:
    """Change detection for SAR imagery."""
    
    @staticmethod
    def log_ratio(
        before: xr.DataArray,
        after: xr.DataArray,
        epsilon: float = 1e-10,
        input_is_db: bool = False,
    ) -> xr.DataArray:
        """Compute log-ratio change detection.
        
        Args:
            before: Reference image (earlier time)
            after: Target image (later time)
            epsilon: Small value to avoid log(0)
            input_is_db: If True, input is already in dB, so just subtract (after - before)
        Returns:
            Log-ratio change map in dB
        """
        if input_is_db:
            return after - before
        else:
            ratio = (after + epsilon) / (before + epsilon)
            return 10 * np.log10(ratio)
    
    @staticmethod
    def temporal_change(
        data: xr.DataArray,
        time_index_before: int = 0,
        time_index_after: int = -1,
        epsilon: float = 1e-10,
    ) -> Optional[xr.DataArray]:
        """Compute change between two time steps.
        
        Args:
            data: DataArray with time dimension
            time_index_before: Index of reference image
            time_index_after: Index of target image
            epsilon: Small value to avoid log(0)
            
        Returns:
            Change detection result or None if insufficient data
        """
        if "time" not in data.dims or len(data.time) < 2:
            return None
        
        image_before = data.isel(time=time_index_before)
        image_after = data.isel(time=time_index_after)
        
        return ChangeDetector.log_ratio(image_before, image_after, epsilon)
    
    @staticmethod
    def to_db(data: xr.DataArray, epsilon: float = 1e-10) -> xr.DataArray:
        """Convert linear backscatter to dB.
        
        Args:
            data: Linear backscatter values
            epsilon: Small value to avoid log(0)
            
        Returns:
            Backscatter in dB
        """
        return 10 * np.log10(data + epsilon)
    
    @staticmethod
    def get_time_range(data: xr.DataArray) -> Optional[Tuple[str, str]]:
        """Get the time range from data.
        
        Args:
            data: DataArray with time dimension
            
        Returns:
            Tuple of (min_time, max_time) as strings or None
        """
        if "time" not in data.dims or len(data.time) == 0:
            return None
        
        min_time = str(data.time.min().values)[:10]
        max_time = str(data.time.max().values)[:10]
        return min_time, max_time