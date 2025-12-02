"""
Dropdown Locator - Handles finding and locating Ant Design dropdown/Select fields
Single Responsibility: Locate dropdowns by various criteria without hardcoded selectors
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Optional, List
from framework.base.base_page import BasePage
from framework.context.element_context import ElementContext, ElementInfo
from framework.components.dropdown_identifier import DropdownIdentifier


class DropdownLocator(BasePage):
    """
    Handles locating/finding Ant Design dropdown/Select fields on the page
    Single Responsibility: Find dropdowns by various identification methods
    Uses Ant Design class patterns, data-attr-id, aria attributes, and semantic labels
    """
    
    def __init__(self, driver: webdriver):
        """
        Initialize Dropdown Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.identifier = DropdownIdentifier()
    
    def find_dropdown_by_data_attr(self, data_attr_id: str, timeout: int = 10,
                                    context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find dropdown by custom data-atr-id attribute
        PRIORITY: This is the primary method for finding dropdowns
        
        Args:
            data_attr_id: Value of data-atr-id attribute
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            # Try to find by data-atr-id directly on select/dropdown element or parent container
            element = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"].ant-select', timeout)
            if not element:
                element = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"].ant-dropdown-trigger', timeout)
            if not element:
                # Try finding parent container with data-atr-id
                element = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"] .ant-select', timeout)
            if not element:
                element = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"] .ant-dropdown-trigger', timeout)
            if not element:
                # Try finding any element with data-atr-id and check if it contains ant-select or ant-dropdown
                candidates = self.find_elements(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"]', timeout)
                for candidate in candidates:
                    class_attr = candidate.get_attribute('class') or ''
                    if 'ant-select' in class_attr or 'ant-dropdown' in class_attr:
                        element = candidate
                        break
                    # Check if candidate contains ant-select or ant-dropdown
                    try:
                        select_elem = candidate.find_element(By.CSS_SELECTOR, '.ant-select, .ant-dropdown-trigger')
                        element = select_elem
                        break
                    except:
                        pass
            
            if element and context:
                self._store_element_in_context(element, data_attr_id, context)
            return element
        except TimeoutException:
            return None
    
    def find_dropdown_by_semantic_label(self, label_text: str, timeout: int = 10,
                                        context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find dropdown by semantic label (no quotes needed in feature files)
        Tries multiple strategies: data-attr-id first, then label, aria-label, placeholder
        
        Args:
            label_text: Label text to search for (e.g., "Country", "Role")
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        # Strategy 1: Try data-attr-id first (normalize label to data-attr-id format)
        data_attr_candidates = [
            label_text.lower().replace(' ', '-'),
            label_text.lower().replace(' ', '_'),
            label_text.lower().replace(' ', ''),
        ]
        
        for candidate in data_attr_candidates:
            try:
                element = self.find_dropdown_by_data_attr(candidate, timeout=2, context=context)
                if element:
                    return element
            except:
                pass
        
        # Strategy 2: Use existing label matching
        return self.find_dropdown_by_label(label_text, exact_match=False, timeout=timeout, context=context)
    
    def find_dropdown_by_label(self, label_text: str, exact_match: bool = False,
                               timeout: int = 10, context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find dropdown by label text (semantic matching)
        Uses aria-label, associated label element, Form.Item label, or text content (for Dropdown menu components)
        
        Args:
            label_text: Label text to search for
            exact_match: If True, match exact text; if False, partial/fuzzy match
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        element = None
        try:
            # Strategy 1: Find by aria-label
            try:
                if exact_match:
                    element = self.find_element(By.CSS_SELECTOR, f'.ant-select[aria-label="{label_text}"]', timeout=2)
                else:
                    # Find all dropdowns and check aria-label
                    all_dropdowns = self.find_all_ant_dropdowns(timeout=timeout)
                    for dd in all_dropdowns:
                        aria_label = dd.get_attribute('aria-label') or ''
                        if label_text.lower() in aria_label.lower():
                            element = dd
                            break
                if element and context:
                    self._store_element_in_context(element, label_text, context)
                if element:
                    return element
            except:
                pass
            
            # Strategy 1.5: Find by text content (for Dropdown menu components like "Hover me", "Click me")
            try:
                all_dropdowns = self.find_all_ant_dropdowns(timeout=timeout)
                for dd in all_dropdowns:
                    try:
                        text = dd.text.strip()
                        if exact_match:
                            if text == label_text:
                                element = dd
                                break
                        else:
                            if label_text.lower() in text.lower() or text.lower() in label_text.lower():
                                element = dd
                                break
                    except:
                        pass
                if element and context:
                    self._store_element_in_context(element, label_text, context)
                if element:
                    return element
            except:
                pass
            
            # Strategy 2: Find by associated label element (Form.Item label)
            try:
                # Find label element with text
                if exact_match:
                    label_xpath = f"//label[text()='{label_text}']"
                else:
                    label_xpath = f"//label[contains(text(), '{label_text}')]"
                
                label_elem = self.find_element(By.XPATH, label_xpath, timeout=3)
                if label_elem:
                    # Find associated dropdown (could be sibling or in same Form.Item)
                    # Try to find ant-select near the label
                    try:
                        # Check if label has for attribute
                        for_attr = label_elem.get_attribute('for')
                        if for_attr:
                            element = self.find_element(By.ID, for_attr, timeout=2)
                            if element and 'ant-select' in (element.get_attribute('class') or ''):
                                if context:
                                    self._store_element_in_context(element, label_text, context)
                                return element
                    except:
                        pass
                    
                    # Find ant-select in same parent container
                    try:
                        parent = label_elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'ant-form-item')]")
                        element = parent.find_element(By.CSS_SELECTOR, '.ant-select')
                        if element and context:
                            self._store_element_in_context(element, label_text, context)
                        return element
                    except:
                        pass
            except:
                pass
            
            # Strategy 3: Find by placeholder (some dropdowns use placeholder)
            try:
                all_dropdowns = self.find_all_ant_dropdowns(timeout=timeout)
                for dd in all_dropdowns:
                    # Get placeholder from selector element
                    try:
                        selector = dd.find_element(By.CSS_SELECTOR, '.ant-select-selector')
                        placeholder = selector.get_attribute('placeholder') or ''
                        if label_text.lower() in placeholder.lower():
                            if context:
                                self._store_element_in_context(dd, label_text, context)
                            return dd
                    except:
                        pass
            except:
                pass
            
            return None
        except TimeoutException:
            return None
    
    def find_dropdown_by_type(self, dropdown_type: str, timeout: int = 10,
                               context: Optional[ElementContext] = None) -> List[WebElement]:
        """
        Find all dropdowns of a specific type
        
        Args:
            dropdown_type: Type of dropdown ('single', 'multiple', 'tags', 'searchable', 'tree', 'cascader')
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found elements
            
        Returns:
            List of WebElements matching the type
        """
        try:
            all_dropdowns = self.find_all_ant_dropdowns(timeout=timeout)
            typed_dropdowns = []
            
            for dd in all_dropdowns:
                dd_info = self.identifier.identify_dropdown_type(dd)
                if dd_info.get('type') == dropdown_type:
                    typed_dropdowns.append(dd)
                    if context and len(typed_dropdowns) == 1:
                        # Store first element
                        data_attr_id = dd_info.get('data_attr_id')
                        key = data_attr_id or dropdown_type
                        self._store_element_in_context(dd, key, context)
            
            return typed_dropdowns
        except TimeoutException:
            return []
    
    def find_dropdown_by_position(self, position: int, timeout: int = 10,
                                   context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find dropdown by position/index (1-based)
        
        Args:
            position: Position/index (1-based)
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            all_dropdowns = self.find_all_ant_dropdowns(timeout=timeout)
            if 1 <= position <= len(all_dropdowns):
                element = all_dropdowns[position - 1]
                if context:
                    dd_info = self.identifier.identify_dropdown_type(element)
                    data_attr_id = dd_info.get('data_attr_id')
                    # Use position as key for easier context access
                    key = data_attr_id or str(position)
                    self._store_element_in_context(element, key, context)
                return element
            return None
        except TimeoutException:
            return None
    
    def find_all_ant_dropdowns(self, timeout: int = 10, include_all: bool = False) -> List[WebElement]:
        """
        Find all Ant Design dropdown/Select fields on the page
        Includes both Select components (.ant-select) and Dropdown components (.ant-dropdown-trigger)
        Uses comprehensive JavaScript-based detection for better coverage
        
        Args:
            timeout: Maximum wait time in seconds
            include_all: If True, includes ALL selects (not just Ant Design)
            
        Returns:
            List of all dropdown WebElements
        """
        try:
            import time
            # Scroll page to load dynamic content
            self.execute_js("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
            # Use comprehensive JavaScript to find ALL dropdown elements
            js_result = self.execute_js("""
                var allElements = [];
                var seenIds = new Set();
                
                // Function to check if element is visible
                function isVisible(el) {
                    if (!el) return false;
                    var style = window.getComputedStyle(el);
                    if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
                        return false;
                    }
                    if (el.offsetParent === null && el.tagName !== 'BODY') {
                        return false;
                    }
                    return true;
                }
                
                // Function to add element if not duplicate
                function addElement(el) {
                    if (!el || !isVisible(el)) return;
                    var elId = el.id || el.className || el.tagName + el.textContent.substring(0, 20);
                    if (seenIds.has(elId)) return;
                    seenIds.add(elId);
                    allElements.push(el);
                }
                
                // 1. Find native select elements
                document.querySelectorAll('select').forEach(function(el) {
                    addElement(el);
                });
                
                // 2. Find Ant Design Select components (.ant-select)
                document.querySelectorAll('.ant-select').forEach(function(el) {
                    addElement(el);
                });
                
                // 3. Find Ant Design Dropdown triggers (all variations)
                var dropdownSelectors = [
                    '.ant-dropdown-trigger',
                    '[class*="ant-dropdown-trigger"]',
                    'a[class*="ant-dropdown"]',
                    'button[class*="ant-dropdown"]',
                    'span[class*="ant-dropdown"]',
                    'div[class*="ant-dropdown"]',
                    '[aria-haspopup="menu"]',
                    '[role="button"][class*="dropdown"]'
                ];
                
                dropdownSelectors.forEach(function(selector) {
                    try {
                        document.querySelectorAll(selector).forEach(function(el) {
                            addElement(el);
                        });
                    } catch(e) {}
                });
                
                // 4. Find elements with dropdown-related aria attributes
                document.querySelectorAll('[aria-haspopup="menu"], [aria-haspopup="listbox"]').forEach(function(el) {
                    if (el.className && (el.className.includes('ant-') || el.className.includes('dropdown'))) {
                        addElement(el);
                    }
                });
                
                // 5. Find elements by data attributes that might indicate dropdowns
                document.querySelectorAll('[data-atr-id], [data-attr-id]').forEach(function(el) {
                    var classAttr = el.className || '';
                    if (classAttr.includes('ant-select') || classAttr.includes('ant-dropdown') || 
                        classAttr.includes('dropdown') || el.tagName === 'SELECT') {
                        addElement(el);
                    }
                });
                
                // Return array of elements (JavaScript will convert to node list)
                return Array.from(allElements);
            """)
            
            # Convert JavaScript elements to Selenium WebElements
            elements = []
            if js_result:
                # Get all unique selectors and find elements using Selenium
                all_selectors = [
                    'select',
                    '.ant-select',
                    '.ant-dropdown-trigger',
                    '[class*="ant-dropdown-trigger"]',
                    'a[class*="ant-dropdown"]',
                    'button[class*="ant-dropdown"]',
                    'span[class*="ant-dropdown"]',
                    'div[class*="ant-dropdown"]',
                    '[aria-haspopup="menu"]',
                    '[aria-haspopup="listbox"]',
                    '[role="button"][class*="dropdown"]'
                ]
                
                seen_elements = set()
                for selector in all_selectors:
                    try:
                        found_elements = self.find_elements(By.CSS_SELECTOR, selector, timeout=3)
                        for elem in found_elements:
                            try:
                                # Use element ID or location as unique identifier
                                elem_id = elem.id or f"{elem.tag_name}_{elem.location['x']}_{elem.location['y']}"
                                if elem_id not in seen_elements:
                                    # Check if element is actually visible
                                    try:
                                        if elem.is_displayed() or elem.size.get('height', 0) > 0:
                                            seen_elements.add(elem_id)
                                            elements.append(elem)
                                    except:
                                        # If is_displayed fails, try to add anyway
                                        seen_elements.add(elem_id)
                                        elements.append(elem)
                            except:
                                pass
                    except:
                        pass
            
            # Additional fallback: Use Selenium directly if JavaScript didn't find enough
            if len(elements) < 5 and include_all:
                # Try native select elements
                try:
                    selects = self.find_elements(By.TAG_NAME, 'select', timeout=3)
                    for sel in selects:
                        if sel not in elements:
                            elements.append(sel)
                except:
                    pass
                
                # Try Ant Design Select
                try:
                    ant_selects = self.find_elements(By.CSS_SELECTOR, '.ant-select', timeout=3)
                    for sel in ant_selects:
                        if sel not in elements:
                            elements.append(sel)
                except:
                    pass
                
                # Try all dropdown trigger variations
                dropdown_selectors = [
                    'a.ant-dropdown-trigger',
                    'button.ant-dropdown-trigger',
                    'span.ant-dropdown-trigger',
                    'div.ant-dropdown-trigger',
                    '[class*="ant-dropdown-trigger"]'
                ]
                for selector in dropdown_selectors:
                    try:
                        found = self.find_elements(By.CSS_SELECTOR, selector, timeout=2)
                        for elem in found:
                            if elem not in elements:
                                elements.append(elem)
                    except:
                        pass
            
            # Remove duplicates more reliably using element comparison
            unique_elements = []
            seen = set()
            for elem in elements:
                try:
                    # Create unique identifier
                    elem_id = elem.id
                    if not elem_id:
                        try:
                            location = elem.location
                            size = elem.size
                            elem_id = f"{elem.tag_name}_{location['x']}_{location['y']}_{size['width']}_{size['height']}"
                        except:
                            try:
                                elem_id = f"{elem.tag_name}_{elem.text[:20]}"
                            except:
                                elem_id = str(hash(str(elem)))
                    
                    if elem_id not in seen:
                        seen.add(elem_id)
                        unique_elements.append(elem)
                except:
                    # If we can't create ID, add anyway (might be unique)
                    unique_elements.append(elem)
            
            return unique_elements
            
        except Exception as e:
            print(f"Error finding dropdowns: {str(e)}")
            return []
    
    def _store_element_in_context(self, element: WebElement, key: str, context: ElementContext) -> None:
        """
        Store a dropdown element in the context after identifying it
        
        Args:
            element: WebElement to store
            key: Key to use for storing in context
            context: ElementContext to store the element
        """
        try:
            # Identify dropdown properties
            dropdown_info = self.identifier.identify_dropdown_type(element)
            
            # Create ElementInfo
            element_info = ElementInfo(
                element=element,
                element_type='dropdown',
                application_type=dropdown_info.get('application_type'),
                data_attr_id=dropdown_info.get('data_attr_id') or key if key.startswith('data_attr_') else None,
                metadata={
                    'type': dropdown_info.get('type'),
                    'size': dropdown_info.get('size'),
                    'disabled': dropdown_info.get('disabled'),
                    'loading': dropdown_info.get('loading'),
                    'placeholder': dropdown_info.get('placeholder'),
                    'label': dropdown_info.get('label'),
                    'searchable': dropdown_info.get('searchable'),
                    'selected_values': dropdown_info.get('selected_values'),
                    'options_count': dropdown_info.get('options_count'),
                    'available_options': dropdown_info.get('available_options'),
                    **dropdown_info.get('metadata', {})
                }
            )
            
            # Use data_attr_id as key if available, otherwise use provided key
            context_key = dropdown_info.get('data_attr_id') or key
            context.store_element(context_key, element_info)
        except Exception as e:
            print(f"Error storing dropdown in context: {str(e)}")

