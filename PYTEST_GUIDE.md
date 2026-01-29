# Pytest Learning Guide

## Table of Contents
1. [Pytest Basics](#pytest-basics)
2. [Fixtures (conftest.py)](#fixtures)
3. [Mocking](#mocking)
4. [Assertions](#assertions)
5. [Running Tests](#running-tests)
6. [Test Organization](#test-organization)

---

## Pytest Basics

### What is pytest?
- A testing framework for Python
- Makes it easy to write small tests, yet scales for complex functional testing
- No boilerplate code required (unlike unittest)

### Key Concepts:
- **Test Discovery**: pytest automatically finds files starting with `test_` or ending with `_test.py`
- **Test Functions**: Functions starting with `test_` are automatically run as tests
- **Assertions**: Use simple `assert` statements (no need for `self.assertEqual()`)
- **Fixtures**: Reusable setup code
- **Parametrization**: Run same test with different inputs
- **Mocking**: Replace real objects with fake ones for testing

---

## Fixtures

**What are fixtures?**
- Reusable pieces of code that set up test data
- Run automatically before tests
- Defined with `@pytest.fixture` decorator
- Can depend on other fixtures

**Example from our `conftest.py`:**

```python
@pytest.fixture
def sample_bbox():
    """Provides a sample bounding box (Berlin area)."""
    return (13.0, 52.3, 13.7, 52.7)
```

**Usage:**
```python
def test_something(sample_bbox):  # pytest injects the fixture
    # sample_bbox is now available
    print(sample_bbox)  # (13.0, 52.3, 13.7, 52.7)
```

**Fixture Scopes:**
- `function` (default): Run once per test
- `class`: Run once per test class
- `module`: Run once per file
- `session`: Run once per test session

**Example with scope:**
```python
@pytest.fixture(scope="module")
def expensive_setup():
    # This runs only once for the entire module
    return some_expensive_operation()
```

---

## Mocking

**What is mocking?**
- Replace real objects with fake ones during testing
- Useful when:
  - You don't want to hit external APIs
  - You want to test error handling
  - Real objects are slow or expensive

**Types of Mocking:**

### 1. Mock Objects (`unittest.mock.Mock`)
```python
from unittest.mock import Mock

# Create a mock object
mock_client = Mock()

# Set return values
mock_client.search.return_value = ["item1", "item2"]

# Use it
result = mock_client.search()  # Returns ["item1", "item2"]

# Verify it was called
mock_client.search.assert_called_once()
```

### 2. Patching (`@patch`)
```python
from unittest.mock import patch

@patch('module.ClassName')
def test_something(mock_class):
    # mock_class replaces the real class
    mock_class.return_value = Mock()
```

### 3. Property Mocking (`PropertyMock`)
```python
from unittest.mock import PropertyMock

with patch.object(MyClass, 'my_property', new_callable=PropertyMock) as mock_prop:
    mock_prop.return_value = "fake value"
```

---

## Assertions

**Basic Assertions:**
```python
assert value == expected
assert value is not None
assert value in list
assert isinstance(value, type)
```

**With Error Messages:**
```python
assert value == expected, f"Expected {expected}, got {value}"
```

**Pytest Special Assertions:**
```python
import pytest

# Test for exceptions
with pytest.raises(ValueError):
    raise ValueError("error")

# Test for warnings
with pytest.warns(UserWarning):
    warnings.warn("warning", UserWarning)

# Approximate comparisons
assert value == pytest.approx(3.14, rel=1e-2)
```

---

## Running Tests

### Basic Commands:
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific file
pytest tests/test_stac_client.py

# Run specific test
pytest tests/test_stac_client.py::test_search_with_mock

# Run tests matching pattern
pytest -k "stac"

# Show print statements
pytest -s

# Stop at first failure
pytest -x

# Show local variables on failure
pytest -l
```

### Coverage:
```bash
# Run with coverage report
pytest --cov=sar_processing tests/

# Generate HTML coverage report
pytest --cov=sar_processing --cov-report=html tests/
```

### Markers:
```python
import pytest

@pytest.mark.slow
def test_slow_function():
    pass

@pytest.mark.integration
def test_with_api():
    pass
```

Run specific markers:
```bash
pytest -m slow          # Run only slow tests
pytest -m "not slow"    # Skip slow tests
```

---

## Test Organization

### Our Test Structure:

```
tests/
├── conftest.py              # Shared fixtures
├── test_stac_client.py      # Tests for STAC client
├── test_data_loader.py      # Tests for data loading
├── test_change_detection.py # Tests for change detection
├── test_statistics.py       # Tests for statistics
└── test_batch_processor.py  # Tests for batch processing
```

### Best Practices:

1. **One test file per module**: `test_stac_client.py` tests `stac_client.py`
2. **Descriptive test names**: `test_search_with_valid_bbox()` not `test1()`
3. **Arrange-Act-Assert pattern**:
   ```python
   def test_something():
       # Arrange: Set up test data
       data = [1, 2, 3]
       
       # Act: Execute the function
       result = sum(data)
       
       # Assert: Check the result
       assert result == 6
   ```
4. **One assertion per test** (when possible)
5. **Test edge cases**: empty inputs, None, negative numbers, etc.
6. **Use fixtures** for common setup
7. **Mock external dependencies**: APIs, databases, file systems

---

## Next Steps

1. **Read**: `conftest.py` - Learn about fixtures
2. **Study**: `test_stac_client.py` - Learn about mocking
3. **Practice**: `test_change_detection.py` - Learn about parametrization
4. **Run**: `pytest -v` - See tests in action

---

## Quick Reference

| Task | Command |
|------|---------|
| Run all tests | `pytest` |
| Verbose output | `pytest -v` |
| Show prints | `pytest -s` |
| Run one file | `pytest tests/test_file.py` |
| Run one test | `pytest tests/test_file.py::test_name` |
| Coverage | `pytest --cov=module` |
| Stop on fail | `pytest -x` |
| Skip slow tests | `pytest -m "not slow"` |

---

## Common Patterns

### Testing Exceptions:
```python
def test_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        result = 1 / 0
```

### Parametrized Tests:
```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected
```

### Setup and Teardown:
```python
@pytest.fixture
def resource():
    # Setup
    r = create_resource()
    
    yield r  # Provide to test
    
    # Teardown (runs after test)
    r.cleanup()
```
