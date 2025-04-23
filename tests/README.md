# Testing the Drinkaware Integration

This document describes how to set up and run tests for the Drinkaware Home Assistant integration.

## Test Structure

The tests are organized as follows:

```
tests/
├── conftest.py           # Common test fixtures
├── fixtures/             # Mock API data
│   ├── activity.json
│   ├── assessment.json
│   ├── drinks.json
│   ├── goals.json
│   ├── stats.json
│   └── summary.json
├── test_config_flow.py   # Tests for the config flow
├── test_coordinator.py   # Tests for the data update coordinator
├── test_init.py          # Tests for component setup
├── test_sensor.py        # Tests for sensors
└── test_services.py      # Tests for service functionality
```

## Setting Up the Test Environment

### Prerequisites

- Python 3.9 or higher
- Home Assistant development environment
- pytest and pytest-homeassistant-custom-component

### Installation

1. Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/your-username/drinkaware.git
cd drinkaware
```

2. Set up a virtual environment and install the required packages:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install Home Assistant for development
pip install homeassistant pytest pytest-asyncio pytest-homeassistant-custom-component

# Optional: Install additional tools
pip install pylint flake8 black
```

3. Create a symbolic link to the custom component for testing:

```bash
mkdir -p custom_components
ln -s ../custom_components/drinkaware custom_components/drinkaware
```

## Running Tests

### Run All Tests

```bash
pytest -xvs tests/
```

### Run Specific Tests

```bash
# Run a specific test file
pytest -xvs tests/test_sensor.py

# Run a specific test function
pytest -xvs tests/test_services.py::test_log_drink_service

# Run tests with a specific mark
pytest -xvs tests -m "parametrize"
```

### Test Options

- `-x`: Stop after the first failure
- `-v`: Verbose output
- `-s`: Show print statements in output
- `--cov=custom_components.drinkaware`: Generate coverage report (requires pytest-cov)

## Test Results Interpretation

After running the tests, you'll see output similar to:

```
================== test session starts ==================
...
collected 42 items

tests/test_config_flow.py::test_form_user PASSED
tests/test_config_flow.py::test_account_name_step[Test Account] PASSED
...

================== 42 passed in 5.67s ==================
```

### Coverage Report (Optional)

To generate a coverage report, install pytest-cov:

```bash
pip install pytest-cov
```

Then run:

```bash
pytest -xvs --cov=custom_components.drinkaware tests/
```

For an HTML report:

```bash
pytest -xvs --cov=custom_components.drinkaware --cov-report=html tests/
```

This creates a `htmlcov` directory with an HTML report.

## CI Integration

### GitHub Actions

Add a `.github/workflows/tests.yaml` file:

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install homeassistant pytest pytest-asyncio pytest-homeassistant-custom-component pytest-cov
      - name: Set up test environment
        run: |
          mkdir -p custom_components
          ln -s $GITHUB_WORKSPACE/custom_components/drinkaware custom_components/drinkaware
      - name: Run tests
        run: |
          pytest -xvs --cov=custom_components.drinkaware --cov-report=xml tests/
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Best Practices

1. **Mock external dependencies**: Always mock API calls, file system access, and other external dependencies.
2. **Test edge cases**: Include tests for error conditions, invalid inputs, and boundary values.
3. **Separate unit and integration tests**: Use smaller unit tests for individual functions and larger integration tests for component interactions.
4. **Keep tests independent**: Each test should run independently without depending on state from other tests.
5. **Maintain test fixtures**: Update test fixtures when API responses change.

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure the custom_components symlink is correctly set up.
2. **Fixture errors**: Check that fixture files exist in the correct locations.
3. **Async issues**: Make sure all async functions are properly awaited.

### Debug Tips

1. Add print statements with `print()` and run tests with `-s` flag.
2. Use `breakpoint()` to start the debugger during test execution.
3. Check Home Assistant logs for additional information.