"""
Table Locator - Handles finding and locating Ant Design tables
Single Responsibility: Locate tables by various criteria without hardcoded selectors in tests
Detection relies ONLY on Ant Design table classes and optional data-attr-id attributes.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Optional, List, Dict
from framework.base.base_page import BasePage
from framework.context.element_context import ElementContext, ElementInfo
from framework.utils.pattern_discovery import PatternDiscovery


class TableLocator(BasePage):
    """
    Handles locating/finding Ant Design tables on the page.
    Detection rules (as requested):
      - Ant Design class patterns ONLY:
        * ant-table
        * ant-table-thead
        * ant-table-tbody
        * ant-table-row
        * ant-table-cell
        * ant-table-column-sort
        * ant-table-selection-column
        * ant-table-expanded-row
      - Optional enhancer: data-attr-id / data-atr-id
    No manual XPath/CSS selectors in feature files – all discovery is automatic here.
    """
    
    def __init__(self, driver: webdriver):
        """
        Initialize Table Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.pattern_discovery = PatternDiscovery(driver)
    
    def find_table_by_data_attr(self, data_attr_id: str, timeout: int = 10, 
                                 context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find table by custom data-atr-id or data-attr-id attribute
        
        Args:
            data_attr_id: Value of data-atr-id or data-attr-id attribute
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            # Try data-atr-id first
            element = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"]', timeout)
            if element and context:
                self._store_element_in_context(element, data_attr_id, context)
                return element
        except TimeoutException:
            pass
        
        # Try data-attr-id as fallback
        try:
            element = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
            if element and context:
                self._store_element_in_context(element, data_attr_id, context)
            return element
        except TimeoutException:
            return None
    
    def _find_ant_design_tables_by_structure(self, timeout: int = 10) -> List[WebElement]:
        """
        Find Ant Design tables by analyzing DOM structure.
        STRICTLY uses Ant Design class patterns, no generic role/tag scanning.
        Only finds TOP-LEVEL table wrappers to avoid nested duplicates.
        """
        tables = []
        seen_ids = set()
        
        try:
            # Use JavaScript to find only top-level table wrappers
            # This avoids finding nested table cells/rows as separate tables
            script = """
            var tables = [];
            var wrappers = document.querySelectorAll('.ant-table-wrapper, .ant-table-container');
            
            for (var i = 0; i < wrappers.length; i++) {
                var wrapper = wrappers[i];
                
                // Check if it has table structure (thead or tbody)
                var hasThead = wrapper.querySelector('.ant-table-thead, thead');
                var hasTbody = wrapper.querySelector('.ant-table-tbody, tbody');
                
                if (!hasThead && !hasTbody) continue;
                
                // Check if this wrapper is NOT nested inside another wrapper
                var isNested = false;
                for (var j = 0; j < i; j++) {
                    if (wrappers[j].contains(wrapper)) {
                        isNested = true;
                        break;
                    }
                }
                
                if (!isNested) {
                    tables.push(wrapper);
                }
            }
            
            // If no wrappers found, try finding .ant-table directly (but only top-level)
            if (tables.length === 0) {
                var antTables = document.querySelectorAll('.ant-table');
                for (var i = 0; i < antTables.length; i++) {
                    var table = antTables[i];
                    var hasThead = table.querySelector('.ant-table-thead, thead');
                    var hasTbody = table.querySelector('.ant-table-tbody, tbody');
                    
                    if (hasThead || hasTbody) {
                        // Check if not nested
                        var isNested = false;
                        for (var j = 0; j < i; j++) {
                            if (antTables[j].contains(table)) {
                                isNested = true;
                                break;
                            }
                        }
                        if (!isNested) {
                            tables.push(table);
                        }
                    }
                }
            }
            
            return tables;
            """
            
            wrapper_elements = self.driver.execute_script(script)
            
            # Convert JavaScript elements to WebElements
            for wrapper_ref in wrapper_elements:
                try:
                    # Get the actual element
                    wrapper = self.driver.execute_script("return arguments[0];", wrapper_ref)
                    if wrapper:
                        # Verify it's a valid table structure
                        try:
                            has_thead = wrapper.find_elements(By.CSS_SELECTOR, ".ant-table-thead, thead")
                            has_tbody = wrapper.find_elements(By.CSS_SELECTOR, ".ant-table-tbody, tbody")
                            if has_thead or has_tbody:
                                elem_id = id(wrapper)
                                if elem_id not in seen_ids:
                                    seen_ids.add(elem_id)
                                    tables.append(wrapper)
                        except:
                            continue
                except:
                    continue
                    
        except Exception as e:
            print(f"   >> Error finding tables by structure: {str(e)}")
        
        return tables
    
    def find_table_by_text(self, text: str, timeout: int = 10,
                           context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find table by header text or visible text content.
        Uses only Ant Design table classes and optional data-attr-id.
        
        Args:
            text: Text to search for (e.g., column header name)
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        # Strategy 1: Scan already-discovered Ant Design tables for matching text
        try:
            all_tables = self.find_all_tables(timeout, context=None)
            text_lower = text.lower()

            for table in all_tables:
                try:
                    # Look at headers and cells inside this table only
                    header_elems = table.find_elements(
                        By.CSS_SELECTOR,
                        ".ant-table-thead .ant-table-cell, .ant-table-thead th",
                    )
                    cell_elems = table.find_elements(
                        By.CSS_SELECTOR,
                        ".ant-table-tbody .ant-table-cell, .ant-table-tbody td",
                    )

                    found = False
                    for h in header_elems:
                        if text_lower in (h.text or "").lower():
                            found = True
                            break
                    if not found:
                        for c in cell_elems:
                            if text_lower in (c.text or "").lower():
                                found = True
                                break

                    if found:
                        if context:
                            self._store_element_in_context(table, text, context)
                        return table
                except Exception:
                    continue
        except Exception:
            pass

        # Strategy 2: Try data-attr-id pattern discovery
        try:
            normalized_text = text.lower().replace(' ', '-').replace('_', '-')
            matching_attr_id = self.pattern_discovery.find_matching_data_attr_id(normalized_text, 'table')
            if matching_attr_id:
                element = self.find_table_by_data_attr(matching_attr_id, timeout=3, context=context)
                if element:
                    print(f"   >> Found table using pattern discovery: {matching_attr_id}")
                    return element
            
            # Generate candidates
            candidates = self.pattern_discovery.generate_candidates(normalized_text, 'table')
            for candidate in candidates:
                try:
                    element = self.find_table_by_data_attr(candidate, timeout=2, context=context)
                    if element:
                        print(f"   >> Found table using pattern candidate: {candidate}")
                        return element
                except:
                    continue
        except:
            pass
        
        return None
    
    def find_all_tables(self, timeout: int = 10, 
                       context: Optional[ElementContext] = None) -> List[WebElement]:
        """
        Find all Ant Design tables on the page using allowed strategies only:
          - Ant Design class patterns (ant-table*, ant-table-thead/tbody/row/cell/...)
          - Optional data-attr-id pattern discovery
        
        Args:
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store found elements
            
        Returns:
            List of all table WebElements found
        """
        all_tables: List[WebElement] = []
        seen_ids = set()

        # Strategy 1: Find by Ant Design structure/classes
        structure_tables = self._find_ant_design_tables_by_structure(timeout)
        for table in structure_tables:
            elem_id = id(table)
            if elem_id not in seen_ids:
                seen_ids.add(elem_id)
                all_tables.append(table)
                if context:
                    self._store_element_in_context(table, f"table_{len(all_tables)}", context)
                    # Print table title when found
                    try:
                        from framework.components.table_identifier import TableIdentifier
                        identifier = TableIdentifier()
                        title = identifier.get_table_title(table, self.driver)
                        if title:
                            print(f"   >> Table {len(all_tables)}: '{title}'")
                    except:
                        pass

        # Strategy 2: Find by data-attr-id pattern discovery (ANT-only enhancer)
        try:
            patterns = self.pattern_discovery.discover_all_data_attr_ids(timeout)
            table_patterns = patterns.get('table', [])
            for pattern_id in table_patterns:
                table = self.find_table_by_data_attr(pattern_id, timeout=2, context=context)
                if table:
                    elem_id = id(table)
                    if elem_id not in seen_ids:
                        seen_ids.add(elem_id)
                        all_tables.append(table)
        except:
            pass
        
        return all_tables
    
    def find_table_by_index(self, index: int, timeout: int = 10,
                            context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find table by its index (first table = 0, second = 1, etc.)
        
        Args:
            index: Zero-based index of the table
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        all_tables = self.find_all_tables(timeout, context)
        if 0 <= index < len(all_tables):
            return all_tables[index]
        return None
    
    def _store_element_in_context(self, element: WebElement, key: str, 
                                  context: ElementContext):
        """
        Store element in context
        
        Args:
            element: WebElement to store
            key: Key to use in context
            context: ElementContext instance
        """
        try:
            # Store basic information about the table.
            # We do NOT use an 'identifier' field because ElementInfo does not define it.
            element_info = ElementInfo(
                element=element,
                element_type='table',
                data_attr_id=key,
                metadata={'key': key}
            )
            context.store_element(key, element_info)
        except Exception as e:
            print(f"   >> Error storing element in context: {str(e)}")

