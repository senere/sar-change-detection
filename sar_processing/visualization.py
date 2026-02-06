"""Visualization functions for SAR data."""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from typing import Optional, Tuple
from .config import VisualizationConfig
from .change_detection import ChangeDetector


class SARVisualizer:
    """Visualization for SAR data and change detection."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """Initialize visualizer.
        
        Args:
            config: Visualization configuration
        """
        self.config = config or VisualizationConfig()
    
    def plot_change_detection(
        self,
        before: xr.DataArray,
        after: xr.DataArray,
        change: xr.DataArray,
        figsize: Optional[Tuple[int, int]] = None,
    ) -> Tuple[plt.Figure, np.ndarray]:
        """Plot before, after, and change images.
        
        Args:
            before: Reference image
            after: Target image
            change: Change detection result
            figsize: Figure size override
            
        Returns:
            Tuple of (figure, axes)
        """
        figsize = figsize or self.config.figsize
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        # Compute if needed
        before_data = before.compute() if hasattr(before.data, "compute") else before
        after_data = after.compute() if hasattr(after.data, "compute") else after
        change_data = change.compute() if hasattr(change.data, "compute") else change
        
        # Before image (in dB)
        before_db = ChangeDetector.to_db(before_data)
        im1 = axes[0].imshow(
            before_db,
            cmap=self.config.cmap_gray,
            vmin=self.config.db_min,
            vmax=self.config.db_max,
        )
        before_time = str(before.time.values)[:10] if "time" in before.coords else "N/A"
        axes[0].set_title(f"Before\n{before_time}")
        axes[0].axis("off")
        plt.colorbar(im1, ax=axes[0], label="Backscatter (dB)")
        
        # After image (in dB)
        after_db = ChangeDetector.to_db(after_data)
        im2 = axes[1].imshow(
            after_db,
            cmap=self.config.cmap_gray,
            vmin=self.config.db_min,
            vmax=self.config.db_max,
        )
        after_time = str(after.time.values)[:10] if "time" in after.coords else "N/A"
        axes[1].set_title(f"After\n{after_time}")
        axes[1].axis("off")
        plt.colorbar(im2, ax=axes[1], label="Backscatter (dB)")
        
        # Change detection
        im3 = axes[2].imshow(
            change_data,
            cmap=self.config.cmap_change,
            vmin=self.config.change_min,
            vmax=self.config.change_max,
        )
        axes[2].set_title("Change Detection\n(Log Ratio)")
        axes[2].axis("off")
        plt.colorbar(im3, ax=axes[2], label="Change (dB)")
        
        plt.tight_layout()
        return fig, axes
    
    def plot_temporal_stats(
        self,
        mean: xr.DataArray,
        std: xr.DataArray,
        figsize: Tuple[int, int] = (12, 5),
    ) -> Tuple[plt.Figure, np.ndarray]:
        """Plot temporal mean and standard deviation.
        
        Args:
            mean: Temporal mean
            std: Temporal standard deviation
            figsize: Figure size
            
        Returns:
            Tuple of (figure, axes)
        """
        mean_data = mean.compute() if hasattr(mean.data, "compute") else mean
        std_data = std.compute() if hasattr(std.data, "compute") else std
        
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        
        # Mean in dB
        mean_db = ChangeDetector.to_db(mean_data)
        im1 = axes[0].imshow(mean_db, cmap=self.config.cmap_gray)
        axes[0].set_title("Temporal Mean (dB)")
        axes[0].axis("off")
        plt.colorbar(im1, ax=axes[0])
        
        # Std in dB
        std_db = ChangeDetector.to_db(std_data)
        im2 = axes[1].imshow(std_db, cmap=self.config.cmap_stats)
        axes[1].set_title("Temporal Std Dev (dB)")
        axes[1].axis("off")
        plt.colorbar(im2, ax=axes[1])
        
        plt.tight_layout()
        return fig, axes