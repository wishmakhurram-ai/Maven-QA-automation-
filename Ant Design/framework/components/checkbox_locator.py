"""
Checkbox Locator - Handles finding and locating Ant Design Checkbox components
Single Responsibility: Locate checkboxes by various criteria without hardcoded selectors
Detection relies ONLY on Ant Design checkbox classes and optional data-attr-id attributes.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Optional, List, Dict
from framework.base.base_page import BasePage
from framework.context.element_context import ElementContext, ElementInfo
from framework.components.checkbox_identifier import CheckboxIdentifier
from framework.utils.pattern_discovery import PatternDiscovery


class CheckboxLocator(BasePage):
    """
    Handles locating/finding Ant Design Checkbox components on the page
    Single Responsibility: Find checkboxes by various identification methods
    Uses Ant Design class patterns, data-attr-id, aria attributes, and semantic labels
    Automatically discovers data-attr-id patterns from the page
    """
    
    def __init__(self, driver: webdriver):
        """
        Initialize Checkbox Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.identifier = CheckboxIdentifier()
        self.pattern_discovery = PatternDiscovery(driver)
    
    def find_checkbox_by_data_attr(self, data_attr_id: str, timeout: int = 10,
                                    context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find checkbox by custom data-atr-id or data-attr-id attribute
        PRIORITY: This is the primary method for finding checkboxes
        
        Args:
            data_attr_id: Value of data-atr-id or data-attr-id attribute
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            # Try data-atr-id first (original attribute name)
            element = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"]', timeout)
            if element and self.identifier.is_checkbox_element(element):
                if context:
                    self._store_element_in_context(element, data_attr_id, context)
                return element
        except TimeoutException:
            pass
        
        # Try data-attr-id as fallback
        try:
            element = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
            if element and self.identifier.is_checkbox_element(element):
                if context:
                    self._store_element_in_context(element, data_attr_id, context)
                return element
        except TimeoutException:
            pass
        
        # Try finding checkbox inside element with data-attr-id
        try:
            wrapper = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"]', timeout)
            if wrapper:
                checkbox = self._find_checkbox_in_container(wrapper)
                if checkbox:
                    if context:
                        self._store_element_in_context(checkbox, data_attr_id, context)
                    return checkbox
        except:
            pass
        
        try:
            wrapper = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
            if wrapper:
                checkbox = self._find_checkbox_in_container(wrapper)
                if checkbox:
                    if context:
                        self._store_element_in_context(checkbox, data_attr_id, context)
                    return checkbox
        except:
            pass
        
        return None
    
    def find_checkbox_by_semantic_label(self, label_text: str, group_name: Optional[str] = None,
                                        timeout: int = 10,
                                        context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find checkbox by semantic label (no quotes needed in feature files)
        Automatically discovers data-attr-id patterns from the page
        Tries multiple strategies: discovered patterns first, then aria-label, associated label, Form.Item context
        
        Args:
            label_text: Label text to search for (e.g., "Accept Terms", "Email Notifications")
            group_name: Optional checkbox group name to narrow search
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        # Strategy 1: Try automatic pattern discovery first
        try:
            matching_attr_id = self.pattern_discovery.find_matching_data_attr_id(label_text, 'checkbox')
            if matching_attr_id:
                element = self.find_checkbox_by_data_attr(matching_attr_id, timeout=3, context=context)
                if element:
                    return element
        except:
            pass
        
        # Strategy 2: Generate candidates based on discovered pattern structure
        try:
            candidates = self.pattern_discovery.generate_candidates(label_text, 'checkbox')
            for candidate in candidates:
                try:
                    element = self.find_checkbox_by_data_attr(candidate, timeout=2, context=context)
                    if element:
                        return element
                except:
                    continue
        except:
            pass
        
        # Strategy 3: If group_name provided, search within that group first
        if group_name:
            group_checkboxes = self.find_checkboxes_in_group(group_name, timeout=timeout)
            for checkbox in group_checkboxes:
                checkbox_info = self.identifier.identify_checkbox_type(checkbox)
                if checkbox_info.get('label_text') and label_text.lower() in checkbox_info['label_text'].lower():
                    if context:
                        self._store_element_in_context(checkbox, label_text, context)
                    return checkbox
        
        # Strategy 4: Try aria-label
        try:
            normalized_label = label_text.lower().strip()
            xpath = f'//input[@type="checkbox" and @aria-label="{label_text}"] | //input[@type="checkbox" and contains(@aria-label, "{label_text}")]'
            elements = self.driver.find_elements(By.XPATH, xpath)
            for element in elements:
                if self.identifier.is_checkbox_element(element):
                    if context:
                        self._store_element_in_context(element, label_text, context)
                    return element
        except:
            pass
        
        # Strategy 5: Find by associated label element (Form.Item context)
        try:
            # Look for label text, then find checkbox nearby
            label_xpath = f'//label[contains(text(), "{label_text}")] | //span[contains(text(), "{label_text}")] | //div[contains(text(), "{label_text}")]'
            labels = self.driver.find_elements(By.XPATH, label_xpath)
            
            for label in labels:
                try:
                    # Find checkbox in same Form.Item or nearby
                    parent = label.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-form-item")]')
                    if parent:
                        checkbox = self._find_checkbox_in_container(parent)
                        if checkbox:
                            if context:
                                self._store_element_in_context(checkbox, label_text, context)
                            return checkbox
                except:
                    # Try finding checkbox after label
                    try:
                        checkbox = label.find_element(By.XPATH, './following::*[contains(@class, "ant-checkbox-wrapper") or contains(@class, "ant-checkbox")][1]')
                        if checkbox and self.identifier.is_checkbox_element(checkbox):
                            if context:
                                self._store_element_in_context(checkbox, label_text, context)
                            return checkbox
                    except:
                        continue
        except:
            pass
        
        # Strategy 6: Fuzzy text match - find checkbox near text
        try:
            # Find all checkboxes and check nearby text
            checkboxes = self.find_all_checkboxes(timeout=3)
            for checkbox in checkboxes:
                try:
                    checkbox_info = self.identifier.identify_checkbox_type(checkbox)
                    checkbox_label = checkbox_info.get('label_text', '').lower()
                    if normalized_label in checkbox_label or label_text.lower() in checkbox_label:
                        if context:
                            self._store_element_in_context(checkbox, label_text, context)
                        return checkbox
                except:
                    continue
        except:
            pass
        
        return None
    
    def find_checkbox_group_by_name(self, group_name: str, timeout: int = 10) -> Optional[WebElement]:
        """
        Find checkbox group by name attribute or semantic label
        
        Args:
            group_name: Group name or label (e.g., "Preferences", "Notifications")
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement of checkbox group if found, None otherwise
        """
        try:
            # Strategy 1: Find by data-attr-id pattern
            try:
                matching_attr_id = self.pattern_discovery.find_matching_data_attr_id(group_name, 'checkbox-group')
                if matching_attr_id:
                    group = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{matching_attr_id}"].ant-checkbox-group, [data-attr-id="{matching_attr_id}"] .ant-checkbox-group', timeout=3)
                    if group:
                        return group
            except:
                pass
            
            # Strategy 2: Find by fieldset or form label
            try:
                # Find label or heading with group name
                label_xpath = f'//label[contains(text(), "{group_name}")] | //legend[contains(text(), "{group_name}")] | //h3[contains(text(), "{group_name}")] | //h4[contains(text(), "{group_name}")]'
                labels = self.driver.find_elements(By.XPATH, label_xpath)
                
                for label in labels:
                    try:
                        # Find checkbox group nearby
                        parent = label.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-form-item") or contains(@class, "ant-checkbox-group")][1]')
                        group = self._find_checkbox_group_in_container(parent)
                        if group:
                            return group
                    except:
                        # Try finding group after label
                        try:
                            group = label.find_element(By.XPATH, './following::*[contains(@class, "ant-checkbox-group")][1]')
                            if group:
                                return group
                        except:
                            continue
            except:
                pass
            
            # Strategy 3: Find by name attribute (if checkboxes share a name)
            try:
                checkboxes = self.driver.find_elements(By.CSS_SELECTOR, f'input[type="checkbox"][name="{group_name}"]')
                if checkboxes:
                    # Get the group container
                    first_checkbox = checkboxes[0]
                    group = self.identifier._find_checkbox_group(first_checkbox)
                    if group:
                        return group
            except:
                pass
            
        except:
            pass
        
        return None
    
    def find_checkboxes_in_group(self, group_name: str, timeout: int = 10) -> List[WebElement]:
        """
        Find all checkboxes in a specific group
        
        Args:
            group_name: Group name or label
            timeout: Maximum wait time in seconds
            
        Returns:
            List of WebElements representing checkboxes in the group
        """
        checkboxes = []
        try:
            group = self.find_checkbox_group_by_name(group_name, timeout)
            if group:
                checkboxes = self._find_all_checkboxes_in_container(group)
        except:
            pass
        return checkboxes
    
    def find_all_checkboxes(self, timeout: int = 10) -> List[WebElement]:
        """
        Find all Ant Design Checkbox components on the page (optimized)
        Uses JavaScript for faster bulk finding
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            List of WebElements representing checkboxes
        """
        checkboxes = []
        seen_elements = set()
        
        import time
        start_time = time.time()
        max_time = 3  # Reduced to 3 seconds for faster execution
        
        # Optimized Strategy: Use JavaScript to find all wrappers at once
        try:
            # Single JavaScript call to find all checkbox wrappers
            wrapper_elements = self.driver.execute_script("""
                var wrappers = document.querySelectorAll('.ant-checkbox-wrapper');
                var result = [];
                for(var i=0; i<wrappers.length; i++){
                    var w = wrappers[i];
                    if(w && w.className && w.className.includes('ant-checkbox-wrapper')){
                        result.push(w);
                    }
                }
                return result;
            """)
            
            # Convert to WebElements (they're already WebElements from execute_script)
            for wrapper in wrapper_elements[:100]:  # Limit to 100 for performance
                if time.time() - start_time > max_time:
                    break
                try:
                    elem_id = id(wrapper)
                    if elem_id not in seen_elements:
                        checkboxes.append(wrapper)
                        seen_elements.add(elem_id)
                except:
                    continue
        except:
            # Fallback to Selenium find_elements
            try:
                wrappers = self.driver.find_elements(By.CSS_SELECTOR, '.ant-checkbox-wrapper')
                for wrapper in wrappers[:100]:  # Limit to 100
                    if time.time() - start_time > max_time:
                        break
                    try:
                        elem_id = id(wrapper)
                        if elem_id not in seen_elements:
                            checkboxes.append(wrapper)
                            seen_elements.add(elem_id)
                    except:
                        continue
            except Exception as e:
                print(f"   >> Error finding checkboxes: {str(e)[:50]}")
        
        print(f"   → Identified {len(checkboxes)} unique checkbox(es)")
        return checkboxes
    
    def find_checkbox_by_position(self, position: int, timeout: int = 10,
                                 context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find checkbox by position/index (1-based)
        
        Args:
            position: Position/index of checkbox (1-based)
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        checkboxes = self.find_all_checkboxes(timeout)
        
        if position > 0 and position <= len(checkboxes):
            element = checkboxes[position - 1]
            if context:
                self._store_element_in_context(element, f'checkbox_{position}', context)
            return element
        
        return None
    
    def find_checkbox_in_group_by_index(self, group_name: str, index: int, timeout: int = 10) -> Optional[WebElement]:
        """
        Find checkbox in a group by index (1-based)
        
        Args:
            group_name: Group name or label
            index: Index within group (1-based)
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement if found, None otherwise
        """
        checkboxes = self.find_checkboxes_in_group(group_name, timeout)
        
        if index > 0 and index <= len(checkboxes):
            return checkboxes[index - 1]
        
        return None
    
    def _find_checkbox_in_container(self, container: WebElement) -> Optional[WebElement]:
        """Find a checkbox element within a container"""
        try:
            # Try to find checkbox wrapper
            try:
                wrapper = container.find_element(By.CSS_SELECTOR, '.ant-checkbox-wrapper')
                if wrapper and self.identifier.is_checkbox_element(wrapper):
                    return wrapper
            except:
                pass
            
            # Try to find checkbox input
            try:
                checkbox_input = container.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                if checkbox_input:
                    # Try to get wrapper
                    try:
                        wrapper = checkbox_input.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-checkbox-wrapper")][1]')
                        return wrapper
                    except:
                        return checkbox_input
            except:
                pass
            
            # Check if container itself is a checkbox
            if self.identifier.is_checkbox_element(container):
                return container
            
        except:
            pass
        return None
    
    def _find_all_checkboxes_in_container(self, container: WebElement) -> List[WebElement]:
        """Find all checkbox elements within a container"""
        checkboxes = []
        try:
            wrappers = container.find_elements(By.CSS_SELECTOR, '.ant-checkbox-wrapper')
            for wrapper in wrappers:
                if self.identifier.is_checkbox_element(wrapper):
                    checkboxes.append(wrapper)
        except:
            pass
        return checkboxes
    
    def _find_checkbox_group_in_container(self, container: WebElement) -> Optional[WebElement]:
        """Find checkbox group within a container"""
        try:
            # Check if container itself is group
            class_attr = container.get_attribute('class') or ''
            if 'ant-checkbox-group' in class_attr:
                return container
            
            # Try to find group inside
            try:
                group = container.find_element(By.CSS_SELECTOR, '.ant-checkbox-group')
                return group
            except:
                pass
            
        except:
            pass
        return None
    
    def _store_element_in_context(self, element: WebElement, key: str, context: ElementContext):
        """
        Store element in context with checkbox information
        
        Args:
            element: WebElement to store
            key: Key to use in context
            context: ElementContext to store in
        """
        try:
            checkbox_info = self.identifier.identify_checkbox_type(element)
            
            # Get data_attr_id from checkbox_info or use key if it's a data-attr-id
            data_attr_id = checkbox_info.get('data_attr_id')
            if not data_attr_id and key and not key.startswith(('checkbox_', 'button_', 'input_')):
                # If key looks like a data-attr-id, use it
                data_attr_id = key
            
            # Create ElementInfo
            element_info = ElementInfo(
                element=element,
                element_type='checkbox',
                application_type=checkbox_info.get('application_type'),
                data_attr_id=data_attr_id,
                metadata=checkbox_info
            )
            context.store_element(key, element_info)
        except Exception as e:
            print(f"Error storing checkbox in context: {str(e)}")

