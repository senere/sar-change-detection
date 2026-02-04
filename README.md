# SAR Project 1

A toolkit for processing Sentinel-1 SAR data, including change detection, statistics, and visualization. 

## Features
- Batch processing for multiple regions and time periods
- Change detection algorithms
- Statistical analysis of SAR data
- Data loading and STAC client integration
- Visualization tools
- Comprehensive test suite

## Installation
Install dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

## Usage
Import the package in your Python code:

```python
from sar_processing import STACClient, SARDataLoader, ChangeDetector, SARStatistics, SARVisualizer, BatchProcessor
```

See the example notebooks and scripts for end-to-end workflows.

## Testing
Run tests with pytest:

```bash
pytest
```

## Project Structure
- `sar_processing/` — Core library modules
- `tests/` — Unit and integration tests
- `requirements.txt` — Python dependencies

## License
Specify your license here.

---
For more details, see the learning guides and notebooks included in the repository.
