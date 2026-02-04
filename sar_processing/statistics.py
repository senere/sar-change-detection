"""Statistical analysis for SAR data."""
import xarray as xr
from typing import Dict, Union
from dask.diagnostics.progress import ProgressBar
from collections.abc import Mapping


class SARStatistics:
    """Statistical computations for SAR data."""
    
    @staticmethod
    def temporal_stats(
        data: xr.DataArray,
        compute: bool = True,
        show_progress: bool = True,
    ) -> Dict[str, xr.DataArray]:
        """Compute temporal statistics.
        
        Args:
            data: DataArray with time dimension
            compute: Whether to compute immediately or return lazy results
            show_progress: Show progress bar during computation
            
        Returns:
            Dictionary with mean and std deviation
        """
        if "time" not in data.dims or len(data.time) == 0:
            raise ValueError("Data must have a time dimension with at least one value")
        
        mean = data.mean(dim="time")
        std = data.std(dim="time")
        
        if compute:
            if show_progress:
                with ProgressBar():
                    mean = mean.compute()
                    std = std.compute()
            else:
                mean = mean.compute()
                std = std.compute()
        
        return {"mean": mean, "std": std}
    
    @staticmethod
    def spatial_stats(data: xr.DataArray, compute: bool = True) -> Mapping[str, float | xr.DataArray]:
        """Compute spatial statistics for a single image.
        
        Args:
            data: DataArray (2D or 3D)
            compute: Whether to compute immediately
            
        Returns:
            Dictionary with min, max, mean, std
        """
        stats = {
            "min": data.min(),
            "max": data.max(),
            "mean": data.mean(),
            "std": data.std(),
        }
        
        if compute:
            stats = {k: float(v.compute()) for k, v in stats.items()}
        
        return stats
    
    @staticmethod
    def percentiles(
        data: xr.DataArray,
        percentiles: list = [10, 25, 50, 75, 90],
        compute: bool = True,
    ) -> Dict[str, float]:
        """Compute percentiles.
        
        Args:
            data: DataArray
            percentiles: List of percentile values
            compute: Whether to compute immediately
            
        Returns:
            Dictionary mapping percentile to value
        """
        import numpy as np
        
        result = {}
        for p in percentiles:
            result[f"p{p}"] = data.quantile(p / 100.0)
        
        if compute:
            result = {k: float(v.compute()) for k, v in result.items()}
        
        return result