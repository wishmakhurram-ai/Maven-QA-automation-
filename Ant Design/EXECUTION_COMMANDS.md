# Upload Framework Execution Commands

## 🚀 Quick Start Commands

### 1. Run All Upload Tests

```bash
# Run all upload automation tests
pytest tests/test_upload_automation.py -v -s

# Run with detailed output
pytest tests/test_upload_automation.py -v -s --tb=short

# Run with HTML report
pytest tests/test_upload_automation.py -v -s --html=reports/upload_report.html --self-contained-html
```

### 2. Run Specific Scenarios

```bash
# Run specific scenario by tag
pytest tests/test_upload_automation.py -v -s -m "UPLOAD-001"

# Run smoke tests only
pytest tests/test_upload_automation.py -v -s -m "smoke"

# Run multiple tags
pytest tests/test_upload_automation.py -v -s -m "UPLOAD-001 or UPLOAD-002"
```

### 3. Run Specific Scenario by Name

```bash
# Run single file upload test
pytest tests/test_upload_automation.py::test_upload_a_single_file_to_an_upload_component -v -s

# Run multiple files test
pytest tests/test_upload_automation.py::test_upload_multiple_files_to_an_upload_component -v -s

# Run drag and drop test
pytest tests/test_upload_automation.py::test_drag_and_drop_file_upload -v -s
```

### 4. Run with Custom URL

```bash
# Set base URL via environment variable
$env:MAVEN_BASE_URL="https://your-app.com"
pytest tests/test_upload_automation.py -v -s

# Or set in feature file Background
# Given the Maven app URL is "https://your-app.com/login"
```

### 5. Debug Mode

```bash
# Run with maximum verbosity and print statements
pytest tests/test_upload_automation.py -v -s -vv

# Run with pdb debugger on failure
pytest tests/test_upload_automation.py -v -s --pdb

# Run with traceback
pytest tests/test_upload_automation.py -v -s --tb=long
```

### 6. Run with Coverage

```bash
# Install coverage first: pip install pytest-cov
pytest tests/test_upload_automation.py -v -s --cov=framework.components.upload_handler --cov=framework.components.upload_locator --cov=framework.components.upload_identifier
```

### 7. Run All Tests (Including Upload)

```bash
# Run all tests including upload
pytest tests/ -v -s

# Run all tests with upload tag
pytest tests/ -v -s -m "upload or UPLOAD"
```

## 📋 Common Command Patterns

### Pattern 1: Run and Generate Report

```bash
pytest tests/test_upload_automation.py -v -s --html=reports/upload_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').html --self-contained-html
```

### Pattern 2: Run with Screenshots on Failure

```bash
# Install pytest-html first
pytest tests/test_upload_automation.py -v -s --html=reports/report.html --self-contained-html --capture=no
```

### Pattern 3: Run Specific Feature File

```bash
# Run upload feature file directly
pytest features/upload_automation.feature -v -s
```

### Pattern 4: Run with Parallel Execution

```bash
# Install pytest-xdist first: pip install pytest-xdist
pytest tests/test_upload_automation.py -v -s -n auto
```

## 🔧 Test Execution Examples

### Example 1: Run Single Upload Test

```bash
# Windows PowerShell
pytest tests/test_upload_automation.py::test_upload_a_single_file_to_an_upload_component -v -s

# Output will show:
# - Upload component detection
# - File upload process
# - Verification steps
# - Upload summary
```

### Example 2: Run All Upload Tests with Report

```bash
# Windows PowerShell
pytest tests/test_upload_automation.py -v -s --html=reports/upload_test_report.html --self-contained-html

# Check reports/upload_test_report.html for detailed results
```

### Example 3: Run with Custom Files

```bash
# Create test files first
New-Item -ItemType File -Path "test_document.pdf" -Force
New-Item -ItemType File -Path "test_image.png" -Force

# Run test
pytest tests/test_upload_automation.py -v -s
```

## 📊 View Test Results

### Console Output

The framework prints detailed information:
- Upload component detection
- File upload progress
- Upload verification
- Upload component summary

### Report Files

Reports are saved in `reports/` directory:
- `test_report_YYYYMMDD_HHMMSS.txt` - Text report
- `upload_test_report.html` - HTML report (if generated)

## 🐛 Troubleshooting Commands

### Check Framework Loading

```bash
# Verify framework loads correctly
python -c "import framework.components.upload_handler; import steps.upload_steps; print('✓ Framework loaded')"
```

### Check Pattern Discovery

```bash
# Test PatternDiscovery integration
python -c "from framework.utils.pattern_discovery import PatternDiscovery; from selenium import webdriver; driver = webdriver.Chrome(); pd = PatternDiscovery(driver); print('✓ PatternDiscovery loaded')"
```

### Run with Verbose Logging

```bash
# Enable debug logging
pytest tests/test_upload_automation.py -v -s --log-cli-level=DEBUG
```

## 📝 Example Test Execution Flow

```bash
# 1. Navigate to application
# 2. Framework automatically discovers upload components using PatternDiscovery
# 3. Upload files using semantic labels
# 4. Verify uploads
# 5. Generate summary report

# Full command:
pytest tests/test_upload_automation.py -v -s --html=reports/upload_report.html
```

## 🎯 Quick Reference

| Command | Description |
|---------|-------------|
| `pytest tests/test_upload_automation.py -v -s` | Run all upload tests |
| `pytest tests/test_upload_automation.py -v -s -m "UPLOAD-001"` | Run specific test by tag |
| `pytest tests/test_upload_automation.py -v -s --html=reports/report.html` | Generate HTML report |
| `pytest tests/test_upload_automation.py -v -s -k "single"` | Run tests matching keyword |
| `pytest tests/test_upload_automation.py -v -s --tb=short` | Short traceback on failure |

## 🔍 PatternDiscovery Integration

The framework now uses PatternDiscovery to:
1. **Discover data-attr-id patterns** for upload components
2. **Match upload labels** to discovered patterns
3. **Generate candidates** for upload component identification
4. **Auto-detect** upload components by pattern structure

This means upload components are identified using the same pattern discovery mechanism as other components!



