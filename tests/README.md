# SpotifiWrapped Test Suite

Simple test suite for SpotifiWrapped core functionality.

## Running Tests

```bash
# Run all tests
python tests/test_runner.py

# Run specific test file
python -m unittest tests.test_database
python -m unittest tests.test_genre_extractor
```

## Test Files

- `test_database.py` - Database operations (18 tests)
- `test_genre_extractor.py` - Genre extraction (18 tests)

## Requirements

- Python 3.8+
- No external dependencies required