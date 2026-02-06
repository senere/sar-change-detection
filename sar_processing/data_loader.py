"""Data loading functionality for SAR data."""

from typing import List, Optional, Tuple
import xarray as xr
from pystac import Item
from odc.stac import load
from .config import ProcessingConfig
import numpy as np
import scipy.ndimage
from .change_detection import ChangeDetector


class SARDataLoader:
    """Loader for SAR data from STAC items."""
    
    def __init__(self, config: Optional[ProcessingConfig] = None):
        """Initialize data loader.
        
        Args:
            config: Processing configuration
        """
        self.config = config or ProcessingConfig()
    
    def load(
        self,
        items: List[Item],
        bbox: Optional[Tuple[float, float, float, float]] = None,
        crs: Optional[str] = None,
        resolution: Optional[int] = None,
    ) -> xr.Dataset:
        """Load data from STAC items.
        
        Args:
            items: Signed STAC items
            bbox: Optional bounding box (min_lon, min_lat, max_lon, max_lat)
            crs: Optional CRS override
            resolution: Optional resolution override
            
        Returns:
            xarray Dataset with loaded data
        """
        load_kwargs = {
            "bands": self.config.bands,
            "chunks": self.config.to_chunks_dict(),
            "crs": crs or self.config.crs,
            "resolution": resolution or self.config.resolution,
        }
        
        if bbox is not None:
            load_kwargs["bbox"] = bbox
        
        stack = load(items, **load_kwargs)
        return stack
    
    def get_polarization(
        self,
        dataset: xr.Dataset,
        polarization: str = "vv",
        sort_by_time: bool = True,
        speckle_filter: bool = False,
        filter_size: int = 3,
        to_db: bool = False,
    ) -> xr.DataArray:
        """Extract, optionally sort, filter, and dB-scale a polarization band.
        
        Args:
            dataset: Input xarray Dataset
            polarization: Polarization to extract (vv or vh)
            sort_by_time: Whether to sort by time
            speckle_filter: Whether to apply median speckle filter
            filter_size: Size of the median filter window
            to_db: Whether to convert to dB scale
        Returns:
            DataArray for the specified polarization
        """
        data = getattr(dataset, polarization.lower())
        
        if sort_by_time and "time" in data.dims:
            data = data.sortby("time")

        # Apply speckle filtering if requested
        if speckle_filter:
            if "y" in data.dims and "x" in data.dims:
                data = xr.apply_ufunc(
                    scipy.ndimage.median_filter,
                    data,
                    kwargs={"size": filter_size},
                    input_core_dims=[["y", "x"]],
                    output_core_dims=[["y", "x"]],
                    vectorize=True,
                    dask="parallelized",
                    output_dtypes=[data.dtype],
                )
            else:
                data = xr.DataArray(
                    scipy.ndimage.median_filter(data.values, size=filter_size),
                    coords=data.coords,
                    dims=data.dims,
                    name=data.name,
                    attrs=data.attrs,
                )

        # Convert to dB if requested
        if to_db:
            data = ChangeDetector.to_db(data)

        return data