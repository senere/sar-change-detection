"""
Pytest Tutorial: Parametrized Tests
Learn how to run the same test with different inputs
"""

import pytest
import numpy as np


# ============================================================
# Example 1: Basic Parametrization
# ============================================================

@pytest.mark.parametrize("input,expected", [
    (1, 2),      # First test: double(1) should be 2
    (2, 4),      # Second test: double(2) should be 4
    (5, 10),     # Third test: double(5) should be 10
    (0, 0),      # Edge case: double(0) should be 0
    (-3, -6),    # Negative: double(-3) should be -6
])
def test_double(input, expected):
    """This test runs 5 times with different inputs!"""
    result = input * 2
    assert result == expected


# ============================================================
# Example 2: Multiple Parameters
# ============================================================

@pytest.mark.parametrize("a,b,expected_sum,expected_product", [
    (2, 3, 5, 6),
    (0, 5, 5, 0),
    (-1, 1, 0, -1),
    (10, 10, 20, 100),
])
def test_math_operations(a, b, expected_sum, expected_product):
    """Test multiple operations with same inputs."""
    assert a + b == expected_sum
    assert a * b == expected_product


# ============================================================
# Example 3: Using pytest.param for Named Tests
# ============================================================

@pytest.mark.parametrize("value,expected", [
    pytest.param(100, 20, id="100_to_20dB"),
    pytest.param(1, 0, id="1_to_0dB"),
    pytest.param(1000, 30, id="1000_to_30dB"),
])
def test_to_db_conversion(value, expected):
    """Convert to dB with named test cases."""
    result = 10 * np.log10(value)
    assert np.isclose(result, expected)


# ============================================================
# Example 4: Testing Exception Cases
# ============================================================

@pytest.mark.parametrize("input", [
    0,          # Division by zero
    -1,         # Negative number
    -100,       # Large negative
])
def test_log10_invalid_inputs(input):
    """Test that log10 raises error for invalid inputs."""
    with pytest.raises((ValueError, RuntimeWarning)):
        result = 10 * np.log10(input)


# ============================================================
# Example 5: Combining Parametrize with Fixtures
# ============================================================

@pytest.fixture
def base_array():
    """Fixture provides base test data."""
    return np.array([1, 2, 3, 4, 5])


@pytest.mark.parametrize("multiplier", [2, 5, 10])
def test_array_multiplication(base_array, multiplier):
    """Test works with fixture AND parametrization!"""
    result = base_array * multiplier
    expected = np.array([1*multiplier, 2*multiplier, 3*multiplier, 
                         4*multiplier, 5*multiplier])
    assert np.array_equal(result, expected)


# ============================================================
# Example 6: Parametrize Multiple Arguments Separately
# ============================================================

@pytest.mark.parametrize("operation", ["add", "subtract", "multiply"])
@pytest.mark.parametrize("value", [1, 5, 10])
def test_operations_matrix(operation, value):
    """
    This creates a test matrix:
    - test_operations_matrix[add-1]
    - test_operations_matrix[add-5]
    - test_operations_matrix[add-10]
    - test_operations_matrix[subtract-1]
    - ... (9 tests total!)
    """
    base = 10
    
    if operation == "add":
        result = base + value
        assert result > base
    elif operation == "subtract":
        result = base - value
        assert result < base
    elif operation == "multiply":
        result = base * value
        assert result >= base


# ============================================================
# Example 7: Skipping Specific Parameter Combinations
# ============================================================

@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (2, 3, 5),
    pytest.param(0, 0, 0, marks=pytest.mark.skip(reason="Known issue with zeros")),
    (5, -5, 0),
])
def test_addition_with_skip(a, b, expected):
    """Some parameter combinations can be skipped."""
    assert a + b == expected


# ============================================================
# Example 8: Real-World SAR Example
# ============================================================

@pytest.mark.parametrize("before,after,expected_change_type", [
    (1.0, 2.0, "increase"),      # Doubling = increase
    (2.0, 1.0, "decrease"),      # Halving = decrease
    (1.0, 1.0, "no_change"),     # Same = no change
    (0.5, 2.0, "large_increase"), # 4x increase
])
def test_change_detection_scenarios(before, after, expected_change_type):
    """Test different change detection scenarios."""
    # Compute dB change
    change_db = 10 * np.log10(after / before)
    
    if expected_change_type == "increase":
        assert change_db > 0
    elif expected_change_type == "decrease":
        assert change_db < 0
    elif expected_change_type == "no_change":
        assert np.isclose(change_db, 0)
    elif expected_change_type == "large_increase":
        assert change_db > 6  # More than 6 dB


# ============================================================
# How to Run These Tests
# ============================================================

"""
Run all tests:
    pytest test_parametrize_tutorial.py -v

Run specific test:
    pytest test_parametrize_tutorial.py::test_double -v

Run with specific parameter:
    pytest test_parametrize_tutorial.py -v -k "1_to_0dB"

See test names:
    pytest test_parametrize_tutorial.py --collect-only
"""
