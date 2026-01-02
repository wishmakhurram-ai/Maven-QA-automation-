"""
Radio Locator - Handles finding and locating Ant Design Radio components
Single Responsibility: Locate radios by various criteria without hardcoded selectors
Detection relies ONLY on Ant Design radio classes and optional data-attr-id attributes.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Optional, List, Dict
from framework.base.base_page import BasePage
from framework.context.element_context import ElementContext, ElementInfo
from framework.components.radio_identifier import RadioIdentifier
from framework.utils.pattern_discovery import PatternDiscovery


class RadioLocator(BasePage):
    """
    Handles locating/finding Ant Design Radio components on the page
    Single Responsibility: Find radios by various identification methods
    Uses Ant Design class patterns, data-attr-id, aria attributes, and semantic labels
    Automatically discovers data-attr-id patterns from the page
    """
    
    def __init__(self, driver: webdriver):
        """
        Initialize Radio Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.identifier = RadioIdentifier()
        self.pattern_discovery = PatternDiscovery(driver)
    
    def find_radio_by_data_attr(self, data_attr_id: str, timeout: int = 10,
                                 context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find radio by custom data-atr-id or data-attr-id attribute
        PRIORITY: This is the primary method for finding radios
        
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
            if element and self.identifier.is_radio_element(element):
                if context:
                    self._store_element_in_context(element, data_attr_id, context)
                return element
        except TimeoutException:
            pass
        
        # Try data-attr-id as fallback
        try:
            element = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
            if element and self.identifier.is_radio_element(element):
                if context:
                    self._store_element_in_context(element, data_attr_id, context)
                return element
        except TimeoutException:
            pass
        
        # Try finding radio inside element with data-attr-id
        try:
            wrapper = self.find_element(By.CSS_SELECTOR, f'[data-atr-id="{data_attr_id}"]', timeout)
            if wrapper:
                radio = self._find_radio_in_container(wrapper)
                if radio:
                    if context:
                        self._store_element_in_context(radio, data_attr_id, context)
                    return radio
        except:
            pass
        
        try:
            wrapper = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
            if wrapper:
                radio = self._find_radio_in_container(wrapper)
                if radio:
                    if context:
                        self._store_element_in_context(radio, data_attr_id, context)
                    return radio
        except:
            pass
        
        return None
    
    def find_radio_by_semantic_label(self, label_text: str, group_name: Optional[str] = None,
                                     timeout: int = 10,
                                     context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find radio by semantic label (no quotes needed in feature files)
        Automatically discovers data-attr-id patterns from the page
        Tries multiple strategies: discovered patterns first, then aria-label, associated label, Form.Item context
        
        Args:
            label_text: Label text to search for (e.g., "Male", "Visa")
            group_name: Optional radio group name to narrow search
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        # Strategy 1: Try automatic pattern discovery first
        try:
            matching_attr_id = self.pattern_discovery.find_matching_data_attr_id(label_text, 'radio')
            if matching_attr_id:
                element = self.find_radio_by_data_attr(matching_attr_id, timeout=3, context=context)
                if element:
                    return element
        except:
            pass
        
        # Strategy 2: Generate candidates based on discovered pattern structure
        try:
            candidates = self.pattern_discovery.generate_candidates(label_text, 'radio')
            for candidate in candidates:
                try:
                    element = self.find_radio_by_data_attr(candidate, timeout=2, context=context)
                    if element:
                        return element
                except:
                    continue
        except:
            pass
        
        # Strategy 3: If group_name provided, search within that group first
        if group_name:
            group_radios = self.find_radios_in_group(group_name, timeout=timeout)
            for radio in group_radios:
                radio_info = self.identifier.identify_radio_type(radio)
                if radio_info.get('label_text') and label_text.lower() in radio_info['label_text'].lower():
                    if context:
                        self._store_element_in_context(radio, label_text, context)
                    return radio
        
        # Strategy 4: Try aria-label
        try:
            normalized_label = label_text.lower().strip()
            xpath = f'//input[@type="radio" and @aria-label="{label_text}"] | //input[@type="radio" and contains(@aria-label, "{label_text}")]'
            elements = self.driver.find_elements(By.XPATH, xpath)
            for element in elements:
                if self.identifier.is_radio_element(element):
                    if context:
                        self._store_element_in_context(element, label_text, context)
                    return element
        except:
            pass
        
        # Strategy 5: Find by associated label element (Form.Item context)
        try:
            # Look for label text, then find radio nearby
            label_xpath = f'//label[contains(text(), "{label_text}")] | //span[contains(text(), "{label_text}")] | //div[contains(text(), "{label_text}")]'
            labels = self.driver.find_elements(By.XPATH, label_xpath)
            
            for label in labels:
                try:
                    # Find radio in same Form.Item or nearby
                    parent = label.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-form-item")]')
                    if parent:
                        radio = self._find_radio_in_container(parent)
                        if radio:
                            if context:
                                self._store_element_in_context(radio, label_text, context)
                            return radio
                except:
                    # Try finding radio after label
                    try:
                        radio = label.find_element(By.XPATH, './following::*[contains(@class, "ant-radio-wrapper") or contains(@class, "ant-radio")][1]')
                        if radio and self.identifier.is_radio_element(radio):
                            if context:
                                self._store_element_in_context(radio, label_text, context)
                            return radio
                    except:
                        continue
        except:
            pass
        
        # Strategy 6: Fuzzy text match - find radio near text
        try:
            # Find all radios and check nearby text
            radios = self.find_all_radios(timeout=3)
            for radio in radios:
                try:
                    radio_info = self.identifier.identify_radio_type(radio)
                    radio_label = radio_info.get('label_text', '').lower()
                    if normalized_label in radio_label or label_text.lower() in radio_label:
                        if context:
                            self._store_element_in_context(radio, label_text, context)
                        return radio
                except:
                    continue
        except:
            pass
        
        return None
    
    def find_radio_group_by_name(self, group_name: str, timeout: int = 10) -> Optional[WebElement]:
        """
        Find radio group by name attribute or semantic label
        
        Args:
            group_name: Group name or label (e.g., "Payment Method", "Gender")
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement of radio group if found, None otherwise
        """
        try:
            # Strategy 1: Find by name attribute
            radios = self.driver.find_elements(By.CSS_SELECTOR, f'input[type="radio"][name="{group_name}"]')
            if radios:
                # Get the group container
                first_radio = radios[0]
                group = self.identifier._find_radio_group(first_radio)
                if group:
                    return group
            
            # Strategy 2: Find by data-attr-id pattern
            try:
                matching_attr_id = self.pattern_discovery.find_matching_data_attr_id(group_name, 'radio-group')
                if matching_attr_id:
                    group = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{matching_attr_id}"].ant-radio-group, [data-attr-id="{matching_attr_id}"] .ant-radio-group', timeout=3)
                    if group:
                        return group
            except:
                pass
            
            # Strategy 3: Find by fieldset or form label
            try:
                # Find label or heading with group name
                label_xpath = f'//label[contains(text(), "{group_name}")] | //legend[contains(text(), "{group_name}")] | //h3[contains(text(), "{group_name}")] | //h4[contains(text(), "{group_name}")]'
                labels = self.driver.find_elements(By.XPATH, label_xpath)
                
                for label in labels:
                    try:
                        # Find radio group nearby
                        parent = label.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-form-item") or contains(@class, "ant-radio-group")][1]')
                        group = self._find_radio_group_in_container(parent)
                        if group:
                            return group
                    except:
                        # Try finding group after label
                        try:
                            group = label.find_element(By.XPATH, './following::*[contains(@class, "ant-radio-group")][1]')
                            if group:
                                return group
                        except:
                            continue
            except:
                pass
            
        except:
            pass
        
        return None
    
    def find_radios_in_group(self, group_name: str, timeout: int = 10) -> List[WebElement]:
        """
        Find all radios in a specific group
        
        Args:
            group_name: Group name or label
            timeout: Maximum wait time in seconds
            
        Returns:
            List of WebElements representing radios in the group
        """
        radios = []
        try:
            group = self.find_radio_group_by_name(group_name, timeout)
            if group:
                radios = self._find_all_radios_in_container(group)
        except:
            pass
        return radios
    
    def find_all_radios(self, timeout: int = 10) -> List[WebElement]:
        """
        Find all Ant Design Radio components on the page
        
        Args:
            timeout: Maximum wait time in seconds (not used directly, but for consistency)
            
        Returns:
            List of WebElements representing radios
        """
        radios = []
        seen_elements = set()
        
        import time
        start_time = time.time()
        max_time = 5  # Maximum 5 seconds for finding radios
        
        # Strategy 1: Find by Ant Design class (fastest and most reliable)
        if time.time() - start_time < max_time:
            try:
                # Find radio wrappers
                wrappers = self.driver.find_elements(By.CSS_SELECTOR, '.ant-radio-wrapper')
                for wrapper in wrappers:
                    if time.time() - start_time > max_time:
                        break
                    try:
                        elem_id = id(wrapper)
                        if elem_id not in seen_elements:
                            if self.identifier.is_radio_element(wrapper):
                                radios.append(wrapper)
                                seen_elements.add(elem_id)
                    except:
                        continue
            except Exception as e:
                print(f"   >> Error finding radios by wrapper: {str(e)}")
        
        # Strategy 2: Find by input[type="radio"]
        if time.time() - start_time < max_time:
            try:
                inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
                for input_elem in inputs:
                    if time.time() - start_time > max_time:
                        break
                    try:
                        elem_id = id(input_elem)
                        if elem_id not in seen_elements:
                            # Get wrapper for this input
                            try:
                                wrapper = input_elem.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-radio-wrapper")][1]')
                                wrapper_id = id(wrapper)
                                if wrapper_id not in seen_elements:
                                    radios.append(wrapper)
                                    seen_elements.add(wrapper_id)
                                    seen_elements.add(elem_id)
                            except:
                                # If no wrapper, use input itself
                                radios.append(input_elem)
                                seen_elements.add(elem_id)
                    except:
                        continue
            except Exception as e:
                print(f"   >> Error finding radios by input: {str(e)}")
        
        # Strategy 3: Find radio button style
        if time.time() - start_time < max_time:
            try:
                button_wrappers = self.driver.find_elements(By.CSS_SELECTOR, '.ant-radio-button-wrapper')
                for wrapper in button_wrappers:
                    if time.time() - start_time > max_time:
                        break
                    try:
                        elem_id = id(wrapper)
                        if elem_id not in seen_elements:
                            radios.append(wrapper)
                            seen_elements.add(elem_id)
                    except:
                        continue
            except Exception as e:
                print(f"   >> Error finding radio buttons: {str(e)}")
        
        print(f"   → Identified {len(radios)} unique radio(s)")
        return radios
    
    def find_radio_by_position(self, position: int, timeout: int = 10,
                               context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find radio by position/index (1-based)
        
        Args:
            position: Position/index of radio (1-based)
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        radios = self.find_all_radios(timeout)
        
        if position > 0 and position <= len(radios):
            element = radios[position - 1]
            if context:
                self._store_element_in_context(element, f'radio_{position}', context)
            return element
        
        return None
    
    def find_radio_in_group_by_index(self, group_name: str, index: int, timeout: int = 10) -> Optional[WebElement]:
        """
        Find radio in a group by index (1-based)
        
        Args:
            group_name: Group name or label
            index: Index within group (1-based)
            timeout: Maximum wait time in seconds
            
        Returns:
            WebElement if found, None otherwise
        """
        radios = self.find_radios_in_group(group_name, timeout)
        
        if index > 0 and index <= len(radios):
            return radios[index - 1]
        
        return None
    
    def _find_radio_in_container(self, container: WebElement) -> Optional[WebElement]:
        """Find a radio element within a container"""
        try:
            # Try to find radio wrapper
            try:
                wrapper = container.find_element(By.CSS_SELECTOR, '.ant-radio-wrapper, .ant-radio-button-wrapper')
                if wrapper and self.identifier.is_radio_element(wrapper):
                    return wrapper
            except:
                pass
            
            # Try to find radio input
            try:
                radio_input = container.find_element(By.CSS_SELECTOR, 'input[type="radio"]')
                if radio_input:
                    # Try to get wrapper
                    try:
                        wrapper = radio_input.find_element(By.XPATH, './ancestor::*[contains(@class, "ant-radio-wrapper")][1]')
                        return wrapper
                    except:
                        return radio_input
            except:
                pass
            
            # Check if container itself is a radio
            if self.identifier.is_radio_element(container):
                return container
            
        except:
            pass
        return None
    
    def _find_all_radios_in_container(self, container: WebElement) -> List[WebElement]:
        """Find all radio elements within a container"""
        radios = []
        try:
            wrappers = container.find_elements(By.CSS_SELECTOR, '.ant-radio-wrapper, .ant-radio-button-wrapper')
            for wrapper in wrappers:
                if self.identifier.is_radio_element(wrapper):
                    radios.append(wrapper)
        except:
            pass
        return radios
    
    def _find_radio_group_in_container(self, container: WebElement) -> Optional[WebElement]:
        """Find radio group within a container"""
        try:
            # Check if container itself is group
            class_attr = container.get_attribute('class') or ''
            if 'ant-radio-group' in class_attr:
                return container
            
            # Try to find group inside
            try:
                group = container.find_element(By.CSS_SELECTOR, '.ant-radio-group')
                return group
            except:
                pass
            
        except:
            pass
        return None
    
    def _store_element_in_context(self, element: WebElement, key: str, context: ElementContext):
        """
        Store element in context with radio information
        
        Args:
            element: WebElement to store
            key: Key to use in context
            context: ElementContext to store in
        """
        try:
            radio_info = self.identifier.identify_radio_type(element)
            
            # Get data_attr_id from radio_info or use key if it's a data-attr-id
            data_attr_id = radio_info.get('data_attr_id')
            if not data_attr_id and key and not key.startswith(('radio_', 'button_', 'input_')):
                # If key looks like a data-attr-id, use it
                data_attr_id = key
            
            # Create ElementInfo
            element_info = ElementInfo(
                element=element,
                element_type='radio',
                application_type=radio_info.get('application_type'),
                data_attr_id=data_attr_id,
                metadata=radio_info
            )
            context.store_element(key, element_info)
        except Exception as e:
            print(f"Error storing radio in context: {str(e)}")

