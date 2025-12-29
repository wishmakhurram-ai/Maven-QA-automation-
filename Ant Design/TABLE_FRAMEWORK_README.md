# Ant Design Table Automation Framework

A complete, locator-less Python + Selenium framework to automatically detect and interact with Ant Design Tables without hardcoded selectors.

## ✅ Features

### 1. Automatic Table Recognition
- Detects all Ant Design tables automatically
- Classifies tables as:
  - Standard data table
  - Bordered table
  - Table with pagination
  - Table with row selection (checkbox/radio)
  - Expandable row table
  - Sortable table
  - Filterable table
  - Table with fixed header/columns

### 2. Auto-Detect Table Properties
For each detected table, extracts:
- Number of rows (visible & total if paginated)
- Number of columns
- Column headers (text, order)
- Sortable columns
- Filterable columns
- Expandable rows
- Row selection enabled (checkbox/radio)
- Pagination presence
- Empty state / loading state

### 3. No Hardcoded Selectors
- ❌ NO hardcoded XPath
- ❌ NO hardcoded CSS selectors
- ✅ Uses ONLY:
  - `data-attr-id` / `data-atr-id` attributes
  - `role="table"`, `role="row"`, `role="cell"` attributes
  - Visible header and cell text
  - DOM traversal & JavaScript inspection
  - Pattern discovery (similar to button/input handlers)

### 4. Behavioral Abilities

#### Row & Cell Interaction
- Read all rows
- Read cell value by column name
- Find row by column value
- Click buttons/links inside a row

#### Sorting
- `sort_by_column("Created Date", "asc")`
- `sort_by_column("Name", "desc")`

#### Filtering
- Apply column filters (if present)
- Clear filters

#### Row Selection
- Select row by column value
- Select all rows
- Deselect rows

#### Expandable Rows
- Detect expandable rows
- Expand/collapse rows
- Read expanded content

#### Pagination (if table has it)
- Detect pagination automatically
- Go to next/previous page
- Go to page number
- Validate total records

## 📁 Files Created

1. **`framework/components/table_locator.py`**
   - Finds tables using data-attr-id, roles, DOM traversal
   - NO hardcoded selectors

2. **`framework/components/table_identifier.py`**
   - Analyzes table properties
   - Identifies table type and features

3. **`framework/components/table_handler.py`**
   - Main handler for all table interactions
   - Reading, sorting, filtering, selecting, expanding, paginating

4. **`steps/table_steps.py`**
   - Gherkin step definitions for table operations
   - Works with pytest-bdd

5. **`tests/test_table_automation.py`**
   - Test file linking to feature file

6. **`features/table_automation.feature`**
   - Gherkin feature file with test scenarios

7. **`test_table_framework.py`**
   - Standalone Python script to test the framework
   - Run directly: `python test_table_framework.py`

## 🚀 Usage

### Option 1: Run Standalone Test Script

```bash
python test_table_framework.py
```

This will:
1. Open Ant Design table documentation page
2. Find all tables automatically
3. Print table summary
4. Test reading, sorting, filtering, selection, expansion, pagination

### Option 2: Run with pytest-bdd

```bash
pytest tests/test_table_automation.py -v -s
```

### Option 3: Use in Your Tests

```python
from framework.components.table_handler import TableHandler
from framework.context.element_context import ElementContext

# Create handler
element_context = ElementContext()
table_handler = TableHandler(driver, context=element_context)

# Identify table (auto-discovery)
table_handler.identify_and_store("0", identifier_type='index')

# Print table summary
table_handler.print_table_summary()

# Read all rows
rows = table_handler.read_all_rows()

# Read cell by column name
value = table_handler.read_cell_value("Name", row_index=0)

# Sort table
table_handler.sort_by_column("Name", "asc")

# Select row
table_handler.select_row_by_column_value("Name", "John")

# Pagination
table_handler.go_to_next_page()
```

## 📝 Gherkin Steps Available

### Table Identification
- `Given I identify the table with data-atr-id "{id}"`
- `Given I identify the table with text "{text}"`
- `Given I identify the table at index {index}`
- `Given I identify the first table`

### Reading
- `When I read all rows from the table`
- `When I read the cell value from column "{name}" at row {index}`
- `When I find the row with column "{name}" equal to "{value}"`
- `When I print the table summary`

### Sorting
- `When I sort the table by column "{name}" in {asc|desc} order`

### Filtering
- `When I apply filter to column "{name}" with value "{value}"`
- `When I clear all filters`

### Selection
- `When I select the row with column "{name}" equal to "{value}"`
- `When I select all rows`
- `When I deselect all rows`

### Expansion
- `When I expand row at index {index}`
- `When I collapse row at index {index}`
- `When I read expanded content from row at index {index}`

### Pagination
- `When I go to the next page`
- `When I go to the previous page`
- `When I go to page {number}`

### Verification
- `Then the table should have {count} rows`
- `Then the table should have {count} columns`
- `Then the table should have column "{name}"`

## 🔍 How It Works

1. **Table Detection**: Uses multiple strategies:
   - `role="table"` attribute
   - DOM structure analysis (thead, tbody, tr, th, td)
   - Ant Design class patterns (`.ant-table`)
   - `data-attr-id` pattern discovery
   - Standard HTML `<table>` tags

2. **Property Analysis**: Uses JavaScript to inspect:
   - Table structure
   - Column headers
   - Sort/filter capabilities
   - Selection mechanisms
   - Pagination presence
   - Expandable rows

3. **Interaction**: Uses JavaScript execution for:
   - Clicking sort/filter triggers
   - Selecting checkboxes/radios
   - Expanding/collapsing rows
   - Navigating pagination

## ✨ Key Benefits

1. **Zero Selector Maintenance**: No XPath or CSS selectors to maintain
2. **Automatic Discovery**: Finds tables automatically using multiple strategies
3. **Column Name Based**: Interact by column name, not index
4. **Comprehensive**: Handles all Ant Design table features
5. **Readable Output**: Prints beautiful table summaries
6. **Gherkin Support**: Works with pytest-bdd for BDD testing

## 🎯 Example Output

```
================================================================================
TABLE SUMMARY
================================================================================
Type: with_pagination
Visible Rows: 10
Total Rows: 50
Columns: 5

Headers: Name, Age, Email, Status, Actions
Sortable Columns: Name, Age
Filterable Columns: Status
Row Selection: Checkbox enabled
Pagination: Yes

--------------------------------------------------------------------------------
TABLE DATA
--------------------------------------------------------------------------------
Name                 | Age                  | Email                | Status               | Actions              
John Doe             | 25                   | john@example.com     | Active               | Edit Delete          
Jane Smith           | 30                   | jane@example.com     | Active               | Edit Delete          
...
================================================================================
```

## 📋 Requirements

- Python 3.7+
- Selenium
- pytest-bdd (for Gherkin tests)
- ChromeDriver (for Chrome browser)

## 🔧 Integration

The framework is already integrated into your project:
- ✅ `conftest.py` updated to include `TableHandler`
- ✅ `steps/table_steps.py` imported in `conftest.py`
- ✅ Ready to use in existing tests

## 🐛 Troubleshooting

If tables are not found:
1. Check if page has loaded completely
2. Verify tables use standard Ant Design structure
3. Check browser console for JavaScript errors
4. Try identifying by index: `table_handler.identify_and_store("0", identifier_type='index')`

## 📚 Next Steps

1. Run `python test_table_framework.py` to test against Ant Design docs
2. Use in your feature files with Gherkin steps
3. Extend with custom table operations as needed

---

**Framework Status**: ✅ Complete and Ready to Use













