"""
Quick test script to verify all modules work together.
Run this to test your SAR processing pipeline.
"""

from sar_processing import (
    STACClient,
    SARDataLoader,
    ChangeDetector,
    SARStatistics,
    SARVisualizer,
    BatchProcessor,
)
from sar_processing.config import STACConfig, ProcessingConfig

def main():
    print("🚀 Testing SAR Processing Pipeline...")
    
    # Initialize modules
    stac_client = STACClient()
    data_loader = SARDataLoader()
    
    # Search for data (small test)
    print("\n1. Searching for data...")
    items = stac_client.search_and_sign(
        bbox=(13.0, 52.0, 13.5, 52.5),  # Small area
        datetime="2022-01-01/2022-01-15",
        limit=2
    )
    print(f"   ✅ Found {len(items)} items")
    
    if len(items) == 0:
        print("   ⚠️ No data found. Try different dates/region.")
        return
    
    # Load data
    print("\n2. Loading data...")
    dataset = data_loader.load(items)
    vv_data = data_loader.get_polarization(dataset, "vv")
    print(f"   ✅ Loaded data shape: {vv_data.shape}")
    
    # Change detection
    if len(vv_data.time) >= 2:
        print("\n3. Change detection...")
        change = ChangeDetector.temporal_change(vv_data)
        if change is not None:
            print(f"   ✅ Change map computed")
            print(f"   Range: {float(change.min()):.2f} to {float(change.max()):.2f} dB")
    
    # Statistics
    if len(vv_data.time) > 0:
        print("\n4. Computing statistics...")
        stats = SARStatistics.temporal_stats(vv_data, show_progress=False)
        print(f"   ✅ Statistics computed")
    
    print("\n✅ All modules working correctly!")
    print("\nNext steps:")
    print("  - Open example_end_to_end.ipynb for full examples")
    print("  - Run 'pytest tests/' to run all tests")
    print("  - Customize configurations for your region")

if __name__ == "__main__":
    main()
