# Day 4 Demo: Advanced Features

## Overview
This notebook demonstrates:
1. Logging setup and usage
2. Progress tracking with tqdm
3. Generator pattern for memory efficiency
4. Testing with parametrize

Let's explore each concept!

---

## 1. Setting Up Logging

First, let's configure logging to see what our code is doing:

```python
import logging
import sys

# Configure logging to show in notebook
logging.basicConfig(
    level=logging.INFO,  # Show INFO and above
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Show in notebook output
    ]
)

# Get our module's logger
logger = logging.getLogger('sar_processing')
logger.setLevel(logging.DEBUG)  # Show all levels for our code

print("✅ Logging configured!")
```

---

## 2. Testing the STAC Client with Logging

Now let's use the STAC client and watch the logs:

```python
from sar_processing.stac_client import STACClient
from sar_processing.config import STACConfig

# Create client
config = STACConfig(limit=5)  # Limit to 5 items for demo
client = STACClient(config=config)

print("\n" + "="*60)
print("Watch the logs below to see what's happening:")
print("="*60 + "\n")

# This will log: initialization, catalog opening, searching, etc.
items = client.search(
    bbox=(13.0, 52.0, 14.0, 53.0),  # Berlin area
    datetime="2022-01-01/2022-01-15",
)

print(f"\n✅ Found {len(items)} items")
```

---

## 3. Generator Pattern Demo

Let's compare memory usage between list and generator approaches:

```python
import sys

# Regular list approach (loads all into memory)
def get_items_list(client, bbox, datetime, limit=100):
    """Returns a list of all items."""
    items = client.search(bbox, datetime, limit)
    return items

# Generator approach (yields one at a time)
def get_items_generator(client, bbox, datetime, limit=100):
    """Yields items one at a time."""
    for item in client.search_generator(bbox, datetime, limit):
        yield item

# Demo: process just first 3 items
bbox = (13.0, 52.0, 14.0, 53.0)
datetime = "2022-01-01/2022-01-31"

print("Using generator (memory efficient):")
print("-" * 40)

count = 0
for item in client.search_generator(bbox, datetime, limit=10):
    print(f"Processing item {count + 1}: {item.id[:30]}...")
    count += 1
    if count >= 3:  # Process only first 3
        print("Stopping early - other items not loaded!")
        break

print(f"\n✅ Processed {count} items without loading all into memory")
```

### When to Use Generators

Use generators when:
- ✅ Dataset is large (thousands/millions of items)
- ✅ You only need to iterate once
- ✅ You might not process all items

Use lists when:
- ✅ Dataset is small (< 100 items)
- ✅ You need to iterate multiple times
- ✅ You need random access (items[5])

---

## 4. Progress Tracking Demo

Let's process multiple regions with progress tracking:

```python
from sar_processing.batch_processor import BatchProcessor, ProcessingTask
from sar_processing.data_loader import SARDataLoader

# Create processor
data_loader = SARDataLoader()
processor = BatchProcessor(
    stac_client=client,
    data_loader=data_loader
)

# Define multiple tasks
tasks = [
    ProcessingTask(
        name="Berlin_Jan",
        bbox=(13.0, 52.0, 14.0, 53.0),
        datetime="2022-01-01/2022-01-15"
    ),
    ProcessingTask(
        name="Berlin_Feb",
        bbox=(13.0, 52.0, 14.0, 53.0),
        datetime="2022-02-01/2022-02-15"
    ),
    ProcessingTask(
        name="Hamburg",
        bbox=(9.5, 53.3, 10.3, 53.8),
        datetime="2022-01-01/2022-01-15"
    ),
]

print("\nProcessing tasks with progress bar:")
print("="*60)

# Process with progress bar (you'll see a tqdm progress bar!)
results = processor.process_tasks(
    tasks,
    compute_stats=False,  # Skip stats for faster demo
    compute_change=False,
    show_progress=True
)

print(f"\n✅ Processed {len(results)} tasks")
for task_name, result in results.items():
    if 'error' in result:
        print(f"  - {task_name}: {result['error']}")
    else:
        print(f"  - {task_name}: {result['num_items']} items, shape={result['shape']}")
```

---

## 5. Different Log Levels in Action

Let's demonstrate different log levels:

```python
# Create a logger for demo
demo_logger = logging.getLogger('demo')

print("Demonstrating log levels:")
print("-" * 60)

demo_logger.debug("This is DEBUG - detailed diagnostic info")
demo_logger.info("This is INFO - general information")
demo_logger.warning("This is WARNING - something unexpected")
demo_logger.error("This is ERROR - something failed")
demo_logger.critical("This is CRITICAL - system failure!")

print("\nNote: DEBUG might not show because we set level to INFO")
print("To see DEBUG, run: logging.basicConfig(level=logging.DEBUG)")
```

---

## 6. Real-World Example: Processing Large Dataset

Here's how all concepts work together:

```python
def process_large_region_efficiently(
    client,
    bbox,
    datetime_ranges,
    show_progress=True
):
    """
    Process a large region across multiple time periods.
    
    Features:
    - Logging for debugging
    - Generator for memory efficiency
    - Progress tracking for user feedback
    """
    logger.info(f"Starting large region processing")
    logger.info(f"  Region: {bbox}")
    logger.info(f"  Time periods: {len(datetime_ranges)}")
    
    all_items = []
    
    # Use tqdm for progress
    from tqdm import tqdm
    periods = tqdm(datetime_ranges, desc="Time periods", disable=not show_progress)
    
    for period in periods:
        periods.set_description(f"Processing {period}")
        
        # Use generator for memory efficiency
        logger.debug(f"Searching for {period}")
        
        for item in client.search_generator(bbox, period, limit=10):
            logger.debug(f"  Found item: {item.id}")
            all_items.append(item)
        
        logger.info(f"  Period {period}: found {len(all_items)} total items so far")
    
    logger.info(f"✅ Processing complete: {len(all_items)} total items")
    return all_items


# Demo
datetime_ranges = [
    "2022-01-01/2022-01-15",
    "2022-02-01/2022-02-15",
    "2022-03-01/2022-03-15",
]

items = process_large_region_efficiently(
    client,
    bbox=(13.0, 52.0, 14.0, 53.0),
    datetime_ranges=datetime_ranges,
    show_progress=True
)

print(f"\n✅ Total items found: {len(items)}")
```

---

## 7. Summary

### What We Demonstrated:

1. **Logging**
   - Configured logging to see what's happening
   - Different log levels (DEBUG, INFO, WARNING, ERROR)
   - Logging helps debugging and monitoring

2. **Generator Pattern**
   - Memory-efficient processing
   - Process items one at a time
   - Can stop early without loading everything

3. **Progress Tracking**
   - tqdm shows progress bars
   - User feedback for long operations
   - Can be disabled when not needed

4. **Best Practices**
   - Combine all features for robust code
   - Log important operations
   - Show progress to users
   - Use generators for large datasets

### Next Steps:

1. Run the tests: `pytest tests/test_advanced_day4.py -v`
2. Read the full guide: `DAY4_LEARNING_GUIDE.md`
3. Try adding logging to your own code
4. Experiment with generators for large datasets
5. Write parametrized tests for your functions

---

## 🎓 Key Takeaways

✅ **Logging is essential** - It helps you understand what your code is doing
✅ **Generators save memory** - Use them for large datasets
✅ **Progress bars improve UX** - Users need feedback
✅ **Test everything** - Use parametrize for efficiency

**Happy coding! 🚀**
