"""Configuration management for SAR processing."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class STACConfig:
    """Configuration for STAC catalog searches."""
    
    stac_url: str = "https://planetarycomputer.microsoft.com/api/stac/v1"
    collection: str = "sentinel-1-grd"
    orbit_state: str = "descending"
    instrument_mode: str = "IW"
    limit: Optional[int] = None


@dataclass
class ProcessingConfig:
    """Configuration for data processing."""
    
    bands: List[str] = field(default_factory=lambda: ["vh", "vv"])
    chunk_size: Tuple[int, int] = (512, 512)
    resolution: int = 20
    crs: str = "EPSG:32633"  # Default for Central Europe
    
    def to_chunks_dict(self) -> dict:
        """Convert chunk_size to dictionary format."""
        return {"x": self.chunk_size[0], "y": self.chunk_size[1]}


@dataclass
class VisualizationConfig:
    """Configuration for visualization."""
    
    db_min: float = -25 # for higher contrast use db_min=-15, db_max=10
    db_max: float = 5
    change_min: float = -5
    change_max: float = 5
    figsize: Tuple[int, int] = (18, 5)
    cmap_gray: str = "gray"
    cmap_change: str = "RdBu_r"
    cmap_stats: str = "viridis"