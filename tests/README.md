# KahnemanBench Tests

This directory contains tests for the KahnemanBench project.

## Test Files

- `test_structure_only.py` - Basic structure and syntax tests (no dependencies)
- `test_basic_functionality.py` - Functionality tests (requires dependencies)
- `test_integration.py` - Integration tests with mock data

## Running Tests

### Quick Structure Test (No Dependencies)
```bash
python3 tests/test_structure_only.py
```

### Full Tests (Requires Virtual Environment)
```bash
# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r pyproject.toml

# Run all tests
python3 tests/test_basic_functionality.py
python3 tests/test_integration.py
```

## What the Tests Verify

1. **File Structure**: New numbered folder organization exists
2. **Script Syntax**: All Python scripts have valid syntax
3. **Path Updates**: Scripts reference new folder paths correctly
4. **Data Loading**: Core dataset can be loaded and parsed
5. **Model Initialization**: Core classes can be instantiated
6. **Pipeline Flow**: End-to-end pipeline structure is correct