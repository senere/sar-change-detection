# Day 4 Learning Guide: Advanced Testing & Best Practices

## 🎯 Learning Objectives

Today you'll learn:
1. **Comprehensive Testing** - Writing thorough tests with edge cases
2. **Parametrized Testing** - Testing multiple scenarios efficiently
3. **Logging** - Adding professional logging to your code
4. **Progress Tracking** - User feedback for long operations
5. **Generator Patterns** - Memory-efficient processing of large datasets
6. **Documentation** - Writing clear, helpful documentation

---

## 📚 Table of Contents

1. [Logging](#1-logging)
2. [Progress Tracking](#2-progress-tracking)
3. [Generator Pattern](#3-generator-pattern)
4. [Parametrized Testing](#4-parametrized-testing)
5. [Testing Logging](#5-testing-logging)
6. [Best Practices](#6-best-practices)
7. [Practice Exercises](#7-practice-exercises)

---

## 1. Logging

### Why Logging?

Logging helps you:
- **Debug** issues in production
- **Track** what your code is doing
- **Monitor** performance and errors
- **Understand** user behavior

### Log Levels

Python's logging module has 5 levels (from lowest to highest):

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed information for debugging")      # Level 10
logger.info("General informational messages")          # Level 20
logger.warning("Warning messages")                      # Level 30
logger.error("Error messages")                          # Level 40
logger.critical("Critical errors")                      # Level 50
```

### When to Use Each Level

| Level | Use Case | Example |
|-------|----------|---------|
| **DEBUG** | Detailed diagnostic info | "Variable x = 123", "Entering function" |
| **INFO** | General progress updates | "Processing 100 items", "Server started" |
| **WARNING** | Unexpected but recoverable | "Config file not found, using defaults" |
| **ERROR** | Errors that need attention | "Failed to load file", "API request failed" |
| **CRITICAL** | System-breaking errors | "Database unreachable", "Out of memory" |

### Real Example from Our Code

```python
# sar_processing/stac_client.py

import logging

logger = logging.getLogger(__name__)

class STACClient:
    def __init__(self, config=None):
        self.config = config or STACConfig()
        logger.debug(f"Initialized STACClient with URL: {self.config.stac_url}")
    
    def search(self, bbox, datetime, limit=None):
        logger.info(f"Searching STAC catalog: bbox={bbox}, datetime={datetime}")
        
        items = list(search.items())
        logger.info(f"Found {len(items)} items")
        
        if len(items) == 0:
            logger.warning(f"No items found for bbox={bbox}")
        
        return items
```

### Configuring Logging

```python
# Set up logging in your main script or notebook
import logging

# Basic configuration
logging.basicConfig(
    level=logging.INFO,  # Show INFO and above
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or more advanced
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # Log to file
        logging.StreamHandler()          # Also print to console
    ]
)
```

---

## 2. Progress Tracking

### Why Progress Tracking?

For long-running operations, users need to know:
- ✅ That something is happening
- ⏱️ How long it will take
- 📊 What's currently being processed

### Using tqdm

`tqdm` is the best library for progress bars in Python:

```python
from tqdm import tqdm
import time

# Simple progress bar
for i in tqdm(range(100)):
    time.sleep(0.01)  # Simulate work

# With description
for i in tqdm(range(100), desc="Processing items"):
    time.sleep(0.01)

# With custom postfix
pbar = tqdm(range(100))
for i in pbar:
    pbar.set_postfix({"loss": 0.5 - i/200})
    time.sleep(0.01)
```

### Real Example from Our Code

```python
# sar_processing/batch_processor.py

from tqdm import tqdm

def process_tasks(self, tasks, show_progress=True):
    """Process multiple tasks with progress tracking."""
    results = {}
    
    # Wrap tasks in tqdm for progress bar
    task_iterator = tqdm(tasks, desc="Processing tasks", disable=not show_progress)
    
    for task in task_iterator:
        # Update description for current task
        task_iterator.set_description(f"Processing {task.name}")
        
        # Process the task...
        results[task.name] = process(task)
    
    return results
```

### Advanced Progress Tracking

```python
from tqdm import tqdm

# Nested progress bars
for dataset in tqdm(['train', 'val', 'test'], desc="Datasets"):
    for epoch in tqdm(range(10), desc="Epochs", leave=False):
        # Training code...
        pass

# Manual progress bar
with tqdm(total=100) as pbar:
    for i in range(10):
        # Do some work
        pbar.update(10)  # Manually update progress
```

---

## 3. Generator Pattern

### What are Generators?

Generators are **memory-efficient** iterators that yield items one at a time instead of loading everything into memory.

### List vs Generator

```python
# ❌ BAD - Loads all 1 million items into memory
def get_all_items():
    items = []
    for i in range(1_000_000):
        items.append(process_item(i))
    return items

all_items = get_all_items()  # Memory: ~80 MB

# ✅ GOOD - Yields items one at a time
def get_items_generator():
    for i in range(1_000_000):
        yield process_item(i)

for item in get_items_generator():  # Memory: ~80 bytes
    use(item)
```

### Key Differences

| Aspect       | List                       | Generator |
|--------------|----------------------------|-----------|
| **Memory**   | Stores all items           | Stores one item at a time |
| **Speed**    | All items created upfront  | Items created as needed |
| **Reusable** | Can iterate multiple times | Can only iterate once |
| **Use case** | Small datasets             | Large datasets |

### Real Example from Our Code

```python
# sar_processing/stac_client.py

def search_generator(self, bbox, datetime, limit=None):
    """Search for items using generator pattern (memory efficient).
    
    This is useful for large datasets as it yields items one at a time
    instead of loading all items into memory at once.
    """
    search = self.client.search(
        collections=[self.config.collection],
        bbox=bbox,
        datetime=datetime,
        limit=limit,
    )
    
    # Yield items one at a time
    for item in search.items():
        logger.debug(f"Yielding item: {item.id}")
        yield item

# Usage
client = STACClient()

# Process items without loading all into memory
for item in client.search_generator(bbox, datetime):
    process(item)  # Process one item at a time
```

### When to Use Generators

✅ **Use generators when:**
- Processing large datasets (millions of records)
- Reading large files line by line
- Streaming data from APIs
- You only need to iterate once

❌ **Don't use generators when:**
- Dataset is small (< 1000 items)
- Need to access items multiple times
- Need random access (item[5])
- Need to know total length upfront

### Generator Examples

```python
# Read large file line by line
def read_large_file(filename):
    with open(filename) as f:
        for line in f:
            yield line.strip()

# Infinite generator
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Generator with transformation
def process_items(items):
    for item in items:
        processed = transform(item)
        if is_valid(processed):
            yield processed
```

---

## 4. Parametrized Testing

### Why Parametrize?

Instead of writing multiple similar tests, write **one test** that runs with **different inputs**.

### Basic Example

```python
import pytest

# ❌ WITHOUT parametrize - repetitive
def test_add_small():
    assert add(1, 2) == 3

def test_add_medium():
    assert add(10, 20) == 30

def test_add_large():
    assert add(100, 200) == 300

# ✅ WITH parametrize - clean and efficient
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),      # small
    (10, 20, 30),   # medium
    (100, 200, 300) # large
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Real Example from Our Tests

```python
# tests/test_advanced_day4.py

@pytest.mark.parametrize("size,expected_count", [
    ("small", 2),      # Test with 2 items
    ("medium", 10),    # Test with 10 items
    ("large", 50),     # Test with 50 items
])
def test_search_different_sizes(size, expected_count):
    """Test searching with different dataset sizes."""
    client = STACClient()
    
    # Create mock items based on size
    mock_items = [Mock(id=f"item_{i}") for i in range(expected_count)]
    
    # ... setup mocks ...
    
    items = client.search(bbox=(13, 52, 14, 53), datetime="2022-01-01/2022-01-31")
    
    assert len(items) == expected_count
```

### Advanced Parametrize

```python
# Multiple parameters
@pytest.mark.parametrize("bbox,datetime,is_valid", [
    ((13, 52, 14, 53), "2022-01-01/2022-01-31", True),
    ((-180, -90, 180, 90), "2022-01-01/2022-01-31", True),
    ((10, 10, 9, 9), "2022-01-01/2022-01-31", False),  # Invalid bbox
])
def test_search_validation(bbox, datetime, is_valid):
    if is_valid:
        result = search(bbox, datetime)
        assert result is not None
    else:
        with pytest.raises(ValueError):
            search(bbox, datetime)

# Using ids for better test names
@pytest.mark.parametrize("size,count", [
    (1, 10),
    (100, 1000),
    (1000, 10000),
], ids=["small", "medium", "large"])
def test_performance(size, count):
    # Test runs will show as:
    # test_performance[small]
    # test_performance[medium]
    # test_performance[large]
    pass
```

---

## 5. Testing Logging

### The caplog Fixture

pytest provides `caplog` to capture log messages during tests:

```python
import logging

def test_function_logs_correctly(caplog):
    """Test that function logs the expected messages."""
    
    # Set logging level
    with caplog.at_level(logging.INFO):
        my_function()  # Function that logs
    
    # Check logs
    assert "Expected message" in caplog.text
    assert caplog.records[0].levelname == "INFO"
```

### Real Examples from Our Tests

```python
# tests/test_advanced_day4.py

def test_search_logging_info(caplog):
    """Test that search method logs at INFO level."""
    client = STACClient()
    
    # ... setup mocks ...
    
    with caplog.at_level(logging.INFO):
        client.search(bbox=(13, 52, 14, 53), datetime="2022-01-01/2022-01-31")
    
    # Verify logs
    assert "Searching STAC catalog" in caplog.text
    assert "Found 0 items" in caplog.text
    assert any(record.levelname == "INFO" for record in caplog.records)


def test_search_warning_on_no_results(caplog):
    """Test that WARNING is logged when no items are found."""
    client = STACClient()
    
    # Mock to return empty results
    # ... setup ...
    
    with caplog.at_level(logging.WARNING):
        client.search(bbox=(13, 52, 14, 53), datetime="2022-01-01/2022-01-31")
    
    # Check warning was logged
    assert "No items found" in caplog.text
    warning_records = [r for r in caplog.records if r.levelname == "WARNING"]
    assert len(warning_records) > 0
```

### Advanced Log Testing

```python
def test_multiple_log_levels(caplog):
    """Test that different log levels are used correctly."""
    
    with caplog.at_level(logging.DEBUG):
        complex_function()
    
    # Check specific log levels
    debug_logs = [r for r in caplog.records if r.levelname == "DEBUG"]
    info_logs = [r for r in caplog.records if r.levelname == "INFO"]
    error_logs = [r for r in caplog.records if r.levelname == "ERROR"]
    
    assert len(debug_logs) == 3
    assert len(info_logs) == 1
    assert len(error_logs) == 0


def test_log_message_content(caplog):
    """Test specific content of log messages."""
    
    with caplog.at_level(logging.INFO):
        process_user(user_id=123, name="Alice")
    
    # Check log contains specific values
    assert "user_id=123" in caplog.text
    assert "Alice" in caplog.text
    
    # Check using record attributes
    assert caplog.records[0].module == "user_module"
    assert caplog.records[0].funcName == "process_user"
```

---

## 6. Best Practices

### Testing Best Practices

#### 1. **Arrange-Act-Assert Pattern**

```python
def test_user_registration():
    # ARRANGE - Set up test data
    user_data = {"name": "Alice", "email": "alice@example.com"}
    
    # ACT - Perform the action
    result = register_user(user_data)
    
    # ASSERT - Verify the result
    assert result.success == True
    assert result.user.name == "Alice"
```

#### 2. **Test One Thing at a Time**

```python
# ❌ BAD - Testing multiple things
def test_user_operations():
    user = create_user("Alice")
    assert user.name == "Alice"
    
    updated = update_user(user, name="Bob")
    assert updated.name == "Bob"
    
    deleted = delete_user(user)
    assert deleted == True

# ✅ GOOD - Separate tests
def test_create_user():
    user = create_user("Alice")
    assert user.name == "Alice"

def test_update_user():
    user = create_user("Alice")
    updated = update_user(user, name="Bob")
    assert updated.name == "Bob"

def test_delete_user():
    user = create_user("Alice")
    result = delete_user(user)
    assert result == True
```

#### 3. **Use Descriptive Test Names**

```python
# ❌ BAD
def test_search():
    pass

def test_error():
    pass

# ✅ GOOD
def test_search_returns_items_when_matches_found():
    pass

def test_search_returns_empty_list_when_no_matches():
    pass

def test_search_raises_value_error_for_invalid_bbox():
    pass
```

#### 4. **Mock External Dependencies**

```python
# ✅ GOOD - Mock external API
def test_fetch_weather():
    with patch('weather_api.get_temperature') as mock_api:
        mock_api.return_value = 25.0
        
        temp = fetch_current_temperature("Berlin")
        
        assert temp == 25.0
        mock_api.assert_called_once_with("Berlin")
```

### Logging Best Practices

#### 1. **Use Appropriate Log Levels**

```python
# ✅ GOOD
logger.debug(f"Processing item {i} of {total}")  # Detailed info
logger.info(f"Started processing {total} items")  # User feedback
logger.warning("Config file missing, using defaults")  # Potential issue
logger.error(f"Failed to load file: {filename}")  # Error occurred
```

#### 2. **Include Context in Log Messages**

```python
# ❌ BAD
logger.info("Processing started")
logger.error("Failed")

# ✅ GOOD
logger.info(f"Processing started: {len(items)} items, bbox={bbox}")
logger.error(f"Failed to load file {filename}: {str(error)}")
```

#### 3. **Don't Log Sensitive Information**

```python
# ❌ BAD
logger.info(f"User logged in: password={password}")

# ✅ GOOD
logger.info(f"User logged in: user_id={user_id}")
```

### Code Organization Best Practices

#### 1. **Separate Concerns**

```python
# Good structure
sar_processing/
    __init__.py
    stac_client.py      # STAC API interactions
    data_loader.py       # Data loading logic
    batch_processor.py   # Batch processing
    config.py           # Configuration

tests/
    __init__.py
    test_stac_client.py
    test_data_loader.py
    test_batch_processor.py
    conftest.py         # Shared fixtures
```

#### 2. **Use Type Hints**

```python
from typing import List, Optional, Tuple

def search(
    bbox: Tuple[float, float, float, float],
    datetime: str,
    limit: Optional[int] = None
) -> List[Item]:
    """Search for items."""
    pass
```

#### 3. **Write Docstrings**

```python
def process_data(data: np.ndarray, method: str = "mean") -> float:
    """Process data using specified method.
    
    Args:
        data: Input data array
        method: Processing method ("mean", "median", "std")
        
    Returns:
        Processed value
        
    Raises:
        ValueError: If method is not supported
        
    Example:
        >>> data = np.array([1, 2, 3, 4, 5])
        >>> process_data(data, "mean")
        3.0
    """
    pass
```

---

## 7. Practice Exercises

### Exercise 1: Add Logging

Add logging to this function:

```python
def download_file(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)
    return filename
```

<details>
<summary>Solution</summary>

```python
import logging

logger = logging.getLogger(__name__)

def download_file(url, filename):
    logger.info(f"Downloading {url} to {filename}")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        logger.debug(f"Downloaded {len(response.content)} bytes")
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Successfully saved to {filename}")
        return filename
        
    except requests.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        raise
    except IOError as e:
        logger.error(f"Failed to save file {filename}: {e}")
        raise
```
</details>

### Exercise 2: Create a Generator

Convert this function to use a generator:

```python
def process_large_dataset(items):
    results = []
    for item in items:
        processed = expensive_operation(item)
        results.append(processed)
    return results
```

<details>
<summary>Solution</summary>

```python
def process_large_dataset(items):
    """Process items using generator pattern."""
    for item in items:
        processed = expensive_operation(item)
        yield processed

# Usage
for result in process_large_dataset(items):
    use(result)  # Process one at a time
```
</details>

### Exercise 3: Write Parametrized Tests

Write parametrized tests for this function:

```python
def calculate_discount(price, discount_percent):
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)
```

<details>
<summary>Solution</summary>

```python
import pytest

@pytest.mark.parametrize("price,discount,expected", [
    (100, 0, 100),      # No discount
    (100, 10, 90),      # 10% discount
    (100, 50, 50),      # 50% discount
    (100, 100, 0),      # 100% discount
    (50, 20, 40),       # Different price
])
def test_calculate_discount(price, discount, expected):
    result = calculate_discount(price, discount)
    assert result == expected


@pytest.mark.parametrize("price,discount", [
    (100, -10),   # Negative discount
    (100, 101),   # Over 100%
    (100, 150),   # Way over 100%
])
def test_calculate_discount_invalid(price, discount):
    with pytest.raises(ValueError):
        calculate_discount(price, discount)
```
</details>

### Exercise 4: Test Logging

Write tests for the logging in Exercise 1's solution:

<details>
<summary>Solution</summary>

```python
def test_download_file_logs_success(caplog):
    """Test that successful download logs correctly."""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.content = b"file content"
        mock_get.return_value = mock_response
        
        with caplog.at_level(logging.INFO):
            download_file("http://example.com/file.txt", "file.txt")
        
        assert "Downloading http://example.com/file.txt" in caplog.text
        assert "Successfully saved to file.txt" in caplog.text


def test_download_file_logs_error(caplog):
    """Test that failed download logs error."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.RequestException("Network error")
        
        with caplog.at_level(logging.ERROR):
            with pytest.raises(requests.RequestException):
                download_file("http://example.com/file.txt", "file.txt")
        
        assert "Failed to download" in caplog.text
        assert "Network error" in caplog.text
```
</details>

---

## 🎓 Summary

### What You Learned Today

1. **Logging**
   - Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Add context to log messages
   - Test logging with caplog fixture

2. **Progress Tracking**
   - Use tqdm for user feedback
   - Make it optional with `show_progress` parameter
   - Update descriptions dynamically

3. **Generator Pattern**
   - Memory-efficient processing with `yield`
   - One item at a time vs loading all
   - When to use generators vs lists

4. **Parametrized Testing**
   - Test multiple scenarios with one test
   - Use `@pytest.mark.parametrize`
   - Make tests more maintainable

5. **Comprehensive Testing**
   - Test edge cases
   - Test error conditions
   - Combine multiple concepts

### Key Takeaways

✅ **Always add logging** - It helps debug production issues
✅ **Show progress** - Users need feedback on long operations
✅ **Use generators** - For large datasets to save memory
✅ **Parametrize tests** - Don't repeat yourself
✅ **Test everything** - Normal cases, edge cases, errors

### Next Steps

1. Run the tests: `pytest tests/test_advanced_day4.py -v`
2. Check test coverage: `pytest --cov=sar_processing tests/`
3. Try the exercises above
4. Add logging to your existing code
5. Convert list operations to generators where appropriate

---

## 📖 Additional Resources

- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [tqdm Documentation](https://tqdm.github.io/)
- [Python Generators](https://realpython.com/introduction-to-python-generators/)
- [pytest Parametrize](https://docs.pytest.org/en/latest/how-to/parametrize.html)
- [pytest Logging](https://docs.pytest.org/en/latest/how-to/logging.html)

---

**Happy Testing! 🚀**
