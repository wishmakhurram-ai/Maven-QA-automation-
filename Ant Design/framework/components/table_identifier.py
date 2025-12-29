"""
Table Identifier - Analyzes table properties and characteristics
Single Responsibility: Identify and analyze table features
NO hardcoded selectors - uses DOM traversal and JavaScript inspection
"""
from selenium.webdriver.remote.webelement import WebElement
from typing import Dict, List, Optional, Set
import re


class TableIdentifier:
    """
    Identifies and analyzes Ant Design table properties
    Single Responsibility: Analyze table characteristics
    """
    
    def __init__(self):
        """Initialize Table Identifier"""
        pass
    
    def identify_table_type(self, table_element: WebElement, driver) -> str:
        """
        Identify the type of table (standard, bordered, paginated, etc.)
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance for JavaScript execution
            
        Returns:
            Table type string (e.g., 'standard', 'bordered', 'with_pagination', etc.)
        """
        try:
            # Use JavaScript to analyze table structure
            script = """
            var table = arguments[0];
            var type = 'standard';
            
            // Check for bordered table
            var hasBordered = table.className && table.className.includes('ant-table-bordered');
            if (hasBordered) type = 'bordered';
            
            // Check for pagination
            var pagination = table.closest('.ant-table-wrapper')?.querySelector('.ant-pagination');
            if (pagination) type = 'with_pagination';
            
            // Check for row selection (checkbox/radio)
            var hasCheckbox = table.querySelector('input[type="checkbox"]') !== null;
            var hasRadio = table.querySelector('input[type="radio"]') !== null;
            if (hasCheckbox || hasRadio) type = 'with_selection';
            
            // Check for expandable rows
            var hasExpandIcon = table.querySelector('.ant-table-row-expand-icon') !== null;
            if (hasExpandIcon) type = 'expandable';
            
            // Check for sortable columns
            var sortableHeaders = table.querySelectorAll('.ant-table-column-sorter');
            if (sortableHeaders.length > 0) type = 'sortable';
            
            // Check for filters
            var filterHeaders = table.querySelectorAll('.ant-table-filter-trigger');
            if (filterHeaders.length > 0) type = 'filterable';
            
            // Check for fixed header/columns
            var fixedHeader = table.querySelector('.ant-table-header')?.classList.contains('ant-table-header-fixed');
            var fixedColumn = table.querySelector('.ant-table-cell-fix-left, .ant-table-cell-fix-right');
            if (fixedHeader || fixedColumn) type = 'fixed_header_or_column';
            
            return type;
            """
            
            table_type = driver.execute_script(script, table_element)
            return table_type or 'standard'
        except Exception as e:
            print(f"   >> Error identifying table type: {str(e)}")
            return 'standard'
    
    def get_table_title(self, table_element: WebElement, driver) -> Optional[str]:
        """
        Get the main header/title of the table
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            Table title/header as string, or None if not found
        """
        try:
            script = """
            var table = arguments[0];
            var title = null;
            
            // Strategy 1: Look for <caption> element
            var caption = table.querySelector('caption');
            if (caption && caption.textContent.trim()) {
                title = caption.textContent.trim();
                return title;
            }
            
            // Strategy 2: Look for heading (h1-h6) above the table
            var wrapper = table.closest('.ant-table-wrapper, .ant-table-container, .ant-table');
            if (wrapper) {
                var current = wrapper.previousElementSibling;
                var attempts = 0;
                while (current && attempts < 5) {
                    var heading = current.querySelector('h1, h2, h3, h4, h5, h6, .ant-typography, [class*="title"]');
                    if (heading) {
                        var text = heading.textContent.trim();
                        if (text && text.length > 0 && text.length < 200) {
                            title = text;
                            return title;
                        }
                    }
                    // Also check if the element itself is a heading
                    if (current.tagName && /^H[1-6]$/.test(current.tagName)) {
                        var text = current.textContent.trim();
                        if (text && text.length > 0 && text.length < 200) {
                            title = text;
                            return title;
                        }
                    }
                    current = current.previousElementSibling;
                    attempts++;
                }
            }
            
            // Strategy 3: Look for title in parent container
            var parent = table.closest('div, section, article');
            if (parent) {
                var titleElement = parent.querySelector('h1, h2, h3, h4, h5, h6, .ant-typography-title, [class*="title"], [class*="header"]');
                if (titleElement) {
                    var text = titleElement.textContent.trim();
                    if (text && text.length > 0 && text.length < 200) {
                        title = text;
                        return title;
                    }
                }
            }
            
            // Strategy 4: Look for aria-label or title attribute
            if (table.getAttribute('aria-label')) {
                title = table.getAttribute('aria-label');
                return title;
            }
            if (table.getAttribute('title')) {
                title = table.getAttribute('title');
                return title;
            }
            
            // Strategy 5: Look for data-attr-id that might indicate purpose
            var dataAttrId = table.getAttribute('data-attr-id') || table.getAttribute('data-atr-id');
            if (dataAttrId && dataAttrId !== 'table_1' && dataAttrId !== 'table_2') {
                // Convert data-attr-id to readable title
                title = dataAttrId.replace(/-/g, ' ').replace(/_/g, ' ');
                title = title.charAt(0).toUpperCase() + title.slice(1);
                return title;
            }
            
            return null;
            """
            
            title = driver.execute_script(script, table_element)
            return title if title else None
        except Exception as e:
            print(f"   >> Error getting table title: {str(e)}")
            return None
    
    def get_table_properties(self, table_element: WebElement, driver) -> Dict:
        """
        Get all properties of a table
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            Dictionary with table properties
        """
        properties = {
            'type': self.identify_table_type(table_element, driver),
            'title': self.get_table_title(table_element, driver),
            'rows': self.get_row_count(table_element, driver),
            'columns': self.get_column_count(table_element, driver),
            'headers': self.get_column_headers(table_element, driver),
            'sortable_columns': self.get_sortable_columns(table_element, driver),
            'filterable_columns': self.get_filterable_columns(table_element, driver),
            'has_row_selection': self.has_row_selection(table_element, driver),
            'has_pagination': self.has_pagination(table_element, driver),
            'has_expandable_rows': self.has_expandable_rows(table_element, driver),
            'empty_state': self.get_empty_state(table_element, driver),
            'loading_state': self.get_loading_state(table_element, driver)
        }
        return properties
    
    def get_row_count(self, table_element: WebElement, driver) -> Dict[str, int]:
        """
        Get row count (visible and total if paginated)
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            Dictionary with 'visible' and 'total' row counts
        """
        try:
            script = """
            var table = arguments[0];
            var visibleRows = table.querySelectorAll('tbody tr:not(.ant-table-placeholder)').length;
            
            // Try to get total from pagination
            var pagination = table.closest('.ant-table-wrapper')?.querySelector('.ant-pagination');
            var total = visibleRows;
            if (pagination) {
                var totalText = pagination.querySelector('.ant-pagination-total-text');
                if (totalText) {
                    var match = totalText.textContent.match(/(\\d+)/);
                    if (match) total = parseInt(match[1]);
                }
            }
            
            return {visible: visibleRows, total: total};
            """
            
            counts = driver.execute_script(script, table_element)
            return counts or {'visible': 0, 'total': 0}
        except Exception as e:
            print(f"   >> Error getting row count: {str(e)}")
            return {'visible': 0, 'total': 0}
    
    def get_column_count(self, table_element: WebElement, driver) -> int:
        """
        Get number of columns
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            Number of columns
        """
        try:
            script = """
            var table = arguments[0];
            var headers = table.querySelectorAll('thead th, thead .ant-table-cell');
            return headers.length;
            """
            
            count = driver.execute_script(script, table_element)
            return count or 0
        except Exception as e:
            print(f"   >> Error getting column count: {str(e)}")
            return 0
    
    def get_column_headers(self, table_element: WebElement, driver) -> List[Dict]:
        """
        Get column headers with their text and order
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            List of dictionaries with 'text' and 'index' for each header
        """
        try:
            script = """
            var table = arguments[0];
            var headers = [];
            var headerElements = table.querySelectorAll('thead th, thead .ant-table-cell');
            
            for (var i = 0; i < headerElements.length; i++) {
                var header = headerElements[i];
                
                // Primary source: visible text
                var text = header.textContent ? header.textContent.trim() : '';
                
                // Fallbacks for headers that use icons/tooltips instead of text
                if (!text) {
                    var titleAttr = header.getAttribute('title');
                    var ariaLabel = header.getAttribute('aria-label');
                    var dataKey = header.getAttribute('data-column-key') || header.getAttribute('data-col') || header.getAttribute('data-field');
                    
                    if (titleAttr && titleAttr.trim()) {
                        text = titleAttr.trim();
                    } else if (ariaLabel && ariaLabel.trim()) {
                        text = ariaLabel.trim();
                    } else if (dataKey && dataKey.trim()) {
                        // Convert machine key to human readable (e.g., created_at -> Created At)
                        var readable = dataKey.replace(/[_-]+/g, ' ').trim();
                        if (readable.length > 0) {
                            text = readable.charAt(0).toUpperCase() + readable.slice(1);
                        }
                    }
                }
                
                // Remove sort/filter icons text and arrows from the final label
                if (text) {
                    text = text.replace(/^[↑↓↕]/, '').trim();
                    text = text.replace(/[↑↓↕]$/, '').trim();
                }
                
                // Check for sortable - look for sorter class or sort icon
                var isSortable = header.querySelector('.ant-table-column-sorter') !== null ||
                                 header.querySelector('.ant-table-column-sorters') !== null ||
                                 header.querySelector('.anticon-caret-up') !== null ||
                                 header.querySelector('.anticon-caret-down') !== null ||
                                 header.classList.contains('ant-table-column-has-sorters');
                
                // Check for filterable
                var isFilterable = header.querySelector('.ant-table-filter-trigger') !== null ||
                                   header.querySelector('.ant-table-filter-column') !== null;
                
                headers.push({
                    text: text,
                    index: i,
                    sortable: isSortable,
                    filterable: isFilterable
                });
            }
            
            return headers;
            """
            
            headers = driver.execute_script(script, table_element)
            return headers or []
        except Exception as e:
            print(f"   >> Error getting column headers: {str(e)}")
            return []
    
    def get_sortable_columns(self, table_element: WebElement, driver) -> List[str]:
        """
        Get list of sortable column names
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            List of sortable column header texts
        """
        headers = self.get_column_headers(table_element, driver)
        return [h['text'] for h in headers if h.get('sortable', False)]
    
    def get_filterable_columns(self, table_element: WebElement, driver) -> List[str]:
        """
        Get list of filterable column names
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            List of filterable column header texts
        """
        headers = self.get_column_headers(table_element, driver)
        return [h['text'] for h in headers if h.get('filterable', False)]
    
    def has_row_selection(self, table_element: WebElement, driver) -> Dict[str, bool]:
        """
        Check if table has row selection (checkbox or radio)
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            Dictionary with 'checkbox' and 'radio' boolean values
        """
        try:
            script = """
            var table = arguments[0];
            var hasCheckbox = table.querySelector('input[type="checkbox"]') !== null;
            var hasRadio = table.querySelector('input[type="radio"]') !== null;
            return {checkbox: hasCheckbox, radio: hasRadio};
            """
            
            result = driver.execute_script(script, table_element)
            return result or {'checkbox': False, 'radio': False}
        except Exception as e:
            print(f"   >> Error checking row selection: {str(e)}")
            return {'checkbox': False, 'radio': False}
    
    def has_pagination(self, table_element: WebElement, driver) -> bool:
        """
        Check if table has pagination
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            True if pagination exists, False otherwise
        """
        try:
            script = """
            var table = arguments[0];
            var pagination = table.closest('.ant-table-wrapper')?.querySelector('.ant-pagination');
            return pagination !== null;
            """
            
            result = driver.execute_script(script, table_element)
            return result or False
        except Exception as e:
            print(f"   >> Error checking pagination: {str(e)}")
            return False
    
    def has_expandable_rows(self, table_element: WebElement, driver) -> bool:
        """
        Check if table has expandable rows
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            True if expandable rows exist, False otherwise
        """
        try:
            script = """
            var table = arguments[0];
            var expandIcon = table.querySelector('.ant-table-row-expand-icon');
            return expandIcon !== null;
            """
            
            result = driver.execute_script(script, table_element)
            return result or False
        except Exception as e:
            print(f"   >> Error checking expandable rows: {str(e)}")
            return False
    
    def get_empty_state(self, table_element: WebElement, driver) -> Optional[str]:
        """
        Get empty state message if table is empty
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            Empty state message text or None
        """
        try:
            script = """
            var table = arguments[0];
            var emptyState = table.querySelector('.ant-empty, .ant-table-placeholder');
            if (emptyState) {
                return emptyState.textContent.trim();
            }
            return null;
            """
            
            result = driver.execute_script(script, table_element)
            return result
        except Exception as e:
            print(f"   >> Error getting empty state: {str(e)}")
            return None
    
    def get_loading_state(self, table_element: WebElement, driver) -> bool:
        """
        Check if table is in loading state
        
        Args:
            table_element: Table WebElement
            driver: WebDriver instance
            
        Returns:
            True if loading, False otherwise
        """
        try:
            script = """
            var table = arguments[0];
            var loading = table.querySelector('.ant-spin, .ant-table-loading');
            return loading !== null;
            """
            
            result = driver.execute_script(script, table_element)
            return result or False
        except Exception as e:
            print(f"   >> Error checking loading state: {str(e)}")
            return False

