# Ant Design Automation Framework

A generic automation framework for Ant Design components using Python and Selenium. This framework automatically identifies button types and performs actions without requiring explicit selectors.

## Features

- **Automatic Button Type Detection**: Automatically identifies Ant Design button types (primary, default, dashed, text, link, danger)
- **Multiple Identification Methods**: Supports identification by:
  - Custom `data-atr-id` attribute
  - Button text content
  - Button type
  - Auto-detection (tries all methods)
- **Generic and Reusable**: No hardcoded selectors, works with any Ant Design button
- **Gherkin/BDD Support**: Includes step definitions for behavior-driven testing
- **Button State Detection**: Identifies button properties (disabled, loading, size, shape, etc.)

## Framework Structure

```
.
├── framework/
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   └── base_page.py          # Base page object class
│   ├── components/
│   │   ├── __init__.py
│   │   └── button_handler.py     # Generic button handler
│   └── utils/
│       ├── __init__.py
│       └── selector_config.py    # Selector configurations
├── tests/
│   ├── __init__.py
│   ├── test_button_automation.py    # Button automation tests
│   ├── test_input_automation.py     # Input automation tests
│   └── test_dropdown_automation.py  # Dropdown automation tests
├── steps/
│   └── button_steps.py           # Gherkin step definitions
├── requirements.txt
└── README.md
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Download ChromeDriver and ensure it's in your PATH, or specify the path in your code.

## Usage

### Basic Usage - Direct Python

```python
from selenium import webdriver
from framework.components.button_handler import ButtonHandler

# Setup driver
driver = webdriver.Chrome()
driver.get("https://your-ant-design-page.com")

# Initialize button handler
button_handler = ButtonHandler(driver)

# Click button by data-atr-id (recommended)
button_handler.click_button("submit-button", identifier_type='data_attr')

# Click button by text
button_handler.click_button("Submit", identifier_type='text')

# Click button by type (clicks first button of that type)
button_handler.click_button("primary", identifier_type='type')

# Auto-detect and click (tries all methods)
button_handler.click_button_by_auto_detect("submit-button")

driver.quit()
```

### Using with Gherkin/BDD (Behave)

Create a feature file `features/button_automation.feature`:

```gherkin
Feature: Ant Design Button Automation

  Scenario: Click button using data-atr-id
    Given I am on the "https://ant.design/components/button" page
    When I click the button with data-atr-id "submit-button"
    Then the button should be clicked successfully

  Scenario: Click button by text
    Given I am on the "https://ant.design/components/button" page
    When I click the button with text "Submit"
    Then the button should be clicked successfully

  Scenario: Auto-detect and click button
    Given I am on the "https://ant.design/components/button" page
    When I auto-detect and click the button "submit-button"
    Then the button should be clicked successfully
```

Run with behave:
```bash
behave features/button_automation.feature
```

## Button Identification Methods

### 1. By Custom Data Attribute (Recommended)
```python
button_handler.click_button("my-button-id", identifier_type='data_attr')
```
Requires your HTML to have: `<button data-atr-id="my-button-id">Click Me</button>`

### 2. By Text Content
```python
button_handler.click_button("Submit", identifier_type='text')
```
Finds button by its visible text (partial match).

### 3. By Button Type
```python
button_handler.click_button("primary", identifier_type='type')
```
Clicks the first button of the specified type (primary, default, dashed, text, link, danger).

### 4. Auto-Detection (Most Generic)
```python
button_handler.click_button_by_auto_detect("submit-button")
```
Tries all methods in sequence: data-attr-id → text → type.

## Button Information

Get detailed information about a button without clicking:

```python
button_info = button_handler.get_button_info("submit-button", identifier_type='data_attr')

print(f"Type: {button_info['type']}")        # primary, default, dashed, etc.
print(f"Size: {button_info['size']}")        # large, middle, small
print(f"Text: {button_info['text']}")        # Button text content
print(f"Disabled: {button_info['disabled']}") # True/False
print(f"Loading: {button_info['loading']}")   # True/False
print(f"Shape: {button_info['shape']}")      # default, round, circle
```

## Button Types Supported

The framework automatically recognizes these Ant Design button types:
- **Primary**: `ant-btn-primary`
- **Default**: `ant-btn-default`
- **Dashed**: `ant-btn-dashed`
- **Text**: `ant-btn-text`
- **Link**: `ant-btn-link`
- **Danger**: `ant-btn-dangerous`

## Advanced Features

### Find All Buttons
```python
buttons = button_handler.find_all_ant_buttons()
for button in buttons:
    info = button_handler.identify_button_type(button)
    print(f"Button: {info['text']}, Type: {info['type']}")
```

### Check Button State
```python
button_info = button_handler.get_button_info("submit-button")
if not button_info['disabled'] and not button_info['loading']:
    button_handler.click_button("submit-button", identifier_type='data_attr')
```

## Custom Data Attribute

To use the `data-atr-id` attribute in your Ant Design components:

```jsx
// React example
<Button data-atr-id="submit-button" type="primary">
  Submit
</Button>
```

```html
<!-- HTML example -->
<button class="ant-btn ant-btn-primary" data-atr-id="submit-button">
  Submit
</button>
```

## Example Test Files

See the test files in the `tests/` directory for complete examples:
- `tests/test_button_automation.py` - Button automation examples
- `tests/test_input_automation.py` - Input automation examples
- `tests/test_dropdown_automation.py` - Dropdown automation examples

You can also run the standalone example scripts:
- `run_dropdown_example.py` - Dropdown automation demo
- `run_input_example.py` - Input automation demo

## Gherkin Step Definitions

Available steps in `steps/button_steps.py`:

- `Given I am on the "{page_url}" page`
- `When I click the button with data-atr-id "{data_attr_id}"`
- `When I click the button with text "{button_text}"`
- `When I click the "{button_type}" type button`
- `When I auto-detect and click the button "{identifier}"`
- `Then the button should be clicked successfully`
- `Then the button with data-atr-id "{data_attr_id}" should be "{state}"`
- `Then I should see "{count}" buttons of type "{button_type}"`

## Requirements

- Python 3.7+
- Selenium 4.15.0+
- ChromeDriver (or other WebDriver)
- Behave (optional, for BDD testing)

## Notes

- The framework automatically handles button states (disabled, loading)
- JavaScript click is used as fallback if normal click fails
- All methods include proper wait mechanisms for element visibility and clickability
- The framework is designed to be extensible for other Ant Design components

## Future Enhancements

- Support for other Ant Design components (Input, Select, Form, etc.)
- Enhanced auto-detection for form fields (password, username, etc.)
- Screenshot capture on failures
- Test reporting integration

## License

This framework is provided as-is for automation purposes.




