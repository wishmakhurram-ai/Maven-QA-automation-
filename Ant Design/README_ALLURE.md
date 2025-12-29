# Allure Reporting Setup

This project uses Allure Framework for generating beautiful test reports.

## Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- `allure-pytest` - Pytest integration for Allure
- `allure-python-commons` - Common Allure utilities

### 2. Install Allure Command Line Tool

**Windows (using Scoop):**
```bash
scoop install allure
```

**Windows (using Chocolatey):**
```bash
choco install allure
```

**Windows (Manual):**
1. Download from: https://github.com/allure-framework/allure2/releases
2. Extract to a folder (e.g., `C:\allure`)
3. Add to PATH: Add `C:\allure\bin` to your system PATH

**Verify Installation:**
```bash
allure --version
```

## Usage

### Option 1: Run Tests and Generate Report Automatically

```bash
python run_tests_with_allure.py
```

This will:
1. Run all tests with Allure integration
2. Generate Allure report automatically
3. Open the report in your browser

### Option 2: Run Tests Separately

**Step 1: Run Tests**
```bash
pytest tests/test_maven_automation.py -v
```

**Step 2: Generate and View Report**
```bash
python generate_allure_report.py
```

Or manually:
```bash
allure generate reports/allure-results --clean -o reports/allure-report
allure open reports/allure-report
```

### Option 3: Serve Report (Live Updates)

```bash
python generate_allure_report.py serve
```

Or manually:
```bash
allure serve reports/allure-results
```

This will:
- Start a local server
- Open the report in your browser
- Automatically update when you run new tests

## Report Features

The Allure report includes:

1. **Test Overview**
   - Total tests executed
   - Passed/Failed/Skipped counts
   - Duration statistics

2. **Test Details**
   - Feature file location
   - Line numbers
   - Test descriptions
   - Error messages for failed tests

3. **Test Results**
   - Which tests passed
   - Which tests failed
   - Error details for failures
   - Duration for each test

4. **History**
   - Previous test run results
   - Trends over time

## Report Location

- **Allure Results:** `reports/allure-results/`
- **Generated Report:** `reports/allure-report/`
- **Text Report:** `reports/test_report_YYYYMMDD_HHMMSS.txt`

## Troubleshooting

### "allure: command not found"
- Make sure Allure is installed and in your PATH
- Verify with: `allure --version`

### "No Allure results found"
- Run tests first: `pytest tests/test_maven_automation.py -v`
- Check that `reports/allure-results/` contains JSON files

### Report not opening
- Try opening manually: Navigate to `reports/allure-report/index.html` in your browser
- Or use: `allure open reports/allure-report`


