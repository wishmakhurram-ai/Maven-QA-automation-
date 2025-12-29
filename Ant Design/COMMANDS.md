# Commands Reference

## Setup Commands

### Install Dependencies
```powershell
pip install -r requirements.txt
```

### Verify Installation
```powershell
python --version
pip list | findstr "selenium behave"
```

## Running Examples

### Run Simple Example
```powershell
python examples/simple_usage.py
```

### Run Quick Example Runner (Auto-Click All Buttons)
```powershell
python run_example.py
```

This will automatically:
- Find all Ant Design buttons on the page
- Identify each button type automatically
- Click all clickable buttons (skips disabled ones)
- Show detailed information about each button

You can also specify a custom URL:
```powershell
python run_example.py "https://your-custom-page.com"
```

### Run Specific Test Function
```powershell
python -c "from tests.example_button_test import test_button_by_data_attr; test_button_by_data_attr()"
```

## Running Behave (BDD) Tests

### Run All Feature Files
```powershell
behave
```

### Run Specific Feature File
```powershell
behave features/button_automation.feature
```

### Run with Verbose Output
```powershell
behave --verbose
```

### Run Specific Scenario
```powershell
behave features/button_automation.feature -n "Click button using custom data-atr-id attribute"
```

### Run with Tags (if you add tags)
```powershell
behave --tags @button
```

## Python Interactive Testing

### Start Python REPL and Test
```powershell
python
```

Then in Python:
```python
from selenium import webdriver
from framework.components.button_handler import ButtonHandler
from framework.utils.driver_setup import DriverSetup

driver = DriverSetup.get_chrome_driver()
driver.get("https://ant.design/components/button")
button_handler = ButtonHandler(driver)

# Test auto-detect
button_handler.click_button_by_auto_detect("submit-button")

# Get button info
info = button_handler.get_button_info("submit-button", identifier_type='data_attr')
print(info)
```

## Development Commands

### Check for Linter Errors
```powershell
python -m py_compile framework/**/*.py
```

### Run with Debug Output
```powershell
$env:PYTHONUNBUFFERED=1; python examples/simple_usage.py
```

## Quick Test Commands

### Test Button Handler Import
```powershell
python -c "from framework.components.button_handler import ButtonHandler; print('Import successful!')"
```

### Test Driver Setup
```powershell
python -c "from framework.utils.driver_setup import DriverSetup; print('Driver setup import successful!')"
```

## Notes

- Make sure ChromeDriver is installed and in PATH
- For headless mode, modify the examples to use `headless=True`
- Update URLs in examples to match your test pages
- Add `data-atr-id` attributes to your Ant Design buttons for best results

