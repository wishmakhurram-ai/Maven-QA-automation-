# Quick Start Guide

## Setup (5 minutes)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Download ChromeDriver:**
   - Download from: https://chromedriver.chromium.org/
   - Add to PATH or place in project directory

## Basic Usage

### Example 1: Click Button by Data Attribute (Recommended)

```python
from selenium import webdriver
from framework.components.button_handler import ButtonHandler

driver = webdriver.Chrome()
driver.get("https://your-page.com")

button_handler = ButtonHandler(driver)
button_handler.click_button("submit-button", identifier_type='data_attr')

driver.quit()
```

**HTML Required:**
```html
<button class="ant-btn ant-btn-primary" data-atr-id="submit-button">
  Submit
</button>
```

### Example 2: Auto-Detect Button (Most Generic)

```python
from selenium import webdriver
from framework.components.button_handler import ButtonHandler

driver = webdriver.Chrome()
driver.get("https://your-page.com")

button_handler = ButtonHandler(driver)
# Tries: data-atr-id → text → type
button_handler.click_button_by_auto_detect("submit-button")

driver.quit()
```

### Example 3: Click Button by Text

```python
button_handler.click_button("Submit", identifier_type='text')
```

### Example 4: Click Button by Type

```python
# Clicks first primary button on page
button_handler.click_button("primary", identifier_type='type')
```

## Using with Gherkin/BDD

1. **Create feature file** (`features/my_test.feature`):
```gherkin
Feature: Button Tests

  Scenario: Click submit button
    Given I am on the "https://my-app.com" page
    When I click the button with data-atr-id "submit-button"
    Then the button should be clicked successfully
```

2. **Run with behave:**
```bash
behave features/my_test.feature
```

## How Auto-Detection Works

When you use `click_button_by_auto_detect("identifier")`, the framework:

1. **First tries:** Find button with `data-atr-id="identifier"`
2. **Then tries:** Find button containing text "identifier"
3. **Finally tries:** Find button of type "identifier" (primary, default, etc.)

This makes your tests resilient to changes in button structure.

## Button Types Automatically Detected

- `primary` - Primary buttons (blue)
- `default` - Default buttons (white)
- `dashed` - Dashed border buttons
- `text` - Text-only buttons
- `link` - Link-style buttons
- `danger` - Danger/delete buttons (red)

## Common Patterns

### Get Button Information
```python
info = button_handler.get_button_info("submit-button", identifier_type='data_attr')
print(f"Type: {info['type']}, Disabled: {info['disabled']}")
```

### Find All Buttons
```python
buttons = button_handler.find_all_ant_buttons()
for button in buttons:
    info = button_handler.identify_button_type(button)
    print(f"Found: {info['text']} ({info['type']})")
```

### Check Before Clicking
```python
info = button_handler.get_button_info("submit-button")
if not info['disabled'] and not info['loading']:
    button_handler.click_button("submit-button", identifier_type='data_attr')
```

## Tips

1. **Use `data-atr-id` attributes** - Most reliable method
2. **Use auto-detect** - Most flexible, works with any identifier
3. **Check button state** - Always verify button is enabled before clicking
4. **Handle loading states** - Framework automatically waits for loading to complete

## Troubleshooting

**Button not found?**
- Check if button has `ant-btn` class
- Verify `data-atr-id` attribute is set
- Try using auto-detect method

**Button not clickable?**
- Button might be disabled - check with `get_button_info()`
- Button might be loading - framework waits automatically
- Try JavaScript click (framework does this automatically)

**Multiple buttons match?**
- Use `data-atr-id` for unique identification
- Or use `find_button_by_type()` and select specific index

