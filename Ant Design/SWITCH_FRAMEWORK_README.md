# Ant Design Switch Automation Framework

## Overview

A complete, locator-less Python + Selenium framework for automatically detecting, reading state, and toggling Ant Design Switch components without hardcoded selectors.

## Features

✅ **Automatic Switch Recognition** - Detects all Ant Design Switch components on any page  
✅ **State Detection** - Identifies checked (ON), unchecked (OFF), disabled, and loading states  
✅ **Locator-less** - Uses Ant Design class patterns, data-attr-id, aria attributes, and semantic labels  
✅ **Gherkin-friendly** - Intent-driven step definitions for BDD testing  
✅ **Idempotent Actions** - Toggle only when state differs  
✅ **Position-based Operations** - Toggle by index or first switch  
✅ **Comprehensive Reporting** - Summary of all detected switches with detailed information  

## Architecture

The framework follows a three-layer architecture:

```
┌─────────────────────────────────────────────────────────────┐
│ SWITCH HANDLER (Business Logic Layer)                        │
│ - Orchestrates interactions (toggle, turn_on, turn_off)      │
│ - Coordinates Locator + Identifier                           │
│ - Performs state verification                                │
└─────────────────────────────────────────────────────────────┘
                    ↓ uses
┌─────────────────────────────────────────────────────────────┐
│ SWITCH LOCATOR (Finding Layer)                               │
│ - Finds switches by data-attr-id, label, position            │
│ - Uses PatternDiscovery for auto-detection                   │
│ - No hardcoded XPath or CSS selectors                        │
└─────────────────────────────────────────────────────────────┘
                    ↓ uses
┌─────────────────────────────────────────────────────────────┐
│ SWITCH IDENTIFIER (Analysis Layer)                           │
│ - Analyzes switch properties (state, size, labels)           │
│ - Extracts metadata (disabled, loading, controlled)          │
└─────────────────────────────────────────────────────────────┘
```

## Files Created

### Core Components
- `framework/components/switch_handler.py` - Main handler for switch interactions
- `framework/components/switch_locator.py` - Locator for finding switches
- `framework/components/switch_identifier.py` - Identifier for analyzing switches

### Step Definitions
- `steps/switch_steps.py` - Gherkin step definitions for BDD testing

### Test Files
- `features/switch_automation.feature` - Gherkin feature file with example scenarios
- `tests/test_switch_automation.py` - pytest-bdd test file

### Integration
- Updated `conftest.py` - Added SwitchHandler to context fixture
- Updated `framework/utils/pattern_discovery.py` - Added 'switch' element type support

## Usage Examples

### 1. Gherkin Feature File (BDD)

```gherkin
Feature: Switch Automation
  Scenario: Toggle switch by label
    Given I am on a page with Ant Design Switch components
    When I turn on the switch "Notifications"
    Then the switch "Notifications" should be ON
    When I turn off the switch "Notifications"
    Then the switch "Notifications" should be OFF
```

### 2. Python Code (Direct Usage)

```python
from framework.components.switch_handler import SwitchHandler
from framework.context.element_context import ElementContext

# Initialize
element_context = ElementContext()
switch_handler = SwitchHandler(driver, context=element_context)

# Toggle a switch by semantic label
switch_handler.turn_on("Notifications", identifier_type='auto')

# Check state
is_on = switch_handler.is_switch_on("Notifications")
print(f"Switch is ON: {is_on}")

# Get detailed state
state = switch_handler.get_switch_state("Notifications")
print(f"State: {state}")

# Print summary of all switches
switch_handler.print_switches_summary()
```

### 3. Available Methods

#### Toggle Operations
- `toggle_switch(identifier, identifier_type='auto')` - Toggle switch (ON↔OFF)
- `turn_on(identifier, identifier_type='auto')` - Turn ON (idempotent)
- `turn_off(identifier, identifier_type='auto')` - Turn OFF (idempotent)
- `toggle_first_switch()` - Toggle first switch on page
- `toggle_switch_by_index(index)` - Toggle by position (1-based)
- `toggle_all_switches_matching(condition)` - Toggle all matching switches

#### State Verification
- `get_switch_state(identifier)` - Get full state dictionary
- `is_switch_on(identifier)` - Check if ON (returns bool)
- `is_switch_off(identifier)` - Check if OFF (returns bool)

#### Discovery & Reporting
- `get_all_switches_summary()` - Get summary dictionary
- `print_switches_summary()` - Print readable summary

#### Identification
- `identify_and_store(identifier, identifier_type='auto')` - Store switch in context

## Identifier Types

The framework supports multiple identifier types:

1. **`'auto'`** (default) - Automatic discovery:
   - Tries pattern discovery first (data-attr-id patterns)
   - Falls back to direct data-attr-id search
   - Falls back to semantic label matching

2. **`'data_attr_id'`** - Direct data-attr-id attribute:
   ```python
   switch_handler.toggle_switch("notifications-switch", identifier_type='data_attr_id')
   ```

3. **`'label'` or `'semantic'`** - Semantic label matching:
   ```python
   switch_handler.toggle_switch("Notifications", identifier_type='label')
   ```

4. **`'position'`** - Position/index (1-based):
   ```python
   switch_handler.toggle_switch("1", identifier_type='position')
   ```

## Detection Rules

The framework detects switches using:

1. **Ant Design Classes**:
   - `.ant-switch` - Base switch class
   - `.ant-switch-checked` - Checked (ON) state
   - `.ant-switch-disabled` - Disabled state
   - `.ant-switch-loading` - Loading state
   - `.ant-switch-small` - Small size

2. **ARIA Attributes**:
   - `role="switch"` - Switch role
   - `aria-checked` - Checked state
   - `aria-disabled` - Disabled state
   - `aria-label` - Accessible label

3. **Data Attributes**:
   - `data-attr-id` or `data-atr-id` - Custom identifier (highest priority)

4. **Semantic Labels**:
   - Associated label elements
   - Form.Item context
   - Nearby text content

## Switch State Dictionary

When you call `get_switch_state()`, you receive:

```python
{
    'checked': bool,              # ON/OFF state
    'disabled': bool,              # Disabled state
    'loading': bool,               # Loading state
    'size': 'default'|'small',     # Size
    'checked_label': str|None,     # Text when checked
    'unchecked_label': str|None,   # Text when unchecked
    'has_icon': bool,              # Has icon
    'data_attr_id': str|None,      # Data attribute ID
    'application_type': str|None, # Application type
    'aria_checked': str|None,      # ARIA checked value
    'aria_disabled': str|None,     # ARIA disabled value
    'role': str|None,              # Role attribute
    'controlled': bool|None,       # Controlled vs uncontrolled
    'metadata': dict                # Additional metadata
}
```

## Gherkin Step Definitions

### Given Steps
- `Given I am on a page with Ant Design Switch components`
- `Given I identify the switch with data-atr-id "{data_attr_id}"`
- `Given I identify the switch with label "{label_text}"`

### When Steps
- `When I toggle the switch "{identifier}"`
- `When I turn on the switch "{identifier}"`
- `When I turn off the switch "{identifier}"`
- `When I toggle the first switch`
- `When I toggle the switch at position {position}`
- `When I navigate to a page with switches`

### Then Steps
- `Then the switch "{identifier}" should be ON`
- `Then the switch "{identifier}" should be OFF`
- `Then the switch "{identifier}" should be disabled`
- `Then the switch "{identifier}" should be enabled`
- `Then the switch "{identifier}" should be in loading state`
- `Then the switch "{identifier}" should have size "{size}"`
- `Then I should see {count} switch(es) on the page`
- `Then I should see a summary of all switches`

## Running Tests

```bash
# Run all switch automation tests
pytest tests/test_switch_automation.py -v

# Run specific scenario
pytest tests/test_switch_automation.py::test_detect_and_summarize_all_switches_on_the_page -v

# Run with detailed output
pytest tests/test_switch_automation.py -v -s
```

## Example Output

When you call `print_switches_summary()`, you'll see:

```
============================================================
SWITCH SUMMARY
============================================================
Total Switches: 3
  ON (Checked):  2
  OFF (Unchecked): 1
  Disabled:      0
  Loading:       0
------------------------------------------------------------

Detailed Switch Information:
  1. notifications-switch: ON
      Checked Label: Enabled
  2. dark-mode-switch: ON
      Checked Label: Dark
  3. email-alerts-switch: OFF
      Unchecked Label: Disabled
============================================================
```

## Error Handling

The framework handles errors gracefully:

- **Disabled switches**: Cannot be toggled (returns False with message)
- **Loading switches**: Cannot be toggled (returns False with message)
- **Not found**: Returns None/False with descriptive message
- **Animation delays**: Automatic retry with configurable backoff

## Integration with Existing Framework

The Switch framework integrates seamlessly with the existing automation framework:

- Uses shared `ElementContext` for element storage
- Uses `PatternDiscovery` for automatic data-attr-id pattern detection
- Follows same architecture patterns as Input, Button, Dropdown handlers
- Works with existing conftest.py context fixture

## Requirements

- Python 3.7+
- Selenium WebDriver
- pytest-bdd
- Ant Design components in the application under test

## Notes

- The framework is **locator-less** - no hardcoded XPath or CSS selectors
- **Idempotent operations** - `turn_on()` and `turn_off()` do nothing if already in desired state
- **Automatic retry** - Handles animation delays with configurable retry count and delay
- **Pattern discovery** - Automatically discovers data-attr-id patterns from the page
- **Semantic matching** - Uses fuzzy text matching for labels

## Support

For issues or questions, refer to the existing framework documentation or check the implementation in:
- `framework/components/switch_handler.py`
- `framework/components/switch_locator.py`
- `framework/components/switch_identifier.py`
- `steps/switch_steps.py`




