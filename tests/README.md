# SpotifiWrapped Test Suite

## Running Tests

```bash
# Run all tests
python3 tests/test_runner.py

# Run specific test file
python3 -m unittest tests.test_database
python3 -m unittest tests.test_genre_extractor
```

## Test Files

- `test_database.py` - Database operations (18 tests)
- `test_genre_extractor.py` - Genre extraction (18 tests)

**Total: 36 tests, 100% success rate**