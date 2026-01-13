"""
DatePicker Locator - Handles finding and locating Ant Design DatePicker fields
Single Responsibility: Locate DatePickers by various criteria without hardcoded selectors
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Optional, List
from framework.base.base_page import BasePage
from framework.context.element_context import ElementContext, ElementInfo
from framework.components.datepicker_identifier import DatePickerIdentifier


class DatePickerLocator(BasePage):
    """
    Handles locating/finding Ant Design DatePicker fields on the page
    Single Responsibility: Find DatePickers by various identification methods
    Uses Ant Design class patterns, data-attr-id, aria attributes, and semantic labels
    """
    
    def __init__(self, driver: webdriver):
        """
        Initialize DatePicker Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.identifier = DatePickerIdentifier()
    
    def find_datepicker_by_data_attr(self, data_attr_id: str, timeout: int = 10,
                                      context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find DatePicker by custom data-atr-id or data-attr-id attribute
        PRIORITY: This is the primary method for finding DatePickers
        
        Args:
            data_attr_id: Value of data-atr-id or data-attr-id attribute
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        # Try data-atr-id first (original attribute name)
        element = self._find_datepicker_by_attr_name(data_attr_id, 'data-atr-id', timeout, context)
        if element:
            return element
        
        # Try data-attr-id as fallback (alternative attribute name)
        return self._find_datepicker_by_attr_name(data_attr_id, 'data-attr-id', timeout, context)
    
    def _find_datepicker_by_attr_name(self, data_attr_id: str, attr_name: str, timeout: int = 10,
                                       context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Internal helper to find DatePicker by a specific attribute name
        
        Args:
            data_attr_id: Value of the attribute
            attr_name: Name of the attribute ('data-atr-id' or 'data-attr-id')
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            # Try to find by attribute directly on picker element or parent container
            element = self.find_element(By.CSS_SELECTOR, f'[{attr_name}="{data_attr_id}"].ant-picker', timeout)
            if not element:
                # Try finding parent container with attribute
                element = self.find_element(By.CSS_SELECTOR, f'[{attr_name}="{data_attr_id}"] .ant-picker', timeout)
            if not element:
                # Try finding any element with attribute and check if it contains ant-picker
                candidates = self.find_elements(By.CSS_SELECTOR, f'[{attr_name}="{data_attr_id}"]', timeout)
                for candidate in candidates:
                    class_attr = candidate.get_attribute('class') or ''
                    if 'ant-picker' in class_attr:
                        element = candidate
                        break
                    # Check if candidate contains ant-picker
                    try:
                        picker_elem = candidate.find_element(By.CSS_SELECTOR, '.ant-picker')
                        element = picker_elem
                        break
                    except:
                        pass
            
            if element and context:
                self._store_element_in_context(element, data_attr_id, context)
            return element
        except TimeoutException:
            return None
    
    def find_datepicker_by_semantic_label(self, label_text: str, timeout: int = 10,
                                           context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find DatePicker by semantic label (no quotes needed in feature files)
        Tries multiple strategies: data-attr-id first, then label, aria-label, placeholder
        
        Args:
            label_text: Label text to search for (e.g., "Start Date", "Booking Period")
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
                element = self.find_datepicker_by_data_attr(candidate, timeout=2, context=context)
                if element:
                    return element
            except:
                pass
        
        # Strategy 2: Use existing label matching
        return self.find_datepicker_by_label(label_text, exact_match=False, timeout=timeout, context=context)
    
    def find_datepicker_by_label(self, label_text: str, exact_match: bool = False,
                                  timeout: int = 10, context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find DatePicker by label text (semantic matching)
        Uses aria-label, associated label element, Form.Item label, or placeholder
        
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
                    element = self.find_element(By.CSS_SELECTOR, f'.ant-picker[aria-label="{label_text}"]', timeout=2)
                else:
                    # Find all DatePickers and check aria-label
                    all_datepickers = self.find_all_ant_datepickers(timeout=timeout)
                    for dp in all_datepickers:
                        aria_label = dp.get_attribute('aria-label') or ''
                        if label_text.lower() in aria_label.lower() or aria_label.lower() in label_text.lower():
                            element = dp
                            break
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
                    # Find associated DatePicker (could be sibling or in same Form.Item)
                    # Try to find ant-picker near the label
                    try:
                        # Check if label has for attribute
                        for_attr = label_elem.get_attribute('for')
                        if for_attr:
                            element = self.find_element(By.ID, for_attr, timeout=2)
                            if element and 'ant-picker' in (element.get_attribute('class') or ''):
                                if context:
                                    self._store_element_in_context(element, label_text, context)
                                return element
                    except:
                        pass
                    
                    # Find ant-picker in same parent container
                    try:
                        parent = label_elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'ant-form-item')]")
                        element = parent.find_element(By.CSS_SELECTOR, '.ant-picker')
                        if element and context:
                            self._store_element_in_context(element, label_text, context)
                        return element
                    except:
                        pass
            except:
                pass
            
            # Strategy 3: Find by placeholder
            try:
                all_datepickers = self.find_all_ant_datepickers(timeout=timeout)
                for dp in all_datepickers:
                    # Get placeholder from input element
                    try:
                        inputs = dp.find_elements(By.CSS_SELECTOR, '.ant-picker-input input')
                        for input_elem in inputs:
                            placeholder = input_elem.get_attribute('placeholder') or ''
                            if label_text.lower() in placeholder.lower() or placeholder.lower() in label_text.lower():
                                if context:
                                    self._store_element_in_context(dp, label_text, context)
                                return dp
                    except:
                        pass
            except:
                pass
            
            return None
        except TimeoutException:
            return None
    
    def find_datepicker_by_type(self, picker_type: str, timeout: int = 10,
                                 context: Optional[ElementContext] = None) -> List[WebElement]:
        """
        Find all DatePickers of a specific type
        
        Args:
            picker_type: Type of DatePicker ('date', 'datetime', 'range', 'week', 'month', 'quarter', 'year', 'multiple')
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found elements
            
        Returns:
            List of WebElements matching the type
        """
        try:
            all_datepickers = self.find_all_ant_datepickers(timeout=timeout)
            typed_datepickers = []
            
            for dp in all_datepickers:
                dp_info = self.identifier.identify_datepicker_type(dp)
                if dp_info.get('picker_type') == picker_type:
                    typed_datepickers.append(dp)
                    if context and len(typed_datepickers) == 1:
                        # Store first element
                        data_attr_id = dp_info.get('data_attr_id')
                        key = data_attr_id or picker_type
                        self._store_element_in_context(dp, key, context)
            
            return typed_datepickers
        except TimeoutException:
            return []
    
    def find_datepicker_by_position(self, position: int, timeout: int = 10,
                                     context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find DatePicker by position/index (1-based)
        
        Args:
            position: Position/index (1-based)
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            all_datepickers = self.find_all_ant_datepickers(timeout=timeout)
            if 1 <= position <= len(all_datepickers):
                element = all_datepickers[position - 1]
                if context:
                    picker_info = self.identifier.identify_datepicker_type(element)
                    data_attr_id = picker_info.get('data_attr_id')
                    key = data_attr_id or f'datepicker_{position}'
                    self._store_element_in_context(element, key, context)
                return element
            return None
        except TimeoutException:
            return None
    
    def find_all_ant_datepickers(self, timeout: int = 10) -> List[WebElement]:
        """
        Find all Ant Design DatePicker components on the page
        Uses a robust approach to avoid stale element references
        
        Args:
            timeout: Maximum wait time in seconds
            
        Returns:
            List of WebElements representing DatePickers
        """
        try:
            # Wait for at least one DatePicker to be present
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ant-picker')))
            
            # Use JavaScript to find all DatePicker containers more reliably
            # This avoids stale element issues by getting fresh references
            script = """
            var pickers = [];
            var elements = document.querySelectorAll('.ant-picker');
            for (var i = 0; i < elements.length; i++) {
                var elem = elements[i];
                // Check if it has the DatePicker structure
                if (elem.querySelector('.ant-picker-input') || elem.classList.contains('ant-picker-range')) {
                    pickers.push(elem);
                }
            }
            return pickers.length;
            """
            
            count = self.driver.execute_script(script)
            
            # Now get the elements using Selenium, but do it in a way that avoids stale references
            # Get all elements fresh each time
            all_elements = self.driver.find_elements(By.CSS_SELECTOR, '.ant-picker')
            
            datepickers = []
            for elem in all_elements:
                try:
                    # Quick check - if it has ant-picker class and is visible
                    class_attr = elem.get_attribute('class') or ''
                    if 'ant-picker' not in class_attr:
                        continue
                    
                    # Check if it has the DatePicker structure (input inside)
                    try:
                        input_elem = elem.find_element(By.CSS_SELECTOR, '.ant-picker-input')
                        if input_elem:
                            datepickers.append(elem)
                    except NoSuchElementException:
                        # If no input found, might still be a DatePicker container (like range)
                        if 'ant-picker-range' in class_attr:
                            datepickers.append(elem)
                except StaleElementReferenceException:
                    # Skip stale elements
                    continue
                except Exception:
                    # Skip elements that cause errors
                    continue
            
            return datepickers
        except TimeoutException:
            # If timeout, try one more time with a simpler approach
            try:
                return self.driver.find_elements(By.CSS_SELECTOR, '.ant-picker')
            except:
                return []
        except Exception as e:
            print(f"Error finding DatePickers: {str(e)}")
            # Fallback: try simple find
            try:
                return self.driver.find_elements(By.CSS_SELECTOR, '.ant-picker')
            except:
                return []
    
    def _store_element_in_context(self, element: WebElement, key: str, context: ElementContext) -> None:
        """
        Store element in context with metadata
        
        Args:
            element: WebElement to store
            key: Key to use in context
            context: ElementContext to store in
        """
        try:
            picker_info = self.identifier.identify_datepicker_type(element)
            
            # Get data-attr-id
            data_attr_id = picker_info.get('data_attr_id')
            
            # Create ElementInfo
            element_info = ElementInfo(
                element=element,
                element_type='datepicker',
                application_type=picker_info.get('application_type'),
                data_attr_id=data_attr_id,
                metadata=picker_info
            )
            
            # Store in context
            context.store_element(key, element_info)
        except Exception as e:
            print(f"Error storing DatePicker in context: {str(e)}")
