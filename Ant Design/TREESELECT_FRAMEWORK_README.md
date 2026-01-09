# TreeSelect Automation Framework

## Overview

This framework provides locator-less automation for Ant Design TreeSelect components. It automatically detects and interacts with TreeSelect components without requiring hardcoded XPath or CSS selectors.

## Features

### Automatic TreeSelect Recognition

The framework automatically detects and classifies all Ant Design TreeSelect types:

1. **Basic TreeSelect** - Single selection mode
2. **Multiple Selection** - Multiple node selection
3. **Checkable TreeSelect** - TreeSelect with checkboxes
4. **Disabled TreeSelect** - Disabled state detection
5. **Show Search** - Search-enabled TreeSelect
6. **TreeData Mode** - TreeSelect using treeData prop
7. **Load Data Asynchronously** - Async loading detection
8. **With Custom Icons** - Custom icon detection
9. **Placement** - bottomLeft, bottomRight, topLeft, topRight
10. **Size Variations** - large, default, small

### Locator-less Detection

Detection relies on:
- Ant Design classes: `ant-select`, `ant-select-tree`, `ant-select-tree-select`
- `data-attr-id` attribute (highest priority)
- ARIA attributes: `aria-label`, `aria-disabled`, `aria-expanded`, `aria-selected`, `aria-checked`
- Role attributes: `role="tree"`, `role="treeitem"`
- Tree node structure inspection via JavaScript
- Standard DOM inspection for dropdown overlay

### Gherkin-Friendly Steps

Users can write semantic Gherkin steps without selectors:

```gherkin
When I select "Fruits" from "Category" TreeSelect
When I select multiple options "Apple", "Banana" from "Products" TreeSelect
When I expand "Department" node in "Organization" TreeSelect
When I check all child nodes under "Region" in "Location" TreeSelect
When I search for "pine" in "Tree Species" TreeSelect
Then "Selected Categories" should contain "Electronics > Mobile"
Then "Department" TreeSelect should show 5 selected items
```

### Behavioral Abilities

- ✅ Select single or multiple tree nodes
- ✅ Expand/collapse tree nodes
- ✅ Search within TreeSelect (when search is enabled)
- ✅ Clear selections
- ✅ Check/uncheck nodes in checkable TreeSelect
- ✅ Select all leaf nodes under a parent
- ✅ Handle dropdown state (open/close)
- ✅ Skip disabled nodes automatically
- ✅ Retry actions to handle animation delays or async loading
- ✅ Path-based selection (e.g., "Parent > Child > Grandchild")

## File Structure

```
framework/components/
├── treeselect_handler.py      # Main handler for TreeSelect interactions
├── treeselect_identifier.py    # Identifies TreeSelect types and properties
└── treeselect_locator.py      # Locates TreeSelect components

steps/
└── treeselect_steps.py        # Gherkin step definitions

features/
└── treeselect_automation.feature  # Feature file with scenarios

tests/
└── test_treeselect_automation.py  # Test file
```

## Usage Examples

### Basic Selection

```python
from framework.components.treeselect_handler import TreeSelectHandler
from framework.context.element_context import ElementContext

# Initialize handler
context = ElementContext()
handler = TreeSelectHandler(driver, context=context)

# Select a node
handler.select_node("Node1", "Category TreeSelect", identifier_type='auto')
```

### Multiple Selection

```python
# Select multiple nodes
handler.select_multiple_nodes(
    ["Apple", "Banana", "Orange"],
    "Products TreeSelect",
    identifier_type='auto'
)
```

### Expand/Collapse Nodes

```python
# Expand a node
handler.expand_node("Parent Node", "Organization TreeSelect", identifier_type='auto')

# Collapse a node
handler.collapse_node("Parent Node", "Organization TreeSelect", identifier_type='auto')
```

### Checkable TreeSelect

```python
# Check a node
handler.check_node("Node1", "Checkable TreeSelect", identifier_type='auto')

# Uncheck a node
handler.uncheck_node("Node1", "Checkable TreeSelect", identifier_type='auto')
```

### Search

```python
# Search within TreeSelect
handler.search_in_treeselect("pine", "Tree Species TreeSelect", identifier_type='auto')
```

### Path-Based Selection

```python
# Select node by path
handler.select_node("Parent > Child > Grandchild", "Basic TreeSelect", identifier_type='auto')
```

### Get TreeSelect Information

```python
# Get TreeSelect info
info = handler.get_treeselect_info("Category TreeSelect", identifier_type='auto')
print(f"Type: {info['type']}")
print(f"Selected: {info['selected_labels']}")
print(f"Tree Structure: {info['tree_structure']}")

# Print summary
handler.print_treeselect_summary("Category TreeSelect", identifier_type='auto')
```

## Gherkin Step Definitions

### When Steps

- `When I select "{node_text}" from "{treeselect_label}" TreeSelect`
- `When I select multiple options "{node_list}" from "{treeselect_label}" TreeSelect`
- `When I expand "{node_text}" node in "{treeselect_label}" TreeSelect`
- `When I collapse "{node_text}" node in "{treeselect_label}" TreeSelect`
- `When I check "{node_text}" node in "{treeselect_label}" TreeSelect`
- `When I uncheck "{node_text}" node in "{treeselect_label}" TreeSelect`
- `When I check all child nodes under "{parent_node}" in "{treeselect_label}" TreeSelect`
- `When I search for "{search_text}" in "{treeselect_label}" TreeSelect`
- `When I clear selection in "{treeselect_label}" TreeSelect`
- `When I select all leaf nodes under "{parent_node}" in "{treeselect_label}" TreeSelect`

### Then Steps

- `Then "{treeselect_label}" TreeSelect should contain "{expected_text}"`
- `Then "{treeselect_label}" TreeSelect should show {count} selected items`
- `Then I print summary of "{treeselect_label}" TreeSelect`

### Given Steps (Context-Driven)

- `Given I identify the TreeSelect with data-attr-id "{data_attr_id}"`
- `Given I identify the TreeSelect with label "{label}"`

## Identification Priority

When identifying a TreeSelect, the framework uses this priority order:

1. `data-attr-id` attribute (highest priority)
2. Visible label text or placeholder
3. `aria-label` attribute
4. Form or section context
5. Fallback to first visible TreeSelect if unambiguous

## Tree Node Intelligence

The framework understands:
- Parent-child relationships
- Hierarchical path resolution
- Both TreeData and TreeNode APIs
- Async loading indicators
- Virtual scrolling (if present)
- Checked vs selected states in checkable mode

## Reporting & Logging

The framework provides detailed logging:

- Total TreeSelect count
- Type classification (single/multiple/checkable)
- Current selections with full paths
- Expand/collapse state
- Disabled nodes/components
- Tree depth and breadth statistics
- Skipped actions with clear reasons
- Search operations and results

## Integration

The TreeSelect handler is automatically integrated into the test context:

```python
# In conftest.py
context.treeselect_handler = TreeSelectHandler(driver, context=element_context)
```

## Error Handling

The framework includes:
- TreeSelect-specific exceptions
- Retry logic for async operations
- Graceful handling of disabled nodes
- Clear error messages for debugging

## Requirements

- Python 3.7+
- Selenium
- pytest-bdd
- Ant Design components

## Example Feature File

See `features/treeselect_automation.feature` for complete examples of all TreeSelect operations.

## Notes

- The framework automatically handles dropdown opening/closing
- Virtual scrolling is supported
- Async loading is detected and handled
- The framework skips disabled nodes automatically
- Path-based selection supports "Parent > Child > Grandchild" format
