"""
TreeSelect Locator - Handles finding and locating TreeSelect components
Single Responsibility: Locate TreeSelect components by various criteria using locator-less detection
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Optional, List
from framework.base.base_page import BasePage
from framework.context.element_context import ElementContext, ElementInfo
from framework.components.treeselect_identifier import TreeSelectIdentifier
from framework.utils.pattern_discovery import PatternDiscovery


class TreeSelectLocator(BasePage):
    """
    Handles locating/finding Ant Design TreeSelect components on the page
    Single Responsibility: Find TreeSelect components by various identification methods
    Uses locator-less detection based on Ant Design classes, ARIA attributes, and data-attr-id
    """
    
    def __init__(self, driver: webdriver):
        """
        Initialize TreeSelect Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.identifier = TreeSelectIdentifier()
        self.pattern_discovery = PatternDiscovery(driver)
    
    def find_treeselect_by_data_attr(self, data_attr_id: str, timeout: int = 10,
                                      context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find TreeSelect by custom data-attr-id or data-atr-id attribute
        Automatically stores element in context if context is provided
        
        Args:
            data_attr_id: Value of data-attr-id or data-atr-id attribute
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            # Try data-attr-id first
            element = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
            if element and self._is_treeselect(element):
                if context:
                    self._store_element_in_context(element, data_attr_id, context)
                return element
        except TimeoutException:
            pass
        
        # Try data-atr-id as fallback
        try:
            element = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"]', timeout)
            if element and self._is_treeselect(element):
                if context:
                    self._store_element_in_context(element, data_attr_id, context)
                return element
        except TimeoutException:
            pass
        
        return None
    
    def find_treeselect_by_label(self, label: str, exact_match: bool = False, timeout: int = 10,
                                  context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find TreeSelect by label text or placeholder
        Automatically discovers data-attr-id patterns if text search fails
        Automatically stores element in context if context is provided
        
        Args:
            label: Label text or placeholder to search for
            exact_match: If True, match exact text; if False, partial match
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        element = None
        
        # Strategy 1: Try label-based search
        try:
            if exact_match:
                xpath = f"//label[normalize-space(text())='{label}']/following-sibling::*[contains(@class, 'ant-select')] | " \
                        f"//*[contains(@class, 'ant-select')][preceding-sibling::label[normalize-space(text())='{label}']]"
            else:
                xpath = f"//label[contains(text(), '{label}')]/following-sibling::*[contains(@class, 'ant-select')] | " \
                        f"//*[contains(@class, 'ant-select')][preceding-sibling::label[contains(text(), '{label}')]]"
            
            element = self.find_element(By.XPATH, xpath, timeout)
            if element and self._is_treeselect(element):
                if context:
                    key = self._generate_context_key(element, label)
                    self._store_element_in_context(element, key, context)
                return element
        except TimeoutException:
            pass
        
        # Strategy 2: Try placeholder-based search
        try:
            xpath = f"//*[contains(@class, 'ant-select')]//*[contains(@class, 'ant-select-selection-placeholder') and contains(text(), '{label}')]"
            placeholder_elem = self.find_element(By.XPATH, xpath, timeout)
            if placeholder_elem:
                # Get parent TreeSelect
                element = placeholder_elem.find_element(By.XPATH, "./ancestor::*[contains(@class, 'ant-select')][1]")
                if element and self._is_treeselect(element):
                    if context:
                        key = self._generate_context_key(element, label)
                        self._store_element_in_context(element, key, context)
                    return element
        except TimeoutException:
            pass
        
        # Strategy 3: Try pattern discovery
        try:
            normalized_label = label.lower().replace(' ', '-').replace('_', '-')
            matching_attr_id = self.pattern_discovery.find_matching_data_attr_id(normalized_label, 'treeselect')
            if matching_attr_id:
                element = self.find_treeselect_by_data_attr(matching_attr_id, timeout=3, context=context)
                if element:
                    print(f"   >> Found TreeSelect using pattern discovery: {matching_attr_id}")
                    return element
            
            # Generate candidates
            candidates = self.pattern_discovery.generate_candidates(normalized_label, 'treeselect')
            for candidate in candidates:
                try:
                    element = self.find_treeselect_by_data_attr(candidate, timeout=2, context=context)
                    if element:
                        print(f"   >> Found TreeSelect using pattern candidate: {candidate}")
                        return element
                except:
                    continue
        except:
            pass
        
        return None
    
    def find_treeselect_by_aria_label(self, aria_label: str, timeout: int = 10,
                                       context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find TreeSelect by aria-label attribute
        
        Args:
            aria_label: Value of aria-label attribute
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            element = self.find_element(By.CSS_SELECTOR, f'[aria-label="{aria_label}"].ant-select, .ant-select[aria-label="{aria_label}"]', timeout)
            if element and self._is_treeselect(element):
                if context:
                    self._store_element_in_context(element, aria_label, context)
                return element
        except TimeoutException:
            pass
        
        return None
    
    def find_treeselect_by_position(self, position: int = 1, timeout: int = 10,
                                     context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find TreeSelect by position (first, second, etc.)
        
        Args:
            position: Position index (1-based)
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            elements = self.find_all_treeselects(timeout)
            if elements and len(elements) >= position:
                element = elements[position - 1]
                if context:
                    key = f"treeselect_position_{position}"
                    self._store_element_in_context(element, key, context)
                return element
        except:
            pass
        
        return None
    
    def find_all_treeselects(self, timeout: int = 10) -> List[WebElement]:
        """
        Find all Ant Design TreeSelect components on the page
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            List of all Ant Design TreeSelect WebElements
        """
        treeselects = []
        
        try:
            # Strategy 1: Find by specific TreeSelect classes
            try:
                elements = self.find_elements(By.CSS_SELECTOR, '.ant-select-tree-select, .ant-select.ant-select-tree-select', timeout)
                treeselects.extend([el for el in elements if self._is_treeselect(el)])
            except:
                pass
            
            # Strategy 2: Find all ant-select elements and check if they're TreeSelects
            try:
                all_selects = self.find_elements(By.CSS_SELECTOR, '.ant-select, [class*="ant-select"]', timeout)
                for select in all_selects:
                    if self._is_treeselect(select) and select not in treeselects:
                        treeselects.append(select)
            except:
                pass
            
            # Strategy 3: Use JavaScript to find TreeSelects more reliably
            try:
                js_code = """
                (function() {
                    var treeselects = [];
                    // Find all elements with ant-select class
                    var selects = document.querySelectorAll('.ant-select, [class*="ant-select"]');
                    for (var i = 0; i < selects.length; i++) {
                        var select = selects[i];
                        var classAttr = select.className || '';
                        // Check if it's a TreeSelect (has tree-related classes or tree structure)
                        if (classAttr.indexOf('ant-select-tree') !== -1 || 
                            classAttr.indexOf('tree-select') !== -1 ||
                            select.querySelector('.ant-tree') !== null ||
                            select.querySelector('.ant-select-tree') !== null) {
                            treeselects.push(select);
                        }
                    }
                    return treeselects;
                })();
                """
                js_elements = self.driver.execute_script(js_code)
                if js_elements:
                    # Convert to WebElements
                    for idx, js_elem in enumerate(js_elements):
                        try:
                            # Try to find the element again using its attributes
                            elem_id = js_elem.get('id', '')
                            elem_class = js_elem.get('className', '')
                            if elem_id:
                                try:
                                    elem = self.driver.find_element(By.ID, elem_id)
                                    if elem not in treeselects and self._is_treeselect(elem):
                                        treeselects.append(elem)
                                except:
                                    pass
                        except:
                            pass
            except:
                pass
            
            # Strategy 4: Look for elements that might contain TreeSelect (wrappers)
            try:
                # Look for code examples or demo containers that might have TreeSelects
                demo_containers = self.find_elements(By.CSS_SELECTOR, '.code-box-demo, .ant-row, [class*="demo"], [class*="example"]', timeout=2)
                for container in demo_containers:
                    try:
                        nested_selects = container.find_elements(By.CSS_SELECTOR, '.ant-select, [class*="ant-select"]')
                        for select in nested_selects:
                            if self._is_treeselect(select) and select not in treeselects:
                                treeselects.append(select)
                    except:
                        continue
            except:
                pass
            
            # Remove duplicates while preserving order
            seen = set()
            unique_treeselects = []
            for ts in treeselects:
                try:
                    # Use element's id or a combination of attributes as unique identifier
                    elem_id = id(ts) if hasattr(ts, '__hash__') else None
                    if elem_id and elem_id not in seen:
                        seen.add(elem_id)
                        unique_treeselects.append(ts)
                    elif not elem_id:
                        # Fallback: check by location
                        location = ts.location
                        loc_key = f"{location['x']}_{location['y']}"
                        if loc_key not in seen:
                            seen.add(loc_key)
                            unique_treeselects.append(ts)
                except:
                    # If we can't identify uniquely, just add it
                    unique_treeselects.append(ts)
            
            return unique_treeselects
            
        except Exception as e:
            print(f"   >> Error finding TreeSelects: {str(e)}")
            return []
    
    def _is_treeselect(self, element: WebElement) -> bool:
        """
        Check if an element is a TreeSelect component
        
        Args:
            element: WebElement to check
            
        Returns:
            True if element is a TreeSelect, False otherwise
        """
        try:
            class_attr = element.get_attribute('class') or ''
            
            # Check for TreeSelect-specific classes
            if ('ant-select-tree-select' in class_attr or 
                'ant-select-tree' in class_attr or
                'tree-select' in class_attr.lower()):
                return True
            
            # Check for tree structure inside the element
            try:
                tree = element.find_element(By.CSS_SELECTOR, '.ant-tree, .ant-select-tree')
                if tree:
                    return True
            except:
                pass
            
            # Check if element contains tree nodes (even if dropdown is closed)
            try:
                # Look for any tree-related structure
                has_tree_structure = False
                
                # Check innerHTML for tree-related classes
                inner_html = element.get_attribute('innerHTML') or ''
                if ('ant-tree' in inner_html or 
                    'ant-select-tree' in inner_html or
                    'tree-node' in inner_html.lower()):
                    has_tree_structure = True
                
                # Also check if there's a dropdown that might contain tree
                try:
                    # Check for dropdown trigger that might open to show tree
                    selector = element.find_element(By.CSS_SELECTOR, '.ant-select-selector, .ant-select-selection')
                    if selector:
                        # This looks like a select component, check if it might be TreeSelect
                        # by looking for tree-related data attributes or aria attributes
                        aria_label = element.get_attribute('aria-label') or ''
                        data_attrs = element.get_attribute('data-*') or ''
                        if 'tree' in aria_label.lower() or 'tree' in data_attrs.lower():
                            return True
                except:
                    pass
                
                if has_tree_structure:
                    return True
            except:
                pass
            
            # Use JavaScript to check more thoroughly
            try:
                js_check = self.driver.execute_script("""
                    var elem = arguments[0];
                    var classAttr = elem.className || '';
                    // Check class
                    if (classAttr.indexOf('ant-select-tree') !== -1 || 
                        classAttr.indexOf('tree-select') !== -1) {
                        return true;
                    }
                    // Check for tree structure
                    if (elem.querySelector('.ant-tree') || 
                        elem.querySelector('.ant-select-tree')) {
                        return true;
                    }
                    // Check innerHTML
                    var innerHTML = elem.innerHTML || '';
                    if (innerHTML.indexOf('ant-tree') !== -1 || 
                        innerHTML.indexOf('tree-node') !== -1) {
                        return true;
                    }
                    return false;
                """, element)
                if js_check:
                    return True
            except:
                pass
            
            return False
        except Exception as e:
            # If we can't check, assume it's not a TreeSelect
            return False
    
    def _store_element_in_context(self, element: WebElement, key: str, context: ElementContext) -> None:
        """
        Store an element in the context after identifying it
        
        Args:
            element: WebElement to store
            key: Key to use for storing in context
            context: ElementContext to store the element
        """
        try:
            # Identify TreeSelect properties
            treeselect_info = self.identifier.identify_treeselect_type(element)
            
            # Get data_attr_id from treeselect_info or use key if it's a data-attr-id
            data_attr_id = treeselect_info.get('data_attr_id')
            if not data_attr_id and key and not key.startswith(('treeselect_position_', 'treeselect_')):
                # If key looks like a data-attr-id, use it
                data_attr_id = key
            
            # Create ElementInfo
            element_info = ElementInfo(
                element=element,
                element_type='treeselect',
                application_type=treeselect_info.get('application_type'),
                data_attr_id=data_attr_id,
                metadata={
                    'treeselect_type': treeselect_info.get('type'),
                    'multiple': treeselect_info.get('multiple'),
                    'checkable': treeselect_info.get('checkable'),
                    'disabled': treeselect_info.get('disabled'),
                    'search_enabled': treeselect_info.get('search_enabled'),
                    'placeholder': treeselect_info.get('placeholder'),
                    'size': treeselect_info.get('size'),
                    'placement': treeselect_info.get('placement'),
                    'selected_values': treeselect_info.get('selected_values'),
                    'selected_labels': treeselect_info.get('selected_labels'),
                    'tree_structure': treeselect_info.get('tree_structure'),
                    **treeselect_info.get('metadata', {})
                }
            )
            
            # Use data_attr_id as key if available, otherwise use provided key
            context_key = data_attr_id or key
            context.store_element(context_key, element_info)
        except Exception as e:
            print(f"Error storing element in context: {str(e)}")
    
    def _generate_context_key(self, element: WebElement, fallback: str) -> str:
        """
        Generate a context key for an element
        
        Args:
            element: WebElement to generate key for
            fallback: Fallback key if data-attr-id is not available
            
        Returns:
            Generated key string
        """
        try:
            # Try data-attr-id first
            data_attr_id = element.get_attribute('data-attr-id')
            if not data_attr_id:
                # Try data-atr-id as fallback
                data_attr_id = element.get_attribute('data-atr-id')
            if data_attr_id:
                return data_attr_id
            # Use fallback with element placeholder or label
            try:
                placeholder = element.find_element(By.CSS_SELECTOR, '.ant-select-selection-placeholder')
                text = placeholder.text.strip()[:20] if placeholder.text else fallback
                return f"{fallback}_{text}".replace(' ', '_').lower()
            except:
                return fallback
        except:
            return fallback
