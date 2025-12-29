"""
Switch Locator - Handles finding and locating Ant Design Switch components
Single Responsibility: Locate switches by various criteria without hardcoded selectors
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Optional, List
from framework.base.base_page import BasePage
from framework.context.element_context import ElementContext, ElementInfo
from framework.components.switch_identifier import SwitchIdentifier
from framework.utils.pattern_discovery import PatternDiscovery


class SwitchLocator(BasePage):
    """
    Handles locating/finding Ant Design Switch components on the page
    Single Responsibility: Find switches by various identification methods
    Uses Ant Design class patterns, data-attr-id, aria attributes, and semantic labels
    Automatically discovers data-attr-id patterns from the page
    """
    
    def __init__(self, driver: webdriver):
        """
        Initialize Switch Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.identifier = SwitchIdentifier()
        self.pattern_discovery = PatternDiscovery(driver)
    
    def find_switch_by_data_attr(self, data_attr_id: str, timeout: int = 10,
                                  context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find switch by custom data-atr-id or data-attr-id attribute
        PRIORITY: This is the primary method for finding switches
        
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
            if element and self.identifier.is_switch_element(element):
                if context:
                    self._store_element_in_context(element, data_attr_id, context)
                return element
        except TimeoutException:
            pass
        
        # Try data-attr-id as fallback (alternative attribute name)
        try:
            element = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
            if element and self.identifier.is_switch_element(element):
                if context:
                    self._store_element_in_context(element, data_attr_id, context)
                return element
        except TimeoutException:
            pass
        
        # Try finding switch inside element with data-attr-id
        try:
            wrapper = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"]', timeout)
            if wrapper:
                switch = wrapper.find_element(By.CSS_SELECTOR, '.ant-switch, [role="switch"]')
                if switch:
                    if context:
                        self._store_element_in_context(switch, data_attr_id, context)
                    return switch
        except:
            pass
        
        try:
            wrapper = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
            if wrapper:
                switch = wrapper.find_element(By.CSS_SELECTOR, '.ant-switch, [role="switch"]')
                if switch:
                    if context:
                        self._store_element_in_context(switch, data_attr_id, context)
                    return switch
        except:
            pass
        
        return None
    
    def find_switch_by_semantic_label(self, label_text: str, timeout: int = 10,
                                      context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find switch by semantic label (no quotes needed in feature files)
        Automatically discovers data-attr-id patterns from the page
        Tries multiple strategies: discovered patterns first, then aria-label, associated label, Form.Item context
        
        Args:
            label_text: Label text to search for (e.g., "Notifications", "Dark Mode")
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        # Strategy 1: Try automatic pattern discovery first
        try:
            # Find matching data-attr-id using pattern discovery
            matching_attr_id = self.pattern_discovery.find_matching_data_attr_id(label_text, 'switch')
            if matching_attr_id:
                element = self.find_switch_by_data_attr(matching_attr_id, timeout=3, context=context)
                if element:
                    return element
        except:
            pass
        
        # Strategy 2: Generate candidates based on discovered pattern structure
        try:
            candidates = self.pattern_discovery.generate_candidates(label_text, 'switch')
            for candidate in candidates:
                try:
                    element = self.find_switch_by_data_attr(candidate, timeout=2, context=context)
                    if element:
                        return element
                except:
                    continue
        except:
            pass
        
        # Strategy 3: Try aria-label
        try:
            # Normalize label text for matching
            normalized_label = label_text.lower().strip()
            
            # Find by aria-label
            xpath = f'//*[@role="switch" and @aria-label="{label_text}"] | //*[contains(@aria-label, "{label_text}") and @role="switch"]'
            element = self.find_element(By.XPATH, xpath, timeout=3)
            if element and self.identifier.is_switch_element(element):
                if context:
                    self._store_element_in_context(element, label_text, context)
                return element
        except:
            pass
        
        # Strategy 4: Find by associated label element (Form.Item context)
        try:
            # Look for label text, then find switch nearby
            label_xpath = f'//label[contains(text(), "{label_text}")] | //span[contains(text(), "{label_text}")] | //div[contains(text(), "{label_text}")]'
            labels = self.driver.find_elements(By.XPATH, label_xpath)
            
            for label in labels:
                try:
                    # Find switch in same Form.Item or nearby
                    parent = label.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-form-item")]')
                    if parent:
                        switch = parent.find_element(By.CSS_SELECTOR, '.ant-switch, [role="switch"]')
                        if switch:
                            if context:
                                self._store_element_in_context(switch, label_text, context)
                            return switch
                except:
                    # Try finding switch after label
                    try:
                        switch = label.find_element(By.XPATH, './following::*[contains(@class, "ant-switch") or @role="switch"]')
                        if switch:
                            if context:
                                self._store_element_in_context(switch, label_text, context)
                            return switch
                    except:
                        continue
        except:
            pass
        
        # Strategy 5: Fuzzy text match - find switch near text
        try:
            # Find all switches and check nearby text
            switches = self.find_all_switches(timeout=3)
            for switch in switches:
                try:
                    # Check parent or sibling for label text
                    parent = switch.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-form-item") or contains(@class, "ant-switch-wrapper") or contains(@class, "switch")]')
                    parent_text = parent.text.lower()
                    if normalized_label in parent_text:
                        if context:
                            self._store_element_in_context(switch, label_text, context)
                        return switch
                except:
                    # Try checking siblings and nearby elements
                    try:
                        # Check preceding sibling for label
                        preceding = switch.find_element(By.XPATH, './preceding-sibling::*[1]')
                        if normalized_label in preceding.text.lower():
                            if context:
                                self._store_element_in_context(switch, label_text, context)
                            return switch
                    except:
                        pass
                    
                    # Check following sibling
                    try:
                        following = switch.find_element(By.XPATH, './following-sibling::*[1]')
                        if normalized_label in following.text.lower():
                            if context:
                                self._store_element_in_context(switch, label_text, context)
                            return switch
                    except:
                        pass
                    
                    # Check parent's text content
                    try:
                        parent = switch.find_element(By.XPATH, './..')
                        if normalized_label in parent.text.lower():
                            if context:
                                self._store_element_in_context(switch, label_text, context)
                            return switch
                    except:
                        continue
        except:
            pass
        
        # Strategy 6: Search for text in page and find nearest switch
        try:
            # Find all text nodes containing the label
            xpath = f"//*[contains(text(), '{label_text}') or contains(., '{label_text}')]"
            text_elements = self.driver.find_elements(By.XPATH, xpath)
            
            for text_elem in text_elements:
                try:
                    # Find switch in same container or nearby
                    container = text_elem.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-form-item") or contains(@class, "switch") or contains(@class, "form")]')
                    switch = container.find_element(By.CSS_SELECTOR, '.ant-switch, [role="switch"]')
                    if switch and self.identifier.is_switch_element(switch):
                        if context:
                            self._store_element_in_context(switch, label_text, context)
                        return switch
                except:
                    # Try finding switch in same parent
                    try:
                        parent = text_elem.find_element(By.XPATH, './..')
                        switch = parent.find_element(By.CSS_SELECTOR, '.ant-switch, [role="switch"]')
                        if switch and self.identifier.is_switch_element(switch):
                            if context:
                                self._store_element_in_context(switch, label_text, context)
                            return switch
                    except:
                        continue
        except:
            pass
        
        return None
    
    def find_switch_by_aria_label(self, aria_label: str, timeout: int = 10,
                                   context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find switch by aria-label attribute
        
        Args:
            aria_label: Value of aria-label attribute
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            xpath = f'//*[@role="switch" and @aria-label="{aria_label}"]'
            element = self.find_element(By.XPATH, xpath, timeout)
            if element and self.identifier.is_switch_element(element):
                if context:
                    self._store_element_in_context(element, aria_label, context)
                return element
        except TimeoutException:
            pass
        
        # Try partial match
        try:
            xpath = f'//*[@role="switch" and contains(@aria-label, "{aria_label}")]'
            element = self.find_element(By.XPATH, xpath, timeout)
            if element and self.identifier.is_switch_element(element):
                if context:
                    self._store_element_in_context(element, aria_label, context)
                return element
        except TimeoutException:
            pass
        
        return None
    
    def find_all_switches(self, timeout: int = 10) -> List[WebElement]:
        """
        Find all Ant Design Switch components on the page
        Uses multiple strategies to ensure all switches are found
        Optimized to avoid hanging on large pages
        
        Args:
            timeout: Maximum wait time in seconds (not used directly, but for consistency)
            
        Returns:
            List of WebElements representing switches
        """
        switches = []
        seen_elements = set()  # Track by element ID to avoid duplicates
        
        import time
        start_time = time.time()
        max_time = 5  # Maximum 5 seconds for finding switches
        
        # Strategy 1: Find by Ant Design class (fastest and most reliable)
        if time.time() - start_time < max_time:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, '.ant-switch')
                print(f"   → Found {len(elements)} elements with .ant-switch class")
                for element in elements:
                    if time.time() - start_time > max_time:
                        break
                    try:
                        elem_id = id(element)
                        if elem_id not in seen_elements:
                            # Quick check - just verify it has the class
                            class_attr = element.get_attribute('class') or ''
                            if 'ant-switch' in class_attr:
                                switches.append(element)
                                seen_elements.add(elem_id)
                    except:
                        continue
            except Exception as e:
                print(f"   >> Error finding switches by class: {str(e)}")
        
        # Strategy 2: Find by role="switch" (only if we have time)
        if time.time() - start_time < max_time:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, '[role="switch"]')
                for element in elements:
                    if time.time() - start_time > max_time:
                        break
                    try:
                        elem_id = id(element)
                        if elem_id not in seen_elements:
                            role = element.get_attribute('role')
                            if role == 'switch':
                                switches.append(element)
                                seen_elements.add(elem_id)
                    except:
                        continue
            except Exception as e:
                print(f"   >> Error finding switches by role: {str(e)}")
        
        # Remove duplicates by comparing element properties (simplified)
        unique_switches = []
        seen_properties = set()
        for switch in switches:
            try:
                # Create a simple unique identifier
                switch_id = id(switch)
                if switch_id not in seen_properties:
                    unique_switches.append(switch)
                    seen_properties.add(switch_id)
            except:
                # If we can't get ID, skip it
                continue
        
        print(f"   → Identified {len(unique_switches)} unique switch(es)")
        return unique_switches
    
    def find_switch_by_position(self, position: int, timeout: int = 10,
                                context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find switch by position/index (1-based)
        
        Args:
            position: Position/index of switch (1-based)
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        switches = self.find_all_switches(timeout)
        
        if position > 0 and position <= len(switches):
            element = switches[position - 1]
            if context:
                self._store_element_in_context(element, f'switch_{position}', context)
            return element
        
        return None
    
    def find_switch_by_state(self, checked: bool, timeout: int = 10) -> List[WebElement]:
        """
        Find all switches with a specific state (checked/unchecked)
        
        Args:
            checked: True for checked (ON), False for unchecked (OFF)
            timeout: Maximum wait time in seconds
            
        Returns:
            List of WebElements matching the state
        """
        switches = self.find_all_switches(timeout)
        matching_switches = []
        
        for switch in switches:
            switch_info = self.identifier.identify_switch_type(switch)
            if switch_info['checked'] == checked:
                matching_switches.append(switch)
        
        return matching_switches
    
    def _store_element_in_context(self, element: WebElement, key: str, context: ElementContext):
        """
        Store element in context with switch information
        
        Args:
            element: WebElement to store
            key: Key to use in context
            context: ElementContext to store in
        """
        try:
            switch_info = self.identifier.identify_switch_type(element)
            
            # Get data_attr_id from switch_info or use key if it's a data-attr-id
            data_attr_id = switch_info.get('data_attr_id')
            if not data_attr_id and key and not key.startswith(('switch_', 'button_', 'input_')):
                # If key looks like a data-attr-id, use it
                data_attr_id = key
            
            # Create ElementInfo (matching pattern from button_locator)
            element_info = ElementInfo(
                element=element,
                element_type='switch',
                application_type=switch_info.get('application_type'),
                data_attr_id=data_attr_id,
                metadata=switch_info
            )
            context.store_element(key, element_info)
        except Exception as e:
            print(f"Error storing switch in context: {str(e)}")

