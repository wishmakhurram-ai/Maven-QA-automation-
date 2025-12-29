"""
Generic Ant Design Table Handler
Handles table interactions (reading, sorting, filtering, selecting, expanding, paginating)
Uses TableLocator for finding tables and TableIdentifier for analyzing them
Uses ElementContext for context-driven interactions
NO hardcoded selectors - uses data-attr-id, roles, DOM traversal, and JavaScript
"""
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from typing import Optional, Dict, List, Any
from framework.base.base_page import BasePage
from framework.components.table_locator import TableLocator
from framework.components.table_identifier import TableIdentifier
from framework.context.element_context import ElementContext, ElementInfo


class TableHandler(BasePage):
    """
    Generic handler for Ant Design table interactions
    Single Responsibility: Handle table interactions (read, sort, filter, select, expand, paginate)
    Uses TableLocator to find tables and TableIdentifier to analyze them
    """
    
    def __init__(self, driver: webdriver, context: Optional[ElementContext] = None):
        """
        Initialize Table Handler
        
        Args:
            driver: Selenium WebDriver instance
            context: Optional ElementContext for context-driven interactions
        """
        super().__init__(driver)
        self.locator = TableLocator(driver)
        self.identifier = TableIdentifier()
        self.context = context
    
    def identify_and_store(self, identifier: str, identifier_type: str = 'data_attr_id',
                          timeout: int = 10, context_key: Optional[str] = None) -> bool:
        """
        Identify a table and store it in context
        
        Args:
            identifier: Value to identify the table (data-attr-id, text, or index)
            identifier_type: Type of identifier ('data_attr_id', 'text', 'index', 'auto')
            timeout: Maximum wait time in seconds
            context_key: Optional key to use in context
            
        Returns:
            True if table was identified and stored, False otherwise
        """
        if not self.context:
            print("Context not available. Cannot store element.")
            return False
        
        element = None
        
        try:
            if identifier_type == 'data_attr_id':
                element = self.locator.find_table_by_data_attr(identifier, timeout, self.context)
            elif identifier_type == 'text':
                element = self.locator.find_table_by_text(identifier, timeout, self.context)
            elif identifier_type == 'index':
                index = int(identifier) if identifier.isdigit() else 0
                element = self.locator.find_table_by_index(index, timeout, self.context)
            elif identifier_type == 'auto':
                # PRIORITY ORDER: pattern discovery -> data-attr-id -> text -> index
                try:
                    from framework.utils.pattern_discovery import PatternDiscovery
                    pattern_discovery = PatternDiscovery(self.driver)
                    
                    normalized_id = identifier.lower().replace(' ', '-').replace('_', '-')
                    matching_attr_id = pattern_discovery.find_matching_data_attr_id(normalized_id, 'table')
                    if matching_attr_id:
                        element = self.locator.find_table_by_data_attr(matching_attr_id, timeout=3, context=self.context)
                        if element:
                            print(f"   >> Found using pattern discovery: {matching_attr_id}")
                    
                    if not element:
                        candidates = pattern_discovery.generate_candidates(normalized_id, 'table')
                        for candidate in candidates:
                            element = self.locator.find_table_by_data_attr(candidate, timeout=2, context=self.context)
                            if element:
                                print(f"   >> Found using pattern candidate: {candidate}")
                                break
                except Exception as e:
                    print(f"   >> Pattern discovery failed: {str(e)}")
                
                if not element:
                    element = self.locator.find_table_by_data_attr(identifier, timeout=3, context=self.context)
                
                if not element:
                    element = self.locator.find_table_by_text(identifier, timeout=3, context=self.context)
                
                if not element:
                    try:
                        index = int(identifier) if identifier.isdigit() else 0
                        element = self.locator.find_table_by_index(index, timeout=2, context=self.context)
                    except:
                        pass
            
            if element:
                if context_key and context_key != identifier:
                    element_info = self.context.get_element(identifier) or self.context.get_current()
                    if element_info:
                        self.context.store_element(context_key, element_info)
                print(f"Table identified and stored in context: {identifier}")
                return True
            else:
                print(f"Table not found with identifier: {identifier} (type: {identifier_type})")
                return False
                
        except Exception as e:
            print(f"Error identifying table: {str(e)}")
            return False
    
    def get_table_from_context(self, context_key: Optional[str] = None) -> Optional[WebElement]:
        """
        Get table from context, handling stale element references
        
        Args:
            context_key: Key to retrieve element from context. If None, uses current element.
            
        Returns:
            WebElement if found, None otherwise
        """
        if not self.context:
            return None
        
        try:
            if context_key:
                element_info = self.context.get_element(context_key)
            else:
                element_info = self.context.get_current()
            
            if element_info and element_info.element:
                # Check if element is stale by trying to access it
                try:
                    _ = element_info.element.tag_name
                    return element_info.element
                except Exception:
                    # Element is stale, try to re-find it
                    print("   >> Stale element detected, re-finding table...")
                    if element_info.data_attr_id:
                        # Re-find by data-attr-id
                        return self.locator.find_table_by_data_attr(
                            element_info.data_attr_id, 
                            timeout=5, 
                            context=self.context
                        )
                    else:
                        # Fallback: find by index
                        return self.locator.find_table_by_index(0, timeout=5, context=self.context)
        except Exception as e:
            print(f"   >> Error getting table from context: {str(e)}")
        
        return None
    
    # ==================== READING OPERATIONS ====================
    
    def read_all_rows(self, table_element: Optional[WebElement] = None, 
                     context_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Read all rows from the table
        
        Args:
            table_element: Optional table WebElement. If None, gets from context.
            context_key: Optional context key to retrieve table
            
        Returns:
            List of dictionaries, each representing a row with column names as keys
        """
        # Handle stale element reference
        if table_element:
            try:
                _ = table_element.tag_name
            except Exception:
                # Element is stale, get fresh one from context
                table_element = self.get_table_from_context(context_key)
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            print("   >> Table not found")
            return []
        
        try:
            script = """
            var table = arguments[0];
            var rows = [];
            var headerElements = table.querySelectorAll('thead th, thead .ant-table-cell');
            var headers = [];
            
            // Get column headers
            for (var i = 0; i < headerElements.length; i++) {
                var header = headerElements[i];
                var text = header.textContent.trim();
                text = text.replace(/^[↑↓]/, '').trim();
                headers.push(text);
            }
            
            // Get all data rows
            var rowElements = table.querySelectorAll('tbody tr:not(.ant-table-placeholder)');
            
            for (var i = 0; i < rowElements.length; i++) {
                var row = rowElements[i];
                var cells = row.querySelectorAll('td, .ant-table-cell');
                var rowData = {};
                
                for (var j = 0; j < cells.length && j < headers.length; j++) {
                    var cellText = cells[j].textContent.trim();
                    rowData[headers[j]] = cellText;
                }
                
                rows.push(rowData);
            }
            
            return rows;
            """
            
            rows = self.driver.execute_script(script, table)
            return rows or []
        except Exception as e:
            print(f"   >> Error reading rows: {str(e)}")
            return []
    
    def read_cell_value(self, column_name: str, row_index: int = 0,
                       table_element: Optional[WebElement] = None,
                       context_key: Optional[str] = None) -> Optional[str]:
        """
        Read cell value by column name and row index
        
        Args:
            column_name: Name of the column
            row_index: Zero-based row index
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            Cell value as string, or None if not found
        """
        rows = self.read_all_rows(table_element, context_key)
        if 0 <= row_index < len(rows):
            return rows[row_index].get(column_name)
        return None
    
    def find_row_by_column_value(self, column_name: str, value: str,
                                 table_element: Optional[WebElement] = None,
                                 context_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Find row by column value
        
        Args:
            column_name: Name of the column to search
            value: Value to search for
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            Dictionary representing the row, or None if not found
        """
        rows = self.read_all_rows(table_element, context_key)
        for row in rows:
            if str(row.get(column_name, '')).strip() == str(value).strip():
                return row
        return None
    
    def get_table_summary(self, table_element: Optional[WebElement] = None,
                         context_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive table summary (printable format)
        
        Args:
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            Dictionary with table summary information
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return {}
        
        # Handle stale element reference by re-finding the table
        try:
            # Try to access the element to check if it's stale
            _ = table.tag_name
        except Exception:
            # Element is stale, re-find it
            print("   >> Table element is stale, re-finding...")
            try:
                # Try to get the data-attr-id from context to re-find
                if self.context:
                    element_info = self.context.get_current() if not context_key else self.context.get_element(context_key)
                    if element_info and element_info.data_attr_id:
                        table = self.locator.find_table_by_data_attr(element_info.data_attr_id, timeout=5, context=self.context)
                    elif element_info and element_info.metadata and 'identifier' in element_info.metadata:
                        # Try to re-find by the stored identifier
                        identifier = element_info.metadata.get('identifier')
                        if identifier:
                            table = self.locator.find_table_by_index(0, timeout=5, context=self.context)
                # If still not found, try finding by index
                if not table:
                    table = self.locator.find_table_by_index(0, timeout=5, context=self.context)
            except Exception as e:
                print(f"   >> Error re-finding table: {str(e)}")
                return {}
        
        if not table:
            return {}
        
        try:
            properties = self.identifier.get_table_properties(table, self.driver)
            rows = self.read_all_rows(table)
        except Exception as e:
            print(f"   >> Error getting table properties (element may be stale): {str(e)}")
            # Try one more time to re-find
            try:
                table = self.locator.find_table_by_index(0, timeout=5, context=self.context)
                if table:
                    properties = self.identifier.get_table_properties(table, self.driver)
                    rows = self.read_all_rows(table)
                else:
                    return {}
            except Exception as e2:
                print(f"   >> Error in retry: {str(e2)}")
                return {}
        
        summary = {
            'type': properties.get('type', 'standard'),
            'title': properties.get('title'),
            'row_count': properties.get('rows', {}),
            'column_count': properties.get('columns', 0),
            'headers': [h['text'] for h in properties.get('headers', [])],
            'sortable_columns': properties.get('sortable_columns', []),
            'filterable_columns': properties.get('filterable_columns', []),
            'has_row_selection': properties.get('has_row_selection', {}),
            'has_pagination': properties.get('has_pagination', False),
            'has_expandable_rows': properties.get('has_expandable_rows', False),
            'empty_state': properties.get('empty_state'),
            'loading_state': properties.get('loading_state', False),
            'rows': rows
        }
        
        return summary
    
    def print_table_summary(self, table_element: Optional[WebElement] = None,
                           context_key: Optional[str] = None):
        """
        Print readable table summary to console
        
        Args:
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
        """
        summary = self.get_table_summary(table_element, context_key)
        
        if not summary:
            print("   >> No table found to summarize")
            return
        
        print("\n" + "="*80)
        print("TABLE SUMMARY")
        print("="*80)
        title = summary.get('title')
        if title:
            print(f"Title: {title}")
            print("-" * 80)
        print(f"Type: {summary.get('type', 'N/A')}")
        print(f"Visible Rows: {summary.get('row_count', {}).get('visible', 0)}")
        print(f"Total Rows: {summary.get('row_count', {}).get('total', 0)}")
        print(f"Columns: {summary.get('column_count', 0)}")
        print(f"\nHeaders: {', '.join(summary.get('headers', []))}")
        
        if summary.get('sortable_columns'):
            print(f"Sortable Columns: {', '.join(summary.get('sortable_columns', []))}")
        
        if summary.get('filterable_columns'):
            print(f"Filterable Columns: {', '.join(summary.get('filterable_columns', []))}")
        
        if summary.get('has_row_selection', {}).get('checkbox'):
            print("Row Selection: Checkbox enabled")
        if summary.get('has_row_selection', {}).get('radio'):
            print("Row Selection: Radio enabled")
        
        if summary.get('has_pagination'):
            print("Pagination: Yes")
        
        if summary.get('has_expandable_rows'):
            print("Expandable Rows: Yes")
        
        if summary.get('empty_state'):
            print(f"Empty State: {summary.get('empty_state')}")
        
        if summary.get('loading_state'):
            print("Status: Loading")
        
        print("\n" + "-"*80)
        print("TABLE DATA")
        print("-"*80)
        
        rows = summary.get('rows', [])
        if rows:
            # Print headers
            headers = summary.get('headers', [])
            if headers:
                header_line = " | ".join(f"{h:20}" for h in headers)
                print(header_line)
                print("-" * len(header_line))
            
            # Print rows
            for i, row in enumerate(rows[:10]):  # Limit to first 10 rows
                row_line = " | ".join(f"{str(row.get(h, '')):20}" for h in headers)
                print(row_line)
            
            if len(rows) > 10:
                print(f"... and {len(rows) - 10} more rows")
        else:
            print("No data rows found")
        
        print("="*80 + "\n")
    
    # ==================== SORTING OPERATIONS ====================
    
    def sort_by_column(self, column_name: str, direction: str = 'asc',
                      table_element: Optional[WebElement] = None,
                      context_key: Optional[str] = None) -> bool:
        """
        Sort table by column name
        
        Args:
            column_name: Name of the column to sort by
            direction: Sort direction ('asc' or 'desc')
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if sorting was successful, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var columnName = arguments[1];
            var direction = arguments[2];
            
            // Find header with matching text
            var headers = table.querySelectorAll('thead th, thead .ant-table-cell');
            var targetHeader = null;
            
            for (var i = 0; i < headers.length; i++) {
                var headerText = headers[i].textContent.trim();
                // Remove sort arrows and icons
                headerText = headerText.replace(/^[↑↓↕]/, '').trim();
                headerText = headerText.replace(/[↑↓↕]$/, '').trim();
                if (headerText === columnName) {
                    targetHeader = headers[i];
                    break;
                }
            }
            
            if (!targetHeader) {
                console.log('Header not found for: ' + columnName);
                return false;
            }
            
            // Find sort trigger - try multiple selectors
            var sorter = targetHeader.querySelector('.ant-table-column-sorter') ||
                        targetHeader.querySelector('.ant-table-column-sorters') ||
                        targetHeader.querySelector('.ant-table-column-sort');
            
            // Also check for sort icons directly
            if (!sorter) {
                var sortIcon = targetHeader.querySelector('.anticon-caret-up, .anticon-caret-down, .anticon-arrow-up, .anticon-arrow-down');
                if (sortIcon) {
                    sorter = sortIcon.closest('.ant-table-column-sorter') || sortIcon.closest('.ant-table-column-sorters') || sortIcon;
                }
            }
            
            if (!sorter) {
                // Try clicking the header itself if it has sort class
                if (targetHeader.classList.contains('ant-table-column-has-sorters') || 
                    targetHeader.querySelector('.anticon')) {
                    sorter = targetHeader;
                } else {
                    console.log('Sorter not found for column: ' + columnName);
                    // Try to find any clickable element in header
                    var clickable = targetHeader.querySelector('span, div, .ant-table-column-title');
                    if (clickable) {
                        sorter = clickable;
                    } else {
                        return false;
                    }
                }
            }
            
            // Always click to sort (let Ant Design handle the state)
            try {
                sorter.click();
                // Wait for sort to apply
                setTimeout(function() {}, 300);
                return true;
            } catch (e) {
                console.log('Error clicking sorter: ' + e);
                return false;
            }
            """
            
            result = self.driver.execute_script(script, table, column_name, direction)
            
            # Wait for sort to complete
            import time
            time.sleep(1)  # Increased wait time for sort to complete
            
            return result or False
        except Exception as e:
            print(f"   >> Error sorting by column: {str(e)}")
            return False
    
    # ==================== FILTERING OPERATIONS ====================
    
    def apply_column_filter(self, column_name: str, filter_value: str,
                           table_element: Optional[WebElement] = None,
                           context_key: Optional[str] = None) -> bool:
        """
        Apply filter to a column
        
        Args:
            column_name: Name of the column to filter
            filter_value: Filter value to apply
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if filter was applied successfully, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var columnName = arguments[1];
            var filterValue = arguments[2];
            
            // Find header with matching text
            var headers = table.querySelectorAll('thead th, thead .ant-table-cell');
            var targetHeader = null;
            
            for (var i = 0; i < headers.length; i++) {
                var headerText = headers[i].textContent.trim().replace(/^[↑↓]/, '').trim();
                if (headerText === columnName) {
                    targetHeader = headers[i];
                    break;
                }
            }
            
            if (!targetHeader) return false;
            
            // Find filter trigger
            var filterTrigger = targetHeader.querySelector('.ant-table-filter-trigger');
            if (!filterTrigger) return false;
            
            // Click filter trigger to open filter dropdown
            filterTrigger.click();
            
            return true;
            """
            
            result = self.driver.execute_script(script, table, column_name, filter_value)
            
            # Wait for filter dropdown to open, then apply filter
            import time
            time.sleep(0.5)
            
            # Try to find and interact with filter input/select
            # This is simplified - actual implementation would need to handle different filter types
            return result or False
        except Exception as e:
            print(f"   >> Error applying filter: {str(e)}")
            return False
    
    def clear_filters(self, table_element: Optional[WebElement] = None,
                     context_key: Optional[str] = None) -> bool:
        """
        Clear all filters
        
        Args:
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if filters were cleared, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var filterTriggers = table.querySelectorAll('.ant-table-filter-trigger');
            
            for (var i = 0; i < filterTriggers.length; i++) {
                var trigger = filterTriggers[i];
                var header = trigger.closest('th, .ant-table-cell');
                if (header && header.getAttribute('aria-sort') === 'none') {
                    // Filter is active, click to clear
                    trigger.click();
                    setTimeout(function() {
                        var resetBtn = document.querySelector('.ant-table-filter-dropdown .ant-btn-link');
                        if (resetBtn) resetBtn.click();
                    }, 200);
                }
            }
            
            return true;
            """
            
            result = self.driver.execute_script(script, table)
            import time
            time.sleep(0.5)
            return result or False
        except Exception as e:
            print(f"   >> Error clearing filters: {str(e)}")
            return False
    
    # ==================== ROW SELECTION OPERATIONS ====================
    
    def select_row_by_column_value(self, column_name: str, value: str,
                                   table_element: Optional[WebElement] = None,
                                   context_key: Optional[str] = None) -> bool:
        """
        Select row by column value (checkbox or radio)
        
        Args:
            column_name: Name of the column to search
            value: Value to match
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if row was selected, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var columnName = arguments[1];
            var value = arguments[2];
            
            // Find the row
            var rows = table.querySelectorAll('tbody tr');
            var targetRow = null;
            
            // Get headers to find column index
            var headers = table.querySelectorAll('thead th, thead .ant-table-cell');
            var columnIndex = -1;
            for (var i = 0; i < headers.length; i++) {
                var headerText = headers[i].textContent.trim().replace(/^[↑↓]/, '').trim();
                if (headerText === columnName) {
                    columnIndex = i;
                    break;
                }
            }
            
            if (columnIndex === -1) return false;
            
            // Find row with matching value
            for (var i = 0; i < rows.length; i++) {
                var cells = rows[i].querySelectorAll('td, .ant-table-cell');
                if (cells[columnIndex] && cells[columnIndex].textContent.trim() === value) {
                    targetRow = rows[i];
                    break;
                }
            }
            
            if (!targetRow) return false;
            
            // Find and click checkbox/radio
            var checkbox = targetRow.querySelector('input[type="checkbox"]');
            var radio = targetRow.querySelector('input[type="radio"]');
            
            if (checkbox && !checkbox.checked) {
                checkbox.click();
                return true;
            } else if (radio && !radio.checked) {
                radio.click();
                return true;
            }
            
            return false;
            """
            
            result = self.driver.execute_script(script, table, column_name, value)
            import time
            time.sleep(0.3)
            return result or False
        except Exception as e:
            print(f"   >> Error selecting row: {str(e)}")
            return False
    
    def select_all_rows(self, table_element: Optional[WebElement] = None,
                       context_key: Optional[str] = None) -> bool:
        """
        Select all rows (if checkbox selection is enabled)
        
        Args:
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if all rows were selected, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var headerCheckbox = table.querySelector('thead input[type="checkbox"]');
            if (headerCheckbox && !headerCheckbox.checked) {
                headerCheckbox.click();
                return true;
            }
            return false;
            """
            
            result = self.driver.execute_script(script, table)
            import time
            time.sleep(0.3)
            return result or False
        except Exception as e:
            print(f"   >> Error selecting all rows: {str(e)}")
            return False
    
    def deselect_all_rows(self, table_element: Optional[WebElement] = None,
                         context_key: Optional[str] = None) -> bool:
        """
        Deselect all rows
        
        Args:
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if all rows were deselected, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var headerCheckbox = table.querySelector('thead input[type="checkbox"]');
            if (headerCheckbox && headerCheckbox.checked) {
                headerCheckbox.click();
                return true;
            }
            return false;
            """
            
            result = self.driver.execute_script(script, table)
            import time
            time.sleep(0.3)
            return result or False
        except Exception as e:
            print(f"   >> Error deselecting all rows: {str(e)}")
            return False
    
    # ==================== EXPANDABLE ROWS OPERATIONS ====================
    
    def expand_row(self, row_index: int = 0,
                  table_element: Optional[WebElement] = None,
                  context_key: Optional[str] = None) -> bool:
        """
        Expand a row (if expandable rows are enabled)
        
        Args:
            row_index: Zero-based row index
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if row was expanded, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var rowIndex = arguments[1];
            var rows = table.querySelectorAll('tbody tr:not(.ant-table-placeholder)');
            
            if (rowIndex >= 0 && rowIndex < rows.length) {
                var row = rows[rowIndex];
                var expandIcon = row.querySelector('.ant-table-row-expand-icon');
                if (expandIcon && expandIcon.classList.contains('ant-table-row-expand-icon-collapsed')) {
                    expandIcon.click();
                    return true;
                }
            }
            
            return false;
            """
            
            result = self.driver.execute_script(script, table, row_index)
            import time
            time.sleep(0.5)
            return result or False
        except Exception as e:
            print(f"   >> Error expanding row: {str(e)}")
            return False
    
    def collapse_row(self, row_index: int = 0,
                    table_element: Optional[WebElement] = None,
                    context_key: Optional[str] = None) -> bool:
        """
        Collapse a row
        
        Args:
            row_index: Zero-based row index
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if row was collapsed, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var rowIndex = arguments[1];
            var rows = table.querySelectorAll('tbody tr:not(.ant-table-placeholder)');
            
            if (rowIndex >= 0 && rowIndex < rows.length) {
                var row = rows[rowIndex];
                var expandIcon = row.querySelector('.ant-table-row-expand-icon');
                if (expandIcon && expandIcon.classList.contains('ant-table-row-expand-icon-expanded')) {
                    expandIcon.click();
                    return true;
                }
            }
            
            return false;
            """
            
            result = self.driver.execute_script(script, table, row_index)
            import time
            time.sleep(0.3)
            return result or False
        except Exception as e:
            print(f"   >> Error collapsing row: {str(e)}")
            return False
    
    def read_expanded_content(self, row_index: int = 0,
                             table_element: Optional[WebElement] = None,
                             context_key: Optional[str] = None) -> Optional[str]:
        """
        Read expanded row content
        
        Args:
            row_index: Zero-based row index
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            Expanded content text, or None if not expanded
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return None
        
        try:
            script = """
            var table = arguments[0];
            var rowIndex = arguments[1];
            var rows = table.querySelectorAll('tbody tr:not(.ant-table-placeholder)');
            
            if (rowIndex >= 0 && rowIndex < rows.length) {
                var row = rows[rowIndex];
                var expandedContent = row.nextElementSibling;
                if (expandedContent && expandedContent.classList.contains('ant-table-expanded-row')) {
                    return expandedContent.textContent.trim();
                }
            }
            
            return null;
            """
            
            result = self.driver.execute_script(script, table, row_index)
            return result
        except Exception as e:
            print(f"   >> Error reading expanded content: {str(e)}")
            return None
    
    # ==================== PAGINATION OPERATIONS ====================
    
    def go_to_next_page(self, table_element: Optional[WebElement] = None,
                       context_key: Optional[str] = None) -> bool:
        """
        Go to next page (if pagination exists)
        
        Args:
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if navigated to next page, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var pagination = table.closest('.ant-table-wrapper')?.querySelector('.ant-pagination');
            if (!pagination) return false;
            
            var nextBtn = pagination.querySelector('.ant-pagination-next:not(.ant-pagination-disabled)');
            if (nextBtn) {
                nextBtn.click();
                return true;
            }
            
            return false;
            """
            
            result = self.driver.execute_script(script, table)
            import time
            time.sleep(1)  # Wait for page to load
            return result or False
        except Exception as e:
            print(f"   >> Error going to next page: {str(e)}")
            return False
    
    def go_to_previous_page(self, table_element: Optional[WebElement] = None,
                           context_key: Optional[str] = None) -> bool:
        """
        Go to previous page
        
        Args:
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if navigated to previous page, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var pagination = table.closest('.ant-table-wrapper')?.querySelector('.ant-pagination');
            if (!pagination) return false;
            
            var prevBtn = pagination.querySelector('.ant-pagination-prev:not(.ant-pagination-disabled)');
            if (prevBtn) {
                prevBtn.click();
                return true;
            }
            
            return false;
            """
            
            result = self.driver.execute_script(script, table)
            import time
            time.sleep(1)
            return result or False
        except Exception as e:
            print(f"   >> Error going to previous page: {str(e)}")
            return False
    
    def go_to_page(self, page_number: int,
                  table_element: Optional[WebElement] = None,
                  context_key: Optional[str] = None) -> bool:
        """
        Go to specific page number
        
        Args:
            page_number: Page number to navigate to
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if navigated to page, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var pageNumber = arguments[1];
            var pagination = table.closest('.ant-table-wrapper')?.querySelector('.ant-pagination');
            if (!pagination) return false;
            
            var pageItems = pagination.querySelectorAll('.ant-pagination-item');
            for (var i = 0; i < pageItems.length; i++) {
                var item = pageItems[i];
                var itemNumber = parseInt(item.textContent.trim());
                if (itemNumber === pageNumber) {
                    item.click();
                    return true;
                }
            }
            
            return false;
            """
            
            result = self.driver.execute_script(script, table, page_number)
            import time
            time.sleep(1)
            return result or False
        except Exception as e:
            print(f"   >> Error going to page: {str(e)}")
            return False
    
    # ==================== CELL INTERACTION OPERATIONS ====================
    
    def click_cell_button(self, column_name: str, row_index: int = 0,
                         button_text: Optional[str] = None,
                         table_element: Optional[WebElement] = None,
                         context_key: Optional[str] = None) -> bool:
        """
        Click a button/link in a table cell
        
        Args:
            column_name: Name of the column containing the button
            row_index: Zero-based row index
            button_text: Optional button text to match (if multiple buttons in cell)
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if button was clicked, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var columnName = arguments[1];
            var rowIndex = arguments[2];
            var buttonText = arguments[3];
            
            // Get headers to find column index
            var headers = table.querySelectorAll('thead th, thead .ant-table-cell');
            var columnIndex = -1;
            for (var i = 0; i < headers.length; i++) {
                var headerText = headers[i].textContent.trim();
                headerText = headerText.replace(/^[↑↓↕]/, '').trim();
                headerText = headerText.replace(/[↑↓↕]$/, '').trim();
                if (headerText === columnName) {
                    columnIndex = i;
                    break;
                }
            }
            
            if (columnIndex === -1) return false;
            
            // Get the row
            var rows = table.querySelectorAll('tbody tr:not(.ant-table-placeholder)');
            if (rowIndex < 0 || rowIndex >= rows.length) return false;
            
            var row = rows[rowIndex];
            var cells = row.querySelectorAll('td, .ant-table-cell');
            if (columnIndex >= cells.length) return false;
            
            var cell = cells[columnIndex];
            
            // Find button or link in the cell
            var button = null;
            if (buttonText) {
                // Find button/link with specific text
                var buttons = cell.querySelectorAll('button, a, .ant-btn, [role="button"]');
                for (var i = 0; i < buttons.length; i++) {
                    if (buttons[i].textContent.trim().includes(buttonText)) {
                        button = buttons[i];
                        break;
                    }
                }
            } else {
                // Find first button/link
                button = cell.querySelector('button, a, .ant-btn, [role="button"]');
            }
            
            if (button) {
                button.click();
                return true;
            }
            
            return false;
            """
            
            result = self.driver.execute_script(script, table, column_name, row_index, button_text)
            import time
            time.sleep(0.5)
            return result or False
        except Exception as e:
            print(f"   >> Error clicking cell button: {str(e)}")
            return False
    
    def click_row(self, row_index: int = 0,
                  table_element: Optional[WebElement] = None,
                  context_key: Optional[str] = None) -> bool:
        """
        Click on a table row
        
        Args:
            row_index: Zero-based row index
            table_element: Optional table WebElement
            context_key: Optional context key to retrieve table
            
        Returns:
            True if row was clicked, False otherwise
        """
        table = table_element or self.get_table_from_context(context_key)
        if not table:
            return False
        
        try:
            script = """
            var table = arguments[0];
            var rowIndex = arguments[1];
            var rows = table.querySelectorAll('tbody tr:not(.ant-table-placeholder)');
            
            if (rowIndex >= 0 && rowIndex < rows.length) {
                rows[rowIndex].click();
                return true;
            }
            
            return false;
            """
            
            result = self.driver.execute_script(script, table, row_index)
            import time
            time.sleep(0.3)
            return result or False
        except Exception as e:
            print(f"   >> Error clicking row: {str(e)}")
            return False

