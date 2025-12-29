"""
Input Locator - Handles finding and locating Ant Design input fields
Single Responsibility: Locate inputs by various criteria without hardcoded selectors
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from typing import Optional, List
from framework.base.base_page import BasePage
from framework.context.element_context import ElementContext, ElementInfo
from framework.components.input_identifier import InputIdentifier
from framework.utils.pattern_discovery import PatternDiscovery


class InputLocator(BasePage):
    """
    Handles locating/finding Ant Design input fields on the page
    Single Responsibility: Find inputs by various identification methods
    Uses Ant Design class patterns, data-attr-id, aria attributes, and semantic labels
    Automatically discovers data-attr-id patterns from the page
    """
    
    def __init__(self, driver: webdriver):
        """
        Initialize Input Locator
        
        Args:
            driver: Selenium WebDriver instance
        """
        super().__init__(driver)
        self.identifier = InputIdentifier()
        self.pattern_discovery = PatternDiscovery(driver)
    
    def find_input_by_data_attr(self, data_attr_id: str, timeout: int = 10,
                                  context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find input by custom data-atr-id or data-attr-id attribute
        PRIORITY: This is the primary method for finding inputs
        
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
            if element and context:
                self._store_element_in_context(element, data_attr_id, context)
                return element
        except TimeoutException:
            pass
        
        # Try data-attr-id as fallback (alternative attribute name)
        try:
            element = self.find_element(By.CSS_SELECTOR, f'[data-attr-id="{data_attr_id}"]', timeout)
            if element and context:
                self._store_element_in_context(element, data_attr_id, context)
            return element
        except TimeoutException:
            return None
    
    def find_input_by_semantic_label(self, label_text: str, timeout: int = 10,
                                     context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find input by semantic label (no quotes needed in feature files)
        Automatically discovers data-attr-id patterns from the page
        Tries multiple strategies: discovered patterns first, then placeholder, aria-label, associated label
        
        Args:
            label_text: Label text to search for (e.g., "Firm Name", "Email")
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        # Strategy 1: Try automatic pattern discovery first
        try:
            # Find matching data-attr-id using pattern discovery
            matching_attr_id = self.pattern_discovery.find_matching_data_attr_id(label_text, 'input')
            if matching_attr_id:
                element = self.find_input_by_data_attr(matching_attr_id, timeout=3, context=context)
                if element:
                    return element
        except:
            pass
        
        # Strategy 2: Generate candidates based on discovered pattern structure
        try:
            candidates = self.pattern_discovery.generate_candidates(label_text, 'input')
            for candidate in candidates:
                try:
                    element = self.find_input_by_data_attr(candidate, timeout=2, context=context)
                    if element:
                        return element
                except:
                    continue
        except:
            pass
        
        # Strategy 3: Try simple normalized patterns
        normalized_label = label_text.lower().replace(' ', '-').replace('_', '-')
        simple_candidates = [
            normalized_label,
            label_text.lower().replace(' ', '_'),
            label_text.lower().replace(' ', ''),
        ]
        
        for candidate in simple_candidates:
            try:
                element = self.find_input_by_data_attr(candidate, timeout=2, context=context)
                if element:
                    return element
            except:
                pass
        
        # Strategy 4: Use existing label matching (placeholder, aria-label, etc.)
        return self.find_input_by_label(label_text, exact_match=False, timeout=timeout, context=context)
    
    def find_input_by_label(self, label_text: str, exact_match: bool = False, 
                             timeout: int = 10, context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find input by label text (semantic matching)
        Uses placeholder, aria-label, nearby label element, or associated label
        
        Args:
            label_text: Label text to search for
            exact_match: If True, match exact text; if False, partial/fuzzy match
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            # Try multiple strategies
            element = None
            
            # Strategy 1: Find by placeholder
            if exact_match:
                xpath = f"//input[@placeholder='{label_text}'] | //textarea[@placeholder='{label_text}']"
            else:
                xpath = f"//input[contains(@placeholder, '{label_text}')] | //textarea[contains(@placeholder, '{label_text}')]"
            
            try:
                element = self.find_element(By.XPATH, xpath, timeout=5)
            except:
                pass
            
            # Strategy 2: Find by aria-label
            if not element:
                if exact_match:
                    xpath = f"//input[@aria-label='{label_text}'] | //textarea[@aria-label='{label_text}']"
                else:
                    xpath = f"//input[contains(@aria-label, '{label_text}')] | //textarea[contains(@aria-label, '{label_text}')]"
                try:
                    element = self.find_element(By.XPATH, xpath, timeout=5)
                except:
                    pass
            
            # Strategy 3: Find by associated label element
            if not element:
                if exact_match:
                    label_xpath = f"//label[normalize-space(text())='{label_text}']"
                else:
                    label_xpath = f"//label[contains(text(), '{label_text}')]"
                try:
                    labels = self.find_elements(By.XPATH, label_xpath, timeout=5)
                    for label in labels:
                        # Get 'for' attribute
                        label_for = label.get_attribute('for')
                        if label_for:
                            element = self.find_element(By.ID, label_for, timeout=2)
                            if element:
                                break
                        # Or find input/textarea within label
                        inputs = label.find_elements(By.TAG_NAME, "input")
                        textareas = label.find_elements(By.TAG_NAME, "textarea")
                        if inputs:
                            element = inputs[0]
                            break
                        if textareas:
                            element = textareas[0]
                            break
                except:
                    pass
            
            # Strategy 4: Find by nearby label (using Ant Design structure)
            if not element:
                # Ant Design Input.Group or Form.Item structure
                xpath = "//span[contains(@class, 'ant-input')]//input | //span[contains(@class, 'ant-input')]//textarea"
                try:
                    candidates = self.find_elements(By.XPATH, xpath, timeout=5)
                    for candidate in candidates:
                        # Check placeholder, aria-label, or nearby text
                        placeholder = candidate.get_attribute('placeholder') or ''
                        aria_label = candidate.get_attribute('aria-label') or ''
                        if exact_match:
                            if label_text.lower() == placeholder.lower() or label_text.lower() == aria_label.lower():
                                element = candidate
                                break
                        else:
                            if label_text.lower() in placeholder.lower() or label_text.lower() in aria_label.lower():
                                element = candidate
                                break
                except:
                    pass
            
            if element and context:
                key = self._generate_context_key(element, label_text)
                self._store_element_in_context(element, key, context)
            return element
        except TimeoutException:
            return None
    
    def find_input_by_type(self, input_type: str, timeout: int = 10,
                           context: Optional[ElementContext] = None) -> List[WebElement]:
        """
        Find all inputs of a specific type (text, password, number, email, etc.)
        
        Args:
            input_type: Type of input ('text', 'password', 'number', 'email', 'url', 'search', 'textarea')
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found elements
            
        Returns:
            List of WebElements matching the type
        """
        try:
            elements = []
            
            if input_type == 'textarea':
                # Find textareas
                elements = self.find_elements(By.TAG_NAME, 'textarea', timeout)
            else:
                # Find inputs by type attribute
                elements = self.find_elements(By.CSS_SELECTOR, f'input[type="{input_type}"]', timeout)
            
            # Filter to only Ant Design inputs
            ant_elements = []
            for elem in elements:
                class_attr = elem.get_attribute('class') or ''
                if 'ant-input' in class_attr or elem.find_elements(By.XPATH, "./ancestor::span[contains(@class, 'ant-input')]"):
                    ant_elements.append(elem)
            
            if ant_elements and context:
                # Store first element
                # Use input_type as key if no data-attr-id, otherwise use data-attr-id
                element = ant_elements[0]
                data_attr_id = element.get_attribute('data-atr-id')
                if not data_attr_id:
                    # Try data-attr-id as fallback
                    data_attr_id = element.get_attribute('data-attr-id')
                if data_attr_id:
                    key = data_attr_id
                else:
                    # Use the type as the key for consistency with identify_and_store
                    key = input_type
                self._store_element_in_context(element, key, context)
            
            return ant_elements
        except TimeoutException:
            return []
    
    def find_all_ant_inputs(self, timeout: int = 10, include_all: bool = False) -> List[WebElement]:
        """
        Find all input fields on the page
        
        Args:
            timeout: Maximum wait time in seconds
            include_all: If True, finds ALL inputs (not just Ant Design). If False, only Ant Design inputs.
            
        Returns:
            List of all input WebElements
        """
        try:
            if include_all:
                # Find ALL inputs and textareas on the page (not just Ant Design)
                all_inputs = self.find_elements(By.CSS_SELECTOR, 'input, textarea', timeout)
                
                # Filter out hidden inputs (type="hidden", display:none, visibility:hidden)
                visible_inputs = []
                for inp in all_inputs:
                    try:
                        # Skip hidden inputs
                        input_type = inp.get_attribute('type') or ''
                        if input_type.lower() == 'hidden':
                            continue
                        
                        # Check if element is visible
                        is_displayed = inp.is_displayed()
                        if not is_displayed:
                            continue
                        
                        # Check computed style
                        display = self.execute_js("return window.getComputedStyle(arguments[0]).display;", inp)
                        visibility = self.execute_js("return window.getComputedStyle(arguments[0]).visibility;", inp)
                        
                        if display == 'none' or visibility == 'hidden':
                            continue
                        
                        visible_inputs.append(inp)
                    except:
                        # If we can't check visibility, include it anyway
                        visible_inputs.append(inp)
                
                return visible_inputs
            else:
                # Find only Ant Design inputs
                inputs = self.find_elements(By.CSS_SELECTOR, 'input.ant-input, textarea.ant-input', timeout)
                
                # Also find inputs within Ant Design input containers
                containers = self.find_elements(By.CSS_SELECTOR, '.ant-input-group input, .ant-input-group textarea, .ant-input-affix-wrapper input, .ant-input-affix-wrapper textarea', timeout)
                
                # Combine and deduplicate
                all_inputs = list(set(inputs + containers))
                
                return all_inputs
        except TimeoutException:
            return []
    
    def find_input_by_position(self, position: int, input_type: Optional[str] = None, 
                               timeout: int = 10, context: Optional[ElementContext] = None) -> Optional[WebElement]:
        """
        Find input by position/index
        
        Args:
            position: Position/index (1-based)
            input_type: Optional filter by type ('text', 'password', etc.)
            timeout: Maximum wait time in seconds
            context: Optional ElementContext to store the found element
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            if input_type:
                elements = self.find_input_by_type(input_type, timeout)
            else:
                elements = self.find_all_ant_inputs(timeout)
            
            if elements and 1 <= position <= len(elements):
                element = elements[position - 1]  # Convert to 0-based
                if context:
                    key = self._generate_context_key(element, f"input_{position}")
                    self._store_element_in_context(element, key, context)
                return element
            return None
        except:
            return None
    
    def _store_element_in_context(self, element: WebElement, key: str, context: ElementContext) -> None:
        """
        Store an input element in the context after identifying it
        
        Args:
            element: WebElement to store
            key: Key to use for storing in context
            context: ElementContext to store the element
        """
        try:
            # Identify input properties
            input_info = self.identifier.identify_input_type(element)
            
            # Check for associated button and store it in metadata
            associated_button_info = None
            if input_info.get('has_action_button') and input_info.get('action_button_element'):
                associated_button_info = {
                    'element': input_info.get('action_button_element'),
                    'type': input_info.get('action_button_type'),
                    'text': input_info.get('action_button_text'),
                    'disabled': input_info.get('action_button_element').get_attribute('disabled') is not None
                }
            
            # Create ElementInfo
            element_info = ElementInfo(
                element=element,
                element_type='input',
                application_type=input_info.get('application_type'),
                data_attr_id=input_info.get('data_attr_id') or key if key.startswith('data_attr_') else None,
                metadata={
                    'input_type': input_info.get('input_type'),
                    'size': input_info.get('size'),
                    'disabled': input_info.get('disabled'),
                    'readonly': input_info.get('readonly'),
                    'clearable': input_info.get('clearable'),
                    'has_prefix': input_info.get('has_prefix'),
                    'has_suffix': input_info.get('has_suffix'),
                    'has_action_button': input_info.get('has_action_button', False),
                    'action_button_type': input_info.get('action_button_type'),
                    'action_button_text': input_info.get('action_button_text'),
                    'required': input_info.get('required'),
                    'placeholder': input_info.get('placeholder'),
                    'label': input_info.get('label'),
                    **input_info.get('metadata', {})
                }
            )
            
            # Store associated button info if found
            if associated_button_info:
                element_info.metadata['associated_button'] = associated_button_info
            
            # Use data_attr_id as key if available, otherwise use provided key
            # But if key is already a simple type (like "search", "text"), prefer that
            context_key = input_info.get('data_attr_id') or key
            # If key is a simple type identifier and no data-attr-id, use the key as-is
            if not input_info.get('data_attr_id') and key in ['text', 'password', 'email', 'number', 'tel', 'url', 'search', 'textarea']:
                context_key = key
            context.store_element(context_key, element_info)
        except Exception as e:
            print(f"Error storing input in context: {str(e)}")
    
    def _generate_context_key(self, element: WebElement, fallback: str) -> str:
        """
        Generate a context key for an input element
        
        Args:
            element: WebElement to generate key for
            fallback: Fallback key if data-attr-id is not available
            
        Returns:
            Generated key string
        """
        try:
            # Try data-atr-id first
            data_attr_id = element.get_attribute('data-atr-id')
            if data_attr_id:
                return data_attr_id
            
            # Try data-attr-id as fallback
            data_attr_id = element.get_attribute('data-attr-id')
            if data_attr_id:
                return data_attr_id
            
            # Try placeholder or aria-label
            placeholder = element.get_attribute('placeholder')
            if placeholder:
                return f"{fallback}_{placeholder}".replace(' ', '_').lower()[:30]
            
            aria_label = element.get_attribute('aria-label')
            if aria_label:
                return f"{fallback}_{aria_label}".replace(' ', '_').lower()[:30]
            
            return fallback
        except:
            return fallback

