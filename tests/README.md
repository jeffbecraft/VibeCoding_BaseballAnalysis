# MLB Baseball Analysis - Regression Test Suite

This directory contains comprehensive regression tests for the MLB Baseball Analysis system.

## Test Coverage

### 1. **test_data_fetcher.py**
Tests for the MLB API data fetcher:
- ✓ Initialization with/without caching
- ✓ API request success and error handling
- ✓ Caching functionality
- ✓ Player search
- ✓ Team retrieval
- ✓ Cache statistics and management

### 2. **test_data_processor.py**
Tests for data processing and transformation:
- ✓ Stats leaders extraction
- ✓ Team stats extraction and ranking
- ✓ Data filtering by season
- ✓ Numeric conversion
- ✓ Handling missing data
- ✓ Sorting logic (ascending for ERA/WHIP, descending for others)

### 3. **test_cache.py**
Tests for caching system:
- ✓ Cache initialization
- ✓ Cache key generation
- ✓ Storing and retrieving data
- ✓ Cache expiration (TTL)
- ✓ Clearing cache (all or expired only)
- ✓ Cache statistics
- ✓ Complex data structures

### 4. **test_query_parser.py**
Tests for natural language query parsing:
- ✓ Simple stat queries
- ✓ Player-specific queries
- ✓ Ranking queries
- ✓ Team and league filters
- ✓ Team ranking queries
- ✓ Year extraction
- ✓ Pitching vs hitting stats
- ✓ Player name detection
- ✓ Query type detection

## Running Tests

### Run All Tests
```bash
python run_tests.py
```

### Run Specific Test File
```bash
python run_tests.py --test test_cache
```

### Quiet Mode (Less Output)
```bash
python run_tests.py --quiet
```

### Using unittest directly
```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_data_fetcher

# Run specific test class
python -m unittest tests.test_cache.TestMLBCache

# Run specific test method
python -m unittest tests.test_cache.TestMLBCache.test_set_and_get_cache
```

## Test Output

The test runner provides:
- **Detailed results** for each test
- **Summary report** with pass/fail counts
- **Failure details** with tracebacks
- **Exit code** (0 for success, 1 for failure)

Example output:
```
Running all regression tests...

test_initialization (tests.test_cache.TestMLBCache) ... ok
test_set_and_get_cache (tests.test_cache.TestMLBCache) ... ok
...

======================================================================
TEST SUMMARY
======================================================================

Total Tests Run: 45
✓ Passed: 43
✗ Failed: 0
⚠ Errors: 0
⊘ Skipped: 2

🎉 ALL TESTS PASSED!
======================================================================
```

## Integration Tests

Some tests are marked with `@unittest.skip` to avoid making real API calls during normal test runs. These are integration tests that can be enabled by removing the skip decorator:

```python
@unittest.skip("Integration test - uncomment to run with real API")
def test_real_api_search_players(self):
    ...
```

To run integration tests:
1. Remove the `@unittest.skip` decorator
2. Ensure you have internet connectivity
3. Run the specific test

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: python run_tests.py
```

## Adding New Tests

When adding new features:

1. Create test methods in the appropriate test file
2. Use descriptive test names: `test_<feature>_<scenario>`
3. Include assertions for both success and error cases
4. Add docstrings explaining what's being tested
5. Mock external dependencies (API calls, file I/O)

Example:
```python
def test_new_feature_success(self):
    """Test that new feature works correctly."""
    result = my_function(valid_input)
    self.assertEqual(result, expected_output)

def test_new_feature_error_handling(self):
    """Test that new feature handles errors gracefully."""
    result = my_function(invalid_input)
    self.assertIsNone(result)
```

## Test Best Practices

- ✓ Each test is independent and can run in isolation
- ✓ Tests clean up after themselves (temp files, mocks)
- ✓ Mock external dependencies to avoid flaky tests
- ✓ Test both success and failure paths
- ✓ Use descriptive assertion messages
- ✓ Keep tests fast (under 1 second each)
